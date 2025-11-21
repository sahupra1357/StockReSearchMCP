"""Stock Categorization Agent - Categorizes stocks by price range."""

import logging
from typing import List
from datetime import datetime

from ..types import Stock, CategorizedStocks, StockCategory, AgentResult


logger = logging.getLogger(__name__)


class StockCategorizationAgent:
    """
    Stock Categorization Agent
    Responsible for categorizing stocks based on their price.
    
    Categories:
    - High: Price > $100
    - Medium: Price $10 - $100
    - Low: Price < $10
    """
    
    def __init__(self):
        self.name = "StockCategorizationAgent"
    
    async def categorize_stocks(self, stocks: List[Stock]) -> AgentResult:
        """
        Categorize stocks into high, medium, and low based on price.
        
        Args:
            stocks: List of Stock objects to categorize
            
        Returns:
            AgentResult with CategorizedStocks data
        """
        logger.info(f"[{self.name}] Categorizing {len(stocks)} stocks")
        
        try:
            categorized = CategorizedStocks()
            
            for stock in stocks:
                if stock.price > 100:
                    categorized.high.append(stock)
                elif 10 <= stock.price <= 100:
                    categorized.medium.append(stock)
                else:
                    categorized.low.append(stock)
            
            logger.info(
                f"[{self.name}] Results: {len(categorized.high)} high, "
                f"{len(categorized.medium)} medium, {len(categorized.low)} low"
            )
            
            return AgentResult(
                success=True,
                data={
                    "high": [s.model_dump() for s in categorized.high],
                    "medium": [s.model_dump() for s in categorized.medium],
                    "low": [s.model_dump() for s in categorized.low],
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"[{self.name}] Failed to categorize stocks: {e}")
            return AgentResult(
                success=False,
                error=f"Failed to categorize stocks: {str(e)}",
                timestamp=datetime.now()
            )
    
    def get_category_for_stock(self, stock: Stock) -> StockCategory:
        """
        Get category for a single stock.
        
        Args:
            stock: Stock object
            
        Returns:
            StockCategory enum value
        """
        if stock.price > 100:
            return StockCategory.HIGH
        elif 10 <= stock.price <= 100:
            return StockCategory.MEDIUM
        else:
            return StockCategory.LOW
    
    async def get_stocks_by_category(
        self, 
        stocks: List[Stock], 
        category: StockCategory
    ) -> AgentResult:
        """
        Filter stocks by specific category.
        
        Args:
            stocks: List of stocks
            category: Category to filter by
            
        Returns:
            AgentResult with filtered stocks
        """
        try:
            result = await self.categorize_stocks(stocks)
            
            if not result.success or not result.data:
                return AgentResult(
                    success=False,
                    error="Failed to categorize stocks",
                    timestamp=datetime.now()
                )
            
            filtered_stocks = result.data.get(category.value, [])
            
            return AgentResult(
                success=True,
                data={"stocks": filtered_stocks},
                timestamp=datetime.now()
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to get stocks by category: {str(e)}",
                timestamp=datetime.now()
            )
