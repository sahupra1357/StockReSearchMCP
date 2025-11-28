"""Multi-Agent Orchestrator - Coordinates all agents."""

import logging
from typing import List, Dict, Any

from .stock_search_agent import StockSearchAgent
from .stock_categorization_agent import StockCategorizationAgent
from .stock_analysis_agent import StockAnalysisAgent
from ..types import Stock, StockAnalysis


logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Multi-Agent Orchestrator
    Coordinates multiple agents to fulfill complex stock research queries.
    
    Workflow:
    1. StockSearchAgent searches for stocks in a sector
    2. StockCategorizationAgent categorizes stocks by price
    3. StockAnalysisAgent analyzes each stock with news, events, and recommendations
    """
    
    def __init__(self):
        self.search_agent = StockSearchAgent()
        self.categorization_agent = StockCategorizationAgent()
        self.analysis_agent = StockAnalysisAgent()
    
    async def process_sector_query(self, sector: str) -> Dict[str, Any]:
        """
        Main orchestration method: Search sector, categorize, and analyze.
        
        Args:
            sector: The sector to analyze
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        logger.info(f"\n=== Starting Multi-Agent Analysis for Sector: {sector} ===\n")
        
        try:
            # Step 1: Search for stocks in the sector
            logger.info("Step 1: Searching for stocks...")
            search_result = await self.search_agent.search_stocks_by_sector(sector)
            
            if not search_result.success or not search_result.data:
                return {
                    "success": False,
                    "sector": sector,
                    "total_stocks": 0,
                    "error": search_result.error or "Failed to search stocks"
                }
            
            stocks_data = search_result.data["stocks"]
            stocks = [Stock(**s) for s in stocks_data]
            logger.info(f"Found {len(stocks)} stocks in {sector} sector\n")
            
            # Step 2: Categorize stocks
            logger.info("Step 2: Categorizing stocks...")
            categorize_result = await self.categorization_agent.categorize_stocks(stocks)
            
            if not categorize_result.success or not categorize_result.data:
                return {
                    "success": False,
                    "sector": sector,
                    "total_stocks": len(stocks),
                    "error": categorize_result.error or "Failed to categorize stocks"
                }
            
            categorized = categorize_result.data
            high_stocks = [Stock(**s) for s in categorized["high"]]
            medium_stocks = [Stock(**s) for s in categorized["medium"]]
            low_stocks = [Stock(**s) for s in categorized["low"]]
            
            logger.info(
                f"Categorized: {len(high_stocks)} high, "
                f"{len(medium_stocks)} medium, {len(low_stocks)} low\n"
            )
            
            # Step 3: Analyze stocks in each category
            logger.info("Step 3: Analyzing stocks...")
            
            high_analyses = await self._analyze_category(high_stocks, "high")
            medium_analyses = await self._analyze_category(medium_stocks, "medium")
            low_analyses = await self._analyze_category(low_stocks, "low")
            
            logger.info("\n=== Analysis Complete ===\n")
            
            return {
                "success": True,
                "sector": sector,
                "total_stocks": len(stocks),
                "categorized_stocks": {
                    "high": [s.model_dump() for s in high_stocks],
                    "medium": [s.model_dump() for s in medium_stocks],
                    "low": [s.model_dump() for s in low_stocks],
                },
                "analyses": {
                    "high": high_analyses,
                    "medium": medium_analyses,
                    "low": low_analyses,
                }
            }
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
            return {
                "success": False,
                "sector": sector,
                "total_stocks": 0,
                "error": f"Orchestration failed: {str(e)}"
            }
    
    async def _analyze_category(
        self, 
        stocks: List[Stock], 
        category_name: str
    ) -> List[Dict[str, Any]]:
        """Analyze stocks in a specific category."""
        logger.info(f"Analyzing {len(stocks)} {category_name} stocks...")
        
        analyses = []
        
        for stock in stocks:
            category = self.categorization_agent.get_category_for_stock(stock)
            analysis_result = await self.analysis_agent.analyze_stock(stock, category)
            
            if analysis_result.success and analysis_result.data:
                analyses.append(analysis_result.data["analysis"])
        
        logger.info(f"Completed analysis for {category_name} category")
        return analyses
    
    def format_results(self, result: Dict[str, Any]) -> str:
        """Format results for display."""
        if not result["success"]:
            return f"Error: {result.get('error', 'Unknown error')}"
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"STOCK ANALYSIS REPORT - {result['sector'].upper()} SECTOR")
        lines.append("=" * 80)
        lines.append(f"\nTotal Stocks Analyzed: {result['total_stocks']}\n")
        
        if "analyses" not in result:
            lines.append("No analysis data available\n")
            return "\n".join(lines)
        
        analyses = result["analyses"]
        
        # High-value stocks
        if analyses.get("high"):
            lines.append("\n" + "─" * 80)
            lines.append("HIGH-VALUE STOCKS (Price > $100)")
            lines.append("─" * 80)
            lines.append(self._format_category_analysis(analyses["high"]))
        
        # Medium-value stocks
        if analyses.get("medium"):
            lines.append("\n" + "─" * 80)
            lines.append("MEDIUM-VALUE STOCKS (Price $10-$100)")
            lines.append("─" * 80)
            lines.append(self._format_category_analysis(analyses["medium"]))
        
        # Low-value stocks
        if analyses.get("low"):
            lines.append("\n" + "─" * 80)
            lines.append("LOW-VALUE STOCKS (Price < $10)")
            lines.append("─" * 80)
            lines.append(self._format_category_analysis(analyses["low"]))
        
        lines.append("\n" + "=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def _format_category_analysis(self, analyses: List[Dict[str, Any]]) -> str:
        """Format analysis for a category."""
        lines = []
        
        for analysis_data in analyses:
            analysis = StockAnalysis(**analysis_data)
            stock = analysis.stock
            
            lines.append(f"\n📊 {stock.symbol} - {stock.name}")
            price_str = f"${stock.price:.2f}" if stock.price is not None else "N/A"
            change_str = f"{stock.change_percent:.2f}%" if stock.change_percent is not None else "N/A"
            lines.append(f"   Price: {price_str} | Change: {change_str}")
            lines.append(f"   Trend: {analysis.price_analysis.trend}")
            
            lines.append(f"\n   📰 Recent News ({len(analysis.news)}):")
            for news in analysis.news[:2]:
                lines.append(f"      • {news.title} [{news.sentiment}]")
            
            lines.append(f"\n   📅 Upcoming Events ({len(analysis.events)}):")
            for event in analysis.events[:2]:
                lines.append(f"      • {event.type} - {event.date} [{event.impact} impact]")
            
            lines.append("\n   💡 Recommendation:")
            lines.append(f"      {analysis.recommendation}")
            lines.append("")
        
        return "\n".join(lines)
