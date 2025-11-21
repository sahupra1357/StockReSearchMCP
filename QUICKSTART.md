# Quick Start Guide

## 1. Setup (5 minutes)

```bash
# Navigate to project directory
cd /Users/pradeepsahu/dev_data/StockSearhMCP

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -e .
```

## 2. Test the Installation

```bash
# Run example script to verify everything works
python examples/basic_usage.py
```

You should see a detailed analysis of technology sector stocks.

## 3. Configure Claude Desktop

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

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

**Important:** Update the PYTHONPATH to match your actual installation path!

## 4. Restart Claude Desktop

Close and reopen Claude Desktop completely for the changes to take effect.

## 5. Test in Claude

Try these commands in Claude:

1. "Can you analyze stocks in the technology sector?"
2. "Show me healthcare stocks"
3. "What are the best finance stocks?"

## 6. Verify It's Working

You should see:
- List of stocks in the sector
- Stocks categorized by price (High/Medium/Low)
- Analysis with news, events, and recommendations for each stock

## Troubleshooting

### "Module not found" error
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall
pip install -e .
```

### "Can't find the tool" in Claude
- Double-check the config file path
- Verify JSON syntax (use a JSON validator)
- Restart Claude Desktop completely
- Check that the PYTHONPATH matches your installation

### Want to see logs?
```bash
# Run the server directly to see output
python -m stock_research_mcp.server
```

## Next Steps

1. **Test with different sectors:**
   - technology
   - healthcare
   - finance
   - energy

2. **Review the code:**
   - Check `src/stock_research_mcp/agents/` to see how agents work
   - Look at `src/stock_research_mcp/types.py` for data structures

3. **Add real APIs (optional):**
   - See `examples/real_api_integration.py`
   - Get API keys from Alpha Vantage, News API, etc.
   - Create `.env` file from `.env.example`

## Architecture Overview

```
Query: "Analyze technology stocks"
         ↓
    Orchestrator
         ↓
    [Agent 1: Search] → Finds all tech stocks
         ↓
    [Agent 2: Categorize] → Groups by price
         ↓
    [Agent 3: Analyze] → Analyzes each stock
         ↓
    Formatted Report
```

## Need Help?

- Check README.md for detailed documentation
- Look at examples/ folder for usage examples
- Review agent code in src/stock_research_mcp/agents/
