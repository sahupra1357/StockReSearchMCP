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

# Set default CHROMA_PERSIST_DIR if not set (relative to project root)
if [ -z "$CHROMA_PERSIST_DIR" ]; then
    export CHROMA_PERSIST_DIR="$(cd .. && pwd)/output/chroma_db"
fi

# Display configuration
echo ""
echo "📋 Configuration:"
echo "   CHROMA_PERSIST_DIR: ${CHROMA_PERSIST_DIR}"
echo "   USE_REAL_API: ${USE_REAL_API:-true}"
echo "   USE_CHROMA_SECTORS: ${USE_CHROMA_SECTORS:-true}"
echo ""

# Set PYTHONPATH to project root
export PYTHONPATH="$(cd .. && pwd):$PYTHONPATH"

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Set log file with timestamp
LOG_FILE="../logs/gradio_$(date +%Y%m%d_%H%M%S).log"

# Launch Gradio app
echo "🌐 Launching Gradio interface..."
echo "   Access at: http://localhost:7860"
echo "   Logs: $LOG_FILE"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "📝 All output redirected to log file..."
echo ""

# Redirect output to log file and console
#python ../src/gradio_frontend/gradio_app.py 2>&1 | tee "$LOG_FILE"

# Redirect output to log file only (no console output)
python ../src/gradio_frontend/gradio_app.py >> "$LOG_FILE" 2>&1

