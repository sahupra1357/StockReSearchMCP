# Guide: Using Real APIs for Stock Data

## Quick Comparison

| API Provider | Cost | API Key Required | Best For | Rate Limits |
|-------------|------|------------------|----------|-------------|
| **Yahoo Finance** | Free | ❌ No | Quick prototyping | Unofficial, use responsibly |
| **Alpha Vantage** | Free tier | ✅ Yes | Getting started | 5 calls/min (free) |
| **NASDAQ Data Link** | Free tier | ✅ Yes | Official NASDAQ data | 50 calls/day (free) |
| **Polygon.io** | Free tier | ✅ Yes | Real-time data | Limited on free tier |
| **Financial Modeling Prep** | Free tier | ✅ Yes | Comprehensive data | 250 calls/day (free) |
| **IEX Cloud** | Free tier | ✅ Yes | Real-time quotes | 500k messages/month (free) |

## Recommended Approach: Yahoo Finance (yfinance)

### Why Yahoo Finance?
- ✅ **Free** - No API key needed
- ✅ **Easy** - Python library available
- ✅ **Reliable** - Widely used
- ⚠️ **Note** - Unofficial, check terms of service

### Installation

```bash
pip install yfinance
```

### Basic Usage

```python
import yfinance as yf

# Get single stock
ticker = yf.Ticker("AAPL")
info = ticker.info

print(f"Price: ${info['currentPrice']}")
print(f"Name: {info['longName']}")
print(f"Sector: {info['sector']}")

# Get multiple stocks
tickers = yf.Tickers("AAPL MSFT GOOGL")
for symbol, ticker in tickers.tickers.items():
    info = ticker.info
    print(f"{symbol}: ${info.get('currentPrice', 'N/A')}")

# Get historical data
hist = ticker.history(period="1mo")
print(hist.tail())
```

## Option 2: Alpha Vantage (Recommended for Production)

### Why Alpha Vantage?
- ✅ **Official API** - Well documented
- ✅ **Free Tier** - 5 API calls per minute
- ✅ **Comprehensive** - Stocks, forex, crypto
- ✅ **Legal** - Clear terms of service

### Get Your Free API Key

1. Visit: https://www.alphavantage.co/support/#api-key
2. Sign up (free)
3. Copy your API key

### Installation

```bash
pip install requests
```

### Basic Usage

```python
import requests

API_KEY = "your_api_key_here"

# Get quote
url = f"https://www.alphavantage.co/query"
params = {
    "function": "GLOBAL_QUOTE",
    "symbol": "AAPL",
    "apikey": API_KEY
}

response = requests.get(url, params=params)
data = response.json()
quote = data["Global Quote"]

print(f"Price: ${quote['05. price']}")
print(f"Change: {quote['10. change percent']}")
```

### Sector Search with Alpha Vantage

```python
# Alpha Vantage doesn't have direct sector search
# You need to maintain a list of tickers per sector

technology_stocks = ["AAPL", "MSFT", "GOOGL", "NVDA"]

for symbol in technology_stocks:
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": API_KEY
    }
    response = requests.get(url, params=params)
    # Process response
    time.sleep(12)  # Rate limit: 5 calls/min
```

## Option 3: NASDAQ Data Link (Official NASDAQ)

### Why NASDAQ Data Link?
- ✅ **Official** - Direct from NASDAQ
- ✅ **Historical Data** - Extensive archives
- ⚠️ **Limited Free** - 50 calls/day
- ⚠️ **Delayed Data** - Real-time requires subscription

### Get Your API Key

1. Visit: https://data.nasdaq.com/
2. Sign up
3. Get API key from account settings

### Basic Usage

```python
import requests

NASDAQ_KEY = "your_key_here"

# Get stock data
url = f"https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.json"
params = {"api_key": NASDAQ_KEY}

response = requests.get(url, params=params)
data = response.json()

latest = data["dataset"]["data"][0]
print(f"Date: {latest[0]}")
print(f"Close: ${latest[4]}")
```

## Option 4: Financial Modeling Prep

### Why FMP?
- ✅ **Sector Screening** - Built-in sector search
- ✅ **Comprehensive** - Financial statements, ratios
- ✅ **Free Tier** - 250 calls/day

### Get Your API Key

1. Visit: https://financialmodelingprep.com/developer/docs/
2. Sign up
3. Get free API key

### Sector Search Example

```python
import requests

FMP_KEY = "your_key_here"

# Search by sector (this is what we need!)
url = "https://financialmodelingprep.com/api/v3/stock-screener"
params = {
    "sector": "Technology",
    "limit": 20,
    "apikey": FMP_KEY
}

response = requests.get(url, params=params)
stocks = response.json()

for stock in stocks:
    print(f"{stock['symbol']}: ${stock['price']}")
```

## Integration into Your MCP Server

### Method 1: Update existing agent

```python
# In stock_search_agent.py
from .real_api_fetcher import RealAPIStockFetcher

class StockSearchAgent:
    def __init__(self, use_real_api=False):
        self.name = "StockSearchAgent"
        self.use_real_api = use_real_api
        self._mock_data = self._initialize_mock_data()
        
        if use_real_api:
            self.api_fetcher = RealAPIStockFetcher()
    
    async def _fetch_stocks_from_source(self, sector: str) -> List[Stock]:
        if self.use_real_api:
            # Use real API
            return await self.api_fetcher.fetch_from_yahoo_finance(sector)
        else:
            # Use mock data
            normalized_sector = sector.lower().strip()
            return self._mock_data.get(normalized_sector, [])
```

### Method 2: Environment variable toggle

```python
# In stock_search_agent.py
import os

class StockSearchAgent:
    def __init__(self):
        self.name = "StockSearchAgent"
        self.use_real_api = os.getenv("USE_REAL_API", "false").lower() == "true"
        
        if self.use_real_api:
            from .real_api_fetcher import RealAPIStockFetcher
            self.api_fetcher = RealAPIStockFetcher()
        else:
            self._mock_data = self._initialize_mock_data()
```

Then in your `.env` file:
```bash
USE_REAL_API=true
ALPHA_VANTAGE_API_KEY=your_key_here
```

## Complete Example: Integrating Yahoo Finance

```bash
# Install yfinance
pip install yfinance

# Update your .env
echo "USE_REAL_API=true" >> .env
```

Then the agent automatically uses real data!

## Best Practices

### 1. Handle Rate Limits

```python
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        now = datetime.now()
        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if now - t < timedelta(minutes=1)]
        
        if len(self.calls) >= self.calls_per_minute:
            # Wait until oldest call expires
            wait_time = 60 - (now - self.calls[0]).seconds
            await asyncio.sleep(wait_time)
        
        self.calls.append(now)
```

### 2. Cache Responses

```python
from functools import lru_cache
from datetime import datetime

class CachedFetcher:
    def __init__(self):
        self._cache = {}
        self._cache_duration = 60  # seconds
    
    async def fetch_with_cache(self, symbol):
        if symbol in self._cache:
            cached_data, timestamp = self._cache[symbol]
            if (datetime.now() - timestamp).seconds < self._cache_duration:
                return cached_data
        
        # Fetch fresh data
        data = await self._fetch_from_api(symbol)
        self._cache[symbol] = (data, datetime.now())
        return data
```

### 3. Error Handling

```python
async def fetch_with_retry(self, symbol, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await self._fetch(symbol)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts: {e}")
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## Testing Your Integration

```bash
# Test the real API fetcher
python src/stock_research_mcp/agents/real_api_fetcher.py

# Test with your MCP server
USE_REAL_API=true python test_installation.py
```

## Sector Ticker Lists

Since most APIs don't provide sector search, maintain these mappings:

```python
SECTOR_TICKERS = {
    "technology": {
        "mega_cap": ["AAPL", "MSFT", "GOOGL", "META", "NVDA"],
        "large_cap": ["AMD", "INTC", "CRM", "ORCL", "ADBE"],
        "mid_cap": ["SNOW", "DDOG", "NET", "CRWD"]
    },
    "healthcare": {
        "mega_cap": ["JNJ", "UNH", "LLY", "ABBV"],
        "large_cap": ["PFE", "TMO", "MRK", "ABT"]
    },
    # ... more sectors
}
```

Or scrape from sector ETFs like:
- XLK (Technology)
- XLV (Healthcare)
- XLF (Finance)
- XLE (Energy)

## Cost Comparison (Monthly)

| API | Free Tier | Paid Tier |
|-----|-----------|-----------|
| Yahoo Finance | Unlimited* | N/A |
| Alpha Vantage | 500 calls/day | $50/month (1,200/min) |
| NASDAQ Data Link | 50 calls/day | $50/month (unlimited) |
| Polygon.io | Limited | $29/month (starter) |
| FMP | 250 calls/day | $14/month (unlimited) |

*Unofficial, use at your own risk

## Recommendation for Your MCP Server

**Start with:**
1. Yahoo Finance (yfinance) for development
2. Switch to Alpha Vantage for production
3. Add FMP if you need sector screening

**Implementation:**
```bash
# Install
pip install yfinance requests python-dotenv

# Update .env
USE_REAL_API=true
# Add API keys if using paid services
```

The code in `real_api_fetcher.py` is ready to use! Just uncomment the method you prefer.
