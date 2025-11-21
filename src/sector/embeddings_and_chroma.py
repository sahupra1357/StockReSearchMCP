# embeddings_and_chroma.py
import os
import time
import math
import logging
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from typing import List

logging.basicConfig(level=logging.INFO)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY must be set in environment")

client = OpenAI(api_key=OPENAI_KEY)

# Chroma client (duckdb+parquet persistence)
chroma = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=os.getenv("CHROMA_PERSIST_DIR", "./db"),
))

collection = chroma.get_or_create_collection(
    name="sec_company_vectors",
    metadata={"hnsw:space": "cosine"}
)

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "64"))
RETRY_SLEEP = 2

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Batch-call OpenAI embeddings with basic retry.
    Uses OpenAI python client -> OpenAI.embeddings.create
    """
    out = []
    n = len(texts)
    for i in range(0, n, BATCH_SIZE):
        batch = texts[i:i+BATCH_SIZE]
        success = False
        attempt = 0
        while not success and attempt < 5:
            try:
                resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
                # resp.data is list of embeddings objects
                out.extend([r.embedding for r in resp.data])
                success = True
            except Exception as e:
                attempt += 1
                logging.warning(f"Embedding batch failed (attempt {attempt}): {e}")
                time.sleep(RETRY_SLEEP * attempt)
        if not success:
            # append zero vectors as placeholders (shouldn't happen often)
            logging.error("Persistent embedding failure; appending zero vectors")
            out.extend([[0.0]*1536 for _ in batch])
    return out

def add_to_chroma(ids, docs, embeddings, metadatas=None):
    """
    Add or update documents in chroma collection
    """
    # Upsert: remove if exists and add new (chroma supports add with existing ids)
    collection.add(
        ids=ids,
        documents=docs,
        embeddings=embeddings,
        metadatas=metadatas or [{}]*len(ids)
    )
    chroma.persist()

def build_batch_records(records):
    """
    Input: list of dicts: {"id": ticker, "text": text, "meta": {...}}
    Will embed and write to chroma in batches.
    """
    texts = [r["text"] for r in records]
    ids = [r["id"] for r in records]
    metas = [r.get("meta", {}) for r in records]
    embeddings = embed_texts(texts)
    add_to_chroma(ids, texts, embeddings, metas)
    logging.info(f"Indexed batch of {len(records)} docs")
