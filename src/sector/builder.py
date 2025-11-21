# builder.py
import os
import sys
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from fetch_filings import download_best_filing
from extract_text import extract_business_section_from_file
from embeddings_and_chroma import build_batch_records
from fetch_tickers import fetch_sec_tickers

logging.basicConfig(level=logging.INFO)
TICKERS_FILE = "tickers.json"
SEC_DIR = "sec_filings"

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
    id_for_download = ticker or cik
    try:
        path = download_best_filing(id_for_download, out_dir=SEC_DIR)
        if not path:
            return None
        text = extract_business_section_from_file(path)
        if not text or len(text) < 200:
            return None
        return {"id": ticker, "text": text, "meta": {"cik": cik, "title": entry.get("title")}}
    except Exception as e:
        logging.exception(f"Failed {ticker}: {e}")
        return None

def main():
    tickers = load_or_fetch_tickers()
    max_workers = int(os.getenv("MAX_WORKERS", "8"))
    batch_size = int(os.getenv("BATCH_SIZE", "64"))

    to_index = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(process_one, t): t for t in tickers}
        for fut in as_completed(futures):
            entry = futures[fut]
            res = fut.result()
            if res:
                to_index.append(res)
                if len(to_index) >= batch_size:
                    build_batch_records(to_index)
                    to_index = []
    if to_index:
        build_batch_records(to_index)
    logging.info("Build complete")

if __name__ == "__main__":
    main()
