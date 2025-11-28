#!/usr/bin/env python3
"""
Query and inspect ChromaDB contents.
Usage:
    # 1. Count total documents
    python src/sector/query_chroma.py count

    # 2. List all tickers
    python src/sector/query_chroma.py tickers

    # 3. List first 10 documents (with preview)
    python src/sector/query_chroma.py list

    # 4. List all documents
    python src/sector/query_chroma.py list 100

    # 5. Get specific document by ID
    python src/sector/query_chroma.py get NVDA

    # 6. Get a specific chunk
    python src/sector/query_chroma.py get NVDA_chunk0

    # 7. Semantic search for companies
    python src/sector/query_chroma.py search "artificial intelligence chips"
    python src/sector/query_chroma.py search "biotechnology companies"
    python src/sector/query_chroma.py search "electric vehicles"    
"""

import os
import sys
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

import chromadb
from embeddings_and_chroma import collection, embed_texts

def list_all_documents(limit=None):
    """List all documents in the collection."""
    try:
        results = collection.get()
        total = len(results['ids'])
        
        print(f"\n{'='*80}")
        print(f"CHROMADB CONTENTS - Total Documents: {total}")
        print(f"{'='*80}\n")
        
        display_limit = limit or total
        for i in range(min(display_limit, total)):
            doc_id = results['ids'][i]
            doc_text = results['documents'][i]
            metadata = results['metadatas'][i] if results['metadatas'] else {}
            
            print(f"ID: {doc_id}")
            print(f"Metadata: {metadata}")
            print(f"Text preview: {doc_text[:200]}...")
            print(f"Text length: {len(doc_text)} chars")
            print("-" * 80)
        
        if total > display_limit:
            print(f"\n... and {total - display_limit} more documents")
            print(f"Use: python query_chroma.py list {total} to see all\n")
            
    except Exception as e:
        print(f"Error listing documents: {e}")

def count_documents():
    """Count total documents in collection."""
    try:
        results = collection.get()
        total = len(results['ids'])
        print(f"\nTotal documents in ChromaDB: {total}\n")
        
        # Count by ticker (excluding chunks)
        tickers = set()
        chunks = 0
        for doc_id in results['ids']:
            if '_chunk' in doc_id:
                ticker = doc_id.split('_chunk')[0]
                tickers.add(ticker)
                chunks += 1
            else:
                tickers.add(doc_id)
        
        print(f"Unique tickers: {len(tickers)}")
        print(f"Chunked documents: {chunks}")
        print(f"Single documents: {total - chunks}\n")
        
    except Exception as e:
        print(f"Error counting documents: {e}")

def get_document(doc_id):
    """Get a specific document by ID. Automatically combines chunks if ticker has multiple."""
    try:
        # First, check if this exact ID exists
        results = collection.get(ids=[doc_id])
        
        if results['ids']:
            # Single document found
            print(f"\n{'='*80}")
            print(f"DOCUMENT: {doc_id}")
            print(f"{'='*80}\n")
            
            doc_text = results['documents'][0]
            metadata = results['metadatas'][0] if results['metadatas'] else {}
            
            print(f"Metadata: {metadata}")
            print(f"\nFull Text ({len(doc_text)} chars):")
            print("-" * 80)
            print(doc_text)
            print("-" * 80)
            print()
            return
        
        # Not found - check if there are chunks for this ticker
        all_docs = collection.get()
        
        # Find all chunks for this ticker
        chunk_ids = sorted([id for id in all_docs['ids'] if id.startswith(doc_id + '_chunk')])
        
        if chunk_ids:
            print(f"\n{'='*80}")
            print(f"DOCUMENT: {doc_id} (Combined from {len(chunk_ids)} chunks)")
            print(f"{'='*80}\n")
            
            # Fetch all chunks
            chunk_results = collection.get(ids=chunk_ids)
            
            # Combine chunks in order
            combined_text = ""
            total_chars = 0
            
            for i, chunk_id in enumerate(chunk_results['ids']):
                chunk_text = chunk_results['documents'][i]
                metadata = chunk_results['metadatas'][i] if chunk_results['metadatas'] else {}
                
                print(f"Chunk {i}: {chunk_id} ({len(chunk_text)} chars)")
                print(f"  Metadata: {metadata}")
                
                combined_text += chunk_text
                if i < len(chunk_results['ids']) - 1:
                    combined_text += "\n\n[... CHUNK BOUNDARY ...]\n\n"
                
                total_chars += len(chunk_text)
            
            print(f"\nCombined Text ({total_chars} total chars):")
            print("-" * 80)
            print(combined_text)
            print("-" * 80)
            print()
            return
        
        # No exact match and no chunks found
        print(f"\nDocument '{doc_id}' not found.\n")
        print(f"Available tickers (showing first 20):")
        tickers = set()
        for id in all_docs['ids'][:50]:
            ticker = id.split('_chunk')[0] if '_chunk' in id else id
            tickers.add(ticker)
        print(f"  {', '.join(sorted(tickers)[:20])}")
        print()
        
    except Exception as e:
        print(f"Error getting document: {e}")

def semantic_search(query, n_results=5):
    """Perform semantic search on the collection."""
    try:
        print(f"\nSearching for: '{query}'")
        print(f"{'='*80}\n")
        
        # Get query embedding
        query_embedding = embed_texts([query])[0]
        
        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        print(results)
        print("\n\n")
        print(results.keys())
        if not results['ids'][0]:
            print("No results found.\n")
            return
        
        print(f"Found {len(results['ids'][0])} results:\n")
        
        for i in range(len(results['ids'][0])):
            doc_id = results['ids'][0][i]
            doc_text = results['documents'][0][i]
            distance = results['distances'][0][i] if results.get('distances') else None
            print("^^^^^^^^ ",distance)
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            
            print(f"Rank {i+1}: {doc_id}")
            if distance is not None:
                similarity = 1 - distance
                print(f"Similarity: {similarity:.4f}")
            print(f"Metadata: {metadata.get('ticker', 'N/A')}, Sector: {metadata.get('sector', 'N/A')}, Industry: {metadata.get('industry', 'N/A')}")
            # print(f"Text preview: {doc_text[:300]}...")
            print("-" * 80)
        
        print()
        
    except Exception as e:
        print(f"Error searching: {e}")

def list_tickers():
    """List all unique tickers in the database."""
    try:
        results = collection.get()
        
        # Extract unique tickers
        tickers = set()
        for doc_id in results['ids']:
            if '_chunk' in doc_id:
                ticker = doc_id.split('_chunk')[0]
            else:
                ticker = doc_id
            tickers.add(ticker)
        
        tickers = sorted(tickers)
        
        print(f"\n{'='*80}")
        print(f"TICKERS IN DATABASE ({len(tickers)} total)")
        print(f"{'='*80}\n")
        
        # Display in columns
        for i in range(0, len(tickers), 5):
            row = tickers[i:i+5]
            print("  ".join(f"{t:10}" for t in row))
        
        print()
        
    except Exception as e:
        print(f"Error listing tickers: {e}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_all_documents(limit)
    
    elif command == "count":
        count_documents()
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: python query_chroma.py get <ID>")
            return
        doc_id = sys.argv[2]
        get_document(doc_id)
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python query_chroma.py search <query>")
            return
        query = " ".join(sys.argv[2:])
        n_results = 2
        semantic_search(query, n_results)
    
    elif command == "tickers":
        list_tickers()
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
