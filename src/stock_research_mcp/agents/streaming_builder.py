"""Streaming ChromaDB builder - builds index on first request with progress updates."""

import os
import sys
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import AsyncGenerator, Dict, Any, Optional

# Add sector directory to path
sector_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sector")
if os.path.exists(sector_path) and sector_path not in sys.path:
    sys.path.insert(0, sector_path)

try:
    from fetch_filings import download_best_filing
    from extract_text import extract_business_section_from_file
    from embeddings_and_chroma import build_batch_records, CHROMA_PERSIST_DIR
    from fetch_tickers import fetch_sec_tickers
    HAS_BUILDER = True
except ImportError as e:
    HAS_BUILDER = False
    CHROMA_PERSIST_DIR = "./chroma_db"
    logging.warning(f"Builder components not available: {e}")


logger = logging.getLogger(__name__)


class StreamingChromaBuilder:
    """
    Builds ChromaDB index with streaming progress updates.
    """
    
    def __init__(self):
        self.tickers_file = "tickers.json"
        self.sec_dir = "sec_filings"
        self.max_workers = int(os.getenv("MAX_WORKERS", "4"))  # Reduced for better UX
        self.batch_size = int(os.getenv("BATCH_SIZE", "32"))
    
    def is_chroma_db_built(self) -> bool:
        """Check if ChromaDB already exists and has data."""
        if not os.path.exists(CHROMA_PERSIST_DIR):
            return False
        
        # Check if directory has ChromaDB files
        try:
            files = os.listdir(CHROMA_PERSIST_DIR)
            # Look for chroma.sqlite3 or parquet files
            has_data = any(f.endswith(('.sqlite3', '.parquet')) for f in files)
            return has_data
        except Exception as e:
            logger.warning(f"Error checking ChromaDB: {e}")
            return False
    
    async def build_with_streaming(self) -> AsyncGenerator[str, None]:
        """
        Build ChromaDB index with streaming progress updates.
        
        Yields progress messages that can be sent to the user.
        """
        if not HAS_BUILDER:
            yield "❌ Error: Builder components not available. Please check installation.\n"
            return
        
        try:
            yield "🚀 Starting ChromaDB index build...\n"
            yield f"📁 Storage location: {CHROMA_PERSIST_DIR}\n\n"
            
            # Step 1: Fetch tickers
            yield "📥 Step 1/4: Fetching company tickers from SEC...\n"
            tickers = await self._load_or_fetch_tickers()
            yield f"✅ Found {len(tickers)} companies to index\n\n"
            
            # Step 2: Download filings and process
            yield f"📄 Step 2/4: Downloading SEC filings (using {self.max_workers} workers)...\n"
            yield "⏳ This may take 20-40 minutes depending on your connection...\n"
            
            to_index = []
            total_processed = 0
            total_successful = 0
            
            # Process in batches with progress updates
            with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
                futures = {ex.submit(self._process_one, t): t for t in tickers}
                
                for fut in as_completed(futures):
                    entry = futures[fut]
                    total_processed += 1
                    
                    try:
                        res = fut.result()
                        if res:
                            to_index.append(res)
                            total_successful += 1
                            
                            # Progress update every 10 companies
                            if total_processed % 10 == 0:
                                yield f"   📊 Progress: {total_processed}/{len(tickers)} processed, {total_successful} successful\n"
                            
                            # Build batch when ready
                            if len(to_index) >= self.batch_size:
                                yield f"   💾 Indexing batch of {len(to_index)} companies to ChromaDB...\n"
                                build_batch_records(to_index)
                                to_index = []
                    except Exception as e:
                        logger.error(f"Error processing {entry.get('ticker')}: {e}")
            
            # Index remaining
            if to_index:
                yield f"   💾 Indexing final batch of {len(to_index)} companies...\n"
                build_batch_records(to_index)
            
            yield f"\n✅ Step 2/4 Complete: Successfully indexed {total_successful} companies\n\n"
            
            # Step 3: Verify ChromaDB
            yield "🔍 Step 3/4: Verifying ChromaDB index...\n"
            if self.is_chroma_db_built():
                yield "✅ ChromaDB index verified and ready\n\n"
            else:
                yield "⚠️  Warning: ChromaDB verification failed\n\n"
            
            # Step 4: Complete
            yield "🎉 Step 4/4: Build complete!\n"
            yield f"📊 Total companies indexed: {total_successful}/{len(tickers)}\n"
            yield f"💾 Database location: {CHROMA_PERSIST_DIR}\n"
            yield "\n✨ ChromaDB is now ready for semantic search!\n"
            yield "🔄 Proceeding with your original query...\n\n"
            
        except Exception as e:
            logger.exception(f"Build failed: {e}")
            yield f"\n❌ Error during build: {str(e)}\n"
            yield "⚠️  Falling back to hardcoded sector mappings...\n\n"
    
    async def _load_or_fetch_tickers(self):
        """Load tickers from cache or fetch from SEC."""
        if os.path.exists(self.tickers_file):
            with open(self.tickers_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            tickers = fetch_sec_tickers()
            with open(self.tickers_file, "w", encoding="utf-8") as f:
                json.dump(tickers, f, indent=2)
            return tickers
    
    def _process_one(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single company entry."""
        ticker = entry.get("ticker")
        cik = str(entry.get("cik_str"))
        id_for_download = ticker or cik
        
        try:
            path = download_best_filing(id_for_download, out_dir=self.sec_dir)
            if not path:
                return None
            
            text = extract_business_section_from_file(path)
            if not text or len(text) < 200:
                return None
            
            return {
                "id": ticker,
                "text": text,
                "meta": {"cik": cik, "title": entry.get("title")}
            }
        except Exception as e:
            logger.debug(f"Failed {ticker}: {e}")
            return None


# Singleton instance
_builder_instance = None


def get_streaming_builder() -> StreamingChromaBuilder:
    """Get singleton builder instance."""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = StreamingChromaBuilder()
    return _builder_instance
