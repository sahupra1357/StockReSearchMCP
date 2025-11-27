# builder.py
import os
import sys
import json
import time
from datetime import timedelta
# import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from sector.yahoo_ticker_info import get_yahhoo_sector_info

from sector.fetch_filings import download_best_filing
from sector.extract_text import extract_business_section_from_file
from sector.embeddings_and_chroma import build_batch_records
from sector.fetch_tickers import fetch_sec_tickers
from sector.logging_log import logger

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in project root (2 levels up from this file)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
    else:
        load_dotenv()  # Try to load from current directory
except ImportError:
    print("⚠️  python-dotenv not installed. Using system environment variables only.")
    print("   Install with: pip install python-dotenv")


# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

TICKERS_FILE =  os.getenv("TICKERS_FILE", "./output/tickers.json")  
SEC_DIR = os.getenv("SEC_DIR", "./output/sec_filings")

def load_or_fetch_tickers():
    if os.path.exists(TICKERS_FILE):
        with open(TICKERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        ticks = fetch_sec_tickers()
        with open(TICKERS_FILE, "w", encoding="utf-8") as f:
            json.dump(ticks, f, indent=2)
        return ticks

def process_one(entry):
    ticker = entry.get("ticker")
    cik = str(entry.get("cik_str"))
    name = entry.get("title", "")

    try:
        ticker_info = get_yahhoo_sector_info(ticker)
        sector = ticker_info.get("sector", "")
        industry = ticker_info.get("industry", "")
        summary = ticker_info.get("longBusinessSummary", "")
        logger.debug(f"Fetched sector info for {ticker}: {sector}")
    except Exception as e:
        logger.error(f"Error fetching sector info for {ticker}: {e}")

    id_for_download = ticker or cik
    try:
        # download_best_filing now returns extracted text directly, not path
        sec_text = download_best_filing(id_for_download, out_dir=SEC_DIR)
        
        if not sec_text:
            logger.warning(f"⚠️  No valid business section found for {ticker}")
            return None

        full_text = (summary or "") + "\n" + (sec_text or "")        

        logger.debug(f"✅ Successfully downloaded and processed {ticker} with {len(full_text)} characters")

        return {
                "id": ticker, 
                "documents": full_text, 
                "metadatas": {
                    "ticker": ticker,
                    "sector": sector,
                    "industry": industry,
                    "name": name
                }
            }
    except Exception as e:
        logger.exception(f"❌ Failed {ticker}: {e}")
        return None

def main():
    # Start timing
    start_time = time.time()
    
    # Check required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ Error: OPENAI_API_KEY environment variable is required")
        logger.error("Set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    logger.info("🚀 Starting ChromaDB build process...")
    logger.info(f"📁 ChromaDB will be stored at: {os.getenv('CHROMA_PERSIST_DIR', './chroma_db')}")
    
    tickers = load_or_fetch_tickers()
    tickers = tickers[:100]  # Limit for testing
    max_workers = int(os.getenv("MAX_WORKERS", "8"))
    batch_size = int(os.getenv("BATCH_SIZE", "64"))
    
    logger.info(f"📊 Processing {len(tickers)} companies with {max_workers} workers")
    logger.info(f"💾 Batch size: {batch_size}")
    
    processing_start = time.time()

    to_index = []
    successful = 0
    total = len(tickers)
    
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(process_one, t): t for t in tickers}
        for i, fut in enumerate(as_completed(futures), 1):
            entry = futures[fut]
            res = fut.result()
            if res:
                to_index.append(res)
                successful += 1
                if len(to_index) >= batch_size:
                    logger.info(f"💾 Indexing batch of {len(to_index)} companies...")
                    build_batch_records(to_index)
                    to_index = []
            
            # Progress update every 50 companies
            if i % 50 == 0:
                elapsed = time.time() - processing_start
                avg_time = elapsed / i
                eta_seconds = avg_time * (total - i)
                eta = str(timedelta(seconds=int(eta_seconds)))
                logger.info(f"📊 Progress: {i}/{total} processed, {successful} successful ({(successful/i)*100:.1f}%) | ETA: {eta}")
    
    processing_time = time.time() - processing_start
    
    if to_index:
        logger.info(f"💾 Indexing final batch of {len(to_index)} companies...")
        build_batch_records(to_index)
    
    total_time = time.time() - start_time
    
    logger.info("=" * 80)
    logger.info(f"✅ Build complete!")
    logger.info(f"📊 Successfully indexed {successful}/{total} companies ({(successful/total)*100:.1f}%)")
    logger.info(f"⏱️  Processing time: {str(timedelta(seconds=int(processing_time)))}")
    logger.info(f"⏱️  Total time: {str(timedelta(seconds=int(total_time)))}")
    logger.info(f"📈 Average time per company: {processing_time/total:.2f}s")
    logger.info(f"💾 Database location: {os.getenv('CHROMA_PERSIST_DIR', './chroma_db')}")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()
