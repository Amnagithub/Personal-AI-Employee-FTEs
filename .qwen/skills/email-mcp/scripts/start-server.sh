#!/bin/bash
# Start Email MCP Server (Gmail Integration)
# Port: 8809

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

echo "Starting Email MCP server on port 8809..."

# Check if credentials exist
if [ ! -f "$HOME/.ai_employee/gmail_credentials.json" ]; then
    echo "ERROR: Gmail credentials not found at \$HOME/.ai_employee/gmail_credentials.json"
    echo ""
    echo "Please set up Gmail API credentials:"
    echo "1. Go to https://console.cloud.google.com/"
    echo "2. Enable Gmail API"
    echo "3. Create OAuth 2.0 credentials"
    echo "4. Download credentials.json to ~/.ai_employee/gmail_credentials.json"
    exit 1
fi

# Start the server
npx -y @modelcontextprotocol/server-gmail &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo "✓ Email MCP server started (PID: $SERVER_PID)"
    echo "Port: 8809"
    echo ""
    echo "To verify: python3 $SCRIPT_DIR/verify.py"
    echo "To stop: bash $SCRIPT_DIR/stop-server.sh"
else
    echo "✗ Failed to start Email MCP server"
    exit 1
fi
