#!/usr/bin/env python3
"""
Master Orchestrator for AI Employee - Gold Tier

Coordinates all watchers, MCP servers, and autonomous tasks:
1. Starts and monitors all watcher processes
2. Schedules recurring tasks (daily briefing, weekly audit)
3. Manages MCP server lifecycle
4. Handles error recovery and graceful degradation
5. Integrates with Ralph Wiggum Loop for autonomous operation
"""

import subprocess
import time
import signal
import sys
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import schedule  # Requires: pip install schedule

logger = logging.getLogger('orchestrator')

class ProcessManager:
    """Manages watcher and MCP server processes"""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.restart_count: Dict[str, int] = {}
        self.max_restarts = 5
    
    def start_process(self, name: str, cmd: List[str], 
                     restart_on_failure: bool = True) -> bool:
        """Start a background process"""
        try:
            logger.info(f'🚀 Starting {name}...')
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(Path.cwd())
            )
            
            self.processes[name] = process
            self.restart_count[name] = 0
            
            logger.info(f'   {name} started with PID {process.pid}')
            return True
            
        except Exception as e:
            logger.error(f'❌ Failed to start {name}: {e}')
            return False
    
    def check_process(self, name: str) -> bool:
        """Check if a process is still running"""
        process = self.processes.get(name)
        if not process:
            return False
        
        return process.poll() is None
    
    def restart_process(self, name: str, cmd: List[str]) -> bool:
        """Restart a failed process"""
        if self.restart_count.get(name, 0) >= self.max_restarts:
            logger.error(f'⚠️ Max restarts reached for {name}')
            return False
        
        self.restart_count[name] = self.restart_count.get(name, 0) + 1
        logger.info(f'🔄 Restarting {name} (attempt {self.restart_count[name]})')
        
        return self.start_process(name, cmd)
    
    def stop_process(self, name: str):
        """Stop a process"""
        process = self.processes.get(name)
        if process:
            logger.info(f'🛑 Stopping {name}...')
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            del self.processes[name]
    
    def stop_all(self):
        """Stop all managed processes"""
        logger.info('🛑 Stopping all processes...')
        for name in list(self.processes.keys()):
            self.stop_process(name)


class Orchestrator:
    """Main orchestrator for AI Employee"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.process_manager = ProcessManager()
        self.running = False
        
        # Paths
        self.scripts_path = vault_path / 'scripts'
        self.skills_path = Path(__file__).parent.parent.parent / '.qwen' / 'skills'
        
        # Audit logger
        sys.path.insert(0, str(self.scripts_path))
        from audit_logger import AuditLogger, ActionType
        self.audit = AuditLogger(vault_path)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f'\n📍 Received signal {signum}, shutting down gracefully...')
        self.stop()
        sys.exit(0)
    
    def start_watchers(self):
        """Start all watcher processes"""
        logger.info('\n' + '='*60)
        logger.info('👁️ Starting Watchers')
        logger.info('='*60)
        
        # Gmail Watcher
        self.process_manager.start_process(
            'gmail_watcher',
            ['python', str(self.scripts_path / 'watchers' / 'gmail_watcher.py'), 
             str(self.vault_path), '--interval', '120']
        )
        
        # WhatsApp Watcher
        self.process_manager.start_process(
            'whatsapp_watcher',
            ['python', str(self.scripts_path / 'watchers' / 'whatsapp_watcher.py'),
             str(self.vault_path), '--interval', '30']
        )
        
        # Filesystem Watcher
        self.process_manager.start_process(
            'filesystem_watcher',
            ['python', str(self.scripts_path / 'watchers' / 'filesystem_watcher.py'),
             str(self.vault_path)]
        )
        
        # Log watcher starts
        self.audit.log_action(
            action_type='watcher_started',
            actor='orchestrator',
            target='all_watchers',
            parameters={'watchers': ['gmail', 'whatsapp', 'filesystem']},
            result='success'
        )
    
    def start_mcp_servers(self):
        """Start all MCP servers"""
        logger.info('\n' + '='*60)
        logger.info('🔌 Starting MCP Servers')
        logger.info('='*60)
        
        # Odoo MCP Server
        self.process_manager.start_process(
            'odoo_mcp',
            ['python', str(self.skills_path / 'odoo-mcp' / 'scripts' / 'odoo_mcp_server.py'),
             '--port', '8810']
        )
        
        # Facebook MCP Server
        self.process_manager.start_process(
            'facebook_mcp',
            ['python', str(self.skills_path / 'facebook-mcp' / 'scripts' / 'facebook_mcp_server.py'),
             '--port', '8811']
        )
        
        # Email MCP Server (from Silver Tier)
        email_mcp_script = self.skills_path / 'email-mcp' / 'scripts' / 'mcp-client.py'
        if email_mcp_script.exists():
            self.process_manager.start_process(
                'email_mcp',
                ['python', str(email_mcp_script), 'server', '--port', '8809']
            )
        
        logger.info('✅ All MCP servers started')
    
    def start_odoo(self):
        """Start Odoo ERP via Docker Compose"""
        logger.info('\n' + '='*60)
        logger.info('🏢 Starting Odoo Community Edition')
        logger.info('='*60)
        
        odoo_path = self.vault_path / 'odoo'
        docker_compose = odoo_path / 'docker-compose.yml'
        
        if not docker_compose.exists():
            logger.warning('⚠️ Odoo docker-compose.yml not found, skipping')
            return
        
        try:
            # Check if Odoo is already running
            result = subprocess.run(
                ['docker', 'ps', '--filter', 'name=odoo_community', '--format', '{{.Names}}'],
                capture_output=True,
                text=True
            )
            
            if 'odoo_community' in result.stdout:
                logger.info('✅ Odoo is already running')
            else:
                logger.info('🚀 Starting Odoo with Docker Compose...')
                subprocess.run(
                    ['docker-compose', 'up', '-d'],
                    cwd=str(odoo_path),
                    check=True
                )
                logger.info('✅ Odoo started successfully')
                
                self.audit.log_action(
                    action_type='system_error',  # Using generic type for system operations
                    actor='orchestrator',
                    target='odoo',
                    parameters={'action': 'start'},
                    result='success'
                )
        
        except Exception as e:
            logger.error(f'❌ Failed to start Odoo: {e}')
            self.audit.log_action(
                action_type='system_error',
                actor='orchestrator',
                target='odoo',
                parameters={'action': 'start'},
                result='failure',
                error_message=str(e)
            )
    
    def schedule_tasks(self):
        """Schedule recurring tasks"""
        logger.info('\n' + '='*60)
        logger.info('⏰ Scheduling Recurring Tasks')
        logger.info('='*60)
        
        # Daily Briefing at 8:00 AM
        schedule.every().day.at("08:00").do(self._run_daily_briefing)
        logger.info('   📅 Daily briefing scheduled for 8:00 AM')
        
        # Weekly CEO Briefing on Monday at 9:00 AM
        schedule.every().monday.at("09:00").do(self._run_weekly_briefing)
        logger.info('   📊 Weekly CEO briefing scheduled for Monday 9:00 AM')
        
        # Weekly audit on Sunday at 11:00 PM
        schedule.every().sunday.at("23:00").do(self._run_weekly_audit)
        logger.info('   🔍 Weekly audit scheduled for Sunday 11:00 PM')
        
        # Log cleanup daily at midnight
        schedule.every().day.at("00:00").do(self._run_log_cleanup)
        logger.info('   🧹 Log cleanup scheduled for midnight')
        
        # Health check every 5 minutes
        schedule.every(5).minutes.do(self._run_health_check)
        logger.info('   💓 Health check scheduled every 5 minutes')
    
    def _run_daily_briefing(self):
        """Run daily briefing task"""
        logger.info('\n📋 Running daily briefing...')
        
        try:
            # Use Ralph Wiggum Loop for autonomous operation
            from ralph_wiggum import RalphWiggumLoop
            
            prompt = """
            Generate daily briefing report:
            1. Check Needs_Action folder for pending items
            2. Review Done folder for completed tasks
            3. Check Pending_Approval for items requiring attention
            4. Update Dashboard.md with current status
            
            Output <promise>BRIEFING_COMPLETE</promise> when done.
            """
            
            loop = RalphWiggumLoop(
                prompt=prompt,
                max_iterations=5,
                completion_promise='BRIEFING_COMPLETE'
            )
            
            success = loop.run()
            
            self.audit.log_action(
                action_type='task_completed',
                actor='orchestrator',
                target='daily_briefing',
                result='success' if success else 'partial'
            )
        
        except Exception as e:
            logger.error(f'❌ Daily briefing failed: {e}')
            self.audit.log_action(
                action_type='system_error',
                actor='orchestrator',
                target='daily_briefing',
                result='failure',
                error_message=str(e)
            )
    
    def _run_weekly_briefing(self):
        """Run weekly CEO briefing"""
        logger.info('\n📊 Running weekly CEO briefing...')
        
        try:
            # Run CEO briefing script
            result = subprocess.run(
                ['python', str(self.scripts_path / 'ceo_briefing.py'),
                 '--vault', str(self.vault_path), '--verbose'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info('✅ Weekly CEO briefing generated')
                self.audit.log_action(
                    action_type='ceo_briefing_generated',
                    actor='orchestrator',
                    target='weekly_briefing',
                    result='success'
                )
            else:
                logger.error(f'❌ CEO briefing failed: {result.stderr}')
                self.audit.log_action(
                    action_type='system_error',
                    actor='orchestrator',
                    target='weekly_briefing',
                    result='failure',
                    error_message=result.stderr
                )
        
        except Exception as e:
            logger.error(f'❌ Weekly briefing failed: {e}')
            self.audit.log_action(
                action_type='system_error',
                actor='orchestrator',
                target='weekly_briefing',
                result='failure',
                error_message=str(e)
            )
    
    def _run_weekly_audit(self):
        """Run weekly audit"""
        logger.info('\n🔍 Running weekly audit...')
        
        try:
            # Run audit logger report
            from audit_logger import AuditLogger
            
            audit = AuditLogger(self.vault_path)
            report = audit.generate_report(
                date_from=datetime.now() - timedelta(days=7),
                date_to=datetime.now()
            )
            
            # Save report
            report_path = self.vault_path / 'Logs' / 'weekly_audit.md'
            report_path.write_text(report)
            
            logger.info(f'✅ Weekly audit saved to {report_path}')
            self.audit.log_action(
                action_type='task_completed',
                actor='orchestrator',
                target='weekly_audit',
                result='success'
            )
        
        except Exception as e:
            logger.error(f'❌ Weekly audit failed: {e}')
            self.audit.log_action(
                action_type='system_error',
                actor='orchestrator',
                target='weekly_audit',
                result='failure',
                error_message=str(e)
            )
    
    def _run_log_cleanup(self):
        """Run log cleanup"""
        logger.info('\n🧹 Running log cleanup...')
        
        try:
            from audit_logger import AuditLogger
            
            audit = AuditLogger(self.vault_path)
            audit.cleanup_old_logs()
            
            self.audit.log_action(
                action_type='task_completed',
                actor='orchestrator',
                target='log_cleanup',
                result='success'
            )
        
        except Exception as e:
            logger.error(f'❌ Log cleanup failed: {e}')
    
    def _run_health_check(self):
        """Run health check on all processes"""
        logger.debug('💓 Running health check...')
        
        unhealthy = []
        
        for name in list(self.process_manager.processes.keys()):
            if not self.process_manager.check_process(name):
                logger.warning(f'⚠️ {name} is not running')
                unhealthy.append(name)
        
        if unhealthy:
            logger.warning(f'🔴 Unhealthy processes: {", ".join(unhealthy)}')
            
            # Attempt restart
            for name in unhealthy:
                cmd = self._get_process_command(name)
                if cmd:
                    self.process_manager.restart_process(name, cmd)
    
    def _get_process_command(self, name: str) -> Optional[List[str]]:
        """Get command for a process"""
        commands = {
            'gmail_watcher': ['python', str(self.scripts_path / 'watchers' / 'gmail_watcher.py'),
                            str(self.vault_path), '--interval', '120'],
            'whatsapp_watcher': ['python', str(self.scripts_path / 'watchers' / 'whatsapp_watcher.py'),
                               str(self.vault_path), '--interval', '30'],
            'filesystem_watcher': ['python', str(self.scripts_path / 'watchers' / 'filesystem_watcher.py'),
                                  str(self.vault_path)],
            'odoo_mcp': ['python', str(self.skills_path / 'odoo-mcp' / 'scripts' / 'odoo_mcp_server.py'),
                        '--port', '8810'],
            'facebook_mcp': ['python', str(self.skills_path / 'facebook-mcp' / 'scripts' / 'facebook_mcp_server.py'),
                           '--port', '8811']
        }
        return commands.get(name)
    
    def run_pending_tasks(self):
        """Run pending scheduled tasks"""
        schedule.run_pending()
    
    def start(self):
        """Start the orchestrator"""
        logger.info('\n' + '='*60)
        logger.info('🤖 AI Employee Orchestrator - Gold Tier')
        logger.info('='*60)
        logger.info(f'   Vault: {self.vault_path}')
        logger.info(f'   Started: {datetime.now().isoformat()}')
        logger.info('='*60 + '\n')
        
        self.running = True
        
        # Start Odoo
        self.start_odoo()
        
        # Wait for Odoo to be ready
        logger.info('⏳ Waiting for Odoo to be ready...')
        time.sleep(10)
        
        # Start MCP servers
        self.start_mcp_servers()
        
        # Start watchers
        self.start_watchers()
        
        # Schedule recurring tasks
        self.schedule_tasks()
        
        # Main loop
        logger.info('\n' + '='*60)
        logger.info('🔄 Orchestrator running. Press Ctrl+C to stop.')
        logger.info('='*60 + '\n')
        
        try:
            while self.running:
                self.run_pending_tasks()
                time.sleep(60)  # Check every minute
        
        except KeyboardInterrupt:
            logger.info('\n📍 Keyboard interrupt received')
        finally:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator"""
        logger.info('\n🛑 Stopping orchestrator...')
        self.running = False
        
        # Stop all processes
        self.process_manager.stop_all()
        
        logger.info('✅ Orchestrator stopped')
        
        self.audit.log_action(
            action_type='watcher_stopped',
            actor='orchestrator',
            target='all_processes',
            result='success'
        )


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument('--vault', type=Path, default=Path.cwd(),
                       help='Path to AI Employee Vault')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start orchestrator
    orchestrator = Orchestrator(args.vault)
    orchestrator.start()


if __name__ == '__main__':
    main()
