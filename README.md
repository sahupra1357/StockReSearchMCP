# Stock Research MCP Server (Python)

A sophisticated multi-agent Model Context Protocol (MCP) server for comprehensive stock research and analysis, built with Python.

## 🚀 Features

This MCP server uses a **multi-agent architecture** to provide in-depth stock market analysis:

### 🤖 Three Specialized Agents

1. **Stock Search Agent** - Searches the web for stocks in any sector
2. **Stock Categorization Agent** - Organizes stocks into price categories
3. **Stock Analysis Agent** - Provides detailed analysis with news, events, and recommendations

### 📊 Analysis Pipeline

When you query a sector, the system automatically:

1. **Searches** for all available stocks in that sector
2. **Categorizes** them into three groups:
   - **High-value**: Price > $100
   - **Medium-value**: Price $10-$100
   - **Low-value**: Price < $10
3. **Analyzes** each stock with:
   - Price trend analysis (bullish/bearish)
   - Recent news with sentiment analysis
   - Upcoming events (earnings, dividends, product launches)
   - Investment recommendation

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup

```bash
# Clone or navigate to the project directory
cd /Users/pradeepsahu/dev_data/StockSearhMCP

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## ⚙️ Configuration

Add to your MCP settings file to connect with Claude Desktop or other MCP clients.

### macOS/Linux

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stock-research": {
      "command": "python",
      "args": [
        "-m",
        "stock_research_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "/Users/pradeepsahu/dev_data/StockSearhMCP/src"
      }
    }
  }
}
```

### Alternative: Using the installed script

After installation, you can also use:

```json
{
  "mcpServers": {
    "stock-research": {
      "command": "/Users/pradeepsahu/dev_data/StockSearhMCP/venv/bin/stock-research-mcp"
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stock-research": {
      "command": "python",
      "args": [
        "-m",
        "stock_research_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\YourUsername\\dev_data\\StockSearhMCP\\src"
      }
    }
  }
}
```

## 🎯 Usage

Once configured, you can use the server through MCP-compatible clients like Claude Desktop.

### Example Queries

Ask Claude:
- "Analyze stocks in the technology sector"
- "Show me healthcare stocks and their analysis"
- "What are the best energy stocks right now?"
- "Give me a breakdown of finance sector stocks"

### Available Tools

#### `analyze_sector`

Performs comprehensive multi-agent analysis on a sector.

**Parameters:**
- `sector` (string, required): The sector to analyze

**Supported Sectors:**
- Technology
- Healthcare
- Finance
- Energy

**Example:**
```json
{
  "sector": "technology"
}
```

## 🏗️ Architecture

### Multi-Agent Design

```
User Query
    ↓
Orchestrator
    ↓
    ├─→ StockSearchAgent (searches for stocks)
    ↓
    ├─→ StockCategorizationAgent (groups by price)
    ↓
    └─→ StockAnalysisAgent (analyzes each stock)
         ├─→ Price Analysis
         ├─→ News Sentiment
         ├─→ Event Calendar
         └─→ Recommendation
```

### Project Structure

```
src/stock_research_mcp/
├── __init__.py              # Package initialization
├── server.py                # MCP server entry point
├── types.py                 # Data models (Pydantic)
└── agents/
    ├── __init__.py
    ├── stock_search_agent.py           # Agent 1: Search
    ├── stock_categorization_agent.py   # Agent 2: Categorize
    ├── stock_analysis_agent.py         # Agent 3: Analyze
    └── orchestrator.py                 # Coordinates all agents
```

## 🔧 Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Formatting

```bash
# Format code with Black
black src/

# Type checking with mypy
mypy src/
```

### Running Locally

```bash
# Run the server directly
python -m stock_research_mcp.server

# Or use the installed script
stock-research-mcp
```

## 🌐 Extending with Real Data Sources

Currently, the server uses mock data for demonstration. To integrate real APIs:

### 1. Stock Data APIs

Add real-time stock data integration:

```python
# In stock_search_agent.py
import os
import requests

async def _fetch_stocks_from_source(self, sector: str) -> List[Stock]:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=SECTOR&apikey={api_key}"
    
    response = requests.get(url)
    data = response.json()
    
    # Parse and return Stock objects
    return stocks
```

**Recommended APIs:**
- [Alpha Vantage](https://www.alphavantage.co/) - Free tier available
- [Yahoo Finance API](https://pypi.org/project/yfinance/) - Python library
- [Financial Modeling Prep](https://financialmodelingprep.com/) - Comprehensive data
- [Polygon.io](https://polygon.io/) - Real-time data

### 2. News Integration

Add real news fetching:

```python
# In stock_analysis_agent.py
from newsapi import NewsApiClient

async def _fetch_stock_news(self, stock: Stock) -> List[NewsItem]:
    newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
    articles = newsapi.get_everything(
        q=stock.symbol,
        language='en',
        sort_by='publishedAt'
    )
    
    # Convert to NewsItem objects
    return news_items
```

**Recommended APIs:**
- [News API](https://newsapi.org/) - General news
- [Finnhub](https://finnhub.io/) - Financial news
- [Alpha Vantage News](https://www.alphavantage.co/) - Stock-specific news

### 3. Events & Calendar

Integrate financial calendars:

```python
# In stock_analysis_agent.py
async def _fetch_stock_events(self, stock: Stock) -> List[EventItem]:
    # Fetch from earnings calendar API
    # Parse dividend schedules
    # Get product launch dates
    return events
```

### 4. Environment Variables

Create a `.env` file:

```bash
# .env
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
FINNHUB_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
```

Load in your code:

```python
from dotenv import load_dotenv
load_dotenv()
```

Install python-dotenv:
```bash
pip install python-dotenv
```

## 📊 Output Format

The analysis report includes:

```
================================================================================
STOCK ANALYSIS REPORT - TECHNOLOGY SECTOR
================================================================================
Total Stocks Analyzed: 10

────────────────────────────────────────────────────────────────────────────────
HIGH-VALUE STOCKS (Price > $100)
────────────────────────────────────────────────────────────────────────────────

📊 AAPL - Apple Inc.
   Price: $175.43 | Change: 1.35%
   Trend: bullish
   
   📰 Recent News (3):
      • Apple reports quarterly earnings [positive]
      • Analysts upgrade AAPL rating [positive]
   
   📅 Upcoming Events (3):
      • Earnings Call - 2025-12-19 [high impact]
      • Dividend Payment - 2025-12-04 [medium impact]
   
   💡 Recommendation:
      Stock shows positive momentum. News sentiment is generally positive...
```

## 🛠️ Troubleshooting

### Server won't start

- Ensure virtual environment is activated
- Check Python version: `python --version` (should be 3.10+)
- Reinstall dependencies: `pip install -e .`

### Import errors

- Verify PYTHONPATH in your MCP config
- Make sure you're in the correct directory
- Check that all agent files exist

### No stocks found

- Verify the sector name is correct
- Currently supported: technology, healthcare, finance, energy
- Check logs for error messages

### MCP connection issues

- Restart Claude Desktop after config changes
- Check the config file path is correct
- Verify JSON syntax in config file

## 🔍 Adding New Sectors

To add more sectors with mock data:

```python
# In stock_search_agent.py, update _initialize_mock_data()
def _initialize_mock_data(self) -> dict:
    return {
        "technology": [...],
        "retail": [  # New sector
            Stock(symbol="AMZN", name="Amazon", price=145.50, ...),
            Stock(symbol="WMT", name="Walmart", price=165.30, ...),
        ]
    }
```

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Integration with real financial APIs
- [ ] Advanced technical analysis indicators
- [ ] Machine learning for stock predictions
- [ ] More sophisticated sentiment analysis
- [ ] Historical data analysis
- [ ] Portfolio management features
- [ ] Real-time price updates
- [ ] Additional sectors and international markets

## 📄 License

MIT License

## ⚠️ Disclaimer

**IMPORTANT**: This tool is for educational and research purposes only. The stock analysis and recommendations are based on mock data and should **NOT** be used for actual investment decisions. 

- Always conduct your own research
- Consult with a qualified financial advisor
- Past performance does not guarantee future results
- Investing involves risk, including loss of principal

## 📚 Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Asyncio Guide](https://docs.python.org/3/library/asyncio.html)

## 💡 Tips

1. **Start with mock data** - Test the system before adding API integrations
2. **Rate limiting** - Be mindful of API rate limits when using real data
3. **Caching** - Consider caching API responses to reduce costs
4. **Error handling** - Add robust error handling for production use
5. **Logging** - Use logging to debug issues and monitor performance

---

Built with ❤️ using Python and the Model Context Protocol
