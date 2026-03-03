import json
import faiss
import numpy as np
import pandas as pd
import re
import os
from sentence_transformers import SentenceTransformer

DATASET_PATH = "/home/ansh/Downloads/Gen_AI_Dataset.xlsx"
INDEX_PATH = "data/faiss.index"
META_PATH = "data/meta.json"
OUTPUT_CSV = "submission.csv"
MODEL_NAME = "all-MiniLM-L6-v2"


# -----------------------------
# URL Normalization
# -----------------------------
def normalize_url(url):
    url = url.strip().lower()
    if "://" in url:
        url = url.split("://")[1]
    if "shl.com" in url:
        url = url.split("shl.com")[-1]
    return url.strip("/")


# -----------------------------
# Keyword Extractor
# -----------------------------
def extract_keywords(text):
    return set(re.findall(r'\b[a-z]{4,}\b', text.lower()))


# -----------------------------
# JD Detection
# -----------------------------
def is_job_description(text):
    return len(text.split()) > 50


# -----------------------------
# Structured Query Extraction
# -----------------------------
def extract_structured_query(text):

    text_lower = text.lower()

    role_keywords = [
        "developer","engineer","manager","sales",
        "executive","analyst","assistant",
        "administrator","accountant",
        "marketing","writer","designer",
        "bank","finance","technician"
    ]

    detected_roles = [r for r in role_keywords if r in text_lower]

    seniority = None
    if "senior" in text_lower:
        seniority = "senior"
    elif "junior" in text_lower or "entry" in text_lower:
        seniority = "junior"

    knowledge_intent = any(word in text_lower for word in [
        "technical","programming","knowledge",
        "experience","skills","expert"
    ])

    behavioral_intent = any(word in text_lower for word in [
        "leadership","behavior","personality","competency"
    ])

    return {
        "roles": detected_roles,
        "seniority": seniority,
        "knowledge": knowledge_intent,
        "behavioral": behavioral_intent
    }


# -----------------------------
# Refined Query Builder
# -----------------------------
def build_refined_query(original_query):

    structured = extract_structured_query(original_query)

    components = [original_query]

    if structured["roles"]:
        components.append("Role: " + " ".join(structured["roles"]))

    if structured["seniority"]:
        components.append("Seniority: " + structured["seniority"])

    if structured["knowledge"]:
        components.append("Knowledge test required")

    if structured["behavioral"]:
        components.append("Behavioral competency assessment required")

    return "\n".join(components), structured


# -----------------------------
# Hybrid Reranker
# -----------------------------
def rerank(query, candidates):

    query_lower = query.lower()
    query_tokens = set(re.findall(r'\w+', query_lower))

    for item in candidates:

        slug = item["url"].split("/")[-1].replace("-", " ").lower()
        slug_tokens = set(re.findall(r'\w+', slug))

        name_tokens = set(re.findall(r'\w+', item["name"].lower()))

        # lexical similarity score
        lexical_score = (
            len(slug_tokens & query_tokens) * 1.5 +
            len(name_tokens & query_tokens) * 1.0
        )

        # controlled blending
        item["score"] = (0.7 * item["score"]) + (0.3 * lexical_score)

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


# -----------------------------
# Load Model + Index
# -----------------------------
print("Loading model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")
index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)

meta_urls = [normalize_url(item["url"]) for item in metadata]


# -----------------------------
# Load Train + Test
# -----------------------------
train_df = pd.read_excel(DATASET_PATH, sheet_name="Train-Set")
test_df = pd.read_excel(DATASET_PATH, sheet_name="Test-Set")


# -----------------------------
# Evaluation (Train)
# -----------------------------
def evaluate():

    total = 0
    raw_hits = 0
    final_hits = 0

    for _, row in train_df.iterrows():

        query = row["Query"]
        true_url = normalize_url(row["Assessment_url"])
        true_url_norm = normalize_url(true_url)

        

        if true_url not in meta_urls:
            continue

        total += 1

        jd_mode = is_job_description(query)
        refined_query, structured = build_refined_query(query)

        query_embedding = model.encode(
            "Represent this sentence for searching relevant assessments: " + refined_query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.expand_dims(query_embedding, axis=0)
        scores, indices = index.search(query_embedding, 20)
        top100_urls = [
            normalize_url(metadata[idx]["url"])
            for idx in indices[0]
        ]

        if true_url_norm not in top100_urls:
            print("MISS in top100:", query)

        raw_top10 = [
            normalize_url(metadata[idx]["url"])
            for idx in indices[0][:10]
        ]

        if true_url in raw_top10:
            raw_hits += 1

        candidates = []
        for rank, idx in enumerate(indices[0]):
            item = metadata[idx].copy()
            item["score"] = float(scores[0][rank])
            candidates.append(item)

        candidates = rerank(query, candidates)

        final_top10 = [
            normalize_url(item["url"])
            for item in candidates[:10]
        ]

        if true_url in final_top10:
            final_hits += 1

    print("\n--- TEST Evaluation ---")
    print("Total evaluated:", total)
    print("Raw Recall@10:", round(raw_hits / total, 4))
    print("Final Recall@10:", round(final_hits / total, 4))


# -----------------------------
# Submission Generator (Test)
# -----------------------------
def generate_submission():

    results_rows = []

    for _, row in test_df.iterrows():

        query = row["Query"]

        jd_mode = is_job_description(query)
        refined_query, structured = build_refined_query(query)

        query_embedding = model.encode(
            refined_query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.expand_dims(query_embedding, axis=0)
        scores, indices = index.search(query_embedding, 100)

        candidates = []
        for rank, idx in enumerate(indices[0]):
            item = metadata[idx].copy()
            item["score"] = float(scores[0][rank])
            candidates.append(item)

        candidates = rerank(query, candidates)

        top10 = candidates[:10]

        for item in top10:
            results_rows.append({
                "Query": query,
                "Assessment_url": item["url"]
            })

    submission_df = pd.DataFrame(results_rows)
    submission_df.to_csv(OUTPUT_CSV, index=False)

    print("\nSubmission file generated:", OUTPUT_CSV)


if __name__ == "__main__":
    evaluate()
    generate_submission()
