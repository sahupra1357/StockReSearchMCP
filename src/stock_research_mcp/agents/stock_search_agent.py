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
    
    First search the ticker symbols from internal database (ChromaDB) by sector and then fetch stock details from external APIs or web sources.
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
                self.use_real_api = False
        else:
            logger.info(f"[{self.name}] Could not find any data.")
    
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
            
            if stocks:
                  return AgentResult(
                  success=True,
                  data={"stocks": [stock.model_dump() for stock in stocks]},
                  timestamp=datetime.now()
                  )
            else:
                logger.warning(f"[{self.name}] No stocks found for sector: {sector}")
                return AgentResult(
                    success=False,
                    error=f"No stocks found for sector: {sector}",
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
        
        """
        if self.use_real_api:
            # Use real API (Yahoo Finance by default - free, no API key needed)
            try:
                logger.info(f"[{self.name}] Fetching real data for sector: {sector}")
                stocks = await self.api_fetcher.fetch_from_yahoo_finance(sector)

                if stocks:
                    return stocks
                else:
                    logger.warning(f"[{self.name}] No real stocks found")
            except Exception as e:
                logger.error(f"[{self.name}] Real API failed: {e}")

        return []
    
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
