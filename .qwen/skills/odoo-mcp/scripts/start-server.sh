#!/bin/bash
# Start Odoo MCP Server

echo "🚀 Starting Odoo MCP Server..."

# Check if Odoo is running
if ! curl -s http://localhost:8069 > /dev/null; then
    echo "⚠️  Odoo is not running on port 8069"
    echo "Starting Odoo with Docker Compose..."
    cd AI_Employee_Vault/odoo
    docker-compose up -d
    cd ../..
    sleep 10
fi

# Start MCP server
echo "📡 Starting MCP server on port 8810..."
python3 .qwen/skills/odoo-mcp/scripts/odoo_mcp_server.py --port 8810 &

echo "✅ Odoo MCP Server started"
echo "🔗 Health check: http://localhost:8810/health"
