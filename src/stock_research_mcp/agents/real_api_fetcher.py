"""Real API Integration Examples for Stock Search Agent."""

import os
import logging
from typing import List, Optional
import asyncio

# These imports will be available when packages are installed
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ..types import Stock


logger = logging.getLogger(__name__)


class RealAPIStockFetcher:
    """
    Real API implementations for fetching stock data.
    
    Supports multiple data sources:
    1. Yahoo Finance (yfinance) - Free, no API key
    2. Alpha Vantage - Free tier available
    3. NASDAQ Data Link - Official NASDAQ data
    4. Polygon.io - Real-time data
    5. Financial Modeling Prep - Comprehensive data
    """
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.polygon_key = os.getenv("POLYGON_API_KEY")
        self.fmp_key = os.getenv("FMP_API_KEY")
        self.nasdaq_key = os.getenv("NASDAQ_DATA_LINK_KEY")
    
    # ============================================================
    # METHOD 1: Yahoo Finance (Recommended - Free, No API Key)
    # ============================================================
    
    async def fetch_from_yahoo_finance(self, sector: str) -> List[Stock]:
        """
        Fetch stocks using Yahoo Finance.
        
        Pros: Free, no API key, reliable
        Cons: No official API, terms of service restrictions
        
        Install: pip install yfinance
        """
        if not HAS_YFINANCE:
            logger.error("yfinance not installed. Run: pip install yfinance")
            return []
        
        # Map sector to stock tickers
        sector_tickers = self._get_sector_tickers(sector)
        stocks = []
        
        for ticker in sector_tickers:
            try:
                stock_info = yf.Ticker(ticker)
                info = stock_info.info
                
                stock = Stock(
                    symbol=ticker,
                    name=info.get('longName', ticker),
                    price=info.get('currentPrice') or info.get('regularMarketPrice', 0),
                    sector=sector.title(),
                    market_cap=info.get('marketCap'),
                    change=info.get('regularMarketChange'),
                    change_percent=info.get('regularMarketChangePercent')
                )
                stocks.append(stock)
                logger.info(f"Fetched {ticker}: ${stock.price}")
                
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {e}")
                continue
        
        return stocks
    
    # ============================================================
    # METHOD 2: Alpha Vantage API
    # ============================================================
    
    async def fetch_from_alpha_vantage(self, sector: str) -> List[Stock]:
        """
        Fetch stocks using Alpha Vantage API.
        
        Pros: Official API, comprehensive data
        Cons: Rate limits (5 calls/min on free tier)
        
        Sign up: https://www.alphavantage.co/support/#api-key
        Install: pip install requests
        """
        if not self.alpha_vantage_key:
            logger.error("ALPHA_VANTAGE_API_KEY not set")
            return []
        
        if not HAS_REQUESTS:
            logger.error("requests not installed. Run: pip install requests")
            return []
        
        sector_tickers = self._get_sector_tickers(sector)
        stocks = []
        
        for ticker in sector_tickers:
            try:
                url = f"https://www.alphavantage.co/query"
                params = {
                    "function": "GLOBAL_QUOTE",
                    "symbol": ticker,
                    "apikey": self.alpha_vantage_key
                }
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if "Global Quote" in data:
                    quote = data["Global Quote"]
                    stock = Stock(
                        symbol=ticker,
                        name=ticker,  # Alpha Vantage doesn't provide company name in quote
                        price=float(quote.get("05. price", 0)),
                        sector=sector.title(),
                        change=float(quote.get("09. change", 0)),
                        change_percent=float(quote.get("10. change percent", "0").replace("%", ""))
                    )
                    stocks.append(stock)
                    logger.info(f"Fetched {ticker}: ${stock.price}")
                
                # Rate limiting
                await asyncio.sleep(12)  # Free tier: 5 calls/min
                
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {e}")
                continue
        
        return stocks
    
    # ============================================================
    # METHOD 3: Financial Modeling Prep (FMP)
    # ============================================================
    
    async def fetch_from_fmp(self, sector: str) -> List[Stock]:
        """
        Fetch stocks using Financial Modeling Prep API.
        
        Pros: Comprehensive data, sector screening available
        Cons: Limited free tier
        
        Sign up: https://financialmodelingprep.com/developer/docs/
        """
        if not self.fmp_key:
            logger.error("FMP_API_KEY not set")
            return []
        
        try:
            # FMP has a sector screener endpoint
            url = f"https://financialmodelingprep.com/api/v3/stock-screener"
            params = {
                "sector": sector,
                "limit": 20,
                "apikey": self.fmp_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            stocks = []
            for item in data[:10]:  # Limit to 10 stocks
                stock = Stock(
                    symbol=item.get("symbol", ""),
                    name=item.get("companyName", ""),
                    price=float(item.get("price", 0)),
                    sector=sector.title(),
                    market_cap=item.get("marketCap"),
                    change=item.get("change"),
                    change_percent=item.get("changesPercentage")
                )
                stocks.append(stock)
            
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to fetch from FMP: {e}")
            return []
    
    # ============================================================
    # METHOD 4: Polygon.io
    # ============================================================
    
    async def fetch_from_polygon(self, sector: str) -> List[Stock]:
        """
        Fetch stocks using Polygon.io API.
        
        Pros: Real-time data, websockets available
        Cons: Limited free tier
        
        Sign up: https://polygon.io/
        """
        if not self.polygon_key:
            logger.error("POLYGON_API_KEY not set")
            return []
        
        sector_tickers = self._get_sector_tickers(sector)
        stocks = []
        
        for ticker in sector_tickers:
            try:
                # Get previous day's data
                url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
                params = {"apiKey": self.polygon_key}
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if data.get("results"):
                    result = data["results"][0]
                    
                    # Get company details
                    details_url = f"https://api.polygon.io/v3/reference/tickers/{ticker}"
                    details_response = requests.get(details_url, params=params)
                    details = details_response.json().get("results", {})
                    
                    stock = Stock(
                        symbol=ticker,
                        name=details.get("name", ticker),
                        price=result.get("c", 0),  # Close price
                        sector=sector.title(),
                        market_cap=details.get("market_cap"),
                        change=result.get("c", 0) - result.get("o", 0),
                        change_percent=((result.get("c", 0) - result.get("o", 0)) / result.get("o", 1)) * 100
                    )
                    stocks.append(stock)
                
                await asyncio.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Failed to fetch {ticker}: {e}")
                continue
        
        return stocks
    
    # ============================================================
    # METHOD 5: NASDAQ Data Link (formerly Quandl)
    # ============================================================
    
    async def fetch_from_nasdaq_data_link(self, sector: str) -> List[Stock]:
        """
        Fetch stocks using NASDAQ Data Link API.
        
        Pros: Official NASDAQ data, historical data
        Cons: Requires subscription for real-time data
        
        Sign up: https://data.nasdaq.com/
        """
        if not self.nasdaq_key:
            logger.error("NASDAQ_DATA_LINK_KEY not set")
            return []
        
        # NASDAQ Data Link requires specific dataset codes
        # This is a simplified example
        try:
            sector_tickers = self._get_sector_tickers(sector)
            stocks = []
            
            for ticker in sector_tickers:
                # Example using WIKI prices (EOD data)
                url = f"https://data.nasdaq.com/api/v3/datasets/WIKI/{ticker}.json"
                params = {"api_key": self.nasdaq_key}
                
                response = requests.get(url, params=params)
                data = response.json()
                
                if "dataset" in data:
                    latest = data["dataset"]["data"][0]  # Most recent day
                    
                    stock = Stock(
                        symbol=ticker,
                        name=data["dataset"]["name"],
                        price=latest[4],  # Close price
                        sector=sector.title(),
                        change=latest[4] - latest[1],  # Close - Open
                        change_percent=((latest[4] - latest[1]) / latest[1]) * 100
                    )
                    stocks.append(stock)
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to fetch from NASDAQ Data Link: {e}")
            return []
    
    # ============================================================
    # Helper: Get sector tickers
    # ============================================================
    
    def _get_sector_tickers(self, sector: str) -> List[str]:
        """
        Get a list of representative tickers for a sector.
        
        In production, you could:
        1. Maintain a database of sector classifications
        2. Use sector ETFs as a reference
        3. Query APIs that provide sector screening
        4. Scrape from financial websites
        """
        sector_map = {
            "technology": [
                "AAPL", "MSFT", "GOOGL", "NVDA", "META", 
                "AMD", "INTC", "CRM", "ORCL", "ADBE"
            ],
            "healthcare": [
                "JNJ", "UNH", "PFE", "ABBV", "LLY", 
                "TMO", "MRK", "ABT"
            ],
            "finance": [
                "JPM", "BAC", "V", "MA", "WFC", 
                "GS", "MS", "C", "AXP", "BLK"
            ],
            "energy": [
                "XOM", "CVX", "COP", "SLB", "EOG",
                "MPC", "PSX", "VLO"
            ],
            "consumer": [
                "AMZN", "WMT", "HD", "MCD", "NKE",
                "SBUX", "TGT", "COST"
            ],
            "industrial": [
                "BA", "CAT", "GE", "MMM", "HON",
                "UNP", "UPS", "LMT"
            ]
        }
        
        return sector_map.get(sector.lower(), [])


# ============================================================
# Example Usage
# ============================================================

async def example_usage():
    """Example of using real APIs."""
    fetcher = RealAPIStockFetcher()
    
    # Method 1: Yahoo Finance (Recommended - no API key needed)
    print("Fetching from Yahoo Finance...")
    stocks = await fetcher.fetch_from_yahoo_finance("technology")
    for stock in stocks:
        print(f"  {stock.symbol}: ${stock.price:.2f}")
    
    # Method 2: Alpha Vantage (if API key is set)
    # stocks = await fetcher.fetch_from_alpha_vantage("technology")
    
    # Method 3: FMP (if API key is set)
    # stocks = await fetcher.fetch_from_fmp("technology")
    
    # Method 4: Polygon.io (if API key is set)
    # stocks = await fetcher.fetch_from_polygon("technology")
    
    # Method 5: NASDAQ Data Link (if API key is set)
    # stocks = await fetcher.fetch_from_nasdaq_data_link("technology")


if __name__ == "__main__":
    asyncio.run(example_usage())
