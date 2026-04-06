#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Monitor WhatsApp Web for urgent messages.

This watcher monitors WhatsApp Web using Playwright browser automation
to detect incoming messages containing specific keywords and creates
action files in the Needs_Action folder for Qwen Code to process.

Usage:
    python whatsapp_watcher.py /path/to/vault

Or run once (for testing):
    python whatsapp_watcher.py /path/to/vault --once

Silver Tier - Personal AI Employee FTE
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, Page, BrowserContext
except ImportError:
    print("Error: Playwright not installed.")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)


class WhatsAppWatcher(BaseWatcher):
    """
    Watcher that monitors WhatsApp Web for new messages.
    
    Uses Playwright to automate WhatsApp Web and detect messages
    containing specific keywords. Creates action files in 
    /Needs_Action folder for each matching message.
    """

    def __init__(self, vault_path: str, check_interval: int = 30, headless: bool = False):
        super().__init__(vault_path, check_interval)
        
        # Keywords to monitor (case-insensitive)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'pricing']
        
        # WhatsApp Web URL
        self.whatsapp_url = 'https://web.whatsapp.com'
        
        # Session path for persistent login
        self.session_path = self.vault_path / '.whatsapp_session'
        self.session_path.mkdir(exist_ok=True)
        
        # Playwright instances
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Track processed messages
        self.last_message_timestamps = {}
        self.message_cache_path = self.vault_path / '.whatsapp_cache.json'
        self._load_message_cache()
        
        # Headless mode (False = visible for initial login)
        self.headless = headless
        
        # Connect to WhatsApp Web
        self._connect()
    
    def _load_message_cache(self):
        """Load previously processed message IDs from cache."""
        if self.message_cache_path.exists():
            try:
                with open(self.message_cache_path, 'r', encoding='utf-8') as f:
                    self.last_message_timestamps = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load WhatsApp cache: {e}")
                self.last_message_timestamps = {}
    
    def _save_message_cache(self):
        """Save processed message IDs to cache."""
        try:
            # Keep only last 500 entries
            if len(self.last_message_timestamps) > 500:
                # Convert to list, sort by timestamp, keep last 500
                items = sorted(self.last_message_timestamps.items(), key=lambda x: x[1])
                self.last_message_timestamps = dict(items[-500:])
            
            with open(self.message_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.last_message_timestamps, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save WhatsApp cache: {e}")
    
    def _connect(self):
        """Launch browser and navigate to WhatsApp Web."""
        try:
            self.logger.info("Starting Playwright...")
            self.playwright = sync_playwright().start()
            
            # Launch persistent context with saved session
            self.logger.info(f"Loading session from: {self.session_path}")
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox'
                ]
            )
            
            self.page = self.context.new_page()
            
            # Navigate to WhatsApp Web
            self.logger.info("Navigating to WhatsApp Web...")
            self.page.goto(self.whatsapp_url, wait_until='domcontentloaded', timeout=60000)
            
            # Wait for initial load
            time.sleep(3)
            
            # Check if logged in
            if self._is_logged_in():
                self.logger.info("✓ Connected to WhatsApp Web (logged in)")
            else:
                self.logger.warning("⚠ Not logged in to WhatsApp Web")
                self.logger.info("→ Please scan QR code or wait for browser to show login")
                if not self.headless:
                    self.logger.info("→ Browser is visible for manual login")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to WhatsApp Web: {e}")
            raise
    
    def _is_logged_in(self) -> bool:
        """Check if WhatsApp Web is logged in."""
        try:
            # Look for chat list or search box (indicates logged in)
            search_box = self.page.query_selector('div[contenteditable="true"][data-tab="3"]')
            if search_box:
                return True
            
            # Alternative: check for chat list
            chat_list = self.page.query_selector('div[role="grid"]')
            if chat_list:
                return True
            
            # If we see QR code, not logged in
            qr_code = self.page.query_selector('canvas[data-testid="qrcode"]')
            if qr_code:
                return False
            
            return False
        except Exception as e:
            self.logger.debug(f"Login check failed: {e}")
            return False
    
    def _wait_for_login(self, timeout_seconds: int = 120):
        """Wait for user to log in to WhatsApp Web."""
        if self._is_logged_in():
            return
        
        self.logger.info("Waiting for login... (timeout: {}s)".format(timeout_seconds))
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            time.sleep(2)
            if self._is_logged_in():
                self.logger.info("✓ Login successful!")
                return
            self.logger.info(f"  Waiting... {int(timeout_seconds - (time.time() - start_time))}s remaining")
        
        self.logger.error("Login timeout exceeded")
        raise TimeoutError("Failed to log in to WhatsApp Web")
    
    def _get_unread_messages(self) -> List[Dict[str, Any]]:
        """
        Scrape unread messages from WhatsApp Web.
        
        Returns:
            List of message dictionaries with:
            - chat_name: Name of the chat/contact
            - sender: Sender name (if group) or chat name
            - message: Message text
            - timestamp: When message was received
            - is_group: Whether it's a group chat
        """
        messages = []
        
        try:
            # Wait for chat list to load
            self.page.wait_for_selector('div[role="grid"]', timeout=5000)
            
            # Get all chat items
            chat_items = self.page.query_selector_all('div[role="row"]')
            
            for chat_item in chat_items:
                try:
                    # Check for unread indicator
                    unread_badge = chat_item.query_selector('span[data-testid="unread"]')
                    if not unread_badge:
                        continue
                    
                    # Get chat name
                    chat_name_elem = chat_item.query_selector('span[dir="auto"]')
                    if not chat_name_elem:
                        continue
                    chat_name = chat_name_elem.inner_text()
                    
                    # Click on chat to open it
                    chat_item.click()
                    time.sleep(1)
                    
                    # Wait for messages to load
                    self.page.wait_for_selector('div[role="grid"] div.copyable-text', timeout=5000)
                    
                    # Get recent messages
                    message_elements = self.page.query_selector_all('div[role="grid"] div.copyable-text')
                    
                    for msg_elem in message_elements[-10:]:  # Last 10 messages
                        try:
                            # Get message data
                            msg_data = self._extract_message(msg_elem, chat_name)
                            if msg_data:
                                messages.append(msg_data)
                        except Exception as e:
                            self.logger.debug(f"Failed to extract message: {e}")
                            continue
                    
                    # Go back to chat list
                    self.page.keyboard.press('Escape')
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.debug(f"Failed to process chat: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Failed to get unread messages: {e}")
        
        return messages
    
    def _extract_message(self, element, chat_name: str) -> Optional[Dict[str, Any]]:
        """Extract message data from a message element."""
        try:
            # Get message text
            msg_elem = element.query_selector('span.selectable-text, span[dir="auto"]')
            if not msg_elem:
                return None
            
            message_text = msg_elem.inner_text().strip()
            if not message_text:
                return None
            
            # Get sender (for groups)
            sender_elem = element.query_selector('span[dir="auto"][title]')
            sender = sender_elem.get_attribute('title') if sender_elem else chat_name
            
            # Get timestamp
            time_elem = element.query_selector('span[data-testid="msg-time"]')
            timestamp = time_elem.inner_text() if time_elem else datetime.now().isoformat()
            
            # Check if it's a group message
            is_group = sender != chat_name
            
            # Create unique ID
            msg_id = f"{chat_name}_{message_text[:30]}_{timestamp}"
            
            return {
                'id': msg_id,
                'chat_name': chat_name,
                'sender': sender,
                'message': message_text,
                'timestamp': timestamp,
                'is_group': is_group
            }
            
        except Exception as e:
            self.logger.debug(f"Failed to extract message details: {e}")
            return None
    
    def _message_matches_keywords(self, message_text: str) -> bool:
        """Check if message contains any monitored keywords."""
        message_lower = message_text.lower()
        return any(keyword in message_lower for keyword in self.keywords)
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new messages with keywords.
        
        Returns:
            List of new message dictionaries
        """
        try:
            # Ensure we're logged in
            if not self._is_logged_in():
                self.logger.warning("Not logged in, attempting to wait for login...")
                self._wait_for_login(timeout_seconds=60)
            
            # Get unread messages
            messages = self._get_unread_messages()
            
            # Filter by keywords and new messages
            new_messages = []
            for msg in messages:
                # Check if matches keywords
                if not self._message_matches_keywords(msg['message']):
                    continue
                
                # Check if already processed
                if msg['id'] in self.last_message_timestamps:
                    continue
                
                # Add to processed
                self.last_message_timestamps[msg['id']] = datetime.now().isoformat()
                new_messages.append(msg)
            
            # Save cache
            if new_messages:
                self._save_message_cache()
                self.logger.info(f"Found {len(new_messages)} new matching message(s)")
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            # Try to reconnect
            try:
                self._reconnect()
            except:
                pass
            return []
    
    def _reconnect(self):
        """Reconnect to WhatsApp Web."""
        self.logger.info("Attempting to reconnect...")
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass
        
        self._connect()
    
    def create_action_file(self, item: Dict[str, Any]) -> Path:
        """
        Create a markdown action file for the WhatsApp message.
        
        Args:
            item: Message info dictionary
        
        Returns:
            Path to the created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = item['chat_name'][:40].replace(' ', '_').replace(':', '')
        filename = f"WHATSAPP_{safe_name}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: whatsapp
from: {item['sender']}
chat_name: {item['chat_name']}
received: {datetime.now().isoformat()}
priority: high
status: pending
message_id: {item['id']}
is_group: {str(item['is_group']).lower()}
---

# WhatsApp Message Received

A new WhatsApp message requires your attention.

## Message Details

- **From:** {item['sender']}
- **Chat:** {item['chat_name']}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Group Chat:** {'Yes' if item['is_group'] else 'No'}

---

## Message Content

{item['message']}

---

## Detected Keywords

{', '.join([kw for kw in self.keywords if kw in item['message'].lower()])}

---

## Suggested Actions

- [ ] Read and understand the message
- [ ] Check if reply is needed
- [ ] Draft response (requires approval for sensitive actions)
- [ ] Take any required action (create invoice, schedule meeting, etc.)
- [ ] Mark as complete

---

## Processing Notes

_Add any notes about how this message was handled_

'''
        
        filepath.write_text(content, encoding='utf-8')
        self.logger.info(f"Created action file: {filename}")
        return filepath
    
    def close(self):
        """Clean up Playwright resources."""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("WhatsApp Watcher closed")
        except Exception as e:
            self.logger.debug(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor."""
        self.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('vault_path', help='Path to the Obsidian vault')
    parser.add_argument('--once', action='store_true', help='Run once (for testing)')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds (default: 30)')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create watcher
    watcher = WhatsAppWatcher(args.vault_path, args.interval, args.headless)
    
    try:
        if not args.once:
            # Wait for login if running continuously
            if not watcher._is_logged_in():
                watcher._wait_for_login(timeout_seconds=120)
            watcher.run()
        else:
            # Run once
            count = watcher.run_once()
            print(f"Processed {count} new message(s)")
    except KeyboardInterrupt:
        print("\nWatcher stopped by user")
    finally:
        watcher.close()


if __name__ == '__main__':
    main()
