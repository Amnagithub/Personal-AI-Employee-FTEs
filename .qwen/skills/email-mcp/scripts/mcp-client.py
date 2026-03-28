#!/usr/bin/env python3
"""
Universal MCP Client for Email MCP server.
Supports HTTP and stdio transports.

Usage:
    # List available tools
    python3 mcp-client.py list -u http://localhost:8809

    # Call a tool
    python3 mcp-client.py call -u http://localhost:8809 -t email_send -p '{"to": "...", "subject": "..."}'

    # Emit tool schemas as markdown
    python3 mcp-client.py emit -u http://localhost:8809
"""

import argparse
import asyncio
import json
import sys
from typing import Any, Dict, Optional

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    import httpx
except ImportError:
    print("Error: mcp package not installed. Run: pip install mcp")
    sys.exit(1)


async def run_http(url: str, tool: str, params: Dict[str, Any], action: str):
    """Run tool call via HTTP transport."""
    async with httpx.AsyncClient() as client:
        if action == "list":
            response = await client.get(f"{url}/tools/list")
            result = response.json()
        elif action == "call":
            response = await client.post(
                f"{url}/tools/call",
                json={"name": tool, "arguments": params},
                timeout=60.0
            )
            result = response.json()
        elif action == "emit":
            response = await client.get(f"{url}/tools/list")
            tools = response.json().get("tools", [])
            print("# Email MCP Tools\n")
            for t in tools:
                print(f"## {t['name']}\n")
                print(f"**Description:** {t.get('description', 'N/A')}\n")
                print(f"**Parameters:**\n```json\n{json.dumps(t.get('inputSchema', {}), indent=2)}\n```")
            return
        else:
            print(f"Unknown action: {action}")
            return

    print(json.dumps(result, indent=2))


async def run_stdio(command: str, args: list, tool: str, params: Dict[str, Any], action: str):
    """Run tool call via stdio transport."""
    server_params = StdioServerParameters(
        command=command,
        args=args,
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if action == "list":
                tools = await session.list_tools()
                print(json.dumps({"tools": [t.model_dump() for t in tools.tools]}, indent=2))
            elif action == "call":
                result = await session.call_tool(tool, params)
                print(json.dumps({"result": result}, indent=2))
            elif action == "emit":
                tools = await session.list_tools()
                print("# Email MCP Tools\n")
                for t in tools.tools:
                    print(f"## {t.name}\n")
                    print(f"**Description:** {t.description or 'N/A'}\n")
                    print(f"**Parameters:**\n```json\n{t.inputSchema}\n```")


def main():
    parser = argparse.ArgumentParser(description="MCP Client for Email MCP")
    parser.add_argument("action", choices=["list", "call", "emit"], help="Action to perform")
    parser.add_argument("-u", "--url", default="http://localhost:8809", help="MCP server URL")
    parser.add_argument("-t", "--tool", help="Tool name to call")
    parser.add_argument("-p", "--params", default="{}", help="Tool parameters as JSON string")
    parser.add_argument("--stdio-command", help="Command for stdio transport")
    parser.add_argument("--stdio-args", nargs="*", help="Args for stdio transport")

    args = parser.parse_args()

    params = json.loads(args.params) if args.params else {}

    if args.url.startswith("http"):
        asyncio.run(run_http(args.url, args.tool, params, args.action))
    else:
        if not args.stdio_command:
            print("Error: --stdio-command required for stdio transport")
            sys.exit(1)
        asyncio.run(run_stdio(args.stdio_command, args.stdio_args or [], args.tool, params, args.action))


if __name__ == "__main__":
    main()
