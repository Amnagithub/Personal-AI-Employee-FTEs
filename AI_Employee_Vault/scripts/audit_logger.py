#!/usr/bin/env python3
"""
Comprehensive Audit Logging System

Logs all AI Employee actions with timestamps, actors, targets, and results.
Provides query and reporting capabilities.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger('audit_logger')

class ActionType(Enum):
    """Types of actions that can be logged"""
    EMAIL_READ = "email_read"
    EMAIL_SENT = "email_sent"
    EMAIL_DRAFTED = "email_draft"
    WHATSAPP_RECEIVED = "whatsapp_received"
    WHATSAPP_SENT = "whatsapp_sent"
    FACEBOOK_POST = "facebook_post"
    INSTAGRAM_POST = "instagram_post"
    ODOO_INVOICE_CREATED = "odoo_invoice_created"
    ODOO_INVOICE_VALIDATED = "odoo_invoice_validated"
    ODOO_PAYMENT_REGISTERED = "odoo_payment_registered"
    ODOO_CONTACT_CREATED = "odoo_contact_created"
    FILE_PROCESSED = "file_processed"
    TASK_COMPLETED = "task_completed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_DENIED = "approval_denied"
    RALPH_ITERATION = "ralph_iteration"
    CEO_BRIEFING_GENERATED = "ceo_briefing_generated"
    SYSTEM_ERROR = "system_error"
    WATCHER_STARTED = "watcher_started"
    WATCHER_STOPPED = "watcher_stopped"

@dataclass
class AuditLogEntry:
    """Represents a single audit log entry"""
    timestamp: str
    action_type: str
    actor: str
    target: str
    parameters: Dict
    approval_status: str
    approved_by: str
    result: str
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.logs_path = vault_path / 'Logs'
        self.logs_path.mkdir(exist_ok=True)
        
        # Ensure logs are retained for 90 days minimum
        self.retention_days = 90
    
    def log_action(self, action_type: ActionType, actor: str, target: str,
                  parameters: Dict = None, approval_status: str = 'auto',
                  approved_by: str = 'system', result: str = 'success',
                  error_message: str = None, metadata: Dict = None) -> Path:
        """
        Log an action to the audit log
        
        Args:
            action_type: Type of action (enum)
            actor: Who/what performed the action (e.g., 'qwen_code', 'gmail_watcher')
            target: What was acted upon (e.g., email address, file path)
            parameters: Parameters of the action
            approval_status: 'auto', 'approved', 'denied', 'pending'
            approved_by: Who approved the action (if applicable)
            result: 'success', 'failure', 'partial'
            error_message: Error details if result is failure
            metadata: Additional context
        """
        
        entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            action_type=action_type.value,
            actor=actor,
            target=target,
            parameters=parameters or {},
            approval_status=approval_status,
            approved_by=approved_by,
            result=result,
            error_message=error_message,
            metadata=metadata
        )
        
        # Write to today's log file
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_path / f'{today}.json'
        
        # Load existing logs or create new file
        existing_logs = []
        if log_file.exists():
            try:
                existing_logs = json.loads(log_file.read_text())
            except:
                existing_logs = []
        
        # Append new entry
        existing_logs.append(asdict(entry))
        
        # Write back
        log_file.write_text(json.dumps(existing_logs, indent=2))
        
        logger.info(f'📝 Audit log: {action_type.value} by {actor} → {result}')
        
        return log_file
    
    def get_logs(self, date_from: datetime = None, date_to: datetime = None,
                action_type: ActionType = None, actor: str = None,
                result: str = None) -> List[Dict]:
        """
        Query audit logs with filters
        
        Args:
            date_from: Start date
            date_to: End date
            action_type: Filter by action type
            actor: Filter by actor
            result: Filter by result ('success', 'failure', etc.)
        """
        
        if not date_from:
            date_from = datetime.now() - timedelta(days=self.retention_days)
        if not date_to:
            date_to = datetime.now()
        
        filtered_logs = []
        
        # Iterate through log files in date range
        current_date = date_from
        while current_date <= date_to:
            log_file = self.logs_path / f'{current_date.strftime("%Y-%m-%d")}.json'
            
            if log_file.exists():
                try:
                    day_logs = json.loads(log_file.read_text())
                    
                    # Apply filters
                    for entry in day_logs:
                        if action_type and entry.get('action_type') != action_type.value:
                            continue
                        if actor and entry.get('actor') != actor:
                            continue
                        if result and entry.get('result') != result:
                            continue
                        
                        filtered_logs.append(entry)
                
                except Exception as e:
                    logger.error(f'Error reading {log_file}: {e}')
            
            current_date += timedelta(days=1)
        
        return filtered_logs
    
    def generate_summary(self, date_from: datetime = None, 
                        date_to: datetime = None) -> Dict:
        """
        Generate summary statistics for a period
        
        Returns:
            Dictionary with summary statistics
        """
        
        logs = self.get_logs(date_from, date_to)
        
        summary = {
            'period': {
                'from': date_from.isoformat() if date_from else None,
                'to': date_to.isoformat() if date_to else None
            },
            'total_actions': len(logs),
            'by_result': {
                'success': 0,
                'failure': 0,
                'partial': 0
            },
            'by_actor': {},
            'by_action_type': {},
            'approval_stats': {
                'auto': 0,
                'approved': 0,
                'denied': 0,
                'pending': 0
            },
            'errors': []
        }
        
        for entry in logs:
            # Count by result
            result = entry.get('result', 'unknown')
            if result in summary['by_result']:
                summary['by_result'][result] += 1
            
            # Count by actor
            actor = entry.get('actor', 'unknown')
            summary['by_actor'][actor] = summary['by_actor'].get(actor, 0) + 1
            
            # Count by action type
            action_type = entry.get('action_type', 'unknown')
            summary['by_action_type'][action_type] = summary['by_action_type'].get(action_type, 0) + 1
            
            # Count by approval status
            approval = entry.get('approval_status', 'unknown')
            if approval in summary['approval_stats']:
                summary['approval_stats'][approval] += 1
            
            # Collect errors
            if entry.get('error_message'):
                summary['errors'].append({
                    'timestamp': entry.get('timestamp'),
                    'action_type': entry.get('action_type'),
                    'error': entry.get('error_message')
                })
        
        return summary
    
    def generate_report(self, date_from: datetime = None,
                       date_to: datetime = None) -> str:
        """Generate a human-readable audit report"""
        
        summary = self.generate_summary(date_from, date_to)
        
        # Format report
        report = f"""# AI Employee Audit Report

## Period
{summary['period']['from']} to {summary['period']['to']}

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Actions** | {summary['total_actions']} |
| **Successful** | {summary['by_result']['success']} |
| **Failed** | {summary['by_result']['failure']} |
| **Partial** | {summary['by_result']['partial']} |

## Actions by Actor

| Actor | Count |
|-------|-------|
"""
        
        for actor, count in summary['by_actor'].items():
            report += f"| {actor} | {count} |\n"
        
        report += """
## Actions by Type

| Action Type | Count |
|-------------|-------|
"""
        
        for action_type, count in summary['by_action_type'].items():
            report += f"| {action_type} | {count} |\n"
        
        report += f"""
## Approval Statistics

| Status | Count |
|--------|-------|
| Auto | {summary['approval_stats']['auto']} |
| Approved | {summary['approval_stats']['approved']} |
| Denied | {summary['approval_stats']['denied']} |
| Pending | {summary['approval_stats']['pending']} |

## Success Rate

{self._calculate_success_rate(summary)}

## Errors ({len(summary['errors'])})

"""
        
        if summary['errors']:
            for error in summary['errors'][:10]:  # Show max 10 errors
                report += f"- **{error['timestamp']}** ({error['action_type']}): {error['error']}\n"
        else:
            report += "No errors recorded ✅\n"
        
        report += """
---
*Generated by AI Employee Audit System v1.0*
"""
        
        return report
    
    def _calculate_success_rate(self, summary: Dict) -> str:
        """Calculate success rate percentage"""
        total = summary['total_actions']
        if total == 0:
            return "N/A"
        
        success = summary['by_result']['success']
        rate = (success / total) * 100
        
        if rate >= 95:
            return f"{rate:.1f}% ✅ Excellent"
        elif rate >= 90:
            return f"{rate:.1f}% ✅ Good"
        elif rate >= 80:
            return f"{rate:.1f}% ⚠️ Acceptable"
        else:
            return f"{rate:.1f}% 🔴 Needs Improvement"
    
    def cleanup_old_logs(self):
        """Remove logs older than retention period"""
        logger.info(f'🧹 Cleaning up logs older than {self.retention_days} days...')
        
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        for log_file in self.logs_path.glob('*.json'):
            # Extract date from filename
            try:
                file_date_str = log_file.stem
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f'   Deleted: {log_file.name}')
            
            except ValueError:
                # Skip files with invalid date format
                continue
        
        logger.info(f'   Cleanup complete. Deleted {deleted_count} files')
    
    def export_logs(self, output_file: Path, date_from: datetime = None,
                   date_to: datetime = None):
        """Export logs to a file for backup or analysis"""
        
        logs = self.get_logs(date_from, date_to)
        
        output_file.write_text(json.dumps(logs, indent=2))
        
        logger.info(f'📦 Exported {len(logs)} logs to {output_file}')


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Audit Logger')
    parser.add_argument('--vault', type=Path, default=Path.cwd(),
                       help='Path to AI Employee Vault')
    parser.add_argument('--action', choices=['summary', 'report', 'cleanup', 'export'],
                       default='summary', help='Action to perform')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days to analyze (default: 7)')
    parser.add_argument('--output', type=Path,
                       help='Output file for export')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize logger
    audit = AuditLogger(args.vault)
    
    date_from = datetime.now() - timedelta(days=args.days)
    date_to = datetime.now()
    
    if args.action == 'summary':
        summary = audit.generate_summary(date_from, date_to)
        print(json.dumps(summary, indent=2))
    
    elif args.action == 'report':
        report = audit.generate_report(date_from, date_to)
        print(report)
    
    elif args.action == 'cleanup':
        audit.cleanup_old_logs()
    
    elif args.action == 'export':
        if not args.output:
            parser.error('--output required for export action')
        audit.export_logs(args.output, date_from, date_to)


if __name__ == '__main__':
    main()
