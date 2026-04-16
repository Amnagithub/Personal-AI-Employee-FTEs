#!/bin/bash
# Stop Odoo MCP Server

echo "🛑 Stopping Odoo MCP Server..."

# Kill MCP server process
pkill -f "odoo_mcp_server.py"

echo "✅ Odoo MCP Server stopped"
