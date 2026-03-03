from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import faiss
import numpy as np
import json
import re
from sentence_transformers import SentenceTransformer

# -----------------------------
# Config
# -----------------------------
MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = "data/faiss.index"
META_PATH = "data/meta.json"

app = FastAPI()

print("Loading model...")
model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index...")
index = faiss.read_index(INDEX_PATH)

print("Loading metadata...")
with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)


# -----------------------------
# Test Type Mapping
# -----------------------------
TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behaviour",
    "S": "Simulations"
}


# -----------------------------
# Models
# -----------------------------
class QueryRequest(BaseModel):
    query: str


# -----------------------------
# Utilities
# -----------------------------
def extract_keywords(text):
    return set(re.findall(r'\b[a-z]{4,}\b', text.lower()))


def is_job_description(text):
    return len(text.split()) > 50


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

    knowledge_intent = any(word in text_lower for word in [
        "technical","programming","knowledge","experience","skills","expert"
    ])

    behavioral_intent = any(word in text_lower for word in [
        "leadership","behavior","personality","competency"
    ])

    return {
        "roles": detected_roles,
        "knowledge": knowledge_intent,
        "behavioral": behavioral_intent
    }


def build_refined_query(original_query):
    structured = extract_structured_query(original_query)
    components = [original_query]

    if structured["roles"]:
        components.append("Role: " + " ".join(structured["roles"]))

    if structured["knowledge"]:
        components.append("Knowledge test required")

    if structured["behavioral"]:
        components.append("Behavioral competency assessment required")

    return "\n".join(components), structured


# -----------------------------
# Hybrid Reranking
# -----------------------------
def rerank(query, candidates, structured, jd_mode=False):

    query_lower = query.lower()
    query_keywords = set(query_lower.split())

    for item in candidates:
        boost = 0

        slug = item["url"].split("/")[-1].replace("-", " ").lower()
        slug_tokens = set(slug.split())

        # Strong slug overlap
        boost += 0.7 * len(slug_tokens & query_keywords)

        # Skill overlap
        for skill in item.get("skills", []):
            if skill.lower() in query_lower:
                boost += 0.4

        # Role boost
        for role in structured["roles"]:
            if role in slug or role in item["name"].lower():
                boost += 0.6

        # Knowledge vs Behavioral alignment
        if structured["knowledge"] and "K" in item.get("test_type", []):
            boost += 0.3

        if structured["behavioral"] and any(t in item.get("test_type", []) for t in ["P","C"]):
            boost += 0.3

        item["score"] += boost

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates


# -----------------------------
# Core Recommendation Logic
# -----------------------------
def generate_recommendations(query):

    jd_mode = is_job_description(query)
    refined_query, structured = build_refined_query(query)

    # Dense retrieval (top 100)
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

    # Rerank
    candidates = rerank(query, candidates, structured, jd_mode)

    top10 = candidates[:10]

    formatted = []

    for item in top10:
        formatted.append({
            "url": item.get("url"),
            "name": item.get("name"),
            "adaptive_support": item.get("adaptive_support"),
            "description": item.get("description"),
            "duration": item.get("duration_minutes"),
            "remote_support": item.get("remote_support"),
            "test_type": [
                TEST_TYPE_MAP.get(t, t)
                for t in item.get("test_type", [])
            ]
        })

    return formatted


# -----------------------------
# API Endpoint (JSON)
# -----------------------------
@app.post("/recommend")
def recommend(request: QueryRequest):

    results = generate_recommendations(request.query)

    return {
        "recommended_assessments": results
    }


# -----------------------------
# Web UI
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>SHL Assessment Recommendation Tool</title>
        </head>
        <body>
            <h2>SHL Assessment Recommendation Tool</h2>
            <form action="/recommend_web" method="post">
                <textarea name="query" rows="8" cols="80" placeholder="Enter job description or skills..."></textarea><br><br>
                <button type="submit">Recommend</button>
            </form>
        </body>
    </html>
    """


@app.post("/recommend_web", response_class=HTMLResponse)
def recommend_web(query: str = Form(...)):

    results = generate_recommendations(query)

    html = "<h3>Top 10 Recommendations:</h3><ul>"

    for item in results:
        html += f"<li><a href='{item['url']}' target='_blank'>{item['name']}</a></li>"

    html += "</ul><br><a href='/'>Back</a>"

    return html
