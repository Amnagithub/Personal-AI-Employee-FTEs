---
name: process_inbox
description: |
  Process items in the AI Employee vault Inbox and Needs_Action folders.
  Use this skill when you need to:
  - Review new files dropped in /Inbox
  - Process action items in /Needs_Action
  - Update the Dashboard with current status
  - Move completed tasks to /Done
  
  This is the core skill for the AI Employee's daily operations.
---

# Process Inbox Skill

This skill enables the AI Employee to process incoming items and manage the task workflow.

## Usage

Run this skill from the vault root directory:

```bash
# Process inbox and update dashboard
python scripts/orchestrator.py /path/to/vault

# Or run the watcher to detect new files
python scripts/watchers/filesystem_watcher.py /path/to/vault --once
```

## Workflow

1. **Check Inbox** - Look for new files dropped by the user
2. **Create Action Files** - For each new file, create a corresponding action file in `/Needs_Action`
3. **Process Actions** - Review each action file and determine required steps
4. **Execute Tasks** - Complete the required actions
5. **Mark Complete** - Check off completion boxes in the action file
6. **Move to Done** - Move completed action files to `/Done`
7. **Update Dashboard** - Refresh `Dashboard.md` with current status

## Action File Schema

Each action file follows this structure:

```markdown
---
type: file_drop|email|whatsapp|approval_request
source: original_filename.txt
size: 1234 bytes
received: 2026-02-28T10:30:00
priority: normal|high|critical
status: pending|in_progress|completed
---

# Title

Description of the item.

## Details

- **Field 1:** Value
- **Field 2:** Value

## Suggested Actions

- [ ] Action item 1
- [ ] Action item 2
- [ ] Mark this task as complete when done

## Notes

Additional context or processing notes.
```

## Priority Levels

| Priority | Response Time | Examples |
|----------|---------------|----------|
| Critical | Immediate | System down, major client emergency |
| High | 4 hours | Urgent requests, approaching deadlines |
| Normal | 24 hours | Standard tasks, routine processing |
| Low | 1 week | Nice-to-have, improvements |

## Folder Structure

```
Vault/
├── Inbox/              # Raw incoming files (user drops here)
├── Needs_Action/       # Action files awaiting processing
├── Plans/              # Multi-step task plans
├── Pending_Approval/   # Awaiting human decision
├── Approved/           # Approved actions ready to execute
├── Rejected/           # Declined actions
├── Done/               # Completed tasks (archive)
├── Dashboard.md        # Real-time status overview
├── Company_Handbook.md # Rules of engagement
└── Business_Goals.md   # Objectives and metrics
```

## Integration with Claude Code

To use this skill with Claude Code:

1. Point Claude Code at your vault:
   ```bash
   claude --cd /path/to/vault
   ```

2. Ask Claude to process the inbox:
   ```
   Process all items in /Needs_Action using the process_inbox skill.
   Follow the Company_Handbook rules and update the Dashboard.
   ```

3. For autonomous operation, use the Ralph Wiggum loop:
   ```bash
   claude "Process all files in /Needs_Action, move to /Done when complete"
   ```

## Example Session

```
User: "I dropped a client_invoice.pdf in the Inbox"

AI Employee (using process_inbox skill):
1. Detects new file in /Inbox
2. Creates FILE_DROP_client_invoice_20260228_103000.md in /Needs_Action
3. Reads the invoice content
4. Extracts amount, client name, due date
5. Checks Company_Handbook rules (amount > $500?)
6. If > $500: Creates approval request in /Pending_Approval
7. If <= $500: Logs in Accounting and moves to /Done
8. Updates Dashboard with new status
```

## Testing

Test the skill manually:

```bash
# 1. Drop a test file in Inbox
echo "Test content" > /path/to/vault/Inbox/test_document.txt

# 2. Run the watcher once
python scripts/watchers/filesystem_watcher.py /path/to/vault --once

# 3. Check Needs_Action folder
ls -la /path/to/vault/Needs_Action/

# 4. Run orchestrator
python scripts/orchestrator.py /path/to/vault

# 5. View updated Dashboard
cat /path/to/vault/Dashboard.md
```
