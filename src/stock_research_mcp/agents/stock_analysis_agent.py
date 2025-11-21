"""Stock Analysis Agent - Analyzes stocks with news, events, and price analysis."""

import logging
from typing import List
from datetime import datetime, timedelta

from ..types import (
    Stock, 
    StockCategory, 
    StockAnalysis, 
    NewsItem, 
    EventItem, 
    PriceAnalysis,
    AgentResult
)


logger = logging.getLogger(__name__)


class StockAnalysisAgent:
    """
    Stock Analysis Agent
    Responsible for analyzing individual stocks with news, events, and price analysis.
    
    In production, this would integrate with:
    - News APIs (News API, Finnhub, Alpha Vantage News)
    - Financial calendars (earnings dates, dividend dates)
    - Technical analysis libraries (TA-Lib, pandas-ta)
    - Sentiment analysis models
    """
    
    def __init__(self):
        self.name = "StockAnalysisAgent"
    
    async def analyze_stock(self, stock: Stock, category: StockCategory) -> AgentResult:
        """
        Analyze a stock comprehensively.
        
        Args:
            stock: Stock object to analyze
            category: Stock category
            
        Returns:
            AgentResult with StockAnalysis data
        """
        logger.info(f"[{self.name}] Analyzing stock: {stock.symbol}")
        
        try:
            # Perform parallel analysis
            price_analysis = await self._analyze_price_movement(stock)
            news = await self._fetch_stock_news(stock)
            events = await self._fetch_stock_events(stock)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(
                stock, category, price_analysis, news, events
            )
            
            analysis = StockAnalysis(
                stock=stock,
                category=category,
                price_analysis=price_analysis,
                news=news,
                events=events,
                recommendation=recommendation
            )
            
            return AgentResult(
                success=True,
                data={"analysis": analysis.model_dump()},
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"[{self.name}] Failed to analyze stock: {e}")
            return AgentResult(
                success=False,
                error=f"Failed to analyze stock: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def analyze_multiple_stocks(
        self,
        stocks: List[Stock],
        get_category_fn
    ) -> AgentResult:
        """
        Analyze multiple stocks.
        
        Args:
            stocks: List of stocks to analyze
            get_category_fn: Function to get category for a stock
            
        Returns:
            AgentResult with list of StockAnalysis
        """
        logger.info(f"[{self.name}] Analyzing {len(stocks)} stocks")
        
        try:
            analyses = []
            
            for stock in stocks:
                category = get_category_fn(stock)
                result = await self.analyze_stock(stock, category)
                
                if result.success and result.data:
                    analyses.append(result.data["analysis"])
            
            return AgentResult(
                success=True,
                data={"analyses": analyses},
                timestamp=datetime.now()
            )
        except Exception as e:
            return AgentResult(
                success=False,
                error=f"Failed to analyze multiple stocks: {str(e)}",
                timestamp=datetime.now()
            )
    
    async def _analyze_price_movement(self, stock: Stock) -> PriceAnalysis:
        """
        Analyze price movement and trends.
        
        In production:
        - Fetch historical data
        - Calculate technical indicators (RSI, MACD, Moving Averages)
        - Identify support/resistance levels
        - Determine trend direction
        """
        change_percent = stock.change_percent or 0
        
        # Determine trend
        if change_percent > 2:
            trend = "strong bullish"
        elif change_percent > 0.5:
            trend = "bullish"
        elif change_percent < -2:
            trend = "strong bearish"
        elif change_percent < -0.5:
            trend = "bearish"
        else:
            trend = "neutral"
        
        # Mock support and resistance levels
        support = round(stock.price * 0.95, 2)
        resistance = round(stock.price * 1.05, 2)
        
        return PriceAnalysis(
            current_price=stock.price,
            trend=trend,
            support=support,
            resistance=resistance
        )
    
    async def _fetch_stock_news(self, stock: Stock) -> List[NewsItem]:
        """
        Fetch news for a stock.
        
        In production, integrate with:
        - News API
        - Finnhub News
        - Alpha Vantage News
        - Web scraping from financial news sites
        """
        today = datetime.now()
        
        # Mock news data
        sentiment = "positive" if (stock.change_percent or 0) > 0 else "neutral"
        
        mock_news = [
            NewsItem(
                title=f"{stock.name} reports quarterly earnings",
                source="Financial Times",
                date=today.strftime("%Y-%m-%d"),
                sentiment=sentiment,
                summary=f"{stock.name} released their quarterly earnings report showing mixed results."
            ),
            NewsItem(
                title=f"Analysts upgrade {stock.symbol} rating",
                source="Bloomberg",
                date=(today - timedelta(days=2)).strftime("%Y-%m-%d"),
                sentiment="positive",
                summary=f"Several analysts have upgraded their rating on {stock.symbol} citing strong fundamentals."
            ),
            NewsItem(
                title=f"Market volatility affects {stock.name}",
                source="Reuters",
                date=(today - timedelta(days=5)).strftime("%Y-%m-%d"),
                sentiment="negative",
                summary=f"Recent market volatility has impacted {stock.name}'s stock performance."
            )
        ]
        
        return mock_news
    
    async def _fetch_stock_events(self, stock: Stock) -> List[EventItem]:
        """
        Fetch events for a stock.
        
        In production, integrate with:
        - Earnings calendar APIs
        - Financial event calendars
        - Company investor relations pages
        """
        today = datetime.now()
        
        # Mock events data
        mock_events = [
            EventItem(
                type="Earnings Call",
                date=(today + timedelta(days=30)).strftime("%Y-%m-%d"),
                description=f"Q4 {today.year} Earnings Call",
                impact="high"
            ),
            EventItem(
                type="Dividend Payment",
                date=(today + timedelta(days=15)).strftime("%Y-%m-%d"),
                description="Quarterly dividend payment",
                impact="medium"
            ),
            EventItem(
                type="Product Launch",
                date=(today + timedelta(days=45)).strftime("%Y-%m-%d"),
                description="New product line announcement expected",
                impact="medium"
            )
        ]
        
        return mock_events
    
    def _generate_recommendation(
        self,
        stock: Stock,
        category: StockCategory,
        price_analysis: PriceAnalysis,
        news: List[NewsItem],
        events: List[EventItem]
    ) -> str:
        """Generate investment recommendation based on all analysis."""
        recommendation_parts = []
        
        # Price trend analysis
        if "bullish" in price_analysis.trend:
            recommendation_parts.append("Stock shows positive momentum.")
        elif "bearish" in price_analysis.trend:
            recommendation_parts.append("Stock is experiencing downward pressure.")
        else:
            recommendation_parts.append("Stock is trading sideways.")
        
        # Sentiment analysis
        positive_sentiment = sum(1 for n in news if n.sentiment == "positive")
        negative_sentiment = sum(1 for n in news if n.sentiment == "negative")
        
        if positive_sentiment > negative_sentiment:
            recommendation_parts.append("News sentiment is generally positive.")
        elif negative_sentiment > positive_sentiment:
            recommendation_parts.append("Recent news has been negative.")
        
        # Category-based insights
        if category == StockCategory.HIGH:
            recommendation_parts.append(
                f"As a high-value stock (>${100}), it's generally more stable but may have slower growth."
            )
        elif category == StockCategory.MEDIUM:
            recommendation_parts.append(
                f"As a mid-range stock ($10-$100), it offers a balance of stability and growth potential."
            )
        else:
            recommendation_parts.append(
                f"As a low-priced stock (<$10), it carries higher risk but potential for significant gains."
            )
        
        # Event considerations
        high_impact_events = sum(1 for e in events if e.impact == "high")
        if high_impact_events > 0:
            recommendation_parts.append(
                "Watch for upcoming high-impact events that could affect the stock price."
            )
        
        # Final recommendation
        overall_score = positive_sentiment - negative_sentiment
        if "bullish" in price_analysis.trend:
            overall_score += 1
        elif "bearish" in price_analysis.trend:
            overall_score -= 1
        
        if overall_score > 1:
            recommendation_parts.append("Overall: CONSIDER BUYING")
        elif overall_score < -1:
            recommendation_parts.append("Overall: CONSIDER SELLING or AVOID")
        else:
            recommendation_parts.append("Overall: HOLD or WAIT for better entry point")
        
        return " ".join(recommendation_parts)
