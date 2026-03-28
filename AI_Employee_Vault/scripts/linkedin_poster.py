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
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.pending_approval = vault_path / 'Pending_Approval'
        self.approved = vault_path / 'Approved'
        self.done = vault_path / 'Done'
        
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
        filepath.write_text(content)
        return filepath
    
    def publish_approved(self) -> list:
        """
        Publish all approved posts.
        
        Returns:
            List of published post paths
        """
        published = []
        
        # Get all approved posts
        approved_posts = list(self.approved.glob('LINKEDIN_POST_*.md'))
        
        if not approved_posts:
            print("No approved posts to publish.")
            return published
        
        print(f"Found {len(approved_posts)} approved post(s) to publish.")
        
        for post_path in approved_posts:
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
            
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    user_data_dir=str(Path.home() / '.ai_employee' / 'linkedin_session')
                )
                page = context.new_page()
                
                # Go to LinkedIn
                print("Navigating to LinkedIn...")
                page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
                
                # Wait for page to load
                page.wait_for_timeout(5000)
                
                # Check if logged in
                if 'login' in page.url:
                    print("Not logged in. Please log in to LinkedIn manually.")
                    print("Waiting for login...")
                    
                    # Wait for user to log in
                    for i in range(60):  # Wait up to 2 minutes
                        page.wait_for_timeout(2000)
                        if 'feed' in page.url:
                            print("✓ Logged in successfully")
                            break
                    else:
                        print("✗ Login timeout")
                        browser.close()
                        return False
                
                # Find and click the post creation box
                print("Creating new post...")
                
                # Try to find the post creation input
                try:
                    # Click on the "Start a post" box
                    page.click('div[role="button"]:has-text("Start a post")', timeout=10000)
                except:
                    # Alternative selector
                    try:
                        page.click('button:has-text("Start a post")', timeout=10000)
                    except:
                        print("Could not find post creation button. Manual intervention may be required.")
                        browser.close()
                        return False
                
                # Wait for post dialog to appear
                page.wait_for_timeout(2000)
                
                # Find the text input and fill it
                print("Writing post content...")
                
                # LinkedIn uses a contenteditable div for the post text
                try:
                    # Fill the post text
                    editable = page.locator('div[contenteditable="true"][role="textbox"]').first
                    editable.fill(text[:3000])  # LinkedIn limit
                    
                    # Wait for text to be entered
                    page.wait_for_timeout(1000)
                    
                    # Click Post button
                    print("Publishing post...")
                    post_button = page.locator('button:has-text("Post")').first
                    post_button.click()
                    
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
    parser.add_argument('action', choices=['create', 'publish', 'list-pending', 'list-approved'],
                       help='Action to perform')
    parser.add_argument('--vault', '-v', default='.', help='Path to vault (default: current dir)')
    parser.add_argument('--text', '-t', help='Post text content')
    parser.add_argument('--hashtags', '-H', help='Comma-separated hashtags (without #)')
    parser.add_argument('--schedule', '-s', help='Scheduled time (ISO format)')
    parser.add_argument('--image', '-i', action='append', help='Image file path (can specify multiple)')
    
    args = parser.parse_args()
    
    vault = Path(args.vault).resolve()
    poster = LinkedInPoster(vault)
    
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
        published = poster.publish_approved()
        print(f"\nPublished {len(published)} post(s)")
        
    elif args.action == 'list-pending':
        poster.list_pending()
        
    elif args.action == 'list-approved':
        poster.list_approved()


if __name__ == '__main__':
    main()
