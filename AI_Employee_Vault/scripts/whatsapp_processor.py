#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Auto-Processor for AI Employee.

This script processes WhatsApp action files from Needs_Action folder,
generates intelligent replies, and sends them via WhatsApp Web using Playwright.

Workflow:
1. Scans Needs_Action/ for WHATSAPP_*.md files
2. Reads message content and metadata
3. Analyzes message type and sensitivity
4. Generates intelligent reply
5. For non-sensitive: Sends immediately via WhatsApp Web
6. For sensitive: Creates approval request in Pending_Approval/
7. Moves processed files to Done/

Usage:
    # Test mode (no sending)
    python whatsapp_processor.py /path/to/vault

    # Auto-send mode
    python whatsapp_processor.py /path/to/vault --auto-send

    # Continuous loop
    python whatsapp_processor.py /path/to/vault --loop --loop-interval 60

Silver Tier - Personal AI Employee FTE
"""

import sys
import re
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'watchers'))

try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext
except ImportError:
    print("Error: Playwright not installed.")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)


class WhatsAppReplyGenerator:
    """Generate intelligent replies for WhatsApp messages."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.business_goals = self._load_business_goals()
        self.company_handbook = self._load_company_handbook()
    
    def _load_business_goals(self) -> str:
        """Load Business_Goals.md if available."""
        goals_path = self.vault_path / 'Business_Goals.md'
        if goals_path.exists():
            return goals_path.read_text(encoding='utf-8')
        return ""
    
    def _load_company_handbook(self) -> str:
        """Load Company_Handbook.md if available."""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            return handbook_path.read_text(encoding='utf-8')
        return ""
    
    def analyze_message(self, message_text: str) -> Dict[str, Any]:
        """
        Analyze WhatsApp message to determine type and intent.
        
        Returns:
            Dictionary with:
            - message_type: inquiry, invoice_request, meeting_request, casual, urgent
            - urgency: low, medium, high
            - sensitivity: low, medium, high
            - requires_action: bool
            - suggested_action: str
        """
        text_lower = message_text.lower()
        
        # Detect message type
        message_type = 'general'
        suggested_action = 'Review and respond appropriately'
        
        if any(word in text_lower for word in ['invoice', 'bill', 'payment', 'pay']):
            message_type = 'invoice_request'
            suggested_action = 'Generate and send invoice'
        
        elif any(word in text_lower for word in ['meeting', 'call', 'schedule', 'appointment']):
            message_type = 'meeting_request'
            suggested_action = 'Propose meeting time'
        
        elif any(word in text_lower for word in ['price', 'pricing', 'cost', 'how much', 'rate']):
            message_type = 'pricing_inquiry'
            suggested_action = 'Provide pricing information'
        
        elif any(word in text_lower for word in ['help', 'urgent', 'asap', 'emergency', 'urgent']):
            message_type = 'urgent'
            suggested_action = 'Respond urgently'
        
        elif any(word in text_lower for word in ['hi', 'hello', 'hey', 'good morning', 'good evening']):
            message_type = 'greeting'
            suggested_action = 'Send friendly greeting'
        
        elif any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
            message_type = 'gratitude'
            suggested_action = 'Acknowledge thanks'
        
        # Detect urgency
        urgency = 'low'
        if any(word in text_lower for word in ['urgent', 'asap', 'emergency', 'immediately']):
            urgency = 'high'
        elif any(word in text_lower for word in ['soon', 'quick', 'fast']):
            urgency = 'medium'
        
        # Detect sensitivity
        sensitivity = 'low'
        if any(word in text_lower for word in ['payment', 'money', 'invoice', 'contract', 'legal', 'salary']):
            sensitivity = 'high'
        elif any(word in text_lower for word in ['meeting', 'schedule', 'appointment']):
            sensitivity = 'medium'
        
        # Determine if action needed
        requires_action = message_type not in ['gratitude']
        
        return {
            'message_type': message_type,
            'urgency': urgency,
            'sensitivity': sensitivity,
            'requires_action': requires_action,
            'suggested_action': suggested_action
        }
    
    def generate_reply(self, message_text: str, sender: str, analysis: Dict[str, Any]) -> str:
        """
        Generate contextual reply based on message analysis.
        
        Args:
            message_text: Original message text
            sender: Sender name
            analysis: Message analysis dictionary
        
        Returns:
            Reply text
        """
        msg_type = analysis['message_type']
        
        # Template-based replies (can be enhanced with Qwen Code integration)
        replies = {
            'greeting': f"Hi {sender}! 👋 Great to hear from you. How can I help you today?",
            
            'gratitude': f"You're welcome, {sender}! 😊 Let me know if you need anything else.",
            
            'urgent': f"Hi {sender}, I understand this is urgent. Let me look into this right away and get back to you shortly.",
            
            'invoice_request': f"Hi {sender}, I've received your invoice request. Let me prepare that for you and send it over soon.",
            
            'meeting_request': f"Hi {sender}, I'd be happy to schedule a meeting. What time works best for you this week?",
            
            'pricing_inquiry': f"Hi {sender}, thanks for your interest! Let me get you the pricing details. I'll send that information shortly.",
            
            'general': f"Hi {sender}, thanks for your message! I've received it and will get back to you soon."
        }
        
        return replies.get(msg_type, replies['general'])


class WhatsAppSender:
    """Send WhatsApp messages via Playwright automation."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.session_path = vault_path / '.whatsapp_session'
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.logger = logging.getLogger('WhatsAppSender')
    
    def connect(self):
        """Connect to WhatsApp Web."""
        self.playwright = sync_playwright().start()
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.session_path),
            headless=False,  # Always visible for sending
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = self.context.new_page()
        self.page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
        time.sleep(3)
        self.logger.info("Connected to WhatsApp Web")
    
    def send_message(self, contact_name: str, message: str) -> bool:
        """
        Send a message to a contact via WhatsApp Web.
        
        Args:
            contact_name: Name of contact or phone number
            message: Message text to send
        
        Returns:
            True if sent successfully
        """
        try:
            if not self.page:
                self.connect()
            
            # Search for contact
            search_box = self.page.wait_for_selector(
                'div[contenteditable="true"][data-tab="3"]',
                timeout=10000
            )
            search_box.fill(contact_name)
            time.sleep(2)
            
            # Press Enter to open chat
            search_box.press('Enter')
            time.sleep(2)
            
            # Type message
            message_box = self.page.wait_for_selector(
                'div[contenteditable="true"][data-tab="10"]',
                timeout=10000
            )
            message_box.fill(message)
            time.sleep(1)
            
            # Press Enter to send
            message_box.press('Enter')
            time.sleep(2)
            
            self.logger.info(f"✓ Message sent to {contact_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    def close(self):
        """Clean up resources."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass


class WhatsAppProcessor:
    """Process WhatsApp action files and handle replies."""
    
    def __init__(self, vault_path: str, auto_send: bool = False, use_qwen: bool = False):
        self.vault_path = Path(vault_path)
        self.auto_send = auto_send
        self.use_qwen = use_qwen
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.rejected = self.vault_path / 'Rejected'
        
        # Ensure directories exist
        for d in [self.pending_approval, self.approved, self.done, self.rejected]:
            d.mkdir(exist_ok=True)
        
        # Initialize components
        self.reply_generator = WhatsAppReplyGenerator(self.vault_path)
        self.sender = WhatsAppSender(self.vault_path)
        
        # Logger
        self.logger = logging.getLogger('WhatsAppProcessor')
        
        # Statistics
        self.stats = {
            'processed': 0,
            'sent': 0,
            'approval_pending': 0,
            'errors': 0
        }
    
    def find_whatsapp_files(self) -> List[Path]:
        """Find all WHATSAPP_*.md files in Needs_Action."""
        if not self.needs_action.exists():
            return []
        return list(self.needs_action.glob('WHATSAPP_*.md'))
    
    def parse_action_file(self, filepath: Path) -> Dict[str, Any]:
        """Parse WhatsApp action file to extract metadata and content."""
        content = filepath.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if not frontmatter_match:
            return {}
        
        frontmatter_text = frontmatter_match.group(1)
        body = frontmatter_match.group(2)
        
        # Parse frontmatter
        metadata = {}
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        # Extract message content
        message_match = re.search(r'## Message Content\s*\n(.*?)(?:\n##|\Z)', body, re.DOTALL)
        message = message_match.group(1).strip() if message_match else ''
        
        # Extract detected keywords
        keywords_match = re.search(r'## Detected Keywords\s*\n(.*?)(?:\n##|\Z)', body, re.DOTALL)
        keywords = keywords_match.group(1).strip() if keywords_match else ''
        
        metadata['message'] = message
        metadata['keywords'] = keywords
        metadata['filepath'] = filepath
        
        return metadata
    
    def process_file(self, filepath: Path):
        """Process a single WhatsApp action file."""
        try:
            self.logger.info(f"Processing: {filepath.name}")
            
            # Parse file
            metadata = self.parse_action_file(filepath)
            if not metadata:
                self.logger.error(f"Failed to parse: {filepath.name}")
                self.stats['errors'] += 1
                return
            
            # Extract message details
            sender = metadata.get('from', 'Unknown')
            chat_name = metadata.get('chat_name', sender)
            message = metadata.get('message', '')
            
            if not message:
                self.logger.warning(f"No message content in: {filepath.name}")
                self.stats['errors'] += 1
                return
            
            # Analyze message
            analysis = self.reply_generator.analyze_message(message)
            self.logger.info(f"Message type: {analysis['message_type']}, "
                           f"Urgency: {analysis['urgency']}, "
                           f"Sensitivity: {analysis['sensitivity']}")
            
            # Generate reply
            reply = self.reply_generator.generate_reply(message, sender, analysis)
            
            # Check sensitivity
            if analysis['sensitivity'] == 'high' or self.auto_send == False:
                # Create approval request
                self._create_approval_request(metadata, reply, analysis, filepath)
                self.stats['approval_pending'] += 1
            else:
                # Send immediately
                if self.auto_send:
                    success = self.sender.send_message(chat_name, reply)
                    if success:
                        self.logger.info(f"✓ Reply sent to {chat_name}")
                        self.stats['sent'] += 1
                        self._move_to_done(filepath)
                    else:
                        self.logger.error(f"Failed to send reply")
                        self.stats['errors'] += 1
                else:
                    # Just create approval request
                    self._create_approval_request(metadata, reply, analysis, filepath)
                    self.stats['approval_pending'] += 1
            
            self.stats['processed'] += 1
            
        except Exception as e:
            self.logger.error(f"Error processing {filepath.name}: {e}", exc_info=True)
            self.stats['errors'] += 1
    
    def _create_approval_request(self, metadata: Dict, reply: str, 
                                  analysis: Dict, original_file: Path):
        """Create approval request for sensitive messages."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        chat_name = metadata.get('chat_name', 'Unknown')
        filename = f"WHATSAPP_APPROVAL_{chat_name}_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        content = f'''---
type: whatsapp_approval
action: whatsapp_reply
from: {metadata.get('from', 'Unknown')}
chat_name: {chat_name}
original_file: {original_file.name}
message_type: {analysis['message_type']}
sensitivity: {analysis['sensitivity']}
urgency: {analysis['urgency']}
status: pending
---

# WhatsApp Reply Approval Required

## Original Message

**From:** {metadata.get('from', 'Unknown')}
**Chat:** {chat_name}
**Message:** {metadata.get('message', '')}

## Detected Keywords

{metadata.get('keywords', '')}

## Analysis

- **Type:** {analysis['message_type']}
- **Urgency:** {analysis['urgency']}
- **Sensitivity:** {analysis['sensitivity']}
- **Suggested Action:** {analysis['suggested_action']}

---

## Generated Reply

```
{reply}
```

---

## Approval Required

This reply contains sensitive content and requires your approval before sending.

### To Approve
Move this file to: `Approved/`

### To Reject
Move this file to: `Rejected/`

### To Edit
Edit the reply text above, then move to `Approved/`

---

## Processing Instructions

1. Review the generated reply
2. Edit if needed
3. Move to Approved/ to send
4. Move to Rejected/ to discard

'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created approval request: {filename}")
    
    def process_approved_files(self):
        """Process approved approval requests and send messages."""
        if not self.approved.exists():
            return
        
        approved_files = list(self.approved.glob('WHATSAPP_APPROVAL_*.md'))
        
        for filepath in approved_files:
            try:
                self.logger.info(f"Processing approved: {filepath.name}")
                
                content = filepath.read_text(encoding='utf-8')
                
                # Extract chat name and reply
                chat_match = re.search(r'chat_name:\s*(.+)', content)
                reply_match = re.search(r'## Generated Reply\s*```\s*(.*?)\s*```', content, re.DOTALL)
                
                if not chat_match or not reply_match:
                    self.logger.error(f"Failed to parse approval: {filepath.name}")
                    continue
                
                chat_name = chat_match.group(1).strip()
                reply = reply_match.group(1).strip()
                
                # Send message
                success = self.sender.send_message(chat_name, reply)
                
                if success:
                    self.logger.info(f"✓ Approved message sent to {chat_name}")
                    self._move_to_done(filepath)
                else:
                    self.logger.error(f"Failed to send approved message")
            
            except Exception as e:
                self.logger.error(f"Error processing approved file {filepath.name}: {e}")
    
    def _move_to_done(self, filepath: Path):
        """Move file to Done folder."""
        try:
            dest = self.done / filepath.name
            filepath.rename(dest)
            self.logger.info(f"Moved to Done: {filepath.name}")
        except Exception as e:
            self.logger.error(f"Failed to move to Done: {e}")
    
    def run_once(self):
        """Process all pending WhatsApp files once."""
        self.logger.info("Scanning for WhatsApp action files...")
        
        # Find and process new files
        whatsapp_files = self.find_whatsapp_files()
        if whatsapp_files:
            self.logger.info(f"Found {len(whatsapp_files)} WhatsApp file(s)")
            for filepath in whatsapp_files:
                self.process_file(filepath)
        else:
            self.logger.info("No new WhatsApp files found")
        
        # Process approved files
        self.process_approved_files()
        
        return self.stats
    
    def run_loop(self, interval: int = 60):
        """Run in continuous loop."""
        self.logger.info(f"Starting WhatsApp processor (interval: {interval}s)")
        
        iteration = 0
        try:
            while True:
                iteration += 1
                if iteration % 10 == 0:
                    self.logger.info("✓ Processor running...")
                
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.logger.info("Processor stopped by user")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Auto-Processor')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--auto-send', action='store_true', help='Auto-send non-sensitive replies')
    parser.add_argument('--use-qwen', action='store_true', help='Use Qwen Code for intelligent replies')
    parser.add_argument('--loop', action='store_true', help='Run in continuous loop')
    parser.add_argument('--loop-interval', type=int, default=60, help='Loop interval in seconds (default: 60)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create processor
    processor = WhatsAppProcessor(args.vault_path, args.auto_send, args.use_qwen)
    
    try:
        if args.loop:
            processor.run_loop(args.loop_interval)
        else:
            stats = processor.run_once()
            print(f"\n{'='*60}")
            print(f"Summary:")
            print(f"  Files processed: {stats['processed']}")
            print(f"  Messages sent: {stats['sent']}")
            print(f"  Pending approval: {stats['approval_pending']}")
            print(f"  Errors: {stats['errors']}")
            print(f"{'='*60}")
    except KeyboardInterrupt:
        print("\nProcessor stopped by user")
    finally:
        processor.sender.close()


if __name__ == '__main__':
    main()
