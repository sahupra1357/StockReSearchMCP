# fetch_filings.py
import os
import logging
from sec_edgar_downloader import Downloader
from typing import Optional

logging.basicConfig(level=logging.INFO)
dl = Downloader(".", user_agent=None)  # sec-edgar-downloader will use SEC_EMAIL env var

def download_best_filing(ticker_or_cik: str, out_dir: str = "sec_filings") -> Optional[str]:
    """
    Try: 10-K → 20-F → S-1 → 10-Q → return path to downloaded file (first main file) or None.
    Saves into out_dir/<ticker_or_cik>/<filing_type>/
    """
    os.makedirs(out_dir, exist_ok=True)
    candidates = ["10-K", "20-F", "S-1", "10-Q"]
    for form in candidates:
        try:
            logging.info(f"Attempting {form} for {ticker_or_cik}")
            dl.get(form, ticker_or_cik, download_folder=out_dir)
            # sec-edgar-downloader saves files under out_dir/{ticker_or_cik}/{form}/
            folder = os.path.join(out_dir, ticker_or_cik, form)
            if os.path.isdir(folder):
                # pick first file with .txt or .html
                for fname in sorted(os.listdir(folder)):
                    if fname.lower().endswith((".txt", ".html", ".htm")):
                        path = os.path.join(folder, fname)
                        logging.info(f"Downloaded {path}")
                        return path
        except Exception as e:
            logging.debug(f"{form} not found for {ticker_or_cik}: {e}")
    logging.warning(f"No suitable filing found for {ticker_or_cik}")
    return None
