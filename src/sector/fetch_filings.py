# fetch_filings.py
import os
# import logging
from sec_edgar_downloader import Downloader
from typing import Optional
from pathlib import Path
from sector.sec_parser import extract_business_section_from_file
from sector.logging_log import logger

# logging.basicConfig(level=logging.INFO)

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

output_dir = os.getenv("SEC_DIR", "./output/sec_filings")
sec_company_name = os.getenv("SEC_EDGAR_COMPANY_NAME", "mnsai")
sec_contact_email = os.getenv("SEC_EDGAR_EMAIL", "sahupra1357@gmail.com")

def download_best_filing(ticker_or_cik: str, out_dir: str = "./output/sec_filings") -> Optional[str]:
    """
    Try: 10-K → 20-F → S-1 → 10-Q → extract business section and return text.
    Only moves to next filing type if business section extraction fails.
    Returns the extracted business section text or None if all attempts fail.
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # Create Downloader instance with proper User-Agent
    #dl = Downloader(out_dir, user_agent=USER_AGENT)
    dl = Downloader(sec_company_name, sec_contact_email, output_dir)
    
    candidates = ["10-K", "20-F", "S-1", "10-Q"]
    
    for form in candidates:
        try:
            logger.debug(f"Attempting {form} for {ticker_or_cik}")
            dl.get(form, ticker_or_cik)
            
            # sec-edgar-downloader saves files under out_dir/sec-edgar-filings/{ticker_or_cik}/{form}/
            # Try both possible paths
            possible_folders = [
                os.path.join(out_dir, "sec-edgar-filings", ticker_or_cik, form),
                os.path.join(out_dir, ticker_or_cik, form)
            ]
            
            for folder in possible_folders:
                if not os.path.isdir(folder):
                    continue
                    
                logger.debug(f"📁 Checking folder: {folder}")
                
                # Get all files (some may not have extensions)
                files = sorted(os.listdir(folder))
                if not files:
                    logger.debug(f"⚠️  No files found in {folder}")
                    continue
                
                logger.debug(f"📋 Found {len(files)} files in folder")
                
                # Try files in order - prefer .txt/.html but accept any file
                txt_html_files = [f for f in files if f.lower().endswith((".txt", ".html", ".htm"))]
                other_files = [f for f in files if not f.lower().endswith((".txt", ".html", ".htm")) and not f.startswith('.')]
                all_files = txt_html_files + other_files
                
                logger.debug(f"📄 Will try {len(all_files)} files (txt/html: {len(txt_html_files)}, other: {len(other_files)})")
                # logger.info(f"📄 Will try {all_files})")
                
                for fname in all_files:
                    path = os.path.join(folder, fname)
                    
                    # Each filing number is actually a directory containing the actual files
                    if os.path.isdir(path):
                        logger.debug(f"📁 Found filing directory: {fname}")
                        # List files inside this directory
                        try:
                            filing_files = os.listdir(path)
                            logger.debug(f"   Contains {len(filing_files)} files: {filing_files[:3]}...")
                            
                            # Try each file in the filing directory
                            for filing_file in filing_files:
                                if filing_file.startswith('.'):
                                    continue
                                    
                                file_path = os.path.join(path, filing_file)
                                if not os.path.isfile(file_path):
                                    continue
                                
                                logger.debug(f"📄 Trying file : {filing_file}")
                                
                                # Extract business section from the downloaded file
                                try:
                                    text = extract_business_section_from_file(file_path)
                                    logger.debug(f"Extracted text preview : {text[:50]}...")
                                    if text and len(text) >= 200:
                                        logger.info(f"✅ Successfully extracted business section from {form}/{fname}/{filing_file} ({len(text)} chars) for {ticker_or_cik}")
                                        # logger.info(f"Extracted text preview 1 : {text}...")
                                        return text  # Return text immediately if extraction succeeds
                                    else:
                                        logger.debug(f"⚠️  Business section too short in {filing_file} ({len(text) if text else 0} chars)")
                                except Exception as e:
                                    logger.debug(f"⚠️  Failed to extract from {filing_file}: {e}")
                            
                            # Tried all files in this filing directory, break to try next filing
                            break
                            
                        except Exception as e:
                            logger.warning(f"⚠️  Error reading filing directory {fname}: {e}")
                            continue
                    
                    elif os.path.isfile(path):
                        # Direct file (old format or different structure)
                        logger.debug(f"📄 Trying file: {fname}")
                        
                        try:
                            text = extract_business_section_from_file(path)
                            if text and len(text) >= 200:
                                logger.info(f"✅ Successfully extracted business section from {form} ({len(text)} chars) for {ticker_or_cik}")
                                logger.debug(f"Extracted text preview 2 : {text}...")
                                return text
                            else:
                                logger.debug(f"⚠️  Business section too short in {fname} ({len(text) if text else 0} chars)")
                        except Exception as e:
                            logger.debug(f"⚠️  Failed to extract from {fname}: {e}")
                        
                        # Only try first file per folder
                        break
                
                # If we found and processed files in this folder, don't check alternative path
                if files:
                    break
                        
        except Exception as e:
            logger.debug(f"{form} not found for {ticker_or_cik}: {e}")
            continue  # Try next filing type
    
    logger.warning(f"❌ No suitable filing with valid business section found for {ticker_or_cik}")
    return None
