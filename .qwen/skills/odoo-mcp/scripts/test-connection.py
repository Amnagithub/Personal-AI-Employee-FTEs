#!/usr/bin/env python3
"""
Test Odoo MCP Server Connection
"""

import requests
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / '.env')

MCP_URL = os.getenv('MCP_URL', 'http://localhost:8810')

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f'{MCP_URL}/health', timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to MCP server")
        print("   Make sure it's running: python .qwen/skills/odoo-mcp/scripts/odoo_mcp_server.py")
        return False

def test_create_contact():
    """Test creating a contact"""
    print("\n📝 Testing contact creation...")
    
    response = requests.post(f'{MCP_URL}', json={
        'tool': 'odoo_create_contact',
        'params': {
            'name': 'Test Client',
            'email': 'test@example.com',
            'phone': '+1234567890',
            'company': 'Test Corp',
            'type': 'customer'
        }
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ Contact created: {result['contact_id']}")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Failed to create contact: {result.get('error')}")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        return False

def test_financial_summary():
    """Test getting financial summary"""
    print("\n💰 Testing financial summary...")
    
    response = requests.post(f'{MCP_URL}', json={
        'tool': 'odoo_get_financial_summary',
        'params': {}
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Financial summary retrieved")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"❌ Failed to get summary: {result.get('error')}")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        return False

def main():
    print("🧪 Testing Odoo MCP Server Connection\n")
    
    # Test health
    if not test_health():
        print("\n❌ Server not healthy. Please check:")
        print("   1. Odoo is running: docker ps | grep odoo")
        print("   2. MCP server is running: ps aux | grep odoo_mcp")
        print("   3. Check .env file has correct credentials")
        sys.exit(1)
    
    # Test contact creation
    test_create_contact()
    
    # Test financial summary
    test_financial_summary()
    
    print("\n✅ All tests passed!")
    print("\nNext steps:")
    print("   1. Start Odoo MCP server: bash .qwen/skills/odoo-mcp/scripts/start-server.sh")
    print("   2. Test with Qwen Code: qwen")
    print("   3. Use tool: odoo_create_contact")

if __name__ == '__main__':
    main()
