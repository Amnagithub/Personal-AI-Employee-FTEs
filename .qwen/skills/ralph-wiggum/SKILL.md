# Ralph Wiggum Loop - Autonomous Multi-Step Task Completion

**Purpose:** Keep Qwen Code working autonomously until a task is complete, without requiring manual prompts

**Location:** `.qwen/skills/ralph-wiggum/`

---

## What is the Ralph Wiggum Loop?

The Ralph Wiggum pattern uses a **Stop hook** that intercepts Qwen's exit and re-injects the prompt until:
1. Task completion is detected, OR
2. Maximum iterations reached

This transforms Qwen from an interactive assistant into an **autonomous worker**.

---

## How It Works

```
┌─────────────────────────────────────────────┐
│  1. Orchestrator creates state file         │
│     with task prompt                        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  2. Qwen works on task                      │
│     - Reads files                          │
│     - Makes decisions                      │
│     - Takes actions                        │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  3. Qwen tries to exit                      │
│     Stop hook intercepts                    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  4. Check completion criteria:              │
│     - Is task file in /Done?                │
│     - Did Qwen output TASK_COMPLETE?        │
│     - Max iterations reached?               │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   COMPLETE              INCOMPLETE
   (Allow exit)          (Re-inject prompt,
                          loop continues)
```

---

## Usage

### Basic Usage

```bash
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

### With File Movement Detection (Gold Tier)

```bash
/ralph-loop "Process inbox and handle all emails" \
  --completion-signal-file "/tmp/ralph_complete.flag" \
  --max-iterations 20
```

### With Timeout

```bash
/ralph-loop "Generate weekly report" \
  --completion-promise "REPORT_COMPLETE" \
  --max-iterations 5 \
  --timeout 300
```

---

## Completion Strategies

### 1. Promise-Based (Simple)

Qwen must output a specific string to signal completion:

```
<promise>TASK_COMPLETE</promise>
```

**Pros:**
- Easy to implement
- Qwen controls when done

**Cons:**
- Requires Qwen to remember to output promise
- Can be missed if Qwen forgets

### 2. File Movement (Advanced - Recommended)

Stop hook detects when task file moves to `/Done`:

**Pros:**
- More reliable (completion is natural part of workflow)
- Orchestrator creates state file programmatically
- No special Qwen output required

**Cons:**
- Requires file monitoring
- More complex setup

---

## Implementation

### Stop Hook Script

```python
#!/usr/bin/env python3
"""
Ralph Wiggum Loop Implementation

This script:
1. Monitors Qwen Code execution
2. Intercepts exit attempts
3. Checks completion criteria
4. Re-injects prompt if not complete
"""

import subprocess
import time
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger('ralph_wiggum')

class RalphWiggumLoop:
    def __init__(self, prompt, max_iterations=10, 
                 completion_promise=None, completion_file=None):
        self.prompt = prompt
        self.max_iterations = max_iterations
        self.completion_promise = completion_promise
        self.completion_file = completion_file
        self.iteration = 0
        self.state_file = Path('/tmp/ralph_state.json')
    
    def check_completion(self, output):
        """Check if task is complete"""
        # Strategy 1: Promise-based
        if self.completion_promise:
            if f'<promise>{self.completion_promise}</promise>' in output:
                logger.info('Completion promise detected')
                return True
        
        # Strategy 2: File movement
        if self.completion_file:
            if Path(self.completion_file).exists():
                logger.info('Completion file detected')
                return True
        
        return False
    
    def run(self):
        """Execute the Ralph loop"""
        logger.info(f'Starting Ralph Wiggum Loop: {self.max_iterations} max iterations')
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            logger.info(f'Iteration {self.iteration}/{self.max_iterations}')
            
            # Create state file
            state = {
                'iteration': self.iteration,
                'prompt': self.prompt,
                'start_time': datetime.now().isoformat(),
                'status': 'running'
            }
            self.state_file.write_text(json.dumps(state, indent=2))
            
            # Run Qwen Code
            result = subprocess.run(
                ['qwen', '--prompt', self.prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per iteration
            )
            
            output = result.stdout
            logger.info(f'Qwen output length: {len(output)}')
            
            # Check completion
            if self.check_completion(output):
                logger.info('Task complete!')
                state['status'] = 'complete'
                state['end_time'] = datetime.now().isoformat()
                self.state_file.write_text(json.dumps(state, indent=2))
                return True
            
            # Check for errors
            if result.returncode != 0:
                logger.warning(f'Qwen exited with code {result.returncode}')
                self.prompt += f'\n\nPrevious attempt failed. Error: {result.stderr[:500]}. Please try again.'
            
            # Not complete, continue loop
            self.prompt += '\n\nTask not complete. Continue working.'
        
        # Max iterations reached
        logger.warning(f'Max iterations ({self.max_iterations}) reached')
        state['status'] = 'max_iterations_reached'
        state['end_time'] = datetime.now().isoformat()
        self.state_file.write_text(json.dumps(state, indent=2))
        return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop')
    parser.add_argument('prompt', help='Task prompt')
    parser.add_argument('--max-iterations', type=int, default=10)
    parser.add_argument('--completion-promise', default='TASK_COMPLETE')
    parser.add_argument('--completion-file', default=None)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    
    loop = RalphWiggumLoop(
        prompt=args.prompt,
        max_iterations=args.max_iterations,
        completion_promise=args.completion_promise,
        completion_file=args.completion_file
    )
    
    success = loop.run()
    sys.exit(0 if success else 1)
```

---

## Integration with Orchestrator

The master orchestrator can start Ralph loops for different task types:

```python
# orchestrator.py

from ralph_wiggum import RalphWiggumLoop

def process_needs_action():
    """Start Ralph loop to process Needs_Action folder"""
    prompt = """
    Process all files in /Needs_Action folder:
    1. Read each file
    2. Understand the content and type
    3. Take appropriate action
    4. Move to /Done when complete
    
    Output <promise>TASK_COMPLETE</promise> when all files processed.
    """
    
    loop = RalphWiggumLoop(
        prompt=prompt,
        max_iterations=15,
        completion_promise='TASK_COMPLETE'
    )
    
    return loop.run()

def generate_ceo_briefing():
    """Start Ralph loop to generate weekly report"""
    prompt = """
    Generate Monday Morning CEO Briefing:
    1. Read Business_Goals.md
    2. Check Done/ folder for completed tasks
    3. Analyze accounting data from Odoo
    4. Get Facebook/Instagram summaries
    5. Write Briefings/YYYY-MM-DD_Monday_Briefing.md
    
    Output <promise>BRIEFING_COMPLETE</promise> when done.
    """
    
    loop = RalphWiggumLoop(
        prompt=prompt,
        max_iterations=5,
        completion_promise='BRIEFING_COMPLETE'
    )
    
    return loop.run()
```

---

## Error Recovery

### Graceful Degradation

When components fail:

1. **Qwen Code unavailable:** Watchers continue collecting, queue grows for later
2. **MCP server down:** Actions logged, retry when available
3. **Max iterations reached:** Alert human, partial results saved
4. **Timeout exceeded:** Save state, alert human, pause

### State Persistence

Each iteration saves state to `/tmp/ralph_state.json`:

```json
{
  "iteration": 5,
  "prompt": "Process all files...",
  "start_time": "2026-04-14T10:30:00",
  "end_time": "2026-04-14T10:45:00",
  "status": "complete"
}
```

---

## Best Practices

1. **Set reasonable max iterations:** 10-20 for complex tasks, 3-5 for simple
2. **Use completion files:** More reliable than promise strings
3. **Monitor state files:** Check `/tmp/ralph_state.json` for progress
4. **Log everything:** All iterations logged for debugging
5. **Alert on failures:** Notify human when max iterations reached

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Loop never completes | Check completion criteria, increase max_iterations |
| Too many iterations | Refine prompt, add clearer completion signal |
| Qwen crashes | Check error logs, reduce task complexity |
| Timeout exceeded | Increase timeout, break task into smaller pieces |

---

## Resources

- [Ralph Wiggum Reference](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Stop Hooks Documentation](https://github.com/anthropics/claude-code)
