#!/bin/bash
# Quick start script for running the MCP server with API

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║   SQL to Snowflake MCP Server - Quick Start           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo

# Check dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ All dependencies found"
fi

echo

# Build resources if needed
if [ ! -f "mcp-resources.json" ]; then
    echo "🔍 Building resources..."
    python3 build.py
    echo
fi

# Determine port
PORT=${1:-5000}
HOST=${2:-127.0.0.1}

# Check if port is in use
if command -v lsof &> /dev/null; then
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $PORT is already in use"
        echo "Try: python3 api_server.py $((PORT + 1))"
        exit 1
    fi
fi

echo "🚀 Starting API Server..."
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   URL:  http://$HOST:$PORT"
echo
echo "📡 OpenAPI Schema: http://$HOST:$PORT/api/v1/schema"
echo "📚 Documentation:  http://$HOST:$PORT"
echo
echo "Test endpoints:"
echo "  curl http://$HOST:$PORT/api/v1/resources"
echo "  curl http://$HOST:$PORT/api/v1/index"
echo
echo "Press Ctrl+C to stop"
echo

python3 api_server.py $PORT $HOST
