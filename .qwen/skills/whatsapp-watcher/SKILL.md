---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for new messages with keywords like "urgent", "invoice", "payment".
  Uses Playwright for browser automation. Creates action files in Obsidian vault.
  Note: Be aware of WhatsApp's terms of service when automating.
---

# WhatsApp Watcher

Monitor WhatsApp Web for important messages using browser automation.

## Overview

WhatsApp Watcher uses Playwright to automate WhatsApp Web, monitoring for new messages containing keywords that indicate importance (urgent, invoice, payment, help, etc.).

**Important:** Be aware of WhatsApp's terms of service. This is for personal automation only.

## Prerequisites

1. **Playwright MCP Server** must be running
2. **WhatsApp Web** session must be authenticated
3. **Python dependencies**: playwright

```bash
# Install Playwright
pip install playwright
playwright install chromium

# Start Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
```

## Quick Start

### Run Once

```bash
cd AI_Employee_Vault
python3 scripts/watchers/whatsapp_watcher.py . --once
```

### Run Continuously

```bash
python3 scripts/watchers/whatsapp_watcher.py . --interval 30
```

## Configuration

### Keywords to Monitor

Edit `whatsapp_watcher.py`:

```python
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency']
```

### Check Interval

```bash
# Check every 30 seconds (development)
python3 whatsapp_watcher.py . --interval 30

# Check every 2 minutes (production)
python3 whatsapp_watcher.py . --interval 120
```

## How It Works

1. **Launch WhatsApp Web** with persistent session
2. **Scan for unread messages** containing keywords
3. **Extract message content** and sender info
4. **Create action file** in /Needs_Action

### Example Action File

```markdown
---
type: whatsapp
from: +1234567890
chat: Client Name
received: 2026-01-07T10:30:00
priority: high
status: pending
keywords: invoice, urgent
---

# WhatsApp Message

**From:** +1234567890 (Client Name)
**Chat:** Client Name
**Received:** January 07, 2026 at 10:30 AM

---

**Message:**
Hey, can you send me the invoice for January? It's urgent.

---

## Suggested Actions

- [ ] Generate invoice for January
- [ ] Send via email (requires approval)
- [ ] Reply on WhatsApp
- [ ] Mark as complete
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| WhatsApp Web not loading | Check internet, scan QR code manually |
| Session expired | Re-authenticate WhatsApp Web |
| No messages detected | Verify keywords match message content |
| Browser crashes | Reduce check interval |

## Security

- Session stored locally in `~/.ai_employee/whatsapp_session/`
- Never commit session data to Git
- Use only for personal WhatsApp (not business API)
