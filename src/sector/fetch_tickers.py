# fetch_tickers.py
import httpx
import json
import os


SEC_TICKERS_URL = os.getenv("SEC_TICKERS_URL", "https://www.sec.gov/files/company_tickers.json")
TICKERS_FILE = os.getenv("TICKERS_FILE", "tickers.json")

def fetch_sec_tickers():
    # SEC.gov requires a User-Agent header
    # See: https://www.sec.gov/os/webmaster-faq#code-support
    headers = {
        "User-Agent": "Stock Research MCP Server (sahupra1357@gmail.com)"  # Replace with your email
    }
    r = httpx.get(SEC_TICKERS_URL, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    # data keys are numeric strings — convert to list of dicts
    out = []
    for _, v in data.items():
        out.append({
            "ticker": v.get("ticker"),
            "cik_str": v.get("cik_str"),
            "title": v.get("title"),
            "exchange": v.get("exchange")  # might be None
        })
    return out

if __name__ == "__main__":
    tickers = fetch_sec_tickers()
    print(f"Found {len(tickers)} entries")
    # save to file
    with open(TICKERS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickers, f, indent=2)
    print(f"Saved {TICKERS_FILE}")