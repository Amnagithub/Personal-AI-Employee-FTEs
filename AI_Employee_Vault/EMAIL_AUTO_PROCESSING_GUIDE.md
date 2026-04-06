# Email Auto-Processing Guide - FULLY AUTONOMOUS SYSTEM

## ✅ Complete Autonomous Email System Installed!

Your email system now has **full autonomous capabilities**:
- ✅ Gmail Watcher detects new emails automatically
- ✅ Action files created in `Needs_Action` folder
- ✅ **Email Auto-Processor** reads, understands, and replies to emails
- ✅ **Email MCP Integration** for sending emails via Gmail
- ✅ **Approval Workflow** for sensitive emails
- ✅ **Continuous Loop Mode** - runs 24/7 without manual intervention

## Architecture Overview

```
┌─────────────────┐
│  Gmail Watcher  │  (Checks every 120s)
└────────┬────────┘
         │ Creates action files
         ▼
┌─────────────────────┐
│   Needs_Action/     │
│  EMAIL_*.md files   │
└────────┬────────────┘
         │
         ▼
┌──────────────────────────┐
│ Email Auto-Processor     │  (Checks every 60s)
│  1. Reads email          │
│  2. Generates reply      │
│  3. Sends via MCP        │
│  4. Moves to Done        │
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────┐
│   Email MCP Server  │  (Sends via Gmail API)
│   (Port 8809)       │
└─────────────────────┘
```

## Quick Start - Run Everything

### On Windows (Recommended)

```bash
# Navigate to vault
cd "C:\Users\Saif\Documents\GitHub\Personal AI Employee FTEs\AI_Employee_Vault"

# Start the complete system
bash scripts/run_email_system.sh

# Or use the batch file
scripts\run_email_system.bat
```

### On Linux/WSL

```bash
cd AI_Employee_Vault

# Start the complete system
bash scripts/run_email_system.sh

# Or run in background
bash scripts/run_email_system.sh --daemon
```

## Setup Requirements

### 1. Gmail API Credentials (Required for Sending)

**One-time setup:**

1. **Enable Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Navigate to **APIs & Services > Library**
   - Search for "Gmail API" and enable it

2. **Create OAuth 2.0 Credentials:**
   - Go to **APIs & Services > Credentials**
   - Click **Create Credentials > OAuth client ID**
   - Application type: **Desktop app**
   - Download the `credentials.json` file

3. **Store Credentials:**
   ```bash
   # Create directory
   mkdir -p ~/.ai_employee
   
   # Move credentials file
   cp /path/to/credentials.json ~/.ai_employee/gmail_credentials.json
   ```

4. **Start Email MCP Server:**
   ```bash
   bash .qwen/skills/email-mcp/scripts/start-server.sh
   ```

5. **Verify MCP is Running:**
   ```bash
   python .qwen/skills/email-mcp/scripts/verify.py
   ```
   Expected: `✓ Email MCP server running on port 8809`

### 2. Test the System

**Test mode (no sending):**
```bash
cd AI_Employee_Vault
python scripts/email_auto_processor.py .
```

**Auto-send mode (sends non-sensitive emails):**
```bash
python scripts/email_auto_processor.py . --auto-send
```

**Continuous loop mode (24/7 operation):**
```bash
python scripts/email_auto_processor.py . --loop --loop-interval 60 --auto-send
```

## Using the Master Control Script

The `run_email_system.sh` script manages everything:

### Interactive Mode
```bash
bash scripts/run_email_system.sh
```
Runs in foreground, shows all output in terminal.

### Background/Daemon Mode
```bash
bash scripts/run_email_system.sh --daemon
```
Runs in background, logs to files.

### Check Status
```bash
bash scripts/run_email_system.sh --status
```

### View Logs
```bash
bash scripts/run_email_system.sh --logs
```

### Stop All Services
```bash
bash scripts/run_email_system.sh --stop
```

## Email Auto-Processor Features

### Intelligent Reply Generation
- Detects email type (forward, question, scheduling, etc.)
- Generates contextually appropriate replies
- Handles attachments and labels

### Sensitivity Detection
Automatically detects sensitive emails requiring approval:
- Invoices and payments
- Contracts and legal matters
- Financial discussions
- Urgent/ASAP requests
- Unknown important senders

### Approval Workflow
For sensitive emails:
1. Creates approval request in `Pending_Approval/`
2. Waits for human review
3. Move to `Approved/` to send
4. Move to `Rejected/` to discard

### Auto-Processing Rules
- **Non-sensitive emails**: Replied automatically
- **Sensitive emails**: Require approval
- **Forwards**: Acknowledgment sent
- **Questions**: "Looking into it" response
- **Scheduling requests**: Calendar check response

## Configuration Options

### Email Auto-Processor

| Option | Description | Default |
|--------|-------------|---------|
| `--auto-send` | Automatically send replies | Off (manual) |
| `--use-qwen` | Use Qwen Code for intelligent replies | Off (template) |
| `--loop` | Run continuously | Off (single run) |
| `--loop-interval` | Seconds between checks | 300 (5 min) |
| `--mcp-url` | Email MCP server URL | http://localhost:8809 |

### Gmail Watcher

| Option | Description | Default |
|--------|-------------|---------|
| `--interval` | Seconds between checks | 120 (2 min) |
| `--verbose` | Show detailed logs | Off |
| `--once` | Run once and exit | Off (continuous) |

## Processing Flow

### Standard Email (Non-Sensitive)
```
1. Gmail Watcher detects new email (every 120s)
2. Creates EMAIL_*.md in Needs_Action/
3. Email Auto-Processor detects it (every 60s)
4. Generates appropriate reply
5. Sends via Email MCP server
6. Moves file to Done/
7. Marks original email as read in Gmail
```

### Sensitive Email (Requires Approval)
```
1. Gmail Watcher detects new email
2. Creates EMAIL_*.md in Needs_Action/
3. Email Auto-Processor detects it
4. Detects sensitive content
5. Creates draft in Gmail via MCP
6. Creates APPROVAL_*.md in Pending_Approval/
7. WAITS for human review
8. You move file to Approved/ or Rejected/
9. If approved, sends the draft email
10. Moves file to Done/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Email MCP not running | `bash .qwen/skills/email-mcp/scripts/start-server.sh` |
| OAuth errors | Delete `token.json`, restart MCP server |
| Credentials not found | Place at `~/.ai_employee/gmail_credentials.json` |
| 403 Forbidden | Enable Gmail API in Google Cloud Console |
| Replies not sending | Check MCP server is running: `curl http://localhost:8809/tools/list` |
| No new emails detected | Check Gmail query in watcher (is:unread is:important) |
| Processor not running | Check logs in `logs/` folder |

## Monitoring Your Autonomous System

### Check what's happening

```bash
# View current status
bash scripts/run_email_system.sh --status

# Watch logs in real-time
tail -f logs/gmail_watcher.log
tail -f logs/email_processor.log

# Check pending items
ls Needs_Action/EMAIL_*.md
ls Pending_Approval/*.md
```

### Email Dashboard

The system automatically updates:
- `Dashboard.md` - Current status and metrics
- `.watcher_cache` - Processed email IDs (prevents duplicates)
- `logs/` - Detailed operation logs

## Advanced: Qwen Code Integration

For **truly intelligent** email replies (not just templates):

1. **Manual processing:**
   ```
   In Qwen Code chat:
   "Process all emails in Needs_Action and send intelligent replies"
   ```

2. **Automated (future):**
   - Integrate with Qwen Code API
   - Context-aware replies using Business_Goals.md
   - Learning from previous email patterns

## Security Best Practices

1. **Never commit credentials** - `.gitignore` includes `token.json` and credentials
2. **Review sensitive emails** - Approval workflow catches important messages
3. **Monitor sent emails** - Check `Done/` folder regularly
4. **Rotate OAuth tokens** - Re-authenticate every 90 days
5. **Check logs** - Review `logs/` for unusual activity

## Next Steps

1. ✅ **System is installed** - All scripts ready
2. 🔧 **Set up Gmail API** - Follow setup requirements above
3. 🚀 **Start the system** - Use `bash scripts/run_email_system.sh`
4. 👀 **Monitor** - Check status and logs regularly
5. 🎯 **Fine-tune** - Adjust intervals and sensitivity rules

---

**For questions or issues:**
- Check logs in `logs/` folder
- Review this guide
- Run `bash scripts/run_email_system.sh --help`
