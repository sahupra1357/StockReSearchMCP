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

# Create a virtual environment (using .venv as the directory name)
python -m venv .venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## 🗄️ ChromaDB Setup - Automatic on First Use!

**✨ NEW**: ChromaDB builds automatically on your first query - no manual setup required!

### How It Works

1. **First Query**: When you make your first stock analysis request, the system automatically:
   - Detects that ChromaDB doesn't exist
   - Fetches company data from SEC
   - Downloads and processes filings
   - Builds embeddings and stores in ChromaDB
   - Shows you real-time progress updates
   - Then proceeds with your query

2. **Subsequent Queries**: ChromaDB is stored permanently, so all future queries are instant!

### Required Environment Variables

Set these in your MCP configuration (see Configuration section below):

```bash
# Required: OpenAI API key for embeddings
OPENAI_API_KEY="your-openai-api-key"

# Required: SEC-compliant User-Agent
SEC_API_USER_AGENT="Your Company Name contact@youremail.com"

# Optional: Customize ChromaDB storage location (default: ./chroma_db)
CHROMA_PERSIST_DIR="./chroma_db"

# Optional: Adjust processing (lower = faster but fewer companies)
MAX_WORKERS="4"        # Parallel downloads (default: 4)
BATCH_SIZE="32"        # Embedding batch size (default: 32)
```

### Manual Build (Optional)

If you prefer to build ChromaDB before your first query:

```bash
cd /Users/pradeepsahu/dev_data/StockSearhMCP
source .venv/bin/activate

# Set environment variables
export OPENAI_API_KEY="your-key"
export SEC_API_USER_AGENT="YourCompany contact@example.com"

# Run builder
python src/sector/builder.py
```

**Note**: First-time build takes 20-40 minutes. You'll see progress updates during the build.

## ⚙️ Configuration

Add to your MCP settings file to connect with Claude Desktop or other MCP clients.

### macOS/Linux

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stock-research": {
      "command": "/Users/pradeepsahu/dev_data/StockSearhMCP/.venv/bin/python",
      "args": [
        "-m",
        "stock_research_mcp.server"
      ],
      "env": {
        "PYTHONPATH": "/Users/pradeepsahu/dev_data/StockSearhMCP/src",
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "SEC_API_USER_AGENT": "YourCompany contact@youremail.com",
        "CHROMA_PERSIST_DIR": "/Users/pradeepsahu/dev_data/StockSearhMCP/output/chroma_db",
        "USE_REAL_API": "true",
        "USE_CHROMA_SECTORS": "true",
        "MAX_WORKERS": "4",
        "BATCH_SIZE": "32"
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
      "command": "/Users/pradeepsahu/dev_data/StockSearhMCP/.venv/bin/stock-research-mcp",
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "CHROMA_PERSIST_DIR": "/Users/pradeepsahu/dev_data/StockSearhMCP/output/chroma_db",
        "USE_REAL_API": "true",
        "USE_CHROMA_SECTORS": "true"
      }
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
        "PYTHONPATH": "C:\\Users\\YourUsername\\dev_data\\StockSearhMCP\\src",
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "SEC_API_USER_AGENT": "YourCompany contact@youremail.com",
        "CHROMA_PERSIST_DIR": "C:\\Users\\YourUsername\\dev_data\\StockSearhMCP\\output\\chroma_db",
        "USE_REAL_API": "true",
        "USE_CHROMA_SECTORS": "true",
        "MAX_WORKERS": "4",
        "BATCH_SIZE": "32"
      }
    }
  }
}
```

## 🎯 Usage

Once configured, you can use the server through MCP-compatible clients like Claude Desktop.

### 🤖 How Claude Decides to Use the Tool

**Claude AI automatically decides** when to call the `analyze_sector` tool based on your query:

**✅ Tool WILL be called:**
- "Analyze technology stocks"
- "Show me healthcare sector analysis"
- "What are the best finance stocks?"
- "Use analyze_sector for energy"
- "Search for semiconductor companies"

**❌ Tool might NOT be called:**
- "Tell me about stocks" (too vague, Claude answers from knowledge)
- "What's a good investment?" (general financial advice)
- "Explain the stock market" (educational, not sector analysis)

**💡 Pro Tip:** Be specific about sectors/industries to ensure the tool is used. You can also explicitly say "use the tool" or "analyze the sector."

**Where it happens:** The tool call is handled by the MCP server in `src/stock_research_mcp/server.py` at the `@self.server.call_tool()` decorator, which routes to the multi-agent analysis pipeline.

### How It Works (Complete Flow)

**🎬 First Query** (one-time setup):

1. **User Query** → You ask Claude: "Analyze stocks in the biotechnology sector"

2. **Automatic ChromaDB Build** → System detects no database and builds it:
   - Shows real-time progress: "📥 Fetching company tickers... ✅ Found 8,000 companies"
   - Downloads SEC filings with updates: "📊 Progress: 100/8000 processed"
   - Creates embeddings and stores in ChromaDB
   - Takes 20-40 minutes with streaming progress updates
   - Database persists permanently on disk

3. **Query Execution** → After build completes:
   - Semantic search finds biotechnology companies
   - Multi-agent analysis runs
   - Results displayed

**⚡ Subsequent Queries** (instant):

1. **User Query** → You ask: "Show me semiconductor stocks"

2. **ChromaDB Semantic Search** → Instant lookup from persistent database:
   - Converts "semiconductor" to embedding
   - Finds matching companies in SEC filings
   - Returns tickers (NVDA, AMD, INTC, etc.)

3. **Multi-Agent Processing**:
   - **Search Agent**: Uses ChromaDB + real-time APIs
   - **Categorization Agent**: Groups by price
   - **Analysis Agent**: News, events, recommendations

4. **Result Display** → Comprehensive report in seconds

### Example Queries

Ask Claude:
- "Analyze stocks in the technology sector"
- "Show me biotechnology companies and their analysis"
- "What are the best renewable energy stocks right now?"
- "Give me a breakdown of artificial intelligence sector stocks"
- "Find companies in the semiconductor industry"

**Note**: The ChromaDB enables natural language sector queries! You can ask about specific industries, and the semantic search will find relevant companies based on their actual business descriptions from SEC filings.

### 📋 Viewing MCP Server Logs

**Log locations:**
- Main server log: `~/Library/Logs/Claude/mcp-server-stock-research.log`
- General MCP log: `~/Library/Logs/Claude/mcp.log`

**Useful commands:**
```bash
# Follow live logs
tail -f ~/Library/Logs/Claude/mcp-server-stock-research.log

# View last 100 lines
tail -100 ~/Library/Logs/Claude/mcp-server-stock-research.log

# Search for specific stock
grep "AAPL" ~/Library/Logs/Claude/mcp-server-stock-research.log

# See only errors
grep "ERROR" ~/Library/Logs/Claude/mcp-server-stock-research.log

# View analysis reports
grep -A 50 "STOCK ANALYSIS REPORT" ~/Library/Logs/Claude/mcp-server-stock-research.log
```

**What you'll see:**
- Tool calls: `Processing sector analysis request for: technology`
- Stock fetching: `Fetched AAPL: $276.97`
- Agent workflow: `[StockSearchAgent]`, `[StockCategorizationAgent]`, `[StockAnalysisAgent]`
- ChromaDB operations: `Found 15 stocks in technology sector`
- Full analysis results sent to Claude

### Available Tools

#### `analyze_sector`

Performs comprehensive multi-agent analysis on a sector.

**Parameters:**
- `sector` (string, required): The sector to analyze

**Supported Sectors:**
- **Any sector or industry!** Thanks to ChromaDB semantic search on SEC filings
- Examples: technology, healthcare, finance, energy, biotechnology, semiconductors, renewable energy, artificial intelligence, e-commerce, automotive, pharmaceuticals, real estate, aerospace, telecommunications, retail, etc.

**How it works:** The system uses semantic search on company business descriptions from SEC filings, so you can query any industry using natural language - not limited to predefined categories!

**Example:**
```json
{
  "sector": "technology"
}
```

## 🏗️ Architecture

### Multi-Agent Design with ChromaDB Integration

```
User Query: "Analyze biotechnology sector"
    ↓
Orchestrator
    ↓
    ├─→ StockSearchAgent
    │    ├─→ Query ChromaDB (semantic search on SEC filings)
    │    │   Returns: [MRNA, GILD, BIIB, VRTX, ...]
    │    └─→ Fetch real-time data from Yahoo Finance API
    ↓
    ├─→ StockCategorizationAgent
    │    └─→ Group by price (High: >$100, Medium: $10-$100, Low: <$10)
    ↓
    └─→ StockAnalysisAgent (for each stock)
         ├─→ Price Analysis (trend, momentum)
         ├─→ News Sentiment (from APIs)
         ├─→ Event Calendar (earnings, dividends)
         └─→ Investment Recommendation
    ↓
Final Report to User
```

**Key Innovation**: The system uses **semantic search** on SEC filing data stored in ChromaDB, allowing it to understand natural language sector queries and find relevant companies dynamically, rather than relying on hardcoded mappings.

### Project Structure

```
src/
├── stock_research_mcp/
│   ├── __init__.py              # Package initialization
│   ├── server.py                # MCP server entry point
│   ├── types.py                 # Data models (Pydantic)
│   └── agents/
│       ├── __init__.py
│       ├── stock_search_agent.py           # Agent 1: Search (uses ChromaDB)
│       ├── stock_categorization_agent.py   # Agent 2: Categorize
│       ├── stock_analysis_agent.py         # Agent 3: Analyze
│       ├── orchestrator.py                 # Coordinates all agents
│       ├── real_api_fetcher.py            # Real API integrations
│       └── sector_ticker_fetcher.py       # ChromaDB query helper
└── sector/
    ├── fetch_tickers.py         # Fetch company tickers from SEC
    ├── fetch_filings.py         # Download SEC filings
    ├── extract_text.py          # Extract business sections
    ├── embeddings_and_chroma.py # OpenAI embeddings + ChromaDB
    ├── builder.py               # Build ChromaDB index (run first!)
    └── search_api.py            # Optional: FastAPI search interface
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

### ChromaDB not found / No stocks returned

**Problem**: System falls back to hardcoded sector mappings or returns empty results.

**Solution**:
1. Verify ChromaDB was built: `ls -la output/chroma_db/`
2. Check environment variable: `echo $CHROMA_PERSIST_DIR`
3. Rebuild index: `python src/sector/builder.py`
4. Set `CHROMA_PERSIST_DIR` in MCP config to absolute path: `/Users/pradeepsahu/dev_data/StockSearhMCP/output/chroma_db`

### ChromaDB query error: "Expected include item to be..."

**Problem**: Error in logs: `Error querying ChromaDB: Expected include item to be one of documents, embeddings, metadatas, distances, uris, data, got ids in query.`

**Status**: ✅ **FIXED** - This error has been resolved in the latest version. ChromaDB's `query()` method always returns `ids` by default, so `"ids"` should not be in the `include` parameter.

**If you still see this error**: Make sure you have the latest code from `src/stock_research_mcp/agents/sector_ticker_fetcher.py`

### Server won't start

- Ensure virtual environment is activated
- Check Python version: `python --version` (should be 3.10+)
- Reinstall dependencies: `pip install -e .`
- Verify `OPENAI_API_KEY` is set

### Import errors

- Verify PYTHONPATH in your MCP config
- Make sure you're in the correct directory
- Check that all agent files exist
- Ensure ChromaDB directory is accessible

### Builder script fails

**SEC 403 Error**:
- Set `SEC_API_USER_AGENT` with your contact email
- Example: `"YourCompany contact@example.com"`

**OpenAI API Error**:
- Verify `OPENAI_API_KEY` is valid
- Check API quota/billing at platform.openai.com

**Download timeouts**:
- Reduce `MAX_WORKERS` (try 4 instead of 8)
- Check internet connection

### MCP connection issues

**Problem**: Claude Desktop doesn't show the stock-research tool or can't connect to server.

**Solution checklist:**
1. ✅ **Config location**: Must be `~/Library/Application Support/Claude/claude_desktop_config.json` (user home, not system `/Library`)
2. ✅ **Absolute python path**: Use `/Users/pradeepsahu/dev_data/StockSearhMCP/.venv/bin/python`, NOT just `"python"`
3. ✅ **Valid API key**: Replace `"your-openai-api-key-here"` with actual OpenAI key
4. ✅ **JSON syntax**: Validate at https://jsonlint.com (no trailing commas)
5. ✅ **Full restart**: Quit Claude Desktop (Cmd+Q), wait 5 seconds, reopen
6. ✅ **Check connection**: Look for 🔌 green plug icon in bottom-left corner of Claude Desktop
7. ✅ **View logs**: `tail -f ~/Library/Logs/Claude/mcp*.log` to see connection errors

**Test server manually:**
```bash
cd /Users/pradeepsahu/dev_data/StockSearhMCP
source .venv/bin/activate
python -m stock_research_mcp.server
# Should show: "Stock Research MCP Server starting..."
# Press Ctrl+D to exit
```

**Force tool usage in Claude:**
- Bad: "Tell me about tech stocks" (Claude might answer from knowledge)
- Good: "Analyze technology sector stocks" (Claude will use the tool)
- Explicit: "Use the analyze_sector tool for healthcare"

## 🔄 Updating the ChromaDB Index

### When to Rebuild

Rebuild the ChromaDB index when:
- New companies file with SEC
- You want to refresh with latest 10-K/10-Q filings
- The index becomes corrupted
- You want to expand to more companies

### How to Update

```bash
# Option 1: Full rebuild (deletes old data)
rm -rf output/chroma_db/
python src/sector/builder.py

# Option 2: Incremental update (builder will add/update)
python src/sector/builder.py
```

### Customizing the Index

**Include more/fewer companies**:
Edit `src/sector/fetch_tickers.py` to filter by market cap, exchange, etc.

**Add specific tickers**:
Create a custom ticker list JSON file and modify `builder.py`

**Change filing types**:
Edit `candidates` list in `src/sector/fetch_filings.py`:
```python
candidates = ["10-K", "20-F", "S-1", "10-Q"]  # Modify as needed
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
