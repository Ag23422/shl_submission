import json
import faiss
import numpy as np
import pandas as pd
import re
from sentence_transformers import SentenceTransformer

DATASET_PATH = "/home/ansh/Downloads/Gen_AI Dataset.xlsx"
INDEX_PATH = "faiss.index"
META_PATH = "meta.json"
OUTPUT_CSV = "submission.csv"
MODEL_NAME = "BAAI/bge-base-en-v1.5"


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
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    return set(words)


# -----------------------------
# Hybrid Reranking
# -----------------------------
# -----------------------------
# JD Detection
# -----------------------------
def is_job_description(text):
    return len(text.split()) > 50


# -----------------------------
# Structured Signal Extraction
# -----------------------------
def extract_structured_query(text):

    text_lower = text.lower()

    role_keywords = [
        "developer", "engineer", "manager", "sales",
        "executive", "analyst", "assistant",
        "administrator", "accountant",
        "marketing", "writer", "designer",
        "bank", "finance", "technician"
    ]

    detected_roles = [r for r in role_keywords if r in text_lower]

    seniority = None
    if "senior" in text_lower:
        seniority = "senior"
    elif "junior" in text_lower or "entry" in text_lower:
        seniority = "junior"

    knowledge_intent = any(word in text_lower for word in [
        "technical", "programming", "knowledge",
        "experience", "skills", "expert"
    ])

    behavioral_intent = any(word in text_lower for word in [
        "leadership", "behavior", "personality",
        "competency", "communication"
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

def rerank(query, candidates, structured, jd_mode=False):

    query_lower = query.lower()
    query_keywords = extract_keywords(query)

    for item in candidates:
        boost = 0

        profile_hint = item["url"].split("/")[-1].replace("-", " ").lower()

        # Strong role match boost
        for role in structured["roles"]:
            if role in profile_hint or role in item["name"].lower():
                boost += 0.40 if jd_mode else 0.30

        # Skill overlap boost
        for skill in item.get("skills", []):
            if skill.lower() in query_lower:
                boost += 0.25 if jd_mode else 0.15

        # Job family boost
        if item.get("job_family"):
            if item["job_family"].lower() in query_lower:
                boost += 0.30

        # Knowledge vs Behavioral intent boost
        if structured["knowledge"]:
            if "K" in item.get("test_type", []):
                boost += 0.20

        if structured["behavioral"]:
            if any(t in item.get("test_type", []) for t in ["P", "C"]):
                boost += 0.20

        # Short test boost for quick requests
        if "quick" in query_lower or "short" in query_lower:
            if item.get("duration_minutes") and item["duration_minutes"] <= 15:
                boost += 0.15

        item["score"] += boost

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates

# -----------------------------
# Load Model + Index
# -----------------------------
print("Loading model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading index...")
index = faiss.read_index(INDEX_PATH)

with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)


# -----------------------------
# Load Test Set
# -----------------------------
test_df = pd.read_excel(DATASET_PATH, sheet_name="Test-Set")

results_rows = []

for _, row in test_df.iterrows():

    query = row["Query"]

    jd_mode = is_job_description(query)

    refined_query, structured = build_refined_query(query)

    query_embedding = model.encode(
        "Represent this sentence for searching relevant assessments: " + refined_query,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    query_embedding = np.expand_dims(query_embedding, axis=0)

    scores, indices = index.search(query_embedding, 20)

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