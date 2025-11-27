#!/bin/bash

# Launch Stock Research Gradio Web Interface

echo "🚀 Starting Stock Research Gradio App..."
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Loading from .env file..."
    if [ -f "../.env" ]; then
        # Load .env file, removing inline comments and blank lines
        set -a
        source <(grep -v '^#' ../.env | sed 's/#.*$//' | sed '/^$/d')
        set +a
        echo "✅ Environment variables loaded from .env"
    else
        echo "❌ .env file not found. Please set OPENAI_API_KEY"
        exit 1
    fi
fi

# Display configuration
echo ""
echo "📋 Configuration:"
echo "   CHROMA_PERSIST_DIR: ${CHROMA_PERSIST_DIR:-./output/chroma_db}"
echo "   USE_REAL_API: ${USE_REAL_API:-true}"
echo "   USE_CHROMA_SECTORS: ${USE_CHROMA_SECTORS:-true}"
echo ""

# Set PYTHONPATH to project root
export PYTHONPATH="$(cd .. && pwd):$PYTHONPATH"

# Launch Gradio app
echo "🌐 Launching Gradio interface..."
echo "   Access at: http://localhost:7860"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python ../src/gradio_frontend/gradio_app.py
