# Testing Claude Desktop MCP Connection

## ✅ How to Verify Claude Desktop is Using stock-research

### 1. Check for MCP Connection Indicator
Look at the **bottom-left corner** of Claude Desktop:
- 🔌 **Green plug icon** = MCP servers connected
- Click the plug icon to see list of connected servers
- You should see "stock-research" in the list

### 2. Check Available Tools
In a new conversation with Claude, type:
```
What tools do you have available?
```
Claude should list `analyze_sector` in its response.

### 3. Force Claude to Use the Tool - Test Queries

**Simple test (forces tool use):**
```
Use the analyze_sector tool to analyze technology stocks
```

**Natural language test:**
```
Analyze stocks in the technology sector
```

**Specific request:**
```
Show me high-value technology stocks over $100 with their analysis
```

**Check if ChromaDB needs building:**
```
Search for stocks in the renewable energy sector
```
If ChromaDB is empty, you'll see streaming progress as it builds automatically.

### 4. View MCP Server Logs

**Check if server is running:**
```bash
# View Claude's MCP logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

Look for:
- `Stock Research MCP Server starting...`
- `Tool analyze_sector called with sector: <sector-name>`
- Any error messages

### 5. Manual Server Test

**Test the server directly:**
```bash
cd /Users/pradeepsahu/dev_data/StockSearhMCP
source .venv/bin/activate
python -m stock_research_mcp.server
```

Expected output:
```
Stock Research MCP Server starting...
Registered tool: analyze_sector
```

Then press `Ctrl+D` to send EOF and exit cleanly.

## 🔧 If Claude Doesn't Use the Tool

### A. Restart Claude Desktop Completely
1. Quit Claude Desktop: **Cmd+Q** (not just close window!)
2. Wait 5 seconds
3. Reopen Claude Desktop
4. Check for 🔌 icon in bottom-left

### B. Explicitly Request Tool Use
Claude has discretion on whether to use tools. To force it:

**Use explicit language:**
- "Use the analyze_sector tool..."
- "Call the stock analysis tool..."
- "Search the stock database for..."

**Bad (Claude might not use tool):**
- "Tell me about tech stocks" (might just answer from knowledge)
- "What are good investments?" (too general)

**Good (Claude will use tool):**
- "Analyze technology sector stocks"
- "Use analyze_sector for healthcare"
- "Search for semiconductor stocks"

### C. Check Server Status

**1. Verify server can start:**
```bash
cd /Users/pradeepsahu/dev_data/StockSearhMCP
./.venv/bin/python -m stock_research_mcp.server
# Should not show any import errors or crashes
# Press Ctrl+D to exit
```

**2. Check MCP package installed:**
```bash
source .venv/bin/activate
pip list | grep mcp
# Should show: mcp  x.x.x
```

**3. Verify config syntax:**
```bash
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python3 -m json.tool
# Should output formatted JSON without errors
```

### D. Debug Checklist

- [ ] Config file at: `~/Library/Application Support/Claude/claude_desktop_config.json`
- [ ] Python path in config matches: `/Users/pradeepsahu/dev_data/StockSearhMCP/.venv/bin/python`
- [ ] OPENAI_API_KEY is set to valid key (not placeholder)
- [ ] Claude Desktop fully restarted (Cmd+Q)
- [ ] 🔌 green plug icon visible in Claude
- [ ] Server starts without errors when tested manually
- [ ] Using explicit language in requests

## 📊 Expected Behavior

### First Query (ChromaDB Empty)
```
You: "Analyze technology sector stocks"

Claude: "I'll build the stock database first..."
[Streaming progress shows]
"Building ChromaDB with SEC filings..."
"Processing 50 companies..."
"Processing 100 companies..."
...
"Database built! Now analyzing technology sector..."
[Shows stock analysis results]
```

### Subsequent Queries (ChromaDB Built)
```
You: "Analyze healthcare stocks"

Claude: [Immediately shows results]
"Found 47 healthcare stocks:

HIGH VALUE (>$100):
- AAPL: $175.23 - Analysis...
...
```

## 🎯 Best Test Query

Use this to confirm everything works:
```
Analyze semiconductor stocks and categorize them by price
```

This query will:
1. Force tool usage (specific sector)
2. Test ChromaDB semantic search
3. Test multi-agent coordination
4. Show all three price categories
5. Display full analysis with news/events

## 💡 Pro Tips

**Make Claude use the tool reliably:**
- Start fresh conversation
- Be specific about sector/industry
- Use action words: "analyze", "search", "find"
- Mention price categories or specific requirements

**If tool isn't being used:**
- Claude might answer from general knowledge instead
- Solution: Be more specific or say "use the tool"
- Example: "Don't use your knowledge, use the analyze_sector tool for biotech stocks"
