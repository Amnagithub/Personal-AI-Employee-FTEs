# AI Employee Vault

Your Personal AI Employee's workspace - a local-first, agent-driven task management system.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the File Watcher

```bash
# Run continuously in background
python scripts/watchers/filesystem_watcher.py . &

# Or run once (for testing)
python scripts/watchers/filesystem_watcher.py . --once
```

### 3. Drop a File in Inbox

```bash
echo "Process this document" > Inbox/my_document.txt
```

### 4. Run the Orchestrator

```bash
python scripts/orchestrator.py .
```

### 5. Check Dashboard

```bash
cat Dashboard.md
```

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `Inbox/` | Drop files here for processing |
| `Needs_Action/` | Action items awaiting processing |
| `Done/` | Completed tasks (archive) |
| `Pending_Approval/` | Awaiting your decision |
| `Approved/` | Approved actions ready to execute |
| `Rejected/` | Declined actions |

## Key Files

- `Dashboard.md` - Real-time status overview
- `Company_Handbook.md` - Rules of engagement
- `Business_Goals.md` - Your objectives and metrics

## Skills

- `skills/process_inbox.md` - Core inbox processing skill

## Usage with Claude Code

```bash
# Point Claude Code at this vault
claude --cd /path/to/vault

# Ask Claude to process items
"Process all items in /Needs_Action using the process_inbox skill"
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/watchers/base_watcher.py` | Base class for all watchers |
| `scripts/watchers/filesystem_watcher.py` | Monitors Inbox for new files |
| `scripts/orchestrator.py` | Processes actions and updates Dashboard |

## Bronze Tier Checklist

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System monitoring)
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] Agent Skill implemented (process_inbox)
