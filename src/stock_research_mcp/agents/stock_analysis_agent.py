"""Stock Analysis Agent - Analyzes stocks with news, events, and price analysis."""

import logging
from typing import List
from datetime import datetime, timedelta
import json

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
            logger.info(f"Fetched {len(news)} news items for {stock.symbol}")
            events = await self._fetch_stock_events(stock)
            logger.info(f"Fetched {len(events)} events for {stock.symbol}")
            
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
        Fetch news for a stock from Yahoo Finance.
        
        Uses yfinance library to get real news articles.
        """
        try:
            import yfinance as yf
            
            # Fetch news from Yahoo Finance
            ticker = yf.Ticker(stock.symbol)
            news_items = ticker.news
            
            if not news_items:
                logger.warning(f"No news found for {stock.symbol}")
            
            # Convert Yahoo Finance news to NewsItem objects
            parsed_news = []
            for item in news_items[:5]:  # Limit to top 5 news items
                try:
                    # Handle nested structure: check if 'content' key exists
                    content = item.get('content', item)
                    
                    # Extract title from nested structure
                    title = content.get('title', item.get('title', ''))
                    
                    # Extract summary/description
                    summary = content.get('summary', content.get('description', ''))
                    if not summary:
                        summary = item.get('summary', item.get('description', ''))
                    
                    # Determine sentiment based on title keywords
                    sentiment = self._analyze_sentiment(title)
                    
                    # Convert timestamp to date string
                    # Try multiple possible timestamp fields
                    timestamp = (
                        content.get('providerPublishTime') or 
                        item.get('providerPublishTime') or
                        content.get('pubDate') or
                        item.get('pubDate') or
                        0
                    )
                    
                    if timestamp:
                        # Handle ISO format strings (e.g., "2025-11-27T14:00:00Z")
                        if isinstance(timestamp, str):
                            try:
                                date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime("%Y-%m-%d")
                            except:
                                date = timestamp.split('T')[0]  # Fallback: just get date part
                        else:
                            # Handle Unix timestamp
                            date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                    else:
                        date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Extract publisher/source
                    source = (
                        content.get('publisher', {}).get('name') if isinstance(content.get('publisher'), dict) 
                        else content.get('publisher') or 
                        item.get('publisher') or 
                        'Yahoo Finance'
                    )
                    
                    news_item = NewsItem(
                        title=title,
                        source=source,
                        date=date,
                        sentiment=sentiment,
                        summary=summary[:200] if summary else ''
                    )
                    parsed_news.append(news_item)
                    logger.info(f"Fetched news: {title[:50]}...")
                    
                except Exception as parse_error:
                    logger.warning(f"Failed to parse news item: {parse_error}")
                    continue
            
            return parsed_news if parsed_news else ""
                    
        except ImportError:
            logger.warning("yfinance not installed. Install with: pip install yfinance")
        except Exception as e:
            logger.warning(f"Failed to fetch news for {stock.symbol}: {e}")
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        Simple sentiment analysis based on keywords.
        
        For production, use proper sentiment analysis:
        - TextBlob
        - VADER sentiment analyzer
        - Hugging Face transformers (FinBERT)
        """
        text_lower = text.lower()
        
        positive_words = [
            'surge', 'gain', 'up', 'rise', 'jump', 'rally', 'upgrade',
            'beat', 'strong', 'growth', 'profit', 'success', 'high',
            'soar', 'boost', 'improve', 'positive', 'bullish'
        ]
        
        negative_words = [
            'fall', 'drop', 'down', 'decline', 'loss', 'weak', 'miss',
            'cut', 'downgrade', 'crash', 'plunge', 'concern', 'worry',
            'negative', 'bearish', 'slump', 'struggle', 'warning'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
        
    async def _fetch_stock_events(self, stock: Stock) -> List[EventItem]:
        """
        Fetch actual events for a stock from Yahoo Finance.
        
        Uses yfinance library to get calendar events including:
        - Earnings dates
        - Dividend dates
        - Ex-dividend dates
        - Splits
        
        """
        try:
            import yfinance as yf
            
            # Fetch calendar data from Yahoo Finance
            ticker = yf.Ticker(stock.symbol)
            calendar = ticker.calendar
            
            #logger.info(f"Fetched calendar for {stock.symbol}: {calendar})")
            events = []
            
            # Extract earnings date
            if calendar is not None and 'Earnings Date' in calendar:
                earnings_dates = calendar['Earnings Date']
                if not isinstance(earnings_dates, (list, tuple)):
                    earnings_dates = [earnings_dates]
                
                for i, earnings_date in enumerate(earnings_dates):
                    if earnings_date and str(earnings_date) != 'NaT':
                        try:
                            # Convert to datetime if it's a timestamp
                            if hasattr(earnings_date, 'strftime'):
                                date_str = earnings_date.strftime("%Y-%m-%d")
                            else:
                                date_str = str(earnings_date).split()[0]
                            
                            events.append(EventItem(
                                type="Earnings Report",
                                date=date_str,
                                description=f"{stock.symbol} earnings announcement",
                                impact="high"
                            ))
                            logger.info(f"Found earnings date for {stock.symbol}: {date_str}")
                        except Exception as e:
                            logger.warning(f"Could not parse earnings date: {e}")
            
            # Get dividend information
            try:
                dividends = ticker.dividends
                if dividends is not None and not dividends.empty:
                    # Get the most recent dividend
                    last_dividend = dividends.iloc[-1]
                    last_dividend_date = dividends.index[-1]
                    
                    # Estimate next dividend date (typically quarterly)
                    next_dividend_date = last_dividend_date + timedelta(days=90)
                    
                    if next_dividend_date > datetime.now():
                        events.append(EventItem(
                            type="Dividend Payment",
                            date=next_dividend_date.strftime("%Y-%m-%d"),
                            description=f"Expected quarterly dividend (last: ${last_dividend:.2f})",
                            impact="medium"
                        ))
                        logger.info(f"Estimated next dividend for {stock.symbol}: {next_dividend_date.strftime('%Y-%m-%d')}")
            except Exception as e:
                logger.debug(f"Could not fetch dividend info for {stock.symbol}: {e}")
            
            # Get ex-dividend date if available
            try:
                info = ticker.info
                if 'exDividendDate' in info and info['exDividendDate']:
                    ex_div_timestamp = info['exDividendDate']
                    ex_div_date = datetime.fromtimestamp(ex_div_timestamp)
                    
                    # Only include if it's in the future
                    if ex_div_date > datetime.now():
                        events.append(EventItem(
                            type="Ex-Dividend Date",
                            date=ex_div_date.strftime("%Y-%m-%d"),
                            description="Last day to buy to receive dividend",
                            impact="medium"
                        ))
                        logger.info(f"Found ex-dividend date for {stock.symbol}: {ex_div_date.strftime('%Y-%m-%d')}")
            except Exception as e:
                logger.debug(f"Could not fetch ex-dividend date for {stock.symbol}: {e}")
            
            # If we found real events, return them
            if events:
                return events
            else:
                logger.warning(f"No events found for {stock.symbol}")
                
        except ImportError:
            logger.warning("yfinance not installed. Install with: pip install yfinance")
        except Exception as e:
            logger.warning(f"Failed to fetch events for {stock.symbol}: {e}")
    
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
