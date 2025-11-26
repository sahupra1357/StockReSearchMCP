import re
from bs4 import BeautifulSoup

from sector.logging_log import logger

# import logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Utility cleaners
# ---------------------------------------------------------

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

def remove_table_of_contents(text: str):
    """
    Removes the Table of Contents region in 10-K filings.
    Ensures matching ITEM 1 in TOC does not interfere.
    """
    up = text.upper()
    toc_idx = up.find("TABLE OF CONTENTS")

    if toc_idx == -1:
        return text

    # Look ahead 15k chars to find the fake ITEM 1 in TOC region
    snippet = up[toc_idx: toc_idx + 15000]
    fake_item = re.search(r"ITEM\s+1[^A-Z0-9]", snippet)

    if fake_item:
        cutoff = toc_idx + fake_item.end()
        return text[cutoff:]

    return text


# ---------------------------------------------------------
# Generic section extractor
# ---------------------------------------------------------
def extract_section(text: str, start_patterns, end_patterns, fallback=12000):
    """
    Generic, reusable section extractor used by all specialized extractors.
    start_patterns: list[regex]
    end_patterns: list[regex]
    """

    text = clean_text(text)
    text = remove_table_of_contents(text)

    # Combine start patterns
    start_regex = re.compile("|".join(start_patterns), re.IGNORECASE)

    # Find starting point
    start_match = start_regex.search(text)
    if not start_match:
        return text[:fallback]  # fallback to start of document

    #logger.info(f"Found section start at index {start_match.start()}")
    start = start_match.start()

    # Combine end patterns
    end_regex = re.compile("|".join(end_patterns), re.IGNORECASE)

    # Find end AFTER start
    end_match = end_regex.search(text, start + 10)
    if end_match:
        end = end_match.start()
    else:
        end = start + fallback  # fallback if no boundary found
    logger.debug(f"Found section end at index {start} - {end}")
    return text[start:end].strip()


# ---------------------------------------------------------
# Section-specific implementations
# ---------------------------------------------------------

def extract_business_section(text: str):
    """
    Extracts Item 1. Business.
    Works across 10-K, 20-F, and S-1 formats.
    """
    # start_patterns = [
    #     r"\n\s*ITEM\s+1\.?\s*BUSINESS\s*\n",
    #     r"\n\s*ITEM\s+1\.\s*\n",
    #     r"\n\s*ITEM\s+4\.?\s*INFORMATION ON THE COMPANY\s*\n",  # for 20-F
    # ]

    start_patterns = [
        r"item\s*1[^a-zA-Z]{0,5}business",
        r"item\s*1\s*[-–]\s*business",
        r"business overview",
        r"information on the company"  # for 20-F
    ]

    # end_patterns = [
    #     r"\n\s*ITEM\s+1A\b",
    #     r"\n\s*ITEM\s+2\b",
    #     r"\n\s*ITEM\s+5\b",  # for 20-F
    # ]

    end_patterns = [
        r"\s*ITEM\s+1A\b",
        r"\s*ITEM\s+2\b",
        r"\s*ITEM\s+5\b",  # for 20-F
    ]

    return extract_section(text, start_patterns, end_patterns)


def extract_risk_factors(text: str):
    """
    Extracts Item 1A. Risk Factors.
    Handles 10-K and 20-F.
    """
    # start_patterns = [
    #     r"\n\s*ITEM\s+1A\.?\s*RISK FACTORS\s*\n",
    #     r"\n\s*ITEM\s+3\.?\s*KEY INFORMATION\s*\n",  # 20-F risk section sometimes there
    # ]

    start_patterns = [
        r"item\s*1a[^a-zA-Z]{0,5}risk",
        r"risk factors",
        r"key information"  # 20-F section 3
    ]

    # end_patterns = [
    #     r"\n\s*ITEM\s+1B\b",
    #     r"\n\s*ITEM\s+2\b",
    #     r"\n\s*ITEM\s+4\b",  # 20-F next major section
    # ]

    end_patterns = [
        r"\s*ITEM\s+1B\b",
        r"\s*ITEM\s+2\b",
        r"\s*ITEM\s+4\b",  # 20-F next major section
    ]

    return extract_section(text, start_patterns, end_patterns, fallback=0)


def extract_mda_section(text: str):
    """
    Extracts Item 7 (Management’s Discussion & Analysis).
    Handles 10-K, 10-Q, and 20-F variants.
    """
    # start_patterns = [
    #     r"\n\s*ITEM\s+7\.?\s*MANAGEMENT.?S DISCUSSION",
    #     r"\n\s*ITEM\s+2\.?\s*MANAGEMENT.?S DISCUSSION",  # 10-Q
    #     r"\n\s*ITEM\s+5\.?\s*OPERATING AND FINANCIAL REVIEW",  # 20-F
    # ]

    start_patterns = [
        r"item\s*7[^a-zA-Z]{0,5}management",
        r"management.?s discussion",
        r"operating and financial review",  # 20-F
    ]
    # end_patterns = [
    #     r"\n\s*ITEM\s+7A\b",
    #     r"\n\s*ITEM\s+8\b",
    #     r"\n\s*ITEM\s+6\b",   # for 20-F
    # ]

    end_patterns = [
        r"\s*ITEM\s+7A\b",
        r"\s*ITEM\s+8\b",
        r"\s*ITEM\s+6\b",   # for 20-F
    ]

    return extract_section(text, start_patterns, end_patterns, fallback=0)


def extract_properties_section(text: str):
    """
    Extracts Item 2 (Properties).
    """
    # start_patterns = [
    #     r"\n\s*ITEM\s+2\.?\s*PROPERT(IES|Y)\s*\n"
    # ]

    start_patterns = [
        r"item\s*2[^a-zA-Z]{0,5}propert",
    ]
    # end_patterns = [
    #     r"\n\s*ITEM\s+3\b", 
    #     r"\n\s*ITEM\s+1A\b"
    # ]

    end_patterns = [
        r"\s*ITEM\s+3\b", 
        r"\s*ITEM\s+1A\b"
    ]

    return extract_section(text, start_patterns, end_patterns, fallback=0)



def extract_business_section_from_file(path: str) -> str:
    logger.debug(f"Extracting business section from: {path}")
    try:
        resukt_string = ""
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
        business = extract_business_section(raw)
        risks = extract_risk_factors(raw)
        mda = extract_mda_section(raw)
        props = extract_properties_section(raw)

        resukt_string = "\n\n=== Business Section ===\n" + business 
        if risks:
            resukt_string += "\n\n=== Risk Factors Section ===\n" + risks
        elif mda:
            resukt_string += "\n\n=== MDA Section ===\n"+ mda 
        elif props:
            resukt_string += "\n\n=== Properties Section ===\n"+ props
        logger.debug(f"Extracted {len(resukt_string)} characters from business section")
        # final safe-length trim
        return resukt_string.strip()
    except Exception as e:
        logger.error(f"Error extracting business section from {path}: {e}")
        return ""