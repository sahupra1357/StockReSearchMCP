"""Stock Search Agent - Searches for stocks in a specific sector."""

import os
import logging
from typing import List, Optional
from datetime import datetime

from ..types import Stock, AgentResult


logger = logging.getLogger(__name__)


class StockSearchAgent:
    """
    Stock Search Agent
    Responsible for searching and retrieving stocks in a given sector.
    
    Can use either mock data or real APIs:
    - Yahoo Finance (yfinance) - Free, no API key
    - Alpha Vantage - Official API
    - Financial Modeling Prep - Sector screening
    - Polygon.io - Real-time data
    - NASDAQ Data Link - Official NASDAQ data
    
    Toggle with environment variable: USE_REAL_API=true
    """
    
    def __init__(self, use_real_api: Optional[bool] = None):
        self.name = "StockSearchAgent"
        
        # Determine if we should use real APIs
        if use_real_api is None:
            use_real_api = os.getenv("USE_REAL_API", "false").lower() == "true"
        
        self.use_real_api = use_real_api
        
        if self.use_real_api:
            logger.info(f"[{self.name}] Initialized with REAL API mode")
            try:
                from .real_api_fetcher import RealAPIStockFetcher
                self.api_fetcher = RealAPIStockFetcher()
            except ImportError as e:
                logger.warning(f"[{self.name}] Could not import real API fetcher: {e}")
                logger.warning(f"[{self.name}] Falling back to mock data")
                self.use_real_api = False
                self._mock_data = self._initialize_mock_data()
        else:
            logger.info(f"[{self.name}] Initialized with MOCK DATA mode")
            self._mock_data = self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> dict:
        """Initialize mock stock data for different sectors."""
        return {
            "technology": [
                Stock(symbol="AAPL", name="Apple Inc.", price=175.43, sector="Technology", 
                      market_cap=2800000000000, change=2.34, change_percent=1.35),
                Stock(symbol="MSFT", name="Microsoft Corporation", price=378.91, sector="Technology",
                      market_cap=2820000000000, change=5.67, change_percent=1.52),
                Stock(symbol="GOOGL", name="Alphabet Inc.", price=141.80, sector="Technology",
                      market_cap=1780000000000, change=-1.20, change_percent=-0.84),
                Stock(symbol="NVDA", name="NVIDIA Corporation", price=495.22, sector="Technology",
                      market_cap=1220000000000, change=12.45, change_percent=2.58),
                Stock(symbol="META", name="Meta Platforms Inc.", price=338.54, sector="Technology",
                      market_cap=858000000000, change=3.21, change_percent=0.96),
                Stock(symbol="AMD", name="Advanced Micro Devices", price=119.34, sector="Technology",
                      market_cap=193000000000, change=-2.11, change_percent=-1.74),
                Stock(symbol="INTC", name="Intel Corporation", price=43.21, sector="Technology",
                      market_cap=182000000000, change=0.89, change_percent=2.10),
                Stock(symbol="CRM", name="Salesforce Inc.", price=284.56, sector="Technology",
                      market_cap=278000000000, change=4.32, change_percent=1.54),
                Stock(symbol="ORCL", name="Oracle Corporation", price=115.67, sector="Technology",
                      market_cap=313000000000, change=1.45, change_percent=1.27),
                Stock(symbol="ADBE", name="Adobe Inc.", price=567.89, sector="Technology",
                      market_cap=258000000000, change=-3.45, change_percent=-0.60),
            ],
            "healthcare": [
                Stock(symbol="JNJ", name="Johnson & Johnson", price=156.78, sector="Healthcare",
                      market_cap=387000000000, change=0.87, change_percent=0.56),
                Stock(symbol="UNH", name="UnitedHealth Group", price=524.32, sector="Healthcare",
                      market_cap=490000000000, change=6.54, change_percent=1.26),
                Stock(symbol="PFE", name="Pfizer Inc.", price=28.45, sector="Healthcare",
                      market_cap=160000000000, change=-0.34, change_percent=-1.18),
                Stock(symbol="ABBV", name="AbbVie Inc.", price=168.90, sector="Healthcare",
                      market_cap=298000000000, change=2.10, change_percent=1.26),
                Stock(symbol="LLY", name="Eli Lilly and Company", price=598.45, sector="Healthcare",
                      market_cap=569000000000, change=8.76, change_percent=1.49),
                Stock(symbol="TMO", name="Thermo Fisher Scientific", price=542.11, sector="Healthcare",
                      market_cap=211000000000, change=3.21, change_percent=0.60),
                Stock(symbol="MRK", name="Merck & Co.", price=108.67, sector="Healthcare",
                      market_cap=275000000000, change=1.23, change_percent=1.14),
                Stock(symbol="ABT", name="Abbott Laboratories", price=114.32, sector="Healthcare",
                      market_cap=198000000000, change=0.65, change_percent=0.57),
            ],
            "finance": [
                Stock(symbol="JPM", name="JPMorgan Chase & Co.", price=158.90, sector="Finance",
                      market_cap=459000000000, change=2.34, change_percent=1.50),
                Stock(symbol="BAC", name="Bank of America Corp", price=34.56, sector="Finance",
                      market_cap=272000000000, change=0.45, change_percent=1.32),
                Stock(symbol="V", name="Visa Inc.", price=267.89, sector="Finance",
                      market_cap=549000000000, change=3.21, change_percent=1.21),
                Stock(symbol="MA", name="Mastercard Inc.", price=412.34, sector="Finance",
                      market_cap=391000000000, change=5.67, change_percent=1.39),
                Stock(symbol="WFC", name="Wells Fargo & Company", price=48.76, sector="Finance",
                      market_cap=171000000000, change=0.89, change_percent=1.86),
                Stock(symbol="GS", name="Goldman Sachs Group", price=398.45, sector="Finance",
                      market_cap=134000000000, change=4.32, change_percent=1.10),
                Stock(symbol="MS", name="Morgan Stanley", price=94.23, sector="Finance",
                      market_cap=152000000000, change=1.23, change_percent=1.32),
            ],
            "energy": [
                Stock(symbol="XOM", name="Exxon Mobil Corporation", price=109.45, sector="Energy",
                      market_cap=447000000000, change=1.23, change_percent=1.14),
                Stock(symbol="CVX", name="Chevron Corporation", price=158.67, sector="Energy",
                      market_cap=295000000000, change=2.10, change_percent=1.34),
                Stock(symbol="COP", name="ConocoPhillips", price=118.90, sector="Energy",
                      market_cap=147000000000, change=1.56, change_percent=1.33),
                Stock(symbol="SLB", name="Schlumberger Limited", price=52.34, sector="Energy",
                      market_cap=74000000000, change=0.78, change_percent=1.51),
                Stock(symbol="EOG", name="EOG Resources Inc.", price=127.45, sector="Energy",
                      market_cap=74000000000, change=1.89, change_percent=1.51),
            ],
        }
    
    async def search_stocks_by_sector(self, sector: str) -> AgentResult:
        """
        Search for stocks in a specific sector.
        
        Args:
            sector: The sector to search for (e.g., "technology", "healthcare")
            
        Returns:
            AgentResult with list of stocks
        """
        logger.info(f"[{self.name}] Searching for stocks in sector: {sector}")
        
        try:
            stocks = await self._fetch_stocks_from_source(sector)
            
            return AgentResult(
                success=True,
                data={"stocks": [stock.model_dump() for stock in stocks]},
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"[{self.name}] Failed to search stocks: {e}")
            return AgentResult(
                success=False,
                error=f"Failed to search stocks: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _fetch_stocks_from_source(self, sector: str) -> List[Stock]:
        """
        Fetch stocks from external API or web source.
        
        If USE_REAL_API=true, this will:
        1. Make API calls to financial data providers
        2. Fetch real-time or recent stock data
        3. Parse and normalize the data
        4. Return Stock objects
        
        Otherwise, returns mock data for development/testing.
        """
        if self.use_real_api:
            # Use real API (Yahoo Finance by default - free, no API key needed)
            try:
                logger.info(f"[{self.name}] Fetching real data for sector: {sector}")
                stocks = await self.api_fetcher.fetch_from_yahoo_finance(sector)
                
                if not stocks:
                    logger.warning(f"[{self.name}] No real stocks found, trying mock data")
                    return self._get_mock_stocks(sector)
                
                return stocks
            except Exception as e:
                logger.error(f"[{self.name}] Real API failed: {e}, falling back to mock data")
                return self._get_mock_stocks(sector)
        else:
            # Use mock data
            return self._get_mock_stocks(sector)
    
    def _get_mock_stocks(self, sector: str) -> List[Stock]:
        """Get mock stock data for a sector."""
        normalized_sector = sector.lower().strip()
        stocks = self._mock_data.get(normalized_sector, [])
        
        if not stocks:
            logger.warning(f"[{self.name}] No stocks found for sector: {sector}")
        
        return stocks
    
    async def get_stock_details(self, symbol: str) -> AgentResult:
        """Get detailed information for a specific stock."""
        try:
            # In production, fetch from API
            stock = Stock(
                symbol=symbol,
                name=f"{symbol} Company",
                price=100.0,
                sector="Unknown"
            )
            
            return AgentResult(
                success=True,
                data={"stock": stock.model_dump()},
                timestamp=datetime.now()
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to get stock details: {str(e)}",
                timestamp=datetime.now()
            )
