#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitor Gmail for new important emails.

This watcher monitors Gmail for unread, important emails and creates
action files in the Needs_Action folder for Qwen Code to process.

Usage:
    python gmail_watcher.py /path/to/vault

Or run once (for cron jobs):
    python gmail_watcher.py /path/to/vault --once

Silver Tier - Personal AI Employee FTE
"""

import sys
import logging
import pickle
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    print("Error: Google API packages not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Query for important unread emails
QUERY_TEMPLATE = 'is:unread is:important'


class GmailWatcher(BaseWatcher):
    """
    Watcher that monitors Gmail for new important emails.
    
    Creates action files in /Needs_Action folder for each new email.
    """

    def __init__(self, vault_path: str, credentials_path: str = None, check_interval: int = 120):
        super().__init__(vault_path, check_interval)
        
        # Find credentials
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
            # Default locations
            possible_paths = [
                Path.home() / '.ai_employee' / 'gmail_credentials.json',
                self.vault_path / 'credentials.json',
                Path('credentials.json')
            ]
            for p in possible_paths:
                if p.exists():
                    self.credentials_path = p
                    break
            else:
                self.credentials_path = None
        
        self.token_path = self.vault_path / 'token.json'
        self.service = None
        self._connect()

    def _connect(self):
        """Authenticate and connect to Gmail API."""
        creds = None
        
        # Load cached token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )
            except Exception as e:
                self.logger.warning(f"Failed to load token: {e}")
                creds = None
        
        # Refresh or re-authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                if not self.credentials_path:
                    self.logger.error("No Gmail credentials found")
                    raise FileNotFoundError(
                        "Gmail credentials not found. Please place credentials.json in:\n"
                        "  - ~/.ai_employee/gmail_credentials.json\n"
                        "  - <vault>/credentials.json\n"
                        "  - Current directory"
                    )
                
                self.logger.info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token
            self.token_path.write_text(creds.to_json())
            self.logger.info("OAuth token saved")
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Connected to Gmail API")

    def _get_email_content(self, message_id: str) -> Dict[str, Any]:
        """Fetch full email content."""
        message = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        # Extract body
        body = ''
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part:
                    import base64
                    body = base64.urlsafe_b64decode(part['data']).decode('utf-8')
                    break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            import base64
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')
        
        # Get labels
        labels = [label['name'] for label in message.get('labelIds', [])]
        
        return {
            'id': message_id,
            'from': headers.get('From', 'Unknown'),
            'to': headers.get('To', ''),
            'subject': headers.get('Subject', 'No Subject'),
            'date': headers.get('Date', ''),
            'body': body,
            'labels': labels,
            'has_attachment': 'ATTACH' in message.get('labelIds', [])
        }

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new unread, important emails.
        
        Returns:
            List of email info dictionaries for new emails
        """
        try:
            # Ensure connection
            if self.service is None:
                self._connect()
            
            # Search for unread, important emails
            results = self.service.users().messages().list(
                userId='me',
                q=QUERY_TEMPLATE,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_emails = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    email_data = self._get_email_content(msg['id'])
                    new_emails.append(email_data)
            
            return new_emails
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            # Try to reconnect
            self.service = None
            return []

    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for the email.
        
        Args:
            item: Email info dictionary
            
        Returns:
            Path to the created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = item['subject'][:50].replace(' ', '_').replace(':', '')
        filename = f"EMAIL_{safe_subject}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        # Determine priority
        priority = 'high' if 'important' in item['labels'] else 'normal'
        
        content = f'''---
type: email
from: {item['from']}
subject: {item['subject']}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
message_id: {item['id']}
labels: {', '.join(item['labels'])}
has_attachment: {str(item['has_attachment']).lower()}
---

# Email Received

A new email requires your attention.

## Email Details

- **From:** {item['from']}
- **To:** {item['to']}
- **Subject:** {item['subject']}
- **Date:** {item['date']}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Content

{item['body'][:2000] if item['body'] else '[No text content]'}

---

## Suggested Actions

- [ ] Read and understand the email
- [ ] Draft appropriate reply
- [ ] Create approval request if action needed
- [ ] Archive email after processing
- [ ] Mark this task as complete when done

## Notes

<!-- Add any additional notes or context here -->

'''
        filepath.write_text(content)
        self.processed_ids.add(item['id'])
        self._save_processed_cache()
        
        self.logger.info(f"Created action file: {filepath.name}")
        return filepath

    def run(self):
        """Run the Gmail watcher."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        # First, process any existing emails
        self.logger.info('Checking for existing unread emails...')
        self.run_once()
        
        # Then start continuous monitoring
        super().run()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--credentials', '-c', help='Path to Gmail credentials.json')
    parser.add_argument('--interval', '-i', type=int, default=120, help='Check interval in seconds (default: 120)')
    parser.add_argument('--once', action='store_true', help='Run once and exit (for cron jobs)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    watcher = GmailWatcher(
        args.vault_path,
        credentials_path=args.credentials,
        check_interval=args.interval
    )

    if args.once:
        count = watcher.run_once()
        print(f'Processed {count} new email(s)')
        sys.exit(0)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
