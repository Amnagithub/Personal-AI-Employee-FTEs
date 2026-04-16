#!/usr/bin/env python3
"""
Test Facebook/Instagram MCP Server Connection
"""

import requests
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent.parent.parent.parent / '.env')

MCP_URL = os.getenv('MCP_URL', 'http://localhost:8811')

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
        print("   Make sure it's running: python .qwen/skills/facebook-mcp/scripts/facebook_mcp_server.py")
        return False

def test_facebook_posts():
    """Test getting Facebook posts"""
    print("\n📝 Testing Facebook posts retrieval...")
    
    response = requests.post(f'{MCP_URL}', json={
        'tool': 'facebook_get_posts',
        'params': {'limit': 3}
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ Retrieved {result['count']} Facebook posts")
            if result['posts']:
                print(f"   Latest: {result['posts'][0].get('message', 'No message')[:50]}...")
            return True
        else:
            print(f"❌ Failed to get posts: {result.get('error')}")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        return False

def test_facebook_summary():
    """Test getting Facebook summary"""
    print("\n📊 Testing Facebook summary...")
    
    response = requests.post(f'{MCP_URL}', json={
        'tool': 'facebook_get_summary',
        'params': {}
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ Facebook summary retrieved")
            print(f"   Posts: {result['posts_count']}")
            print(f"   Engagement: {result['total_engagement']}")
            return True
        else:
            print(f"❌ Failed to get summary: {result.get('error')}")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        return False

def test_instagram_posts():
    """Test getting Instagram posts"""
    print("\n📸 Testing Instagram posts...")
    
    response = requests.post(f'{MCP_URL}', json={
        'tool': 'instagram_get_posts',
        'params': {'limit': 3}
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ Retrieved {result['count']} Instagram posts")
            return True
        else:
            print(f"❌ Failed to get posts: {result.get('error')}")
            return False
    else:
        print(f"❌ Request failed: {response.status_code}")
        return False

def main():
    print("🧪 Testing Facebook/Instagram MCP Server Connection\n")
    
    # Test health
    if not test_health():
        print("\n❌ Server not healthy. Please check:")
        print("   1. Facebook MCP server is running")
        print("   2. .env file has FACEBOOK_ACCESS_TOKEN")
        print("   3. FACEBOOK_PAGE_ID is correct")
        sys.exit(1)
    
    # Test Facebook posts
    test_facebook_posts()
    
    # Test Facebook summary
    test_facebook_summary()
    
    # Test Instagram posts
    test_instagram_posts()
    
    print("\n✅ All tests passed!")
    print("\nNext steps:")
    print("   1. Start Facebook MCP server: python .qwen/skills/facebook-mcp/scripts/facebook_mcp_server.py --port 8811")
    print("   2. Test with Qwen Code: qwen")
    print("   3. Use tool: facebook_create_post")

if __name__ == '__main__':
    main()
