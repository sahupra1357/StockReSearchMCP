# Streaming ChromaDB Build - User Experience Guide

## 🎯 What Changed?

**Before**: Users had to manually run `python src/sector/builder.py` and wait 30-60 minutes before using the MCP server.

**Now**: ChromaDB builds automatically on the first query with real-time progress updates streamed to the user!

## 🔄 Complete User Flow

### First Time Use

```
User: "Analyze stocks in the biotechnology sector"
    ↓
System detects: No ChromaDB found
    ↓
Automatic build starts with streaming updates:

================================================================================
📦 FIRST-TIME SETUP: BUILDING CHROMADB INDEX
================================================================================

ℹ️  This is a one-time setup that runs on your first query.
The database will be stored permanently for future use.

🚀 Starting ChromaDB index build...
📁 Storage location: /Users/.../chroma_db

📥 Step 1/4: Fetching company tickers from SEC...
✅ Found 8,000 companies to index

📄 Step 2/4: Downloading SEC filings (using 4 workers)...
⏳ This may take 20-40 minutes depending on your connection...
   📊 Progress: 10/8000 processed, 8 successful
   📊 Progress: 20/8000 processed, 16 successful
   💾 Indexing batch of 32 companies to ChromaDB...
   📊 Progress: 30/8000 processed, 24 successful
   ... (continues with updates every 10 companies)
   
✅ Step 2/4 Complete: Successfully indexed 7,500 companies

🔍 Step 3/4: Verifying ChromaDB index...
✅ ChromaDB index verified and ready

🎉 Step 4/4: Build complete!
📊 Total companies indexed: 7,500/8,000
💾 Database location: /Users/.../chroma_db

✨ ChromaDB is now ready for semantic search!
🔄 Proceeding with your original query...

================================================================================

[Now executes the actual stock analysis...]

================================================================================
STOCK ANALYSIS REPORT - BIOTECHNOLOGY SECTOR
================================================================================
...
```

### All Subsequent Uses

```
User: "Show me semiconductor companies"
    ↓
System detects: ChromaDB exists ✅
    ↓
Instant analysis (no build needed):

================================================================================
STOCK ANALYSIS REPORT - SEMICONDUCTOR SECTOR
================================================================================
Total Stocks Analyzed: 12
...
```

## 📊 Progress Updates

The streaming builder provides detailed progress:

| Stage | Update Type | Example |
|-------|-------------|---------|
| **Initialization** | Status | 🚀 Starting build... |
| **Ticker Fetch** | Count | ✅ Found 8,000 companies |
| **Downloads** | Progress Bar | 📊 Progress: 100/8000 processed |
| **Batch Indexing** | Confirmation | 💾 Indexing batch of 32... |
| **Completion** | Summary | 🎉 Build complete! 7,500 indexed |
| **Verification** | Status | ✅ ChromaDB verified |

## 🛠️ Technical Details

### StreamingChromaBuilder Class

Located in: `src/stock_research_mcp/agents/streaming_builder.py`

**Key Methods**:
- `is_chroma_db_built()` - Checks if ChromaDB already exists
- `build_with_streaming()` - Async generator that yields progress messages
- `_process_one()` - Processes a single company (threaded)

**Features**:
- ✅ Async generator for real-time streaming
- ✅ ThreadPoolExecutor for parallel downloads
- ✅ Batch processing (default: 32 companies per batch)
- ✅ Progress updates every 10 companies
- ✅ Error handling with fallback
- ✅ Persistent storage (survives restarts)

### Server Integration

Located in: `src/stock_research_mcp/server.py`

**Flow**:
```python
async def _handle_analyze_sector(self, arguments):
    # Check on first request only
    if not self.chroma_checked:
        if not self.builder.is_chroma_db_built():
            # Stream build progress to user
            async for progress_msg in self.builder.build_with_streaming():
                output_parts.append(progress_msg)
    
    # Execute normal query
    result = await self.orchestrator.process_sector_query(sector)
    return results
```

## ⚙️ Configuration

### Environment Variables

Set in Claude Desktop config:

```json
{
  "env": {
    "OPENAI_API_KEY": "sk-...",              // Required for embeddings
    "SEC_API_USER_AGENT": "Company email",   // Required for SEC API
    "CHROMA_PERSIST_DIR": "./chroma_db",     // Storage location
    "MAX_WORKERS": "4",                      // Parallel downloads (1-8)
    "BATCH_SIZE": "32"                       // Embedding batch size
  }
}
```

### Performance Tuning

| Setting | Low Power | Balanced | Fast |
|---------|-----------|----------|------|
| MAX_WORKERS | 2 | 4 | 8 |
| BATCH_SIZE | 16 | 32 | 64 |
| Build Time | 45-60 min | 20-40 min | 15-25 min |

## 🎨 User Experience Benefits

### Before (Manual Build)
❌ Users had to read docs to find build command  
❌ Had to wait 30-60 min with no progress visibility  
❌ No clear indication when build was complete  
❌ Error-prone (forgot to set env vars, etc.)  
❌ Confusing - "Why isn't the tool working?"

### After (Automatic Streaming Build)
✅ Zero setup - just start querying  
✅ Real-time progress updates every step  
✅ Clear messages about what's happening  
✅ Automatic error handling with fallbacks  
✅ Intuitive - "Oh, it's building on first use!"

## 🔍 Troubleshooting

### Build Fails

**Error**: OpenAI API key missing  
**Solution**: Set `OPENAI_API_KEY` in MCP config

**Error**: SEC API 403 Forbidden  
**Solution**: Set `SEC_API_USER_AGENT` with your email

**Error**: Timeout downloading filings  
**Solution**: Reduce `MAX_WORKERS` to 2

### Build Takes Too Long

**Issue**: 60+ minutes to complete  
**Solutions**:
- Increase `MAX_WORKERS` to 6-8 (if good connection)
- Reduce number of companies in `fetch_tickers.py`
- Use SSD storage for `CHROMA_PERSIST_DIR`

### ChromaDB Not Persisting

**Issue**: Build runs every time  
**Check**:
1. Verify `CHROMA_PERSIST_DIR` is absolute path
2. Check write permissions on directory
3. Look for `.sqlite3` files in chroma_db/

## 📝 Code Examples

### Check if Build Needed

```python
from streaming_builder import get_streaming_builder

builder = get_streaming_builder()
if builder.is_chroma_db_built():
    print("✅ ChromaDB ready")
else:
    print("❌ Need to build")
```

### Manual Streaming Build

```python
async def manual_build():
    builder = get_streaming_builder()
    
    async for message in builder.build_with_streaming():
        print(message, end='')
```

### Integration in Custom Code

```python
from streaming_builder import get_streaming_builder

async def my_tool():
    builder = get_streaming_builder()
    
    if not builder.is_chroma_db_built():
        print("Building ChromaDB...")
        async for progress in builder.build_with_streaming():
            # Send to UI, log, or stream to client
            await send_to_user(progress)
    
    # Use ChromaDB
    results = query_chromadb(...)
```

## 🚀 Future Enhancements

Potential improvements:
- [ ] Progress percentage (10%, 20%, etc.)
- [ ] ETA calculation
- [ ] Pause/resume capability
- [ ] Incremental updates (add new companies)
- [ ] Background build (start query immediately)
- [ ] Cache partial results
- [ ] Multi-region ChromaDB sync
- [ ] Web UI for build monitoring

## 📚 Related Files

- `src/stock_research_mcp/agents/streaming_builder.py` - Builder implementation
- `src/stock_research_mcp/server.py` - MCP server integration
- `src/sector/builder.py` - Original standalone builder
- `src/sector/embeddings_and_chroma.py` - ChromaDB operations
- `README.md` - User-facing documentation

---

Built with ❤️ for better developer experience!
