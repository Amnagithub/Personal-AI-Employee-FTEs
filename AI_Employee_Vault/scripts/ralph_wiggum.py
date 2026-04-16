#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Autonomous Multi-Step Task Completion

This script keeps Qwen Code working on a task until completion by:
1. Intercepting exit attempts
2. Checking completion criteria
3. Re-injecting the prompt if not complete
"""

import subprocess
import time
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

logger = logging.getLogger('ralph_wiggum')

class RalphWiggumLoop:
    """Implements the Ralph Wiggum pattern for autonomous task completion"""
    
    def __init__(self, prompt, max_iterations=10, 
                 completion_promise=None, completion_file=None, timeout=300):
        """
        Initialize Ralph Wiggum Loop
        
        Args:
            prompt: The task to complete
            max_iterations: Maximum number of iterations before forcing stop
            completion_promise: String Qwen outputs to signal completion
            completion_file: File that appears when task is complete
            timeout: Timeout per iteration in seconds
        """
        self.prompt = prompt
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise
        self.completion_file = Path(completion_file) if completion_file else None
        self.timeout = timeout
        self.iteration = 0
        self.state_file = Path('/tmp/ralph_state.json')
        
        # Vault paths
        self.vault_path = Path.cwd()
        self.done_path = self.vault_path / 'Done'
        self.needs_action_path = self.vault_path / 'Needs_Action'
    
    def check_completion(self, output):
        """Check if task is complete"""
        
        # Strategy 1: Promise-based
        if self.completion_promise:
            if f'<promise>{self.completion_promise}</promise>' in output:
                logger.info('✅ Completion promise detected')
                return True
        
        # Strategy 2: File movement detection
        if self.needs_action_path.exists():
            remaining_files = list(self.needs_action_path.glob('*.md'))
            if len(remaining_files) == 0:
                logger.info('✅ All files moved to Done')
                return True
        
        # Strategy 3: Completion file
        if self.completion_file and self.completion_file.exists():
            logger.info('✅ Completion file detected')
            return True
        
        return False
    
    def save_state(self, status='running', extra=None):
        """Save current state to file"""
        state = {
            'iteration': self.iteration,
            'max_iterations': self.max_iterations,
            'status': status,
            'start_time': getattr(self, 'start_time', datetime.now().isoformat()),
            'last_update': datetime.now().isoformat(),
            'prompt': self.prompt[:200]  # Truncate for readability
        }
        if extra:
            state.update(extra)
        
        self.state_file.write_text(json.dumps(state, indent=2))
    
    def run(self):
        """Execute the Ralph loop"""
        self.start_time = datetime.now().isoformat()
        logger.info(f'🚀 Starting Ralph Wiggum Loop')
        logger.info(f'   Max iterations: {self.max_iterations}')
        logger.info(f'   Completion promise: {self.completion_promise}')
        logger.info(f'   Prompt: {self.prompt[:100]}...')
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            logger.info(f'\n{"="*60}')
            logger.info(f'📍 Iteration {self.iteration}/{self.max_iterations}')
            logger.info(f'{"="*60}')
            
            # Save state
            self.save_state('running')
            
            try:
                # Run Qwen Code
                logger.info('🤖 Running Qwen Code...')
                result = subprocess.run(
                    ['qwen', '--prompt', self.prompt],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=str(self.vault_path)
                )
                
                output = result.stdout
                logger.info(f'   Output length: {len(output)} chars')
                
                # Check completion
                if self.check_completion(output):
                    logger.info('\n🎉 Task complete!')
                    self.save_state('complete', {
                        'end_time': datetime.now().isoformat(),
                        'iterations_used': self.iteration
                    })
                    return True
                
                # Check for errors
                if result.returncode != 0:
                    logger.warning(f'⚠️ Qwen exited with code {result.returncode}')
                    error_msg = result.stderr[:500] if result.stderr else 'Unknown error'
                    logger.warning(f'   Error: {error_msg}')
                    
                    # Add error to prompt for retry
                    self.prompt += f'\n\nPrevious attempt encountered an error: {error_msg}. Please retry with error handling.'
                
                # Not complete, continue loop
                if self.iteration < self.max_iterations:
                    self.prompt += '\n\nTask not yet complete. Continue working on the remaining items.'
                
            except subprocess.TimeoutExpired:
                logger.warning(f'⏱️ Iteration {self.iteration} timed out after {self.timeout}s')
                self.prompt += '\n\nPrevious iteration timed out. Please work more efficiently.'
            
            except Exception as e:
                logger.error(f'❌ Unexpected error: {e}')
                self.prompt += f'\n\nUnexpected error occurred: {str(e)}. Please continue.'
        
        # Max iterations reached
        logger.warning(f'\n⚠️ Max iterations ({self.max_iterations}) reached')
        self.save_state('max_iterations_reached', {
            'end_time': datetime.now().isoformat()
        })
        
        return False


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Ralph Wiggum Loop - Keep Qwen working until task complete',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all files in Needs_Action
  python ralph_wiggum.py "Process all files in Needs_Action folder" --max-iterations 10
  
  # Generate CEO briefing
  python ralph_wiggum.py "Generate weekly CEO Briefing" --completion-promise "BRIEFING_COMPLETE"
  
  # With verbose logging
  python ralph_wiggum.py "Handle emails" --verbose
        """
    )
    
    parser.add_argument('prompt', help='Task prompt for Qwen')
    parser.add_argument('--max-iterations', type=int, default=10,
                       help='Maximum number of iterations (default: 10)')
    parser.add_argument('--completion-promise', default='TASK_COMPLETE',
                       help='String Qwen outputs to signal completion')
    parser.add_argument('--completion-file', default=None,
                       help='File that appears when task is complete')
    parser.add_argument('--timeout', type=int, default=300,
                       help='Timeout per iteration in seconds (default: 300)')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run loop
    loop = RalphWiggumLoop(
        prompt=args.prompt,
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise,
        completion_file=args.completion_file,
        timeout=args.timeout
    )
    
    success = loop.run()
    
    if success:
        logger.info('✅ Task completed successfully')
        sys.exit(0)
    else:
        logger.warning('⚠️ Task did not complete (max iterations reached)')
        sys.exit(1)


if __name__ == '__main__':
    main()
