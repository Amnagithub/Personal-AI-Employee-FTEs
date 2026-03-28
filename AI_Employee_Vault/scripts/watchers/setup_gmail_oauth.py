#!/usr/bin/env python3
"""
Gmail Watcher Setup - OAuth Authentication Helper

This script helps you authenticate with Gmail API and save credentials.

Usage:
    python setup_gmail_oauth.py /path/to/credentials.json
"""

import sys
import os
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    import pickle
except ImportError:
    print("Error: Missing required packages.")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def setup_oauth(credentials_path: str, vault_path: str):
    """Run OAuth flow and save token."""
    
    credentials_path = Path(credentials_path)
    vault_path = Path(vault_path)
    token_path = vault_path / 'token.json'
    
    if not credentials_path.exists():
        print(f"ERROR: Credentials file not found at: {credentials_path}")
        print("\nPlease:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Gmail API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json")
        print(f"6. Place it at: {credentials_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("Gmail OAuth Setup for AI Employee")
    print("=" * 60)
    print()
    print(f"Credentials: {credentials_path}")
    print(f"Token will be saved to: {token_path}")
    print()
    print("Opening browser for authentication...")
    print()
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path), SCOPES
        )
        creds = flow.run_local_server(port=0, open_browser=True)
        
        # Save token
        token_path.write_text(creds.to_json())
        
        print()
        print("=" * 60)
        print("✓ Authentication successful!")
        print("=" * 60)
        print()
        print(f"Token saved to: {token_path}")
        print()
        print("You can now run the Gmail Watcher:")
        print(f"  python scripts/watchers/gmail_watcher.py {vault_path} --interval 120")
        print()
        
        # Test connection
        print("Testing connection to Gmail API...")
        from googleapiclient.discovery import build
        service = build('gmail', 'v1', credentials=creds)
        profile = service.users().getProfile(userId='me').execute()
        print(f"✓ Connected to Gmail API")
        print(f"  Account: {profile['emailAddress']}")
        print()
        
        return True
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Make sure credentials.json is valid")
        print("2. Check that Gmail API is enabled in Google Cloud Console")
        print("3. Try deleting token.json and running again")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python setup_gmail_oauth.py <credentials.json> [vault_path]")
        print()
        print("Arguments:")
        print("  credentials.json  Path to your Gmail API credentials file")
        print("  vault_path        Path to your Obsidian vault (default: current directory)")
        print()
        sys.exit(1)
    
    credentials_path = sys.argv[1]
    vault_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    
    success = setup_oauth(credentials_path, vault_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
