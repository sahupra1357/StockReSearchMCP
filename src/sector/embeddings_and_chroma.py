# embeddings_and_chroma.py
import os
import time
import math
# import logging
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from typing import List
from pathlib import Path
from sector.logging_log import logger

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in project root (2 levels up from this file)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # Try current directory
except ImportError:
    pass  # python-dotenv not required, will use system env vars

# logging.basicConfig(level=logging.INFO)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY must be set in environment")

client = OpenAI(api_key=OPENAI_KEY)

# Chroma persistent client (stores data permanently on disk)
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)

chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

collection = chroma.get_or_create_collection(
    name="sec_company_vectors",
    metadata={"hnsw:space": "cosine"}
)

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "64"))
RETRY_SLEEP = 2

# Max tokens for text-embedding-3-small is 8191
# Approximate: 1 token ~= 4 characters, so max ~32k chars
# Use conservative limit to be safe
MAX_TEXT_LENGTH = 30000  # ~7500 tokens
CHUNK_OVERLAP = 500  # Overlap between chunks to maintain context

def chunk_text(text: str, max_length: int = MAX_TEXT_LENGTH, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into multiple chunks if it exceeds max_length.
    Tries to split at sentence boundaries with overlap between chunks.
    
    Returns:
        List of text chunks, or [original text] if under limit
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Calculate end position
        end = start + max_length
        
        if end >= len(text):
            # Last chunk
            chunks.append(text[start:])
            break
        
        # Try to find a sentence boundary near the end
        chunk_text = text[start:end]
        split_pos = -1
        
        for delimiter in ['. ', '.\n', '! ', '? ']:
            pos = chunk_text.rfind(delimiter)
            if pos > max_length * 0.7:  # At least 70% of chunk
                split_pos = pos + len(delimiter)
                break
        
        if split_pos > 0:
            chunks.append(text[start:start + split_pos])
            # Move start with overlap
            start = start + split_pos - overlap
        else:
            # No good boundary, just split at max_length
            chunks.append(text[start:end])
            start = end - overlap
    
    return chunks

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Batch-call OpenAI embeddings with basic retry.
    Texts should already be chunked to appropriate size.
    Uses OpenAI python client -> OpenAI.embeddings.create
    """
    # Validate all texts are within limits (should be pre-chunked)
    truncated_texts = []
    for idx, text in enumerate(texts):
        if len(text) > MAX_TEXT_LENGTH:
            logger.warning(f"Text {idx} still too long ({len(text)} chars), emergency truncating to {MAX_TEXT_LENGTH}")
            # Emergency truncation (shouldn't happen if chunking works)
            truncated_texts.append(text[:MAX_TEXT_LENGTH])
        else:
            truncated_texts.append(text)
    
    out = []
    n = len(truncated_texts)
    for i in range(0, n, BATCH_SIZE):
        batch = truncated_texts[i:i+BATCH_SIZE]
        success = False
        attempt = 0
        while not success and attempt < 5:
            try:
                resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
                # resp.data is list of embeddings objects
                out.extend([r.embedding for r in resp.data])
                success = True
            except Exception as e:
                error_msg = str(e)
                attempt += 1
                logger.warning(f"Embedding batch failed (attempt {attempt}): {e}")
                
                # If still getting 400 error, reduce batch size further
                if "maximum context length" in error_msg and attempt < 5:
                    logger.warning("Reducing text size further due to token limit...")
                    # Reduce each text in batch by 50%
                    batch = [t[:len(t) // 2] for t in batch]
                
                time.sleep(RETRY_SLEEP * attempt)
        if not success:
            # append zero vectors as placeholders (shouldn't happen often)
            logger.error(f"Persistent embedding failure for batch {i}; appending zero vectors")
            out.extend([[0.0]*1536 for _ in batch])
    return out

def add_to_chroma(ids, docs, embeddings, metadatas=None):
    """
    Add or update documents in chroma collection.
    Uses upsert to handle duplicates - updates if exists, inserts if new.
    PersistentClient automatically persists to disk, no manual persist() needed.
    """
    try:
        # Try upsert first - updates existing or inserts new
        collection.upsert(
            ids=ids,
            documents=docs,
            embeddings=embeddings,
            metadatas=metadatas or [{}]*len(ids)
        )
        logger.debug(f"Upserted {len(ids)} documents (may have updated existing)")
    except Exception as e:
        logger.error(f"Failed to upsert documents: {e}")
        # Try regular add as fallback
        try:
            collection.add(
                ids=ids,
                documents=docs,
                embeddings=embeddings,
                metadatas=metadatas or [{}]*len(ids)
            )
            logger.info(f"Added {len(ids)} documents using fallback add()")
        except Exception as e2:
            logger.error(f"Both upsert and add failed: {e2}")
            raise

def build_batch_records(records):
    """
    Input: list of dicts: {"id": ticker, "documents": text, "metadatas": {...}}
    Will embed and write to chroma in batches.
    Automatically chunks long texts and creates multiple entries.
    """
    all_texts = []
    all_ids = []
    all_metas = []
    
    for r in records:
        text = r["documents"]
        base_id = r["id"]
        meta = r.get("metadatas", {})
        
        # Check if text needs chunking
        if len(text) > MAX_TEXT_LENGTH:
            chunks = chunk_text(text)
            logger.debug(f"Split {base_id} into {len(chunks)} chunks ({len(text)} total chars)")
            
            # Create separate entries for each chunk
            for i, chunk in enumerate(chunks):
                all_texts.append(chunk)
                all_ids.append(f"{base_id}_chunk{i}")
                chunk_meta = meta.copy()
                chunk_meta["chunk_index"] = i
                chunk_meta["total_chunks"] = len(chunks)
                all_metas.append(chunk_meta)
        else:
            # Single entry for short text
            all_texts.append(text)
            all_ids.append(base_id)
            all_metas.append(meta)
    
    # Log text lengths for debugging
    for i, text in enumerate(all_texts):
        logger.debug(f"Record {all_ids[i]}: {len(text)} chars (~{len(text)//4} tokens)")
    
    embeddings = embed_texts(all_texts)
    logger.info(f"Built embeddings for {len(all_ids)} entries (from {len(records)} original records)")
    add_to_chroma(all_ids, all_texts, embeddings, all_metas)
    logger.info(f"Indexed {len(all_ids)} document entries")
