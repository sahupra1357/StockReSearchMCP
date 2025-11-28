"""Example showing how to extend agents with real APIs."""

import os
import asyncio
from typing import List

# Uncomment these when you have API keys
# import yfinance as yf
# from newsapi import NewsApiClient

from stock_research_mcp.agents import StockSearchAgent
from stock_research_mcp.types import Stock


class RealDataStockSearchAgent(StockSearchAgent):
    """Extended agent with real API integration."""
    
    async def _fetch_stocks_from_source(self, sector: str) -> List[Stock]:
        """
        Fetch real stock data from APIs.
        
        This example shows how to integrate with Yahoo Finance.
        Install with: pip install yfinance
        """
        # Example using yfinance (uncomment when ready)
        # sector_tickers = self._get_sector_tickers(sector)
        # stocks = []
        # 
        # for ticker in sector_tickers:
        #     try:
        #         stock_info = yf.Ticker(ticker)
        #         info = stock_info.info
        #         
        #         stock = Stock(
        #             symbol=ticker,
        #             name=info.get('longName', ticker),
        #             price=info.get('currentPrice', 0),
        #             sector=sector,
        #             market_cap=info.get('marketCap'),
        #             change=info.get('regularMarketChange'),
        #             change_percent=info.get('regularMarketChangePercent')
        #         )
        #         stocks.append(stock)
        #     except Exception as e:
        #         print(f"Error fetching {ticker}: {e}")
        # 
        # return stocks
        
        return await super()._fetch_stocks_from_source(sector)
    
    def _get_sector_tickers(self, sector: str) -> List[str]:
        """
        Get list of tickers for a sector.
        
        In production, you might:
        - Use a pre-built sector mapping
        - Query a financial database
        - Scrape from financial websites
        """
        sector_map = {
            "technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "META"],
            "healthcare": ["JNJ", "UNH", "PFE", "ABBV", "LLY"],
            "finance": ["JPM", "BAC", "V", "MA", "WFC"],
            "energy": ["XOM", "CVX", "COP", "SLB", "EOG"]
        }
        return sector_map.get(sector.lower(), [])


async def main():
    """Example usage of extended agent."""
    agent = RealDataStockSearchAgent()
    result = await agent.search_stocks_by_sector("technology")
    
    if result.success:
        print(f"Found {len(result.data['stocks'])} stocks")
        for stock_data in result.data['stocks']:
            stock = Stock(**stock_data)
            print(f"  {stock.symbol}: ${stock.price}")


if __name__ == "__main__":
    asyncio.run(main())
