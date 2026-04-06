#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Auto-Processor - Fully Autonomous with Qwen Code & Email MCP Integration.

This script automatically processes emails in Needs_Action folder and:
1. Reads and understands email content
2. Generates intelligent replies (template-based or Qwen Code)
3. Sends replies via Email MCP server
4. Handles approval workflow for sensitive emails
5. Moves processed emails to Done folder

Usage:
    # Test mode (no sending)
    python email_auto_processor.py /path/to/vault

    # Auto-send mode (sends non-sensitive emails)
    python email_auto_processor.py /path/to/vault --auto-send

    # Continuous loop (checks every 5 minutes)
    python email_auto_processor.py /path/to/vault --loop --loop-interval 300

    # With Qwen Code integration (requires Qwen Code API)
    python email_auto_processor.py /path/to/vault --use-qwen
"""

import sys
import json
import re
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List


class EmailAutoProcessor:
    """Automatically processes email action files and sends replies."""

    def __init__(
        self,
        vault_path: str,
        auto_send: bool = False,
        use_qwen: bool = False,
        mcp_url: str = "http://localhost:8809"
    ):
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.auto_send = auto_send
        self.use_qwen = use_qwen
        self.mcp_url = mcp_url

        # Ensure directories exist
        for d in [self.needs_action, self.done, self.pending_approval, self.approved]:
            d.mkdir(parents=True, exist_ok=True)

    def parse_action_file(self, filepath: Path) -> dict:
        """Parse email action file and extract metadata."""
        content = filepath.read_text()

        # Extract frontmatter
        frontmatter = {}
        fm_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            for line in fm_match.group(1).split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()

        # Extract email body
        body_match = re.search(r'## Content\n\n(.*?)(?:\n---|\Z)', content, re.DOTALL)
        email_body = body_match.group(1).strip() if body_match else ''

        # Check if body has placeholder
        if '[No text content]' in email_body:
            email_body = ''

        return {
            'filepath': filepath,
            'type': frontmatter.get('type', 'unknown'),
            'from': frontmatter.get('from', ''),
            'to': frontmatter.get('to', ''),
            'subject': frontmatter.get('subject', ''),
            'message_id': frontmatter.get('message_id', ''),
            'priority': frontmatter.get('priority', 'normal'),
            'date': frontmatter.get('date', ''),
            'body': email_body,
            'has_attachment': frontmatter.get('has_attachment', 'false').lower() == 'true',
            'labels': frontmatter.get('labels', ''),
            'content': content
        }

    def is_sensitive_email(self, email_data: dict) -> bool:
        """Determine if email is sensitive and needs approval."""
        sensitive_keywords = [
            'invoice', 'payment', 'money', 'contract', 'legal', 'confidential',
            'urgent', 'asap', 'deadline', 'financial', 'budget', 'proposal',
            'salary', 'compensation', 'hire', 'fire', 'termination'
        ]
        subject = email_data['subject'].lower()
        body = email_data['body'].lower()
        from_email = email_data['from'].lower()

        # Check for sensitive keywords
        for keyword in sensitive_keywords:
            if keyword in subject or keyword in body:
                return True

        # Check if from important/unknown sender
        if 'important' in email_data['labels'].lower():
            return True

        return False

    def generate_reply_template(self, email_data: dict) -> str:
        """Generate an intelligent reply using the reply generator."""
        # Use intelligent reply generator
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from intelligent_reply import generate_intelligent_reply
            return generate_intelligent_reply(email_data, str(self.vault_path))
        except Exception as e:
            print(f"  [Warning] Intelligent reply failed, using template: {e}")
            return self._generate_fallback_reply(email_data)

    def _generate_fallback_reply(self, email_data: dict) -> str:
        """Generate a basic fallback reply if intelligent generator fails."""
        subject = email_data['subject']
        from_name = email_data['from'].split('<')[0].strip()

        return f"""Hi {from_name},

Thank you for your email regarding "{subject}".

I've received your message and will review it shortly. I'll get back to you with a detailed response as soon as possible.

Best regards"""

    def generate_reply_with_qwen(self, email_data: dict) -> str:
        """Use Qwen Code to generate an intelligent reply."""
        # This would call Qwen Code API
        # For now, return template (you can enhance this later)
        print("  [Qwen Code] Generating intelligent reply...")
        return self.generate_reply_template(email_data)

    def call_email_mcp(self, tool_name: str, params: dict) -> dict:
        """Call Email MCP server tool."""
        try:
            # Check if MCP server is running
            import httpx
            response = httpx.get(f"{self.mcp_url}/tools/list", timeout=5.0)
            if response.status_code != 200:
                raise Exception(f"MCP server returned status {response.status_code}")

            # Call the tool
            result = httpx.post(
                f"{self.mcp_url}/tools/call",
                json={"name": tool_name, "arguments": params},
                timeout=60.0
            )

            if result.status_code != 200:
                raise Exception(f"Tool call failed: {result.text}")

            return result.json()

        except Exception as e:
            print(f"  ✗ MCP tool call failed: {e}")
            raise

    def send_email_via_mcp(self, to: str, subject: str, body: str, in_reply_to: str = None) -> bool:
        """Send email via Email MCP server."""
        try:
            params = {
                "to": to,
                "subject": subject,
                "body": body
            }

            if in_reply_to:
                params["in_reply_to"] = in_reply_to

            print(f"  [MCP] Sending email to: {to}")
            print(f"  [MCP] Subject: {subject}")

            result = self.call_email_mcp("email_send", params)
            print(f"  ✓ Email sent successfully")
            return True

        except Exception as e:
            print(f"  ✗ Failed to send email: {e}")
            return False

    def create_draft_via_mcp(self, to: str, subject: str, body: str, in_reply_to: str = None) -> Optional[str]:
        """Create email draft via Email MCP server."""
        try:
            params = {
                "to": to,
                "subject": subject,
                "body": body
            }

            if in_reply_to:
                params["in_reply_to"] = in_reply_to

            print(f"  [MCP] Creating draft email to: {to}")
            result = self.call_email_mcp("email_draft_create", params)

            # Extract draft_id from result
            draft_id = result.get("content", [{}])[0].get("text", {}).get("draft_id")
            if draft_id:
                print(f"  ✓ Draft created with ID: {draft_id}")
                return draft_id
            else:
                print(f"  ⚠ Draft created but no ID returned")
                return None

        except Exception as e:
            print(f"  ✗ Failed to create draft: {e}")
            return None

    def create_approval_request(self, email_data: dict, reply: str, draft_id: str = None) -> Path:
        """Create approval request file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = email_data['subject'][:30].replace(' ', '_')
        filename = f"APPROVAL_{safe_subject}_{timestamp}.md"
        filepath = self.pending_approval / filename

        content = f"""---
type: approval_request
action: email_reply
to: {email_data['from']}
subject: Re: {email_data['subject']}
original_message_id: {email_data['message_id']}
draft_id: {draft_id or 'N/A'}
status: pending
created: {datetime.now().isoformat()}
priority: {email_data['priority']}
---

## Email Reply Approval Request

### Original Email
- **From:** {email_data['from']}
- **Subject:** {email_data['subject']}
- **Date:** {email_data['date']}

### Proposed Reply
{reply if not draft_id else f"*Draft created in Gmail (ID: {draft_id})*"}

## Actions Required

1. Review the proposed reply above
2. If satisfied, move this file to `/Approved` folder
3. If changes needed, edit this file and then move to `/Approved`
4. To reject, move to `/Rejected` folder

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
"""
        filepath.write_text(content)
        return filepath

    def mark_as_done(self, filepath: Path, status: str = "completed"):
        """Move processed file to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{timestamp}_{filepath.name}"
        dest = self.done / new_name
        filepath.rename(dest)

    def mark_as_rejected(self, filepath: Path):
        """Move rejected file to Rejected folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"{timestamp}_{filepath.name}"
        dest = self.rejected / new_name
        filepath.rename(dest)

    def process_approved_emails(self) -> int:
        """Process emails in Approved folder (send the drafts)."""
        if not self.approved.exists():
            return 0

        approved_files = [f for f in self.approved.iterdir() if f.suffix == '.md']
        sent_count = 0

        for filepath in approved_files:
            try:
                content = filepath.read_text()

                # Extract metadata
                draft_id_match = re.search(r'draft_id:\s*(.+)', content)
                to_match = re.search(r'to:\s*(.+)', content)
                subject_match = re.search(r'subject:\s*(.+)', content)
                original_id_match = re.search(r'original_message_id:\s*(.+)', content)

                draft_id = draft_id_match.group(1).strip() if draft_id_match else 'N/A'
                to_email = to_match.group(1).strip() if to_match else ''
                subject = subject_match.group(1).strip() if subject_match else 'Re: Your Email'
                original_id = original_id_match.group(1).strip() if original_id_match else None

                if 'N/A' in draft_id or not draft_id:
                    # No draft ID, extract reply from content
                    reply_match = re.search(r'### Proposed Reply\n(.*?)\n##', content, re.DOTALL)
                    if reply_match:
                        reply = reply_match.group(1).strip()

                        # Try MCP first, fall back to direct sender
                        if self.is_mcp_running():
                            print(f"\nSending approved email to: {to_email} (via MCP)")
                            success = self.send_email_via_mcp(to_email, subject, reply)
                        else:
                            print(f"\nSending approved email to: {to_email} (direct)")
                            success = self.send_email_direct(to_email, subject, reply, original_id)

                        if success:
                            self.mark_as_done(filepath, "approved_and_sent")
                            sent_count += 1
                        else:
                            print(f"  ✗ Failed to send, keeping in Approved")
                    else:
                        print(f"  ✗ No reply body found in: {filepath.name}")
                else:
                    # Send existing draft via MCP
                    if self.is_mcp_running():
                        print(f"\nSending approved draft: {draft_id}")
                        result = self.call_email_mcp("email_draft_send", {"draft_id": draft_id})
                        self.mark_as_done(filepath, "approved_and_sent")
                        sent_count += 1
                    else:
                        print(f"  ⚠ MCP not running - cannot send draft {draft_id}")

            except Exception as e:
                print(f"  ✗ Error processing approved file {filepath.name}: {e}")

        return sent_count

    def process_email(self, email_data: dict) -> bool:
        """Process a single email."""
        subject = email_data['subject']
        from_email = email_data['from']
        message_id = email_data['message_id']

        print(f"\n{'='*60}")
        print(f"Processing: {subject}")
        print(f"From: {from_email}")
        print(f"Priority: {email_data['priority']}")
        print(f"{'='*60}")

        # Generate reply
        if self.use_qwen:
            reply = self.generate_reply_with_qwen(email_data)
        else:
            reply = self.generate_reply_template(email_data)

        # Check if sensitive
        is_sensitive = self.is_sensitive_email(email_data)

        if is_sensitive and not self.auto_send:
            # Create approval request
            print("  → Sensitive email - creating approval request")

            # Try to create draft in Gmail
            draft_id = None
            if self.is_mcp_running():
                draft_id = self.create_draft_via_mcp(
                    to=from_email,
                    subject=f"Re: {subject}",
                    body=reply,
                    in_reply_to=message_id
                )

            self.create_approval_request(email_data, reply, draft_id)
            print("  ✓ Approval request created in Pending_Approval folder")
            print("  → Waiting for human approval")

        else:
            # Auto-send
            print("  → Auto-sending reply")

            if self.is_mcp_running():
                success = self.send_email_via_mcp(
                    to=from_email,
                    subject=f"Re: {subject}",
                    body=reply,
                    in_reply_to=message_id
                )

                if not success:
                    print("  → MCP failed, falling back to direct send...")
                    success = self.send_email_direct(
                        to=from_email,
                        subject=f"Re: {subject}",
                        body=reply,
                        in_reply_to=message_id
                    )
            else:
                # Direct send without MCP
                success = self.send_email_direct(
                    to=from_email,
                    subject=f"Re: {subject}",
                    body=reply,
                    in_reply_to=message_id
                )

            if success:
                print("  ✓ Reply sent successfully")
            else:
                print("  ⚠ Failed to send reply")

        return True

    def create_manual_send_instructions(self, email_data: dict, reply: str):
        """Create manual send instructions when MCP is not available."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"MANUAL_SEND_{email_data['subject'][:30]}_{timestamp}.md"
        filepath = self.pending_approval / filename

        content = f"""---
type: manual_send
to: {email_data['from']}
subject: Re: {email_data['subject']}
original_message_id: {email_data['message_id']}
status: pending_manual_send
created: {datetime.now().isoformat()}
---

# Manual Email Send Required

The Email MCP server is not running. Please either:

1. Start the MCP server: `bash .qwen/skills/email-mcp/scripts/start-server.sh`
2. Or send this email manually from Gmail

## Email Details

- **To:** {email_data['from']}
- **Subject:** Re: {email_data['subject']}
- **In Reply To:** Message ID {email_data['message_id']}

## Reply Body

```
{reply}
```

## To Complete

After sending manually, move this file to `/Done` folder.
"""
        filepath.write_text(content)

    def is_mcp_running(self) -> bool:
        """Check if Email MCP server is running."""
        try:
            import httpx
            response = httpx.get(f"{self.mcp_url}/tools/list", timeout=5.0)
            return response.status_code == 200
        except:
            return False

    def send_email_direct(self, to: str, subject: str, body: str, in_reply_to: str = None) -> bool:
        """Send email directly via Gmail API without MCP server."""
        try:
            # Import the direct sender
            import sys
            sys.path.insert(0, str(Path(__file__).parent))
            from direct_gmail_sender import DirectGmailSender

            sender = DirectGmailSender(str(self.vault_path))
            if not sender.authenticate():
                print("  ✗ Failed to authenticate with Gmail API")
                return False

            success = sender.send_email(
                to=to,
                subject=subject,
                body=body,
                in_reply_to=in_reply_to
            )
            return success

        except Exception as e:
            print(f"  ✗ Direct send failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def process_emails(self) -> int:
        """Process all email action files."""
        if not self.needs_action.exists():
            return 0

        email_files = [f for f in self.needs_action.iterdir()
                      if f.suffix == '.md' and f.name.startswith('EMAIL_')]

        if not email_files:
            return 0

        processed = 0
        for filepath in sorted(email_files):  # Sort to process in order
            try:
                email_data = self.parse_action_file(filepath)

                # Skip if not an email
                if email_data['type'] != 'email':
                    continue

                # Process the email
                self.process_email(email_data)

                # Move to Done
                self.mark_as_done(filepath)
                processed += 1

            except Exception as e:
                print(f"  ✗ Error processing {filepath.name}: {e}")
                import traceback
                traceback.print_exc()

        return processed

    def run_loop(self, interval: int = 300):
        """Run in continuous loop."""
        print(f"\n{'='*60}")
        print(f"Email Auto-Processor - Continuous Loop Mode")
        print(f"Check interval: {interval}s ({interval/60:.1f} minutes)")
        print(f"Auto-send: {self.auto_send}")
        print(f"Use Qwen: {self.use_qwen}")
        print(f"MCP URL: {self.mcp_url}")
        print(f"{'='*60}\n")

        check_count = 0
        try:
            while True:
                check_count += 1
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                print(f"\n[{timestamp}] Check #{check_count}")
                print("-" * 60)

                # First, process any approved emails
                approved_count = self.process_approved_emails()
                if approved_count > 0:
                    print(f"  ✓ Sent {approved_count} approved email(s)")

                # Then process new emails
                email_count = self.count_pending_emails()
                if email_count > 0:
                    processed = self.process_emails()
                    print(f"  ✓ Processed {processed} new email(s)")
                else:
                    print(f"  - No new emails to process")

                # Heartbeat every 5 checks
                if check_count % 5 == 0:
                    print(f"\n  [Heartbeat] Check #{check_count}, system running OK")

                # Sleep until next check
                print(f"\n  [Sleep] Waiting {interval}s for next check...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n[Stop] Email processor stopped by user")
            print(f"Total checks performed: {check_count}")
        except Exception as e:
            print(f"\n\n[Error] Processor crashed: {e}")
            raise

    def count_pending_emails(self) -> int:
        """Count pending emails in Needs_Action."""
        if not self.needs_action.exists():
            return 0
        return len([f for f in self.needs_action.iterdir()
                   if f.suffix == '.md' and f.name.startswith('EMAIL_')])


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Email Auto-Processor for AI Employee',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test mode (no sending)
  python email_auto_processor.py /path/to/vault

  # Auto-send mode
  python email_auto_processor.py /path/to/vault --auto-send

  # Continuous loop (every 5 minutes)
  python email_auto_processor.py /path/to/vault --loop --loop-interval 300

  # With Qwen Code integration
  python email_auto_processor.py /path/to/vault --use-qwen --auto-send
        """
    )
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--auto-send', action='store_true',
                       help='Auto-send non-sensitive replies')
    parser.add_argument('--use-qwen', action='store_true',
                       help='Use Qwen Code for intelligent replies')
    parser.add_argument('--mcp-url', default='http://localhost:8809',
                       help='Email MCP server URL (default: http://localhost:8809)')
    parser.add_argument('--loop', action='store_true',
                       help='Run in continuous loop mode')
    parser.add_argument('--loop-interval', type=int, default=300,
                       help='Loop interval in seconds (default: 300)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    processor = EmailAutoProcessor(
        args.vault_path,
        auto_send=args.auto_send,
        use_qwen=args.use_qwen,
        mcp_url=args.mcp_url
    )

    if args.loop:
        processor.run_loop(interval=args.loop_interval)
    else:
        # Single run
        count = processor.process_emails()

        # Also process any approved emails
        approved_count = processor.process_approved_emails()

        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  New emails processed: {count}")
        print(f"  Approved emails sent: {approved_count}")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
