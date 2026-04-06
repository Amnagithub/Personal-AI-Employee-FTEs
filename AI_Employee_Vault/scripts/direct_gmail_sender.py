#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Gmail Sender - Send emails without MCP server.

This script sends emails directly using Gmail API,
bypassing the need for the MCP server.

Usage:
    python direct_gmail_sender.py /path/to/vault
"""

import sys
import base64
from pathlib import Path
from email.mime.text import MIMEText
from typing import Optional


try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
except ImportError:
    print("Error: Google API packages not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class DirectGmailSender:
    """Send emails directly via Gmail API without MCP server."""

    def __init__(self, vault_path: str, credentials_path: str = None):
        self.vault_path = Path(vault_path).resolve()

        # Find credentials
        if credentials_path:
            self.credentials_path = Path(credentials_path)
        else:
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

        self.token_path = self.vault_path / 'token_send.json'
        self.service = None

    def authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Load cached token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )
            except Exception as e:
                print(f"Warning: Failed to load token: {e}")
                creds = None

        # Refresh or re-authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Warning: Token refresh failed: {e}")
                    creds = None

            if not creds:
                if not self.credentials_path:
                    print("Error: Gmail credentials not found")
                    print("\nTo set up:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Enable Gmail API")
                    print("3. Create OAuth 2.0 credentials (Desktop app)")
                    print("4. Download credentials.json")
                    print("5. Save to: ~/.ai_employee/gmail_credentials.json")
                    return False

                print("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            self.token_path.write_text(creds.to_json())
            print("✓ OAuth token saved")

        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Connected to Gmail API")
        return True

    def create_message(self, to: str, subject: str, body: str, in_reply_to: str = None) -> dict:
        """Create a Gmail API message."""
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject

        if in_reply_to:
            message['In-Reply-To'] = in_reply_to

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None) -> bool:
        """Send an email."""
        if not self.service:
            if not self.authenticate():
                return False

        try:
            message = self.create_message(to, subject, body, in_reply_to)

            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            message_id = result.get('id', 'unknown')
            print(f"✓ Email sent successfully (Message ID: {message_id})")
            return True

        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            return False


def process_approved_emails_direct(vault_path: Path) -> int:
    """Process approved emails and send them directly."""
    approved_folder = vault_path / 'Approved'
    if not approved_folder.exists():
        return 0

    approved_files = [f for f in approved_folder.iterdir() if f.suffix == '.md']
    if not approved_files:
        return 0

    print(f"\n{'='*60}")
    print(f"Processing {len(approved_files)} approved email(s)")
    print(f"{'='*60}\n")

    sender = DirectGmailSender(str(vault_path))
    if not sender.authenticate():
        print("\n✗ Cannot authenticate - skipping email sending")
        return 0

    sent_count = 0
    for filepath in approved_files:
        try:
            content = filepath.read_text()

            # Extract metadata
            import re
            to_match = re.search(r'to:\s*(.+)', content)
            subject_match = re.search(r'subject:\s*(.+)', content)
            original_id_match = re.search(r'original_message_id:\s*(.+)', content)

            if not to_match or not subject_match:
                print(f"✗ Invalid approval file: {filepath.name}")
                continue

            to_email = to_match.group(1).strip()
            subject = subject_match.group(1).strip()
            original_id = original_id_match.group(1).strip() if original_id_match else None

            # Extract reply body
            reply_match = re.search(r'### Proposed Reply\n(.*?)\n##', content, re.DOTALL)
            if not reply_match:
                print(f"✗ No reply body found in: {filepath.name}")
                continue

            reply_body = reply_match.group(1).strip()

            print(f"\nSending email:")
            print(f"  To: {to_email}")
            print(f"  Subject: {subject}")
            print(f"  Body preview: {reply_body[:100]}...")

            success = sender.send_email(
                to=to_email,
                subject=subject,
                body=reply_body,
                in_reply_to=original_id
            )

            if success:
                # Move to Done
                import datetime
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = f"{timestamp}_{filepath.name}"
                done_folder = vault_path / 'Done'
                done_folder.mkdir(parents=True, exist_ok=True)
                dest = done_folder / new_name
                filepath.rename(dest)
                print(f"✓ Moved to Done: {dest.name}")
                sent_count += 1
            else:
                print(f"✗ Failed to send, keeping in Approved")

        except Exception as e:
            print(f"✗ Error processing {filepath.name}: {e}")
            import traceback
            traceback.print_exc()

    return sent_count


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Direct Gmail Sender')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    vault_path = Path(args.vault_path).resolve()
    count = process_approved_emails_direct(vault_path)

    print(f"\n{'='*60}")
    print(f"Summary: {count} email(s) sent")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
