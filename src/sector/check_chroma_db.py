import chromadb, os, math
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv('.env')
except: pass

CHROMA_PERSIST_DIR = os.getenv('CHROMA_PERSIST_DIR', './output/chroma_db')
chroma = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection = chroma.get_or_create_collection(name='sec_company_vectors', metadata={'hnsw:space': 'cosine'})

results = collection.get(limit=3, include=['embeddings', 'metadatas'])

print('Total docs:', collection.count())
print('Embeddings in result:', len(results.get('embeddings', [])))
print()

for i in range(min(3, len(results['ids']))):
    doc_id = results['ids'][i]
    meta = results['metadatas'][i]
    emb = results['embeddings'][i]
    
    print(f'Doc {i+1}: {doc_id}')
    print(f'  Metadata: ticker={meta.get("ticker")}, sector={meta.get("sector")}')
    print(f'  Embedding: dim={len(emb)}, first 3={[round(x,4) for x in emb[:3]]}')
    norm = math.sqrt(sum(x*x for x in emb))
    print(f'  L2 norm: {norm:.4f}')
    print()