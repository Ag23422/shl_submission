import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

DATA_PATH = "data/processed_catalog.json"
INDEX_PATH = "data/faiss.index"
META_PATH = "data/meta.json"
MODEL_NAME = "BAAI/bge-base-en-v1.5"


# -----------------------------
# Clean Skills
# -----------------------------
def clean_skills(skills):
    blacklist = {
        "The following areas are covered",
        "All rights reserved",
        "Page",
        "English",
        "Number of Sittings",
        "Example Questions Example Reports",
        "Overall Score One",
        "Multiple Choice",
        "CTT Information Technology Programming"
    }

    cleaned = []

    for s in skills:
        s = s.strip()
        if len(s) < 3:
            continue
        if s in blacklist:
            continue
        if any(word in s.lower() for word in [
            "page", "copyright", "reserved",
            "sittings", "score", "english"
        ]):
            continue
        cleaned.append(s)

    return list(set(cleaned))


# -----------------------------
# Embedding Text Builder (CLEAN)
# -----------------------------
def build_embedding_text(item):

    skills = clean_skills(item.get("skills", []))
    skills_text = ", ".join(skills)

    slug = item['url'].split('/')[-1].replace('-', ' ')

    text = f"""
    Assessment Name: {item.get('name', '')}

    Slug: {slug}

    Description:
    {item.get('description', '')}

    Skills:
    {skills_text}
    """
    return text.strip()


# -----------------------------
# Build Index
# -----------------------------
def build():

    if not os.path.exists(DATA_PATH):
        print("processed_catalog.json not found.")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("Loading model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Preparing texts...")
    texts = [build_embedding_text(item) for item in data]

    print("Encoding...")
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print("Saving index...")
    faiss.write_index(index, INDEX_PATH)

    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Index built. Total vectors:", index.ntotal)


if __name__ == "__main__":
    build()