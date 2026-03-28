#!/usr/bin/env python3
"""
Verify Email MCP server is running.
"""

import sys
import httpx


def verify():
    """Check if Email MCP server is responding."""
    try:
        response = httpx.get("http://localhost:8809/tools/list", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            tools = data.get("tools", [])
            print("✓ Email MCP server running on port 8809")
            print(f"  Available tools: {len(tools)}")
            for tool in tools[:5]:
                print(f"    - {tool.get('name', 'unknown')}")
            if len(tools) > 5:
                print(f"    ... and {len(tools) - 5} more")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except httpx.ConnectError:
        print("✗ Email MCP server not responding on port 8809")
        print("")
        print("To start the server:")
        print("  bash .qwen/skills/email-mcp/scripts/start-server.sh")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
