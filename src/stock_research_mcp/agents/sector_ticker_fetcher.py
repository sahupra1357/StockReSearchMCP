"""Helper module to query ChromaDB for sector-based stock tickers."""

import os
import sys
import logging
from typing import List, Optional

# Add sector directory to path if needed
sector_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sector")
if os.path.exists(sector_path) and sector_path not in sys.path:
    sys.path.insert(0, sector_path)

try:
    # Import ChromaDB components - will use PersistentClient from embeddings_and_chroma
    from sector.embeddings_and_chroma import embed_texts, collection, CHROMA_PERSIST_DIR
    HAS_CHROMA = True
    logging.info(f"ChromaDB loaded from: {CHROMA_PERSIST_DIR}")
except ImportError as e:
    HAS_CHROMA = False
    logging.warning(f"ChromaDB not available: {e}. Falling back to hardcoded sector mappings.")


logger = logging.getLogger(__name__)


class SectorTickerFetcher:
    """
    Fetches stock tickers for a given sector using ChromaDB semantic search.
    Falls back to hardcoded mappings if ChromaDB is not available.
    """
    
    def __init__(self, use_chroma: bool = True):
        """
        Initialize the sector ticker fetcher.
        
        Args:
            use_chroma: If True, attempt to use ChromaDB for semantic search
        """
        self.use_chroma = use_chroma and HAS_CHROMA
        
        if self.use_chroma:
            logger.info("SectorTickerFetcher initialized with ChromaDB")
        else:
            logger.info("SectorTickerFetcher initialized with hardcoded mappings")
    
    def get_tickers_for_sector(
        self, 
        sector: str, 
        limit: int = 20,
        min_relevance: float = 0.3
    ) -> List[str]:
        """
        Get stock tickers for a given sector.
        
        Args:
            sector: The sector name (e.g., "technology", "healthcare")
            limit: Maximum number of tickers to return
            min_relevance: Minimum relevance score (0-1, lower is more similar)
        
        Returns:
            List of stock ticker symbols
        """
        if self.use_chroma:
            return self._get_from_chroma(sector, limit, min_relevance)
    
    def _get_from_chroma(
        self, 
        sector: str, 
        limit: int,
        min_relevance: float
    ) -> List[str]:
        """
        Query ChromaDB for companies in the specified sector.
        
        Uses semantic search to find companies whose business descriptions
        match the sector query.
        """
        try:
            # Create a detailed query for better semantic matching
            query = f"{sector} sector companies, {sector} industry stocks, {sector} business"
            
            # Get embeddings for the query
            query_embedding = embed_texts([query])[0]
            
            # Search ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit * 2,  # Get more results for filtering
                include=["distances", "metadatas"]
            )
            
            if not results or not results.get("ids") or not results["ids"][0]:
                logger.warning(f"No results from ChromaDB for sector: {sector}")
            
            # Filter by relevance and extract tickers
            tickers_set = set()
            ids = results["ids"][0]
            distances = results["distances"][0]
            metadatas = results.get("metadatas", [[]])[0]
            
            for i, (ticker_id, distance, metadata) in enumerate(zip(ids, distances, metadatas)):
                # ChromaDB returns distance (lower is better for cosine)
                if distance <= min_relevance:
                    # Use the ID as ticker (builder.py stores ticker as ID)
                    # if ticker_id and ticker_id.strip():
                    #     tickers.append(ticker_id.strip().upper())
                    if metadata and "ticker" in metadata:
                        ticker_upper = metadata["ticker"].upper()
                        if ticker_upper not in tickers_set:
                            tickers_set.add(ticker_upper)
            
            if tickers_set:
                logger.info(f"Found {len(tickers_set)} tickers from ChromaDB for {sector}")
                return list(tickers_set)[:limit]
            else:
                logger.warning(f"No relevant tickers found in ChromaDB for {sector}, using fallback")
                
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
    
    def search_companies_by_query(
        self, 
        query: str, 
        limit: int = 10
    ) -> List[dict]:
        """
        Flexible semantic search for companies.
        
        Args:
            query: Natural language query (e.g., "electric vehicle companies", 
                   "cloud computing stocks", "pharmaceutical companies")
            limit: Maximum number of results
        
        Returns:
            List of dicts with ticker, distance, and metadata
        """
        if not self.use_chroma:
            logger.warning("ChromaDB not available for semantic search")
            return []
        
        try:
            query_embedding = embed_texts([query])[0]
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["distances", "metadatas", "documents"]
            )
            
            if not results or not results.get("ids"):
                return []
            
            companies = []
            for i in range(len(results["ids"][0])):
                companies.append({
                    "ticker": results["ids"][0][i],
                    "relevance": 1 - results["distances"][0][i],  # Convert distance to similarity
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "snippet": results["documents"][0][i][:200] if results.get("documents") else ""
                })
            
            return companies
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []


# Singleton instance
_fetcher_instance = None

def get_sector_ticker_fetcher(use_chroma: bool = True) -> SectorTickerFetcher:
    """Get or create the singleton SectorTickerFetcher instance."""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = SectorTickerFetcher(use_chroma=use_chroma)
    return _fetcher_instance
