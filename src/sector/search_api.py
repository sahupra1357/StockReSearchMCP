# search_api.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .embeddings_and_chroma import embed_texts, collection

app = FastAPI(title="SEC Category Search API")

class QueryReq(BaseModel):
    query: str
    k: int = 10

@app.post("/search")
def search(req: QueryReq):
    if not req.query:
        raise HTTPException(400, "query is required")
    q_emb = embed_texts([req.query])[0]
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=req.k,
        include=["ids", "distances", "documents", "metadatas"]
    )
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
