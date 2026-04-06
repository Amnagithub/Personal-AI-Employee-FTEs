#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create LinkedIn Post Draft

Creates a LinkedIn post draft in the Pending_Approval folder for human review.

Usage:
    python3 create_draft.py -t "Your post content" -H "AI,Automation,Business" -v ./AI_Employee_Vault
"""

import argparse
import json
from pathlib import Path
from datetime import datetime


def create_draft(text: str, hashtags: list = None, scheduled_time: str = None,
                 images: list = None, vault_path: Path = None) -> Path:
    """
    Create a LinkedIn post draft for approval.

    Args:
        text: Post content
        hashtags: List of hashtags (without #)
        scheduled_time: Optional scheduled publish time
        images: Optional list of image paths
        vault_path: Path to vault (default: current directory)

    Returns:
        Path to created draft file
    """
    if vault_path is None:
        vault_path = Path.cwd()
    else:
        vault_path = Path(vault_path).resolve()

    pending_approval = vault_path / 'Pending_Approval'
    pending_approval.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"LINKEDIN_POST_{timestamp}.md"
    filepath = pending_approval / filename

    # Format hashtags
    hashtag_text = ''
    if hashtags:
        hashtag_text = '\n\n' + ' '.join([f'#{tag}' for tag in hashtags])

    # Full post content (text + hashtags)
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


def main():
    parser = argparse.ArgumentParser(
        description='Create LinkedIn post draft for approval',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 create_draft.py -t "Exciting news about our product!" -H "AI,Automation"
  python3 create_draft.py -t "Post content" -H "AI,Business" -v ./AI_Employee_Vault
        '''
    )
    parser.add_argument('--text', '-t', required=True, help='Post text content')
    parser.add_argument('--hashtags', '-H', help='Comma-separated hashtags (without #)')
    parser.add_argument('--schedule', '-s', help='Scheduled time (ISO format)')
    parser.add_argument('--image', '-i', action='append', help='Image file path (can specify multiple)')
    parser.add_argument('--vault', '-v', default='.', help='Path to vault (default: current dir)')

    args = parser.parse_args()

    hashtags = [h.strip() for h in args.hashtags.split(',')] if args.hashtags else []

    draft_path = create_draft(
        text=args.text,
        hashtags=hashtags,
        scheduled_time=args.schedule,
        images=args.image or [],
        vault_path=args.vault
    )

    print(f"✓ Draft created: {draft_path.name}")
    print(f"  Location: {draft_path}")
    print(f"  Status: Pending approval")
    print(f"\nTo approve: Move file to Approved folder")
    print(f"To publish: python3 publish.py --vault {args.vault}")


if __name__ == '__main__':
    main()
