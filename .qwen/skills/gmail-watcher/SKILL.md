---
name: gmail-watcher
description: |
  Monitor Gmail for new important emails and create action files in Obsidian vault.
  Runs continuously in background, checking every 2 minutes. Creates .md files in
  /Needs_Action folder for Qwen Code to process. Requires Gmail API OAuth setup.
---

# Gmail Watcher

Autonomous email monitoring for your AI Employee.

## Overview

Gmail Watcher runs continuously in the background, monitoring your Gmail inbox for new important emails. When it detects a new email, it creates an action file in your Obsidian vault's `/Needs_Action` folder for Qwen Code to process.

## Prerequisites

### 1. Gmail API Setup

Same credentials as Email MCP:

```bash
# Ensure credentials exist
~/.ai_employee/gmail_credentials.json
```

### 2. Install Dependencies

```bash
cd AI_Employee_Vault
pip install -r requirements.txt
```

Ensure these packages are in `requirements.txt`:
```
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
watchdog
```

### 3. Base Watcher

The Gmail Watcher extends the base watcher class:

```
AI_Employee_Vault/scripts/watchers/
├── base_watcher.py      # Abstract base class
└── gmail_watcher.py     # Gmail implementation
```

## Quick Start

### Run Once (for testing)

```bash
cd AI_Employee_Vault
python3 scripts/watchers/gmail_watcher.py . --once
```

### Run Continuously (background)

```bash
cd AI_Employee_Vault
python3 scripts/watchers/gmail_watcher.py . --verbose
```

### Run with Custom Interval

```bash
# Check every 5 minutes (300 seconds)
python3 scripts/watchers/gmail_watcher.py . --interval 300
```

## How It Works

### 1. Authentication

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# First run: OAuth flow creates token.json
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)
creds = flow.run_local_server(port=0)

# Subsequent runs: Use cached token
creds = Credentials.from_authorized_user_file('token.json')
```

### 2. Check for New Emails

```python
# Query: Unread and important emails
results = service.users().messages().list(
    userId='me',
    q='is:unread is:important'
).execute()

messages = results.get('messages', [])
```

### 3. Create Action File

For each new email:

```markdown
---
type: email
from: client@example.com
subject: Project Inquiry
received: 2026-01-07T10:30:00
priority: high
status: pending
message_id: msg_12345
---

# Email Content

**From:** client@example.com
**Subject:** Project Inquiry
**Received:** January 07, 2026 at 10:30 AM

---

Hi,

I'm interested in your services. Can you send me a quote?

Best regards,
Client Name

---

## Suggested Actions

- [ ] Reply to sender with quote
- [ ] Forward to sales team
- [ ] Schedule follow-up call
- [ ] Archive after processing
```

## Configuration

### Gmail Query Filters

Customize what emails trigger action files:

```python
# In gmail_watcher.py, modify QUERY_TEMPLATE

# Default: Unread and important
QUERY_TEMPLATE = 'is:unread is:important'

# Only from specific senders
QUERY_TEMPLATE = 'is:unread from:client@example.com'

# With specific keywords
QUERY_TEMPLATE = 'is:unread (invoice OR payment OR urgent)'

# Exclude newsletters
QUERY_TEMPLATE = 'is:unread is:important -category:promotions -category:social'
```

### Check Interval

```bash
# Check every 30 seconds (development)
python3 gmail_watcher.py . --interval 30

# Check every 5 minutes (production)
python3 gmail_watcher.py . --interval 300

# Check every 15 minutes (low priority)
python3 gmail_watcher.py . --interval 900
```

## Integration with Qwen Code

### Workflow

1. **Watcher detects email** → Creates action file
2. **Orchestrator triggers Qwen** → Processes action file
3. **Qwen suggests reply** → Creates draft in Email MCP
4. **Human approves** → Moves file to /Approved
5. **Email sent** → Logged to audit file

### Example Session

```bash
# Terminal 1: Run watcher
python3 scripts/watchers/gmail_watcher.py .

# Terminal 2: Run orchestrator
python3 scripts/orchestrator.py .

# Terminal 3: Run Qwen Code
cd AI_Employee_Vault
qwen
```

Prompt Qwen:
```
Check the Needs_Action folder for new emails.
For each email:
1. Read and understand the content
2. Draft an appropriate reply
3. Create approval request if action needed
4. Move processed files to Done
```

## Action File Schema

```yaml
type: email | newsletter | notification
from: sender email address
subject: email subject line
received: ISO 8601 timestamp
priority: high | normal | low
status: pending | processing | done
message_id: Gmail message ID
labels: array of Gmail labels
has_attachment: true | false
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OAuth error | Delete `token.json`, re-run to re-authenticate |
| No emails detected | Check Gmail query filter, verify labels |
| Duplicate action files | Clear `processed_ids` cache |
| API rate limit | Increase check interval |
| Token expired | Re-authenticate with OAuth flow |

## Security

1. **Never commit** `token.json` or `credentials.json`
2. Add to `.gitignore`:
   ```
   *.json
   .env
   __pycache__/
   ```
3. Use **scoped permissions** (read-only for watcher)
4. **Rotate credentials** every 90 days

## Scheduling (Alternative to Continuous)

Instead of running continuously, use cron/Task Scheduler:

### Linux/Mac (cron)

```bash
# Edit crontab
crontab -e

# Check every 5 minutes
*/5 * * * * cd /path/to/AI_Employee_Vault && python3 scripts/watchers/gmail_watcher.py . --once
```

### Windows (Task Scheduler)

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python3" `
  -Argument "scripts/watchers/gmail_watcher.py . --once" `
  -WorkingDirectory "C:\path\to\AI_Employee_Vault"

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "GmailWatcher" `
  -Action $action -Trigger $trigger -User "Saif"
```

## Testing

```bash
# Send test email to yourself
# Run watcher
python3 scripts/watchers/gmail_watcher.py . --once --verbose

# Check output
# Should see: "Processed new email: msg_12345 -> EMAIL_msg_12345.md"

# Verify action file created
ls Needs_Action/
```

## Resources

- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Gmail API Reference](https://developers.google.com/gmail/api/reference/rest)
- [Google Auth Library](https://google-auth.readthedocs.io/)
