#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Watcher - Abstract base class for all AI Employee watchers.

Watchers are lightweight Python scripts that run continuously in the background,
monitoring various inputs and creating actionable files for Claude to process.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.
    
    Subclasses must implement:
    - check_for_updates(): Return list of new items to process
    - create_action_file(item): Create .md file in Needs_Action folder
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        
        # Track processed items to avoid duplicates
        self.processed_ids = set()
        
        # Load previously processed IDs from cache file
        self._load_processed_cache()
    
    def _load_processed_cache(self):
        """Load processed IDs from cache file."""
        cache_file = self.vault_path / '.watcher_cache'
        if cache_file.exists():
            try:
                self.processed_ids = set(cache_file.read_text().strip().split('\n'))
            except Exception as e:
                self.logger.warning(f"Could not load cache: {e}")
    
    def _save_processed_cache(self):
        """Save processed IDs to cache file."""
        cache_file = self.vault_path / '.watcher_cache'
        try:
            # Keep only last 1000 IDs to prevent unbounded growth
            ids = list(self.processed_ids)[-1000:]
            cache_file.write_text('\n'.join(ids))
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")
    
    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.
        
        Returns:
            List of new items (each item should have a unique 'id' field)
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown action file for the item.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file
        """
        pass
    
    def run(self):
        """
        Main run loop - continuously monitors and creates action files.
        
        This method runs indefinitely until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    for item in items:
                        item_id = item.get('id', str(item))
                        if item_id not in self.processed_ids:
                            filepath = self.create_action_file(item)
                            self.processed_ids.add(item_id)
                            self.logger.info(f'Created action file: {filepath.name}')
                            self._save_processed_cache()
                except Exception as e:
                    self.logger.error(f'Error processing items: {e}')
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Watcher crashed: {e}')
            raise
    
    def run_once(self) -> int:
        """
        Run a single check cycle (useful for testing or cron jobs).
        
        Returns:
            Number of action files created
        """
        count = 0
        try:
            items = self.check_for_updates()
            for item in items:
                item_id = item.get('id', str(item))
                if item_id not in self.processed_ids:
                    filepath = self.create_action_file(item)
                    self.processed_ids.add(item_id)
                    self.logger.info(f'Created action file: {filepath.name}')
                    count += 1
            self._save_processed_cache()
        except Exception as e:
            self.logger.error(f'Error in run_once: {e}')
        
        return count
