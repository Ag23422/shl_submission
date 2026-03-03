SHL GenAI Assessment Recommendation System
Overview

This project implements a web-based Retrieval-Augmented Generation (RAG) system that recommends relevant SHL assessments based on user queries. The system supports both short skill-based queries and full Job Descriptions (JD).

It combines semantic vector search with structured lexical alignment to ensure strong taxonomy mapping with SHL’s product catalog.

Key Features

Semantic search using SentenceTransformers (BAAI/bge-base-en-v1.5)

FAISS vector indexing with cosine similarity

Hybrid retrieval (semantic + lexical blending)

PDF parsing using PyMuPDF for structured skill extraction

FastAPI REST API

Minimal web interface for interactive usage

Render deployment ready

CSV submission generator

Evaluation using Mean Recall@10

System Architecture

Catalog Scraping
The SHL product catalog was scraped to collect:

Assessment name

URL

Description

Skills

Duration

Remote support

Adaptive support

Test type

PDF Parsing
Product Fact Sheet PDFs were downloaded and parsed using PyMuPDF to extract structured attributes such as:

Job family

Product category

Skills

Embedding Generation
Cleaned assessment text (name + description + skills) was embedded using SentenceTransformers.

Vector Indexing
Embeddings were indexed using FAISS (IndexFlatIP with normalized vectors for cosine similarity).

Hybrid Retrieval

Dense retrieval retrieves top 100 candidates.

Lightweight lexical blending adjusts scores using token overlap between query and assessment slug/name/skills.

API Deployment
FastAPI serves:

JSON API endpoint

Web interface endpoint

Project Structure

shl_project/
│
├── api/
│ └── main.py
│
├── data/
│ ├── processed_catalog.json
│ ├── faiss.index
│ └── meta.json
│
├── retrieval/
│ ├── build_faiss.py
│ ├── evaluator.py
│ └── submission_generator.py
│
├── requirements.txt
└── README.md

Installation (Local)

Install dependencies:

pip install -r requirements.txt

Run locally:

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

Access:

Web Interface:
http://localhost:8000/

Swagger Docs:
http://localhost:8000/docs

Deployment (Render – Python Environment)

Environment: Python

Build Command:
pip install -r requirements.txt

Start Command:
uvicorn api.main:app --host 0.0.0.0 --port $PORT

API Endpoint

POST /recommend

Request:

{
"query": "Content Writer required with strong SEO knowledge"
}

Response:

{
"recommended_assessments": [
{
"url": "...",
"name": "...",
"adaptive_support": "...",
"description": "...",
"duration": 30,
"remote_support": "...",
"test_type": ["Knowledge & Skills"]
}
]
}

Evaluation

Metric Used: Mean Recall@10

Recall@10 = (Number of relevant assessments in top 10) / (Total relevant assessments for the query)

Mean Recall@10 = (1/N) × Σ Recall@10_i

Where:

N = total number of queries

Recall@10_i = recall for query i

The Train set is used for iteration and tuning.
The Test set is used for final submission evaluation.

Design Decisions

Dense retrieval ensures semantic understanding.

Lexical blending ensures slug-level alignment with dataset ground truth.

Top-100 retrieval increases recall ceiling.

Lightweight reranking avoids destructive score distortion.

Structured output strictly follows SHL-required schema.

Web-based interface satisfies “web-based RAG tool” requirement
