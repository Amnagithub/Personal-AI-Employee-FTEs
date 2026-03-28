#!/bin/bash
# Stop Email MCP Server

echo "Stopping Email MCP server..."

# Find and kill the server process
pkill -f "@modelcontextprotocol/server-gmail" 2>/dev/null || true

# Also kill any process on port 8809
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:8809 2>/dev/null)
    if [ -n "$PID" ]; then
        kill -9 $PID 2>/dev/null || true
        echo "✓ Killed process on port 8809"
    fi
fi

echo "✓ Email MCP server stopped"
