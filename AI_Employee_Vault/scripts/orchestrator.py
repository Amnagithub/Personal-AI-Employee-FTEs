#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Process Needs_Action folder and update Dashboard.

This script scans the /Needs_Action folder, processes action files,
and updates the Dashboard.md with current status.

Usage:
    python orchestrator.py /path/to/vault

Or with Claude Code integration:
    claude "Run the orchestrator to process pending actions"
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class Orchestrator:
    """
    Orchestrates the AI Employee workflow by processing action files
    and maintaining the Dashboard.
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.inbox = self.vault_path / 'Inbox'
        
        # Ensure directories exist
        for d in [self.needs_action, self.done, self.pending_approval, 
                  self.approved, self.rejected, self.inbox]:
            d.mkdir(parents=True, exist_ok=True)
    
    def count_files(self, directory: Path) -> int:
        """Count markdown files in a directory."""
        if not directory.exists():
            return 0
        return len([f for f in directory.iterdir() if f.suffix == '.md'])
    
    def get_pending_items(self) -> List[Dict]:
        """Get list of pending action items."""
        items = []
        if not self.needs_action.exists():
            return items
        
        for filepath in self.needs_action.iterdir():
            if filepath.suffix != '.md':
                continue
            
            content = filepath.read_text()
            
            # Extract metadata from frontmatter
            type_match = re.search(r'type:\s*(\w+)', content)
            priority_match = re.search(r'priority:\s*(\w+)', content)
            source_match = re.search(r'source:\s*(.+)', content)
            
            items.append({
                'path': filepath,
                'name': filepath.stem,
                'type': type_match.group(1) if type_match else 'unknown',
                'priority': priority_match.group(1) if priority_match else 'normal',
                'source': source_match.group(1).strip() if source_match else filepath.name
            })
        
        return sorted(items, key=lambda x: x['priority'], 
                     reverse=True)  # High priority first
    
    def get_approval_items(self) -> List[Path]:
        """Get list of items awaiting approval."""
        if not self.pending_approval.exists():
            return []
        return [f for f in self.pending_approval.iterdir() if f.suffix == '.md']
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        if not self.dashboard.exists():
            self.logger.warning('Dashboard.md not found')
            return
        
        # Count items in each folder
        inbox_count = self.count_files(self.inbox)
        needs_action_count = self.count_files(self.needs_action)
        pending_approval_count = self.count_files(self.pending_approval)
        done_today = 0
        
        # Count files moved to Done today
        if self.done.exists():
            today = datetime.now().strftime('%Y-%m-%d')
            for f in self.done.iterdir():
                if f.suffix == '.md' and today in f.stem:
                    done_today += 1
        
        # Get pending items list
        pending_items = self.get_pending_items()
        approval_items = self.get_approval_items()
        
        # Build the updated dashboard content
        content = f'''---
last_updated: {datetime.now().isoformat()}
status: active
---

# AI Employee Dashboard

## Quick Stats

| Metric | Value |
|--------|-------|
| Pending Items | {needs_action_count} |
| In Progress | 0 |
| Awaiting Approval | {pending_approval_count} |
| Completed Today | {done_today} |

## Inbox Status

<!-- AI Employee will update this section -->
'''
        
        if inbox_count == 0:
            content += '- [ ] No items in Inbox\n'
        else:
            content += f'- [ ] {inbox_count} item(s) in Inbox - needs processing\n'
        
        content += '\n## Needs Action\n\n<!-- Items requiring immediate attention -->\n'
        
        if not pending_items:
            content += '- [ ] No items requiring action\n'
        else:
            for item in pending_items[:10]:  # Show top 10
                content += f'- [ ] **[{item["priority"].upper()}]** {item["source"]}\n'
            if len(pending_items) > 10:
                content += f'- ... and {len(pending_items) - 10} more items\n'
        
        content += '\n## Pending Approvals\n\n<!-- Awaiting human decision -->\n'
        
        if not approval_items:
            content += '- [ ] No pending approvals\n'
        else:
            for item in approval_items:
                content += f'- [ ] {item.stem}\n'
        
        content += '''
## Active Projects

| Project | Status | Next Action |
|---------|--------|-------------|
| (Add projects in Business_Goals.md) | - | - |

## Recent Activity

| Date | Action | Status |
|------|--------|--------|
'''
        
        # Add recent activity from Done folder
        recent_done = []
        if self.done.exists():
            for f in sorted(self.done.iterdir(), reverse=True)[:5]:
                if f.suffix == '.md':
                    recent_done.append({
                        'name': f.stem,
                        'date': f.stat().st_mtime
                    })
        
        if recent_done:
            for item in recent_done:
                date = datetime.fromtimestamp(item['date']).strftime('%Y-%m-%d')
                content += f'| {date} | {item["name"]} | Completed |\n'
        else:
            content += '| - | - | - |\n'
        
        content += f'''
## Notes

> This dashboard is automatically updated by your AI Employee.
> Last processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''
        
        self.dashboard.write_text(content)
        return content
    
    def process_action_files(self) -> Tuple[int, int]:
        """
        Process action files and return counts.
        
        Returns:
            Tuple of (processed_count, moved_to_done)
        """
        processed = 0
        moved = 0
        
        pending_items = self.get_pending_items()
        
        for item in pending_items:
            # Check if this item has been processed (has completion marker)
            content = item['path'].read_text()
            
            # Look for completion markers
            if '[x]' in content and 'Mark this task as complete' in content:
                # Move to Done
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_name = f"{timestamp}_{item['path'].name}"
                dest = self.done / new_name
                item['path'].rename(dest)
                moved += 1
                processed += 1
            else:
                processed += 1
        
        return processed, moved
    
    def run(self, update_dashboard: bool = True) -> Dict:
        """
        Run the orchestrator.
        
        Args:
            update_dashboard: Whether to update Dashboard.md
            
        Returns:
            Dictionary with processing results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'vault_path': str(self.vault_path),
            'inbox_count': self.count_files(self.inbox),
            'needs_action_count': self.count_files(self.needs_action),
            'pending_approval_count': self.count_files(self.pending_approval),
            'processed': 0,
            'moved_to_done': 0
        }
        
        # Process action files
        results['processed'], results['moved_to_done'] = self.process_action_files()
        
        # Update dashboard
        if update_dashboard:
            self.update_dashboard()
        
        return results


def main():
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description='AI Employee Orchestrator'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--no-dashboard',
        action='store_true',
        help='Skip dashboard update'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    orchestrator = Orchestrator(args.vault_path)
    results = orchestrator.run(update_dashboard=not args.no_dashboard)
    
    if args.json:
        print(json.dumps(results, indent=2))
    elif args.verbose:
        print(f"Vault: {results['vault_path']}")
        print(f"Inbox: {results['inbox_count']} files")
        print(f"Needs Action: {results['needs_action_count']} files")
        print(f"Pending Approval: {results['pending_approval_count']} files")
        print(f"Processed: {results['processed']} files")
        print(f"Moved to Done: {results['moved_to_done']} files")
    else:
        print(f"Orchestrator complete. Dashboard updated.")
        print(f"  Inbox: {results['inbox_count']} | Needs Action: {results['needs_action_count']} | Done: {results['moved_to_done']}")


if __name__ == '__main__':
    main()
