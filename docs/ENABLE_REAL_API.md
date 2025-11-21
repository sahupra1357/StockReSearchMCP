# Quick Start: Switch to Real Stock Data

## 🚀 In 3 Simple Steps

### Step 1: Install Yahoo Finance (30 seconds)

```bash
# Make sure you're in the virtual environment
cd /Users/pradeepsahu/dev_data/StockSearhMCP
source venv/bin/activate

# Install yfinance (free, no API key needed!)
pip install yfinance
```

### Step 2: Enable Real API Mode (10 seconds)

```bash
# Create or edit .env file
echo "USE_REAL_API=true" > .env
```

**That's it!** Your MCP server now uses real stock data from Yahoo Finance.

### Step 3: Test It (20 seconds)

```bash
# Test with the example script
python examples/basic_usage.py
```

You should see real, current stock prices!

## 🎯 How It Works

The system automatically:
1. Checks the `USE_REAL_API` environment variable
2. If `true`, fetches real data from Yahoo Finance
3. If `false` or not set, uses mock data

### Architecture

```
StockSearchAgent
    │
    ├─ USE_REAL_API=true?
    │   │
    │   ├─ YES ──→ RealAPIStockFetcher
    │   │           └─ Yahoo Finance API
    │   │              └─ Returns real stock data
    │   │
    │   └─ NO ───→ Mock Data
    │               └─ Returns demo data
    │
    └─ Returns: List[Stock]
```

## 🔄 Switching Between Mock and Real Data

### Use Mock Data (default)

```bash
# Remove or comment out in .env
# USE_REAL_API=true

# Or set to false
echo "USE_REAL_API=false" > .env
```

### Use Real Data

```bash
echo "USE_REAL_API=true" > .env
```

### Programmatic Toggle

```python
# In your code
from stock_research_mcp.agents import StockSearchAgent

# Force real API
agent = StockSearchAgent(use_real_api=True)

# Force mock data
agent = StockSearchAgent(use_real_api=False)

# Use environment variable (default)
agent = StockSearchAgent()
```

## 📊 Comparing Mock vs Real Data

### Test Script

```python
import asyncio
import os
from stock_research_mcp.agents import StockSearchAgent

async def compare():
    # Test with mock data
    print("=== MOCK DATA ===")
    mock_agent = StockSearchAgent(use_real_api=False)
    mock_result = await mock_agent.search_stocks_by_sector("technology")
    
    if mock_result.success:
        stocks = mock_result.data["stocks"]
        for stock in stocks[:3]:
            print(f"  {stock['symbol']}: ${stock['price']}")
    
    # Test with real data
    print("\n=== REAL DATA ===")
    real_agent = StockSearchAgent(use_real_api=True)
    real_result = await real_agent.search_stocks_by_sector("technology")
    
    if real_result.success:
        stocks = real_result.data["stocks"]
        for stock in stocks[:3]:
            print(f"  {stock['symbol']}: ${stock['price']}")

asyncio.run(compare())
```

Save as `test_real_vs_mock.py` and run:
```bash
python test_real_vs_mock.py
```

## 🌐 Using Other APIs

### Option 1: Alpha Vantage (Official, Free Tier)

```bash
# 1. Get free API key from https://www.alphavantage.co/support/#api-key

# 2. Add to .env
echo "USE_REAL_API=true" >> .env
echo "ALPHA_VANTAGE_API_KEY=your_key_here" >> .env

# 3. Update stock_search_agent.py to use Alpha Vantage
# Change line in _fetch_stocks_from_source:
# stocks = await self.api_fetcher.fetch_from_alpha_vantage(sector)
```

### Option 2: Financial Modeling Prep (Has Sector Search!)

```bash
# 1. Get free API key from https://financialmodelingprep.com/developer/docs/

# 2. Add to .env
echo "FMP_API_KEY=your_key_here" >> .env

# 3. Update stock_search_agent.py:
# stocks = await self.api_fetcher.fetch_from_fmp(sector)
```

### Option 3: Multiple APIs (Fallback Chain)

```python
async def _fetch_stocks_from_source(self, sector: str) -> List[Stock]:
    if self.use_real_api:
        try:
            # Try Yahoo Finance first (free)
            return await self.api_fetcher.fetch_from_yahoo_finance(sector)
        except:
            try:
                # Try Alpha Vantage as backup
                return await self.api_fetcher.fetch_from_alpha_vantage(sector)
            except:
                # Fall back to mock data
                return self._get_mock_stocks(sector)
    else:
        return self._get_mock_stocks(sector)
```

## 🔍 Verifying Real Data

### Check the logs

```bash
python -m stock_research_mcp.server
```

You should see:
```
[StockSearchAgent] Initialized with REAL API mode
[StockSearchAgent] Fetching real data for sector: technology
Fetched AAPL: $175.43
Fetched MSFT: $378.91
...
```

### In Claude Desktop

After setting `USE_REAL_API=true` and restarting Claude:

Ask: "What's the current price of Apple stock in the technology sector?"

Claude will use your MCP server and return **real, current prices**.

## 📦 What Gets Installed

```bash
pip install yfinance
```

This installs:
- `yfinance` - Yahoo Finance API wrapper
- `pandas` - Data manipulation (dependency)
- `requests` - HTTP client (dependency)
- `lxml` - HTML parsing (dependency)

Total size: ~50MB

## ⚠️ Important Notes

### Yahoo Finance
- **Free** but unofficial API
- **No API key** required
- **Rate limits**: Be reasonable, don't spam
- **Terms of Service**: Review Yahoo's ToS
- **Best for**: Development, small-scale use

### For Production
- Consider **Alpha Vantage** or **FMP** (official APIs)
- Add **error handling** and **retry logic**
- Implement **caching** to reduce API calls
- Monitor **rate limits**

## 🎯 Configuration Summary

### Development (Mock Data)
```bash
# .env
USE_REAL_API=false
```

### Testing (Real Data, Free)
```bash
# .env
USE_REAL_API=true
# That's it! Uses Yahoo Finance automatically
```

### Production (Real Data, Official APIs)
```bash
# .env
USE_REAL_API=true
ALPHA_VANTAGE_API_KEY=your_key
FMP_API_KEY=your_key
POLYGON_API_KEY=your_key
```

## 🚀 Next Steps

1. ✅ Install yfinance: `pip install yfinance`
2. ✅ Enable real API: `echo "USE_REAL_API=true" > .env`
3. ✅ Test: `python examples/basic_usage.py`
4. ✅ Use in Claude Desktop!

## 🔧 Troubleshooting

### "yfinance not installed"
```bash
pip install yfinance
```

### "No real stocks found"
- Check internet connection
- Verify sector name is correct
- System automatically falls back to mock data

### "Rate limit exceeded"
- Add delays between requests
- Use caching
- Consider paid API tier

### Want to go back to mock data?
```bash
# Remove from .env or set to false
echo "USE_REAL_API=false" > .env
```

---

**You're now using real stock data! 🎉**

The best part? The system automatically falls back to mock data if anything goes wrong, so your MCP server always works.
