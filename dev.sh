#!/usr/bin/env bash
set -e

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading .env configuration..."
fi

export PYTHONUNBUFFERED=1

echo "Starting LiveKit MCP Server with uv..."
uv run python -m livekit_mcp.main
