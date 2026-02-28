#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

This watcher monitors the /Inbox folder for new files dropped by the user.
When a new file is detected, it creates an action file in /Needs_Action
for the AI Employee to process.

Usage:
    python filesystem_watcher.py /path/to/vault

Or run once (for cron jobs):
    python filesystem_watcher.py /path/to/vault --once
"""

import sys
import hashlib
import logging
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class FileDropHandler(FileSystemEventHandler):
    """Handle file system events for dropped files."""
    
    def __init__(self, watcher):
        self.watcher = watcher
    
    def on_created(self, event):
        if event.is_directory:
            return
        self.watcher.process_new_file(Path(event.src_path))


class FilesystemWatcher(BaseWatcher):
    """
    Watcher that monitors the Inbox folder for new files.
    
    When a file is added to /Inbox, creates an action file in /Needs_Action
    with metadata about the dropped file.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.observer = None
    
    def _file_hash(self, filepath: Path) -> str:
        """Generate a unique hash for a file based on name, size, and mtime."""
        try:
            stat = filepath.stat()
            content = f"{filepath.name}:{stat.st_size}:{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return str(filepath)
    
    def check_for_updates(self) -> list:
        """
        Check the Inbox folder for new files.
        
        Returns:
            List of file info dictionaries for new files
        """
        new_files = []
        
        if not self.inbox.exists():
            return new_files
        
        for filepath in self.inbox.iterdir():
            if filepath.is_file() and not filepath.name.startswith('.'):
                file_hash = self._file_hash(filepath)
                if file_hash not in self.processed_ids:
                    new_files.append({
                        'id': file_hash,
                        'path': str(filepath),
                        'name': filepath.name,
                        'size': filepath.stat().st_size,
                        'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                    })
        
        return new_files
    
    def create_action_file(self, item) -> Path:
        """
        Create a markdown action file for the dropped file.
        
        Args:
            item: File info dictionary
            
        Returns:
            Path to the created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = Path(item['name']).stem.replace(' ', '_')
        filename = f"FILE_DROP_{safe_name}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        content = f'''---
type: file_drop
source: {item['name']}
size: {item['size']} bytes
received: {datetime.now().isoformat()}
priority: normal
status: pending
---

# File Drop Received

A new file has been dropped into the Inbox for processing.

## File Details

- **Original Name:** {item['name']}
- **Size:** {item['size']} bytes
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Location:** `{item['path']}`

## Content Preview

<!-- AI Employee: Read the file and summarize its contents here -->

## Suggested Actions

- [ ] Read and understand the file content
- [ ] Categorize the file (document, image, data, etc.)
- [ ] Take appropriate action based on content
- [ ] Move original file to appropriate archive folder
- [ ] Mark this task as complete when done

## Notes

<!-- Add any additional notes or context here -->

'''
        filepath.write_text(content)
        return filepath
    
    def process_new_file(self, filepath: Path):
        """Process a newly created file (called by event handler)."""
        if filepath.parent != self.inbox:
            return
        
        if filepath.name.startswith('.'):
            return
        
        try:
            file_hash = self._file_hash(filepath)
            if file_hash not in self.processed_ids:
                item = {
                    'id': file_hash,
                    'path': str(filepath),
                    'name': filepath.name,
                    'size': filepath.stat().st_size,
                    'modified': datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                }
                action_file = self.create_action_file(item)
                self.processed_ids.add(file_hash)
                self._save_processed_cache()
                self.logger.info(f'Processed new file: {filepath.name} -> {action_file.name}')
        except Exception as e:
            self.logger.error(f'Error processing new file: {e}')
    
    def run(self):
        """Run the watcher with event-based monitoring."""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        
        # First, process any existing files in Inbox
        self.logger.info('Processing existing files in Inbox...')
        self.run_once()
        
        # Then start event-based monitoring
        event_handler = FileDropHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.inbox), recursive=False)
        self.observer.start()
        self.logger.info(f'Watching {self.inbox} for new files...')
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Stopping file watcher...')
            self.observer.stop()
        except Exception as e:
            self.logger.error(f'Watcher crashed: {e}')
            self.observer.stop()
            raise
        
        self.observer.join()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='File System Watcher for AI Employee'
    )
    parser.add_argument(
        'vault_path',
        help='Path to the Obsidian vault'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for cron jobs)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    watcher = FilesystemWatcher(args.vault_path, args.interval)
    
    if args.once:
        count = watcher.run_once()
        print(f'Processed {count} new file(s)')
        sys.exit(0)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
