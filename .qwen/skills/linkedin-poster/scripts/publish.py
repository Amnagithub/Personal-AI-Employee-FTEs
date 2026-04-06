#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publish LinkedIn Posts - WSL Version

This script launches a Windows Python subprocess to handle LinkedIn posting
to avoid WSL/Windows Chrome path issues.

Usage:
    python3 publish.py --vault ./AI_Employee_Vault
"""

import argparse
import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime
from typing import List


def find_windows_python() -> str:
    """Find Windows Python executable from WSL."""
    # Common Windows Python paths (WSL format) - check these in order
    python_paths = [
        "/mnt/c/Users/Saif/AppData/Local/Programs/Python/Python312/python.exe",
        "/mnt/c/Users/Saif/AppData/Local/Programs/Python/Python313/python.exe",
        "/mnt/c/Users/Saif/AppData/Local/Programs/Python/Python311/python.exe",
        "/mnt/c/Users/Saif/AppData/Local/Programs/Python/Python310/python.exe",
        "/mnt/c/Program Files/Python312/python.exe",
        "/mnt/c/Program Files/Python311/python.exe",
        "/mnt/c/Program Files/Python310/python.exe",
        "/mnt/c/Python314/python.exe",
    ]
    
    # First pass: find Python with playwright installed
    for path in python_paths:
        if os.path.exists(path):
            result = subprocess.run(
                [path, '-c', 'import playwright; print("ok")'],
                capture_output=True, text=True
            )
            if result.returncode == 0 and 'ok' in result.stdout:
                return path
    
    # Second pass: return any working Python (user can install playwright)
    for path in python_paths:
        if os.path.exists(path):
            return path
    
    # Try to find via Windows 'where' command
    try:
        result = subprocess.run(
            ['cmd.exe', '/c', 'where', 'python'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line and 'WindowsApps' not in line:  # Skip Windows Store Python
                    wsl_path = line.replace('\\', '/').replace('C:', '/mnt/c')
                    if os.path.exists(wsl_path):
                        return wsl_path
    except:
        pass
    
    return ""


WINDOWS_PYTHON = find_windows_python()

# Embedded Windows script
WINDOWS_SCRIPT = '''
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: Playwright not installed on Windows Python")
    sys.exit(1)

def post_to_linkedin(text, user_data_dir):
    """Post to LinkedIn using Playwright - Semi-automated."""
    chrome_path = r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

    # Try alternative Chrome paths
    if not Path(chrome_path).exists():
        alt_paths = [
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            str(Path.home() / "AppData/Local/Google/Chrome/Application/chrome.exe"),
        ]
        for path in alt_paths:
            if Path(path).exists():
                chrome_path = path
                break

    if not Path(chrome_path).exists():
        print(f"Chrome not found at {chrome_path}")
        return False

    print(f"Using Chrome: {chrome_path}")
    print(f"Using profile: {user_data_dir}")
    print("")
    print("=" * 60)
    print("INSTRUCTIONS:")
    print("1. If you see LinkedIn login, log in manually")
    print("2. Script will click 'Start a post' automatically")
    print("3. Script will fill the text content automatically")
    print("4. YOU just need to click the 'Post' button to publish")
    print("=" * 60)
    print("")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                executable_path=chrome_path,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                ],
                ignore_default_args=['--enable-automation'],
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Navigate to LinkedIn
            print("Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/feed/', wait_until='domcontentloaded', timeout=60000)
            page.wait_for_timeout(3000)

            # Wait for login - with proper page reload detection
            is_logged_in = False
            
            print("")
            print("Waiting for login...")
            for attempt in range(60):  # 120 seconds max
                current_url = page.url
                
                # Check if we're on the feed page (logged in)
                if '/feed' in current_url or '/mycompany' in current_url:
                    print(f"✓ Logged in successfully! (URL: {current_url[:60]}...)")
                    is_logged_in = True
                    break
                
                # Show login status
                if attempt == 0:
                    print("  Login page detected - waiting for you to log in...")
                
                page.wait_for_timeout(2000)
            else:
                print("✗ Login timeout (120 seconds)")
                browser.close()
                return False

            if not is_logged_in:
                browser.close()
                return False

            # Wait a moment for page to fully load
            page.wait_for_timeout(2000)

            # Open post composer using JavaScript
            print("")
            print("Opening post composer...")
            
            # Use JavaScript to find and click the "Start a post" button
            # This is more reliable than Playwright selectors
            try:
                page.evaluate("""
                    () => {
                        // Find all buttons with "Start a post" text
                        const buttons = document.querySelectorAll('button');
                        for (const btn of buttons) {
                            if (btn.textContent.includes('Start a post')) {
                                btn.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                print("  ✓ Triggered post composer via JavaScript")
            except Exception as e:
                print(f"  ⚠️ JavaScript click failed: {str(e)[:50]}")
            
            # Wait for composer to open
            page.wait_for_timeout(8000)
            
            # Take screenshot to see what's happening
            try:
                screenshot_path = 'C:/Users/Saif/AppData/Local/Temp/linkedin_debug.png'
                page.screenshot(path=screenshot_path)
                print("  Screenshot saved for debugging")
            except:
                pass

            # Fill post content using JavaScript
            print("")
            print("Filling post content...")
            text_entered = False
            
            try:
                # Wait for editor to appear
                page.wait_for_timeout(3000)
                
                # Use JavaScript to fill the editor
                # This directly manipulates the DOM and triggers React events
                text_to_insert = text[:3000]
                
                result = page.evaluate(f"""
                    () => {{
                        // Find the editor
                        const editors = document.querySelectorAll('[contenteditable="true"], [role="textbox"]');
                        
                        if (editors.length === 0) {{
                            return {{ success: false, reason: 'No editors found' }};
                        }}
                        
                        const editor = editors[0];
                        
                        // Focus and clear the editor
                        editor.focus();
                        editor.innerText = '';
                        
                        // Use execCommand to insert text (works with React)
                        const success = document.execCommand('insertText', false, `{text_to_insert.replace('`', '\\`').replace('\\n', '\\n')}`);
                        
                        // Dispatch events
                        editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        editor.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        
                        return {{ success: success, length: `{text_to_insert}`.length }};
                    }}
                """)
                
                print(f"  Result: {result}")
                
                if result.get('success'):
                    page.wait_for_timeout(2000)
                    print(f"✓ Post content filled! ({result.get('length')} characters)")
                    text_entered = True
                else:
                    print(f"  ⚠️ Editor not found, trying alternative...")
                    
                    # Alternative: Just type using keyboard
                    page.keyboard.type(text[:2000], delay=20)
                    page.wait_for_timeout(3000)
                    print("✓ Content typed via keyboard!")
                    text_entered = True
                    
            except Exception as e:
                print(f"  ✗ Failed: {str(e)[:60]}...")
                
                # Last resort: just type it
                try:
                    page.keyboard.type(text[:1500], delay=25)
                    page.wait_for_timeout(3000)
                    print("✓ Content entered via fallback typing!")
                    text_entered = True
                except:
                    pass

            if not text_entered:
                print("✗ Could not fill content automatically")
                print("   Please paste your content manually in the LinkedIn post editor")

            # Show instructions for manual Post button click
            print("")
            print("=" * 60)
            print("READY TO PUBLISH!")
            print("Your post content has been filled automatically.")
            print("Please review and click the blue 'Post' button to publish.")
            print("")
            print("Content preview:")
            print("-" * 60)
            print(text[:200] + "..." if len(text) > 200 else text)
            print("-" * 60)
            print("")
            print("Waiting 90 seconds for you to click 'Post'...")
            print("=" * 60)

            # Wait for user to click Post button
            page.wait_for_timeout(90000)

            print("")
            print("✓ Done! Post should be published.")
            
            browser.close()
            return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: windows_post.py <text> <user_data_dir>")
        sys.exit(1)

    text = sys.argv[1]
    user_data_dir = sys.argv[2]

    success = post_to_linkedin(text, user_data_dir)
    sys.exit(0 if success else 1)
'''


class LinkedInPublisher:
    """Publish approved LinkedIn posts using Windows Python subprocess."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.pending_approval = vault_path / 'Pending_Approval'
        self.approved = vault_path / 'Approved'
        self.done = vault_path / 'Done'

        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

    def publish_approved(self) -> List[Path]:
        """Publish all approved posts."""
        published = []
        all_posts = list(self.approved.glob('LINKEDIN_POST_*.md'))

        if not all_posts:
            print("No approved posts to publish.")
            return published

        print(f"Found {len(all_posts)} approved post(s) to publish.")

        for post_path in all_posts:
            try:
                content = post_path.read_text(encoding='utf-8')

                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        body = parts[2]
                        lines = body.strip().split('\n')
                        text_content = '\n'.join([
                            l for l in lines
                            if not l.startswith('#') and l.strip()
                        ])

                        success = self._publish_to_linkedin(text_content)

                        if success:
                            done_path = self.done / post_path.name
                            done_path.write_text(
                                content + f'\n\n---\n\nPublished: {datetime.now().isoformat()}\n',
                                encoding='utf-8'
                            )
                            post_path.unlink()
                            published.append(post_path)
                            print(f"✓ Published: {post_path.name}")
                        else:
                            print(f"✗ Failed to publish: {post_path.name}")
                    else:
                        print(f"✗ Invalid format: {post_path.name}")
                else:
                    print(f"✗ No frontmatter: {post_path.name}")

            except Exception as e:
                print(f"✗ Error publishing {post_path.name}: {e}")

        return published

    def _publish_to_linkedin(self, text: str) -> bool:
        """Publish to LinkedIn via Windows Python subprocess."""
        print("Looking for Windows Python with Playwright...")
        
        if not WINDOWS_PYTHON:
            print("ERROR: Could not find Windows Python")
            print("\nTo fix this, run from Windows PowerShell:")
            print("  pip install playwright")
            print("  playwright install chromium")
            return False
        
        print(f"Using Windows Python: {WINDOWS_PYTHON}")
        
        # Check if playwright is installed
        result = subprocess.run(
            [WINDOWS_PYTHON, '-c', 'import playwright'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print("ERROR: Playwright not installed on Windows Python")
            print("\nTo fix this, run from Windows PowerShell:")
            print(f"  {WINDOWS_PYTHON.replace('/mnt/c', 'C:').replace('/', '\\\\')} -m pip install playwright")
            print(f"  {WINDOWS_PYTHON.replace('/mnt/c', 'C:').replace('/', '\\\\')} -m playwright install chromium")
            return False
        
        # Create temp script file in Windows-accessible location
        windows_temp = "/mnt/c/Users/Saif/AppData/Local/Temp"
        os.makedirs(windows_temp, exist_ok=True)
        script_path_wsl = os.path.join(windows_temp, f"linkedin_post_{os.getpid()}.py")
        script_path_windows = script_path_wsl.replace('/mnt/c', 'C:').replace('/', '\\')
        
        with open(script_path_wsl, 'w') as f:
            f.write(WINDOWS_SCRIPT)
        
        # Create temp user data dir
        user_data_dir = "C:\\Users\\Saif\\AppData\\Local\\Temp\\linkedin_automation"
        
        try:
            # Run Windows Python script with Windows-style path
            cmd = [WINDOWS_PYTHON, script_path_windows, text, user_data_dir]
            print(f"Script path (Windows): {script_path_windows}")
            print(f"Launching LinkedIn poster on Windows...")
            
            result = subprocess.run(
                cmd,
                capture_output=False,
                text=True,
                timeout=180
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("Posting timed out (3 minutes)")
            return False
        except Exception as e:
            print(f"Error running Windows Python: {e}")
            return False
        finally:
            # Cleanup temp script
            try:
                os.unlink(script_path)
            except:
                pass

    def list_pending(self) -> List[Path]:
        """List all pending post drafts."""
        pending = list(self.pending_approval.glob('LINKEDIN_POST_*.md'))

        if pending:
            print(f"\nPending Posts ({len(pending)}):")
            print("-" * 60)
            for post in pending:
                content = post.read_text(encoding='utf-8')
                lines = content.split('\n')
                preview = ''
                for line in lines:
                    if line.strip() and not line.startswith('#') and not line.startswith('---'):
                        preview = line[:80]
                        break

                print(f"📝 {post.name}")
                print(f"   Preview: {preview}...")
                print()
        else:
            print("No pending post drafts.")

        return pending

    def list_approved(self) -> List[Path]:
        """List all approved posts ready to publish."""
        approved = list(self.approved.glob('LINKEDIN_POST_*.md'))

        if approved:
            print(f"\nApproved Posts ({len(approved)}):")
            print("-" * 60)
            for post in approved:
                print(f"✓ {post.name}")
        else:
            print("No approved posts ready to publish.")

        return approved


def main():
    parser = argparse.ArgumentParser(
        description='Publish approved LinkedIn posts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 publish.py --vault ./AI_Employee_Vault
  python3 publish.py --list-pending
  python3 publish.py --list-approved
        '''
    )
    parser.add_argument('--vault', '-v', default='.', help='Path to vault (default: current dir)')
    parser.add_argument('--list-pending', action='store_true', help='Show pending drafts')
    parser.add_argument('--list-approved', action='store_true', help='Show approved posts')

    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    publisher = LinkedInPublisher(vault)

    if args.list_pending:
        publisher.list_pending()
    elif args.list_approved:
        publisher.list_approved()
    else:
        print("Publishing approved posts...")
        published = publisher.publish_approved()
        print(f"\nPublished {len(published)} post(s)")


if __name__ == '__main__':
    main()
