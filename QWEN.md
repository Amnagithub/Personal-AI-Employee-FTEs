# Personal AI Employee FTEs

## Project Overview

This repository contains a comprehensive architectural blueprint and hackathon guide for building a **"Digital FTE" (Full-Time Equivalent)** — an autonomous AI agent that proactively manages personal and business affairs 24/7. The project leverages **Qwen Code** as the reasoning engine and **Obsidian** as the local-first dashboard/memory system.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Core Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine for multi-step task completion |
| **Memory/GUI** | Obsidian (Markdown) | Local knowledge base, dashboard, and state management |
| **Senses (Watchers)** | Python scripts | Monitor Gmail, WhatsApp, filesystems to trigger AI actions |
| **Hands (MCP)** | Model Context Protocol servers | External actions (email, browser automation, payments) |
| **Persistence** | Ralph Wiggum Loop | Stop hook pattern for autonomous multi-step task completion |

### Key Features

- **Watcher Architecture:** Lightweight Python scripts continuously monitor inputs and create actionable `.md` files in `/Needs_Action`
- **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing:** Autonomous weekly audit generating revenue reports, bottleneck analysis, and proactive suggestions
- **Tiered Achievement Levels:** Bronze → Silver → Gold → Platinum (from basic watcher to always-on cloud deployment)

## Directory Structure

```
Personal AI Employee FTEs/
├── .qwen/skills/                    # Qwen Code skills (MCP integrations)
│   └── browsing-with-playwright/    # Browser automation skill
│       ├── SKILL.md                 # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool reference
│       └── scripts/
│           ├── mcp-client.py        # Universal MCP client (HTTP/stdio)
│           ├── start-server.sh      # Start Playwright MCP server
│           ├── stop-server.sh       # Stop Playwright MCP server
│           └── verify.py            # Server health check
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json                 # Skills registry
└── QWEN.md                          # This file
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Qwen Code](https://github.com/anthropics/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](https://nodejs.org/) | v24+ LTS | MCP servers & automation |

### Playwright MCP Server (Browser Automation)

```bash
# Start the server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify it's running
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

```bash
# List available tools
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py list \
  -u http://localhost:8808

# Call a tool
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call \
  -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Emit tool schemas as markdown
python3 .qwen/skills/browsing-with-playwright/scripts/mcp-client.py emit \
  -u http://localhost:8808
```

### Obsidian Vault Setup

Create an Obsidian vault with the following folder structure:

```
AI_Employee_Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items requiring processing
├── In_Progress/        # Currently being worked on
├── Pending_Approval/   # Awaiting human approval
├── Approved/           # Approved actions ready to execute
├── Rejected/           # Declined actions
├── Done/               # Completed tasks
├── Business_Goals.md   # Q1/Q2 objectives and metrics
├── Dashboard.md        # Real-time summary
└── Company_Handbook.md # Rules of engagement
```

## Development Conventions

### Watcher Pattern

All Watcher scripts follow the `BaseWatcher` abstract class pattern:

```python
from abc import ABC, abstractmethod
from pathlib import Path

class BaseWatcher(ABC):
    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass
```

### Action File Schema

```markdown
---
type: email|whatsapp|file_drop|approval_request
from: sender@example.com
subject: Urgent matter
priority: high
status: pending
---

## Content
...

## Suggested Actions
- [ ] Action item 1
- [ ] Action item 2
```

### Human-in-the-Loop Pattern

For sensitive actions (payments, sending emails), Qwen writes an approval request:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Ralph Wiggum Loop (Persistence)

Use the Stop hook pattern to keep Qwen working until task completion:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## MCP Servers Reference

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in for vault operations |
| `@playwright/mcp` | Browser automation | Web scraping, form submission, UI testing |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Payment portals, web automation |

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hours | Obsidian vault, one watcher, basic Qwen integration |
| **Silver** | 20-30 hours | Multiple watchers, MCP server, HITL workflow, scheduling |
| **Gold** | 40+ hours | Full integration, Odoo accounting, Ralph Wiggum loop, audit logging |
| **Platinum** | 60+ hours | Cloud deployment, work-zone specialization, A2A upgrade |

## Resources

- [Main Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Playwright MCP Skill](./.qwen/skills/browsing-with-playwright/SKILL.md)
- [MCP Tools Reference](./.qwen/skills/browsing-with-playwright/references/playwright-tools.md)
- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
