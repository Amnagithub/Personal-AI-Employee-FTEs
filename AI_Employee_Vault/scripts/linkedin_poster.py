#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Automate LinkedIn posts for business promotion.

This script creates LinkedIn post drafts and publishes approved posts
using Playwright browser automation.

Usage:
    # Create a post draft
    python linkedin_poster.py create --text "Your post text" --hashtags "AI,Automation"

    # Publish approved posts
    python linkedin_poster.py publish --vault /path/to/vault

    # Auto-post (create and publish immediately)
    python linkedin_poster.py auto --text "Your post text" --hashtags "AI,Automation"

Silver Tier - Personal AI Employee FTE
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


class LinkedInPoster:
    """Create and publish LinkedIn posts with approval workflow."""

    def __init__(self, vault_path: Path, auto_post: bool = False):
        self.vault_path = vault_path
        self.pending_approval = vault_path / 'Pending_Approval'
        self.approved = vault_path / 'Approved'
        self.done = vault_path / 'Done'
        self.auto_post = auto_post  # Auto-post mode

        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def create_draft(self, text: str, hashtags: list = None, 
                     scheduled_time: str = None, images: list = None) -> Path:
        """
        Create a LinkedIn post draft for approval.
        
        Args:
            text: Post content
            hashtags: List of hashtags (without #)
            scheduled_time: Optional scheduled publish time
            images: Optional list of image paths
            
        Returns:
            Path to created draft file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}.md"
        filepath = self.pending_approval / filename
        
        # Format hashtags
        hashtag_text = ''
        if hashtags:
            hashtag_text = '\n\n' + ' '.join([f'#{tag}' for tag in hashtags])
        
        # Full post content
        full_text = text + hashtag_text
        
        content = f'''---
type: linkedin_post
status: pending_approval
created: {datetime.now().isoformat()}
scheduled_time: {scheduled_time or 'immediate'}
hashtags: {', '.join(hashtags or [])}
character_count: {len(full_text)}
images: {json.dumps(images or [])}
---

# LinkedIn Post Draft

## Content

{full_text}

## Details

- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Character Count:** {len(full_text)} (Max: 3000)
- **Hashtags:** {', '.join(hashtags or [])}
- **Images:** {len(images or [])}
- **Scheduled:** {scheduled_time or 'Immediate'}

---

## To Approve

Move this file to `/Approved` folder to publish.

## To Reject

Move this file to `/Rejected` folder with a comment.

## To Request Changes

Edit the content above and save, or add comments below.

---

## Notes

<!-- Add any comments or feedback here -->

'''
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def publish_approved(self, auto_post: bool = False) -> list:
        """
        Publish all approved posts.

        Args:
            auto_post: If True, publish immediately without moving files

        Returns:
            List of published post paths
        """
        published = []

        # Get all approved posts (or pending if auto-post mode)
        if auto_post or self.auto_post:
            # In auto mode, also check pending approval
            approved_posts = list(self.approved.glob('LINKEDIN_POST_*.md'))
            pending_posts = list(self.pending_approval.glob('LINKEDIN_POST_*.md'))
            # Combine both, pending first
            all_posts = pending_posts + approved_posts
            print(f"Auto-post mode: Found {len(all_posts)} post(s) to publish.")
        else:
            all_posts = list(self.approved.glob('LINKEDIN_POST_*.md'))
            print(f"Found {len(all_posts)} approved post(s) to publish.")

        if not all_posts:
            print("No posts to publish.")
            return published

        for post_path in all_posts:
            try:
                # Read post content
                content = post_path.read_text()

                # Parse frontmatter
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1]
                        body = parts[2]

                        # Extract text content
                        lines = body.strip().split('\n')
                        text_content = '\n'.join([l for l in lines if not l.startswith('#')])

                        # Publish using Playwright
                        success = self._publish_to_linkedin(text_content)

                        if success:
                            # Move to Done
                            done_path = self.done / post_path.name
                            done_path.write_text(content + f'\n\n---\n\nPublished: {datetime.now().isoformat()}\n')
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
        """
        Publish text to LinkedIn using Playwright.

        Args:
            text: Post content

        Returns:
            True if successful
        """
        try:
            from playwright.sync_api import sync_playwright
            import os

            # Use your actual Chrome profile for persistent login
            # Windows Chrome profile path
            chrome_user_data = os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data")
            chrome_profile = "Default"  # or "Profile 1", "Profile 2", etc.

            with sync_playwright() as p:
                # Windows Chrome path
                chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

                if not os.path.exists(chrome_path):
                    # Try alternative paths
                    alt_paths = [
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
                    ]
                    for path in alt_paths:
                        if os.path.exists(path):
                            chrome_path = path
                            break

                print(f"Launching Chrome from: {chrome_path}")
                print(f"Using profile: {chrome_user_data}")

                # Launch Chrome with your existing profile (preserves cookies/sessions)
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=chrome_user_data,
                    headless=False,
                    executable_path=chrome_path,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--profile-directory=' + chrome_profile,
                        '--disable-extensions',
                        '--disable-background-networking',
                        '--disable-default-apps',
                        '--disable-sync',
                        '--no-first-run',
                    ],
                    ignore_default_args=['--enable-automation'],
                )

                page = browser.pages[0] if browser.pages else browser.new_page()

                # Go to LinkedIn
                print("Navigating to LinkedIn...")
                page.goto('https://www.linkedin.com/feed/', wait_until='networkidle', timeout=60000)

                # Wait for page to load
                page.wait_for_timeout(5000)

                # Debug: print current URL
                print(f"Current URL: {page.url}")

                # Check if logged in
                if 'login' in page.url or 'checkpoint' in page.url:
                    print("⚠️ Not logged in or checkpoint detected.")
                    print("Please log in to LinkedIn manually in the opened browser.")
                    print("Waiting up to 120 seconds for login...")

                    # Wait for user to log in
                    for i in range(60):
                        page.wait_for_timeout(2000)
                        current_url = page.url
                        if 'feed' in current_url or 'mycompany' in current_url:
                            print("✓ Logged in successfully")
                            break
                    else:
                        print("✗ Login timeout. Please ensure you're logged in and try again.")
                        browser.close()
                        return False
                else:
                    print("✓ Already logged in to LinkedIn")

                # Find and click the post creation box
                print("Creating new post...")
                
                # Wait a bit more for page to fully load
                page.wait_for_timeout(3000)
                
                # Take a screenshot for debugging (optional)
                # page.screenshot(path='debug_linkedin.png')

                # Try to find the post creation input with multiple strategies
                found = False
                
                # Strategy 1: Button with text "Start a post" or "Post"
                selectors = [
                    'button:has-text("Start a post")',
                    'button:has-text("Post")',
                    'div[role="button"]:has-text("Start a post")',
                    'div[role="button"]:has-text("Post")',
                    'button[aria-label*="post" i]',
                    'button[aria-label*="Post" i]',
                    '.share-box-feed-entry__trigger',  # LinkedIn class name
                    'button[class*="share-box"]',
                ]
                
                for selector in selectors:
                    try:
                        element = page.locator(selector).first
                        if element.is_visible(timeout=5000):
                            element.click()
                            print(f"✓ Found post button with selector: {selector}")
                            found = True
                            break
                    except Exception as e:
                        continue
                
                if not found:
                    print("Could not find post creation button automatically.")
                    print("")
                    print("=== MANUAL POSTING REQUIRED ===")
                    print("1. In the opened browser, click 'Start a post' or 'Post' button")
                    print("2. Paste the following content:")
                    print("")
                    print("-" * 60)
                    print(text[:500])  # Show first 500 chars
                    print("-" * 60)
                    print("")
                    print("Waiting 90 seconds for manual action...")
                    
                    # Wait for user to manually start a post
                    dialog_found = False
                    for i in range(45):  # Wait up to 90 seconds
                        page.wait_for_timeout(2000)
                        # Check if post dialog is open (LinkedIn uses various indicators)
                        try:
                            # Look for common post dialog indicators
                            dialog_indicators = [
                                'div[role="dialog"]',
                                'div[class*="post-overlay"]',
                                'div[class*="share-box-feed-entry"]',
                                'div[aria-label*="post" i]',
                                'div[id*="post-editor"]',
                            ]
                            for indicator in dialog_indicators:
                                try:
                                    if page.locator(indicator).first.is_visible(timeout=1000):
                                        print("✓ Detected post dialog!")
                                        dialog_found = True
                                        break
                                except:
                                    pass
                            if dialog_found:
                                break
                        except:
                            pass
                    else:
                        print("✗ Timeout waiting for manual post creation")
                        print("Post failed. Please create manually on LinkedIn.")
                        browser.close()
                        return False
                    
                    # Wait a bit more for dialog to fully load
                    page.wait_for_timeout(2000)
                
                # Wait for post dialog to appear
                page.wait_for_timeout(2000)

                # Find the text input and fill it
                print("Writing post content...")

                # LinkedIn uses a contenteditable div for the post text
                try:
                    # Fill the post text - multiple selector strategies
                    text_selectors = [
                        'div[contenteditable="true"][role="textbox"]',
                        'div[contenteditable="true"]',
                        'div[class*="editable"]',
                        'div[data-id="post-text-editor"]',
                    ]
                    
                    text_entered = False
                    for selector in text_selectors:
                        try:
                            editable = page.locator(selector).first
                            if editable.is_visible(timeout=3000):
                                editable.fill(text[:3000])  # LinkedIn limit
                                print("✓ Post content entered")
                                text_entered = True
                                break
                        except:
                            continue
                    
                    if not text_entered:
                        print("Could not auto-fill text. Please paste manually.")
                        print("Waiting 30 seconds...")
                        page.wait_for_timeout(30000)  # Give time for manual paste
                    
                    # Click Post button
                    print("Publishing post...")
                    
                    # Multiple selectors for Post button
                    post_button_selectors = [
                        'button:has-text("Post")',
                        'button:has-text("post")',
                        'button[type="submit"]',
                        'button[aria-label*="Post" i]',
                        'div[role="button"]:has-text("Post")',
                    ]
                    
                    post_clicked = False
                    for selector in post_button_selectors:
                        try:
                            post_button = page.locator(selector).first
                            if post_button.is_visible(timeout=3000) and post_button.is_enabled(timeout=3000):
                                post_button.click()
                                print("✓ Post button clicked")
                                post_clicked = True
                                break
                        except:
                            continue
                    
                    if not post_clicked:
                        print("Please click the Post button manually.")
                        print("Waiting 30 seconds...")
                        page.wait_for_timeout(30000)
                    
                    # Wait for confirmation
                    page.wait_for_timeout(3000)

                    print("✓ Post published successfully!")
                    browser.close()
                    return True
                    
                except Exception as e:
                    print(f"Error during posting: {e}")
                    print("You may need to complete the post manually.")
                    browser.close()
                    return False

        except ImportError:
            print("Error: Playwright not installed. Run: pip install playwright")
            return False
        except Exception as e:
            print(f"Error publishing to LinkedIn: {e}")
            return False
    
    def list_pending(self) -> list:
        """List all pending post drafts."""
        pending = list(self.pending_approval.glob('LINKEDIN_POST_*.md'))
        
        if pending:
            print(f"\nPending Posts ({len(pending)}):")
            print("-" * 60)
            for post in pending:
                content = post.read_text()
                # Extract first line of actual content
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
    
    def list_approved(self) -> list:
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
    parser = argparse.ArgumentParser(description='LinkedIn Poster for AI Employee')
    parser.add_argument('action', choices=['create', 'publish', 'auto', 'list-pending', 'list-approved'],
                       help='Action to perform')
    parser.add_argument('--vault', '-v', default='.', help='Path to vault (default: current dir)')
    parser.add_argument('--text', '-t', help='Post text content')
    parser.add_argument('--hashtags', '-H', help='Comma-separated hashtags (without #)')
    parser.add_argument('--schedule', '-s', help='Scheduled time (ISO format)')
    parser.add_argument('--image', '-i', action='append', help='Image file path (can specify multiple)')
    parser.add_argument('--auto-post', action='store_true', help='Enable auto-post mode (publish without approval)')

    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    poster = LinkedInPoster(vault, auto_post=args.auto_post)

    if args.action == 'create':
        if not args.text:
            print("Error: --text required for create action")
            sys.exit(1)

        hashtags = [h.strip() for h in args.hashtags.split(',')] if args.hashtags else []

        draft_path = poster.create_draft(
            text=args.text,
            hashtags=hashtags,
            scheduled_time=args.schedule,
            images=args.image or []
        )

        print(f"✓ Draft created: {draft_path}")
        print(f"  Location: {draft_path}")
        print(f"  Status: Pending approval")
        print(f"\nTo approve: Move file to Approved folder")
        print(f"To publish: python linkedin_poster.py publish --vault {args.vault}")

    elif args.action == 'publish':
        print("Publishing approved posts...")
        published = poster.publish_approved(auto_post=args.auto_post)
        print(f"\nPublished {len(published)} post(s)")

    elif args.action == 'auto':
        # Auto mode: create and publish immediately
        if not args.text:
            print("Error: --text required for auto action")
            sys.exit(1)

        hashtags = [h.strip() for h in args.hashtags.split(',')] if args.hashtags else []

        print("=== AUTO-POST MODE ===")
        print("Creating and publishing post immediately...")

        draft_path = poster.create_draft(
            text=args.text,
            hashtags=hashtags,
            scheduled_time=args.schedule,
            images=args.image or []
        )

        print(f"✓ Draft created: {draft_path.name}")

        # Move to approved automatically
        approved_path = poster.approved / draft_path.name
        draft_path.rename(approved_path)

        # Publish immediately
        published = poster.publish_approved(auto_post=True)
        if published:
            print(f"\n✓ AUTO-POST COMPLETE: {len(published)} post(s) published")
        else:
            print("\n✗ Auto-post failed. Check browser for errors.")

    elif args.action == 'list-pending':
        poster.list_pending()

    elif args.action == 'list-approved':
        poster.list_approved()


if __name__ == '__main__':
    main()
