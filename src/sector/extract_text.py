# extract_text.py
from bs4 import BeautifulSoup
import re

def clean_text(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "lxml")
    # remove scripts/styles
    for s in soup(["script", "style"]):
        s.decompose()
    text = soup.get_text(" ", strip=True)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text

def extract_item1(text: str) -> str:
    """
    Try to extract 'Item 1. Business' section from filing text.
    If fails, return the first ~2000-4000 chars of cleaned doc as fallback.
    """
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

def extract_business_section_from_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()
    cleaned = clean_text(raw)
    extracted = extract_item1(cleaned)
    # final safe-length trim
    return extracted.strip()
