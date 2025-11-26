# extract_text.py
from bs4 import BeautifulSoup
import re
from sector.logging_log import logger

# import logger
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

def clean_text(html_text: str) -> str:
    try:
        soup = BeautifulSoup(html_text, "lxml")
        # remove scripts/styles
        for s in soup(["script", "style"]):
            s.decompose()
        text = soup.get_text(" ", strip=True)
        # collapse whitespace
        text = re.sub(r"\s+", " ", text)
        return text
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        return html_text  # return original if cleaning fails

def extract_item1(text: str) -> str:
    """
    Try to extract 'Item 1. Business' section from filing text.
    If fails, return the first ~2000-4000 chars of cleaned doc as fallback.
    """
    try:
        up = text.upper()
        # common markers
        idx1 = up.find("ITEM 1.")
        if idx1 == -1:
            idx1 = up.find("ITEM 1 -")
        if idx1 == -1:
            # sometimes "ITEM 1 BUSINESS"
            idx1 = up.find("ITEM 1 BUSINESS")
        if idx1 == -1:
            # fallback to using first paragraph
            return text[:4000]

        # find end marker (Item 1A or Item 2)
        idx_end = up.find("ITEM 1A", idx1 + 1)
        if idx_end == -1:
            idx_end = up.find("ITEM 2", idx1 + 1)
        if idx_end == -1:
            # use a chunk length if no marker found
            return text[idx1: idx1 + 4000]

        return text[idx1:idx_end]
    except Exception as e:
        logger.error(f"Error extracting Item 1: {e}")
        return text[:4000]  # fallback

def extract_business_section_from_file(path: str) -> str:
    logger.info(f"Extracting business section from: {path}")
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        cleaned = clean_text(raw)
        extracted = extract_item1(cleaned)
        logger.info(f"Extracted {len(extracted)} characters from business section")
        # final safe-length trim
        return extracted.strip()
    except Exception as e:
        logger.error(f"Error extracting business section from {path}: {e}")
        return ""
