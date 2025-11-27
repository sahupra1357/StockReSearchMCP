"""
Quick Test Script for Gradio Interface

Run this to verify the Gradio app is set up correctly.
"""

import sys
import os

print("🔍 Checking Stock Research Gradio Setup...\n")

# Check 1: Python version
print("1️⃣ Python Version:")
print(f"   {sys.version}")
if sys.version_info >= (3, 10):
    print("   ✅ Python 3.10+ detected\n")
else:
    print("   ❌ Python 3.10+ required\n")
    sys.exit(1)

# Check 2: Required imports
print("2️⃣ Checking Dependencies:")
try:
    import gradio
    print(f"   ✅ Gradio {gradio.__version__}")
except ImportError:
    print("   ❌ Gradio not installed. Run: uv pip install gradio")
    sys.exit(1)

try:
    from stock_research_mcp.agents import MultiAgentOrchestrator
    print("   ✅ MCP Agents available")
except ImportError as e:
    print(f"   ❌ MCP Agents import failed: {e}")
    sys.exit(1)

try:
    from stock_research_mcp.agents.streaming_builder import get_streaming_builder
    print("   ✅ Streaming Builder available")
except ImportError as e:
    print(f"   ❌ Streaming Builder import failed: {e}")
    sys.exit(1)

# Check 3: Environment variables
print("\n3️⃣ Environment Variables:")
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    print(f"   ✅ OPENAI_API_KEY set (starts with: {openai_key[:10]}...)")
else:
    print("   ⚠️  OPENAI_API_KEY not set (ChromaDB won't work)")

chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./output/chroma_db")
print(f"   ℹ️  CHROMA_PERSIST_DIR: {chroma_dir}")

use_real_api = os.getenv("USE_REAL_API", "true")
print(f"   ℹ️  USE_REAL_API: {use_real_api}")

use_chroma = os.getenv("USE_CHROMA_SECTORS", "true")
print(f"   ℹ️  USE_CHROMA_SECTORS: {use_chroma}")

# Check 4: ChromaDB status
print("\n4️⃣ ChromaDB Status:")
if os.path.exists(chroma_dir):
    files = os.listdir(chroma_dir)
    if files:
        print(f"   ✅ ChromaDB exists with {len(files)} files")
        print(f"   📂 Location: {chroma_dir}")
    else:
        print(f"   ⚠️  ChromaDB directory empty (will build on first use)")
else:
    print(f"   ⚠️  ChromaDB not found (will build on first use)")
    print(f"   📂 Will be created at: {chroma_dir}")

# Check 5: Try importing Gradio app
print("\n5️⃣ Gradio App:")
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from gradio_frontend.gradio_app import StockResearchGradioApp
    print("   ✅ Gradio app imports successfully")
    
    app = StockResearchGradioApp()
    print("   ✅ Gradio app initializes successfully")
    
    status = app.get_database_status()
    print(f"   ℹ️  {status}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Final summary
print("\n" + "=" * 60)
print("✅ All checks passed! Ready to launch Gradio interface.")
print("=" * 60)
print("\nTo start the web interface, run:")
print("   ./launch_gradio.sh")
print("   OR")
print("   python gradio_app.py")
print("\nThen open: http://localhost:7860")
print()
