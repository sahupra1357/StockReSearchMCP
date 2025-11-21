"""Type definitions for stock research."""

from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class StockCategory(str, Enum):
    """Stock category based on price."""
    HIGH = "high"      # > $100
    MEDIUM = "medium"  # $10 - $100
    LOW = "low"        # < $10


class Stock(BaseModel):
    """Stock data model."""
    symbol: str
    name: str
    price: float
    sector: str
    market_cap: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None


class CategorizedStocks(BaseModel):
    """Categorized stocks by price range."""
    high: List[Stock] = Field(default_factory=list)    # > $100
    medium: List[Stock] = Field(default_factory=list)  # $10 - $100
    low: List[Stock] = Field(default_factory=list)     # < $10


class NewsItem(BaseModel):
    """News item for a stock."""
    title: str
    source: str
    date: str
    sentiment: Optional[Literal["positive", "negative", "neutral"]] = None
    summary: Optional[str] = None


class EventItem(BaseModel):
    """Event item for a stock."""
    type: str
    date: str
    description: str
    impact: Optional[Literal["high", "medium", "low"]] = None


class PriceAnalysis(BaseModel):
    """Price analysis data."""
    current_price: float
    trend: str
    support: Optional[float] = None
    resistance: Optional[float] = None


class StockAnalysis(BaseModel):
    """Complete stock analysis."""
    stock: Stock
    category: StockCategory
    price_analysis: PriceAnalysis
    news: List[NewsItem]
    events: List[EventItem]
    recommendation: str


class AgentResult(BaseModel):
    """Generic agent result."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
