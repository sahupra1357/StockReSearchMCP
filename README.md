# Stock Research MCP Server

A sophisticated **multi-agent Model Context Protocol (MCP) server** for comprehensive stock research and analysis. Query any sector or industry using natural language and get instant, detailed analysis backed by SEC filings and real-time market data.

## ✨ Key Highlights

- 🤖 **Multi-Agent Architecture**: Three specialized AI agents work together for comprehensive analysis
- 🔍 **Semantic Search**: ChromaDB with 8,000+ company SEC filings enables natural language queries
- 🚀 **Zero Configuration**: Automatic ChromaDB setup on first use with streaming progress
- 🌐 **Dual Interface**: Use via Claude Desktop (MCP) or Gradio web interface
- 📊 **Real-Time Data**: Integration with Yahoo Finance and OpenAI for current market insights
- ⚡ **Fast & Efficient**: ~355ms latency for analysis queries after initial setup

## 📑 Table of Contents

- [Features](#-features)
- [Installation & Quick Start](#-installation--quick-start)
- [ChromaDB Setup](#️-chromadb-setup---automatic-on-first-use)
- [Configuration](#️-configuration)
- [Usage - Two Ways](#-usage---two-ways-to-access)
  - [Gradio Web Interface](#1--gradio-web-interface-easiest)
  - [Claude Desktop (MCP)](#2--claude-desktop-mcp-integration)
- [Architecture](#️-architecture)
- [Development](#-development)
- [Extending with APIs](#-extending-with-real-data-sources)
- [Troubleshooting](#️-troubleshooting)
- [Updating ChromaDB](#-updating-the-chromadb-index)
- [Contributing](#-contributing)
- [License & Disclaimer](#-disclaimer)

## 🚀 Features

### 🤖 Multi-Agent System

**Three Specialized Agents Working Together:**

1. **Stock Search Agent** 
   - Semantic search on SEC filings via ChromaDB
   - Real-time data from Yahoo Finance API
   - Finds companies using natural language queries

2. **Stock Categorization Agent**
   - Groups stocks by price ranges
   - High: >$100, Medium: $10-$100, Low: <$10
   - Smart categorization logic

3. **Stock Analysis Agent**
   - Price trend analysis (bullish/bearish patterns)
   - News sentiment analysis
   - Upcoming events (earnings, dividends)
   - AI-powered investment recommendations

### 📊 Complete Analysis Pipeline

When you query any sector/industry:

1. **Semantic Search** → Finds relevant companies from SEC filings database
2. **Real-Time Fetching** → Gets current prices, changes, market cap from Yahoo Finance
3. **Categorization** → Groups stocks by price range
4. **Deep Analysis** → For each stock:
   - Price trends & momentum
   - Recent news with sentiment
   - Upcoming events calendar
   - Investment recommendation

### 🔍 ChromaDB Integration

- **Automatic Build**: First query triggers one-time setup (20-40 min)
- **8,000+ Companies**: Indexed from SEC EDGAR filings
- **Semantic Search**: Natural language understanding of sectors/industries
- **Persistent Storage**: Database saved permanently for instant future queries
- **Streaming Progress**: Real-time updates during initial build

## 📦 Installation & Quick Start

### Prerequisites

- **Python 3.10+** or higher
- **pip** package manager
- **OpenAI API Key** for embeddings
- **SEC-compliant User-Agent** for filing downloads

### Quick Setup (5 minutes)

```bash
# 1. Navigate to project directory
cd /Users/pradeepsahu/dev_data/StockSearhMCP

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 4. Install dependencies
pip install -e .

# 5. Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export SEC_API_USER_AGENT="YourCompany contact@youremail.com"

# 6. (Optional) Test installation
python test_installation.py
```

### Verify Installation

```bash
# Quick test - should show analysis of technology stocks
python examples/basic_usage.py
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

## 🎯 Usage - Two Ways to Access

### 1. 🌐 Gradio Web Interface (Easiest)

**Launch the web interface for a user-friendly experience:**

```bash
# Option 1: Using launch script
./launch_gradio.sh

# Option 2: Direct Python
python gradio_app.py
```

**Access at:** `http://localhost:7860`

**Features:**
- 🎨 Beautiful web UI with real-time progress bars
- 💡 Example sectors (technology, healthcare, biotech, etc.)
- 📊 Instant analysis results in formatted reports
- 📋 Copy button for results
- 🔄 Database status indicator
- 📱 Mobile-responsive design

**Example Usage:**
1. Enter "technology" or click example button
2. Click "Analyze Sector"
3. Watch progress during first-time ChromaDB build (20-40 min)
4. Get instant results on subsequent queries
5. Copy/share analysis reports

**Advantages:**
- ✅ No MCP configuration needed
- ✅ Works without Claude Desktop
- ✅ Visual progress tracking
- ✅ Easy to share with team
- ✅ Direct API access to all features

### 2. 🤖 Claude Desktop (MCP Integration)

**Use through Claude Desktop for AI-powered interaction:**

Once configured (see Configuration section), Claude automatically decides when to use the tool.

**✅ Queries that trigger the tool:**
```
"Analyze technology stocks"
"Show me healthcare sector analysis"
"What are the best semiconductor companies?"
"Use analyze_sector for renewable energy"
"Search for biotechnology stocks"
```

**❌ Queries that might NOT trigger the tool:**
```
"Tell me about stocks" (too vague - Claude uses general knowledge)
"What's a good investment?" (general advice, not sector-specific)
"Explain the stock market" (educational, not analysis)
```

**💡 Pro Tips:**
- Be specific about sectors/industries
- Use action words: "analyze", "search", "find"
- Explicitly say "use the tool" if needed
- Start fresh conversation for reliable tool usage

### How the System Works

**🎬 First Query Flow** (one-time setup):

```
User asks: "Analyze biotechnology sector"
         ↓
System detects: No ChromaDB found
         ↓
Automatic Build Starts (streaming progress):
  📥 Step 1: Fetching company tickers from SEC → 8,000 companies
  📄 Step 2: Downloading filings (20-40 min)
     Progress: 100/8000, 200/8000... (updates every 10 companies)
     💾 Indexing batches to ChromaDB
  🔍 Step 3: Verifying index
  ✅ Step 4: Build complete! → 7,500 companies indexed
         ↓
Query Execution:
  - Semantic search finds biotechnology companies
  - Multi-agent analysis runs
  - Results displayed
```

**⚡ Subsequent Queries** (instant - <1 second):

```
User asks: "Show me semiconductor stocks"
         ↓
ChromaDB Semantic Search (instant):
  - Convert "semiconductor" to embedding
  - Find matches in SEC filings
  - Returns: NVDA, AMD, INTC, QCOM, etc.
         ↓
Multi-Agent Processing:
  ├─→ Search Agent: Fetch real-time prices (Yahoo Finance)
  ├─→ Categorization Agent: Group by price ranges
  └─→ Analysis Agent: News, events, recommendations
         ↓
Comprehensive Report (formatted & delivered)
```

### Example Queries (Any Sector/Industry!)

**Technology:**
- "Analyze stocks in the technology sector"
- "Show me semiconductor companies"
- "Find artificial intelligence stocks"

**Healthcare:**
- "Analyze biotechnology companies"
- "Show me pharmaceutical stocks"
- "Find medical device companies"

**Other Industries:**
- "What are the best renewable energy stocks?"
- "Analyze e-commerce companies"
- "Find cloud computing stocks"
- "Show me cybersecurity companies"

**Natural Language Works!**
The ChromaDB semantic search understands your intent based on SEC filing business descriptions, so you can query any industry using natural language.

### Available MCP Tool

#### `analyze_sector`

**Description:** Performs comprehensive multi-agent analysis on any sector or industry.

**Parameters:**
- `sector` (string, required): Natural language description of sector/industry

**Supported Sectors:**
- **ANY sector or industry!** Thanks to ChromaDB semantic search on 8,000+ SEC filings
- Not limited to predefined categories - uses natural language understanding

**Examples:**
```json
{"sector": "technology"}
{"sector": "biotechnology"}
{"sector": "renewable energy"}
{"sector": "artificial intelligence"}
{"sector": "semiconductor manufacturing"}
```

### 📋 Debugging & Logs

**View MCP Server Logs:**

```bash
# Follow live logs
tail -f ~/Library/Logs/Claude/mcp-server-stock-research.log

# View last 100 lines
tail -100 ~/Library/Logs/Claude/mcp-server-stock-research.log

# Search for errors
grep "ERROR" ~/Library/Logs/Claude/mcp-server-stock-research.log

# View analysis reports
grep -A 50 "STOCK ANALYSIS REPORT" ~/Library/Logs/Claude/mcp-server-stock-research.log

# Search for specific stock
grep "AAPL" ~/Library/Logs/Claude/mcp-server-stock-research.log
```

**What You'll See in Logs:**
- Tool calls: `Processing sector analysis request for: technology`
- Stock fetching: `Fetched AAPL: $276.97`
- Agent workflow: `[StockSearchAgent]`, `[StockCategorizationAgent]`, `[StockAnalysisAgent]`
- ChromaDB: `Found 15 stocks in technology sector`
- Full analysis results

## 🏗️ Architecture

### System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUERY                               │
│         "Analyze stocks in biotechnology sector"            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP SERVER (server.py)                         │
│  - Receives query via stdio                                 │
│  - Validates input                                          │
│  - Routes to orchestrator                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         ORCHESTRATOR (orchestrator.py)                      │
│  - Coordinates all 3 agents                                 │
│  - Manages workflow pipeline                                │
│  - Formats final output                                     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌─────────────────────┐         ┌─────────────────────────┐
│  STEP 1: SEARCH     │         │  ChromaDB Integration   │
│  ───────────────    │         │  ───────────────────    │
│  StockSearchAgent   │         │  • Semantic search      │
│                     │◄────────┤  • 8,000+ companies     │
│  Actions:           │         │  • SEC filings data     │
│  • Query ChromaDB   │         │  • Natural language     │
│  • Yahoo Finance    │         └─────────────────────────┘
│  • Return stocks    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────┐
│  STEP 2: CATEGORIZE     │
│  ───────────────────    │
│  StockCategorization    │
│                         │
│  • High: >$100          │
│  • Medium: $10-$100     │
│  • Low: <$10            │
└──────────┬──────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│  STEP 3: ANALYZE (for each stock)                        │
│  ─────────────────────────────                           │
│  StockAnalysisAgent                                      │
│                                                          │
│  ┌──────────────────────────────────────────────┐       │
│  │ Price Analysis: trend, momentum, support     │       │
│  └──────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────┐       │
│  │ News Collection: sentiment, sources          │       │
│  └──────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────┐       │
│  │ Events: earnings, dividends, launches        │       │
│  └──────────────────────────────────────────────┘       │
│  ┌──────────────────────────────────────────────┐       │
│  │ Recommendations: signals, advice, risk       │       │
│  └──────────────────────────────────────────────┘       │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FORMATTED REPORT                          │
│  ═══════════════════════════════════════════════════       │
│  STOCK ANALYSIS REPORT - BIOTECHNOLOGY SECTOR               │
│  ═══════════════════════════════════════════════════       │
│  HIGH-VALUE STOCKS (7): MRNA, GILD, BIIB...               │
│  MEDIUM-VALUE STOCKS (12): VRTX, REGN...                   │
│  LOW-VALUE STOCKS (8): Small caps...                       │
│                                                             │
│  Full analysis with news, events, recommendations          │
└─────────────────────────────────────────────────────────────┘
```

**Key Innovation:** Semantic search on SEC filing data enables natural language understanding of sectors/industries - no hardcoded mappings required!

### Project Structure

```
StockSearhMCP/
├── src/
│   ├── stock_research_mcp/           # Main package
│   │   ├── server.py                    → MCP server entry point
│   │   ├── types.py                     → Pydantic data models
│   │   └── agents/                      → Multi-agent system
│   │       ├── orchestrator.py             → Coordinates all agents
│   │       ├── stock_search_agent.py       → Agent 1: Search
│   │       ├── stock_categorization_agent.py → Agent 2: Categorize
│   │       ├── stock_analysis_agent.py     → Agent 3: Analyze
│   │       ├── sector_ticker_fetcher.py    → ChromaDB helper
│   │       └── real_api_fetcher.py         → Yahoo Finance integration
│   └── sector/                        # ChromaDB build system
│       ├── builder.py                    → Main build script
│       ├── fetch_tickers.py              → Get companies from SEC
│       ├── fetch_filings.py              → Download 10-K/10-Q filings
│       ├── extract_text.py               → Extract business descriptions
│       ├── embeddings_and_chroma.py      → OpenAI + ChromaDB
│       └── search_api.py                 → Optional: FastAPI interface
├── gradio_app.py                      # Web interface
├── test_gradio_setup.py               # Gradio verification
├── launch_gradio.sh                   # Launch script
├── examples/
│   ├── basic_usage.py                 # Simple example
│   └── real_api_integration.py        # API integration demo
└── output/
    └── chroma_db/                     # ChromaDB persistent storage
```

### Data Models (types.py)

```python
Stock                           # Company information
├── symbol: str                 # AAPL, MSFT, etc.
├── name: str                   # Apple Inc.
├── price: float                # 175.43
├── sector: str                 # Technology
├── market_cap: float           # Optional
├── change: float               # +1.35
└── change_percent: float       # +0.77%

StockCategory (Enum)            # Price ranges
├── HIGH      (> $100)
├── MEDIUM    ($10-$100)
└── LOW       (< $10)

PriceAnalysis                   # Technical analysis
├── current_price: float
├── trend: str                  # bullish/bearish
├── support: float              # Support level
└── resistance: float           # Resistance level

NewsItem                        # News articles
├── title: str
├── source: str
├── date: str
├── sentiment: str              # positive/negative/neutral
└── summary: str

EventItem                       # Upcoming events
├── type: str                   # Earnings Call, Dividend, etc.
├── date: str
├── description: str
└── impact: str                 # high/medium/low

StockAnalysis                   # Complete analysis
├── stock: Stock
├── category: StockCategory
├── price_analysis: PriceAnalysis
├── news: List[NewsItem]
├── events: List[EventItem]
└── recommendation: str
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

## 📊 Sample Output

The system generates comprehensive reports with this format:

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

### ChromaDB Issues

**Problem: ChromaDB not found / No stocks returned**

✅ **Solutions:**
```bash
# 1. Verify ChromaDB exists
ls -la output/chroma_db/

# 2. Check environment variable
echo $CHROMA_PERSIST_DIR

# 3. Rebuild if needed
python src/sector/builder.py

# 4. Use absolute path in MCP config
CHROMA_PERSIST_DIR="/Users/pradeepsahu/dev_data/StockSearhMCP/output/chroma_db"
```

**Problem: ChromaDB query error: "Expected include item to be..."**

✅ **Status: FIXED** in latest version
- ChromaDB's `query()` always returns `ids` by default
- Latest code removes `"ids"` from `include` parameter
- Update from `src/stock_research_mcp/agents/sector_ticker_fetcher.py` if needed

### MCP Connection Issues

**Problem: Claude Desktop doesn't show the tool**

✅ **Complete Checklist:**

1. **Config Location** (macOS):
   ```bash
   # Must be in user home, not system /Library
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

2. **Absolute Python Path**:
   ```json
   "command": "/Users/pradeepsahu/dev_data/StockSearhMCP/.venv/bin/python"
   ```
   ❌ NOT: `"python"` or `"python3"`

3. **Valid API Key**:
   ```json
   "OPENAI_API_KEY": "sk-proj-actual-key-here"
   ```
   ❌ NOT: `"your-openai-api-key-here"`

4. **JSON Syntax**:
   - Validate at https://jsonlint.com
   - No trailing commas
   - Proper quotes and brackets

5. **Full Restart**:
   ```bash
   # Quit (Cmd+Q), wait 5 sec, reopen
   ```

6. **Check Connection**:
   - Look for 🔌 green plug icon (bottom-left of Claude Desktop)
   - Click to see connected servers list

7. **View Logs**:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

**Test Server Manually:**
```bash
cd /Users/pradeepsahu/dev_data/StockSearhMCP
source .venv/bin/activate
python -m stock_research_mcp.server
# Should show: "Stock Research MCP Server starting..."
# Press Ctrl+D to exit
```

**Force Tool Usage in Claude:**
- ❌ Bad: "Tell me about tech stocks" (Claude uses general knowledge)
- ✅ Good: "Analyze technology sector stocks" (forces tool call)
- ✅ Explicit: "Use the analyze_sector tool for healthcare"

### Installation & Server Issues

**Problem: Server won't start**

```bash
# Check Python version (need 3.10+)
python --version

# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -e .

# Verify OpenAI key
echo $OPENAI_API_KEY
```

**Problem: Import errors**

```bash
# Check PYTHONPATH in MCP config
echo $PYTHONPATH

# Verify all files exist
ls -la src/stock_research_mcp/agents/

# Check ChromaDB access
ls -la output/chroma_db/
```

### Builder Script Issues

**Problem: SEC 403 Forbidden Error**

✅ Set SEC-compliant User-Agent:
```bash
export SEC_API_USER_AGENT="YourCompany contact@example.com"
```

**Problem: OpenAI API Error**

✅ Solutions:
```bash
# Verify key is valid
echo $OPENAI_API_KEY

# Check quota/billing
# Visit: https://platform.openai.com/usage
```

**Problem: Download timeouts**

✅ Reduce workers:
```bash
export MAX_WORKERS="4"  # Instead of 8
export BATCH_SIZE="32"  # Instead of 64
```

### Gradio Interface Issues

**Problem: Port 7860 already in use**

```bash
# Kill existing process
lsof -ti:7860 | xargs kill -9

# Or change port in gradio_app.py
server_port=8080  # Use different port
```

**Problem: Missing Gradio**

```bash
pip install gradio
# Or
uv pip install gradio
```

**Problem: OpenAI key not working**

Check `.env` file:
```bash
cat .env
# Should have: OPENAI_API_KEY=sk-proj-actual-key
```

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
