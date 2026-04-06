# AI Employee - Scripts Directory

## 🚀 Quick Start

### Start the Complete Email System

```bash
# Windows (Git Bash or WSL)
bash scripts/run_email_system.sh

# Windows (Command Prompt)
scripts\run_email_system.bat

# Linux/WSL
bash scripts/run_email_system.sh --daemon
```

## 📁 Script Overview

### Watchers (Monitor External Systems)

| Script | Purpose | Usage |
|--------|---------|-------|
| `watchers/gmail_watcher.py` | Monitor Gmail for new emails | `python watchers/gmail_watcher.py /path/to/vault --interval 120` |
| `watchers/file_watcher.py` | Monitor file drops | `python watchers/file_watcher.py /path/to/vault` |

### Processors (Handle Action Files)

| Script | Purpose | Usage |
|--------|---------|-------|
| `email_auto_processor.py` | Process emails & send replies | `python email_auto_processor.py /path/to/vault --auto-send --loop` |
| `orchestrator.py` | Update dashboard & track progress | `python orchestrator.py /path/to/vault` |

### Master Control

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_email_system.sh` | Start/stop all services | `bash run_email_system.sh [--daemon\|--stop\|--status\|--logs]` |
| `run_email_system.bat` | Windows batch launcher | `run_email_system.bat [--daemon\|--stop\|--status\|--logs]` |

### Utilities

| Script | Purpose | Usage |
|--------|---------|-------|
| `test_email_mcp.py` | Test Email MCP connection | `python test_email_mcp.py` |

## 🎯 Common Workflows

### 1. Test Email Processing (No Sending)

```bash
cd AI_Employee_Vault
python scripts/email_auto_processor.py .
```

This will:
- Read all EMAIL_*.md files in Needs_Action
- Generate reply drafts
- Create approval requests for sensitive emails
- Move processed files to Done
- **NOT send any emails** (safe for testing)

### 2. Auto-Send Non-Sensitive Emails

```bash
python scripts/email_auto_processor.py . --auto-send
```

This will:
- Automatically reply to normal emails
- Create approval requests for sensitive ones
- Send replies via Email MCP (if running)

### 3. Run 24/7 Autonomous Mode

```bash
# Using the master script
bash scripts/run_email_system.sh --daemon

# Or run processor directly
python scripts/email_auto_processor.py . --loop --loop-interval 60 --auto-send
```

### 4. Monitor the System

```bash
# Check status
bash scripts/run_email_system.sh --status

# View logs
bash scripts/run_email_system.sh --logs

# Or manually
tail -f logs/gmail_watcher.log
tail -f logs/email_processor.log
```

### 5. Stop Everything

```bash
bash scripts/run_email_system.sh --stop
```

## 📋 Email Processing Flow

```
┌──────────────────────┐
│  New Email Arrives   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Gmail Watcher       │ ← Runs every 120s
│  (detects email)     │
└──────────┬───────────┘
           │ Creates EMAIL_*.md
           ▼
┌──────────────────────┐
│   Needs_Action/      │
│   (action files)     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Email Auto-Processor │ ← Runs every 60s
│  1. Reads email      │
│  2. Detects type     │
│  3. Generates reply  │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌─────────┐  ┌────────────┐
│ Normal  │  │ Sensitive  │
│ Email   │  │ Email      │
└────┬────┘  └─────┬──────┘
     │             │ Creates APPROVAL_*.md
     ▼             ▼
┌─────────┐  ┌────────────┐
│ Send    │  │Pending_    │
│ Reply   │  │Approval/   │
└────┬────┘  └─────┬──────┘
     │             │ Human reviews
     ▼             ▼
┌─────────┐  ┌────────────┐
│  Done/  │  │ Approved/  │
│         │  │   ↓        │
│         │  │ Send Email │
│         │  │   ↓        │
│         │  │  Done/     │
└─────────┘  └────────────┘
```

## ⚙️ Configuration

### Gmail Watcher Options

```bash
python watchers/gmail_watcher.py /path/to/vault \
  --interval 120        # Check every 2 minutes
  --verbose             # Show detailed logs
  --once                # Run once (for testing)
```

### Email Auto-Processor Options

```bash
python email_auto_processor.py /path/to/vault \
  --auto-send           # Auto-send non-sensitive replies
  --use-qwen            # Use Qwen Code for intelligent replies (future)
  --loop                # Run continuously
  --loop-interval 60    # Check every 60 seconds
  --mcp-url http://localhost:8809  # Email MCP server URL
  --verbose             # Show detailed logs
```

### Master Script Options

```bash
bash run_email_system.sh \
  --daemon              # Run in background
  --stop                # Stop all services
  --status              # Show service status
  --logs                # Show recent logs
  --help                # Show help message
```

## 🔧 Setup Requirements

### Gmail API Credentials (One-Time)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json
5. Place at: `~/.ai_employee/gmail_credentials.json`

### Start Email MCP Server

```bash
bash .qwen/skills/email-mcp/scripts/start-server.sh
```

### Verify MCP is Running

```bash
python .qwen/skills/email-mcp/scripts/verify.py
# Expected: ✓ Email MCP server running on port 8809
```

## 📊 Monitoring & Logs

### Check System Status

```bash
bash scripts/run_email_system.sh --status
```

Output:
```
[✓] Gmail Watcher: Running (PID: 12345)
[✓] Email Auto-Processor: Running (PID: 12346)
[✓] Email MCP Server: Running (port 8809)

[i] Pending emails in Needs_Action: 2
[i] Pending approvals: 1
```

### View Logs

```bash
# Real-time monitoring
tail -f logs/gmail_watcher.log
tail -f logs/email_processor.log

# Or use master script
bash scripts/run_email_system.sh --logs
```

### Check Folders

```bash
# Pending emails
ls Needs_Action/EMAIL_*.md

# Awaiting approval
ls Pending_Approval/*.md

# Completed
ls Done/ -lt | head -20
```

## 🛡️ Security Notes

1. **Never commit credentials**
   - `~/.ai_employee/gmail_credentials.json` is in .gitignore
   - `token.json` is in .gitignore
   - Always keep OAuth files private

2. **Review sensitive emails**
   - Approval workflow catches important messages
   - Manually review Pending_Approval folder

3. **Monitor sent emails**
   - Check Done/ folder regularly
   - Review logs for unusual activity

4. **Rotate credentials**
   - Re-authenticate every 90 days
   - Delete old tokens and re-authorize

## 🐛 Troubleshooting

### Gmail Watcher Not Detecting Emails

```bash
# Run with verbose logging
python watchers/gmail_watcher.py . --once --verbose

# Check OAuth token exists
ls token.json

# Re-authenticate if needed
rm token.json
python watchers/gmail_watcher.py . --once
```

### Email MCP Not Running

```bash
# Start the server
bash .qwen/skills/email-mcp/scripts/start-server.sh

# Verify
python .qwen/skills/email-mcp/scripts/verify.py
```

### Processor Not Sending Emails

```bash
# Test MCP connection
curl http://localhost:8809/tools/list

# Check processor logs
tail -f logs/email_processor.log

# Run in test mode (no sending)
python email_auto_processor.py . --verbose
```

### Services Won't Stop

```bash
# Force stop
bash scripts/run_email_system.sh --stop

# Or manually kill Python processes
taskkill /F /IM python.exe  # Windows
killall python3             # Linux/Mac
```

## 📚 Additional Resources

- **Full Guide:** `EMAIL_AUTO_PROCESSING_GUIDE.md`
- **Email MCP Skill:** `.qwen/skills/email-mcp/SKILL.md`
- **Main Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`

## 🎓 Learning Path

1. **Bronze Tier**: Run watcher once, see action files created
2. **Silver Tier**: Auto-process emails, approval workflow
3. **Gold Tier**: Full autonomous loop with MCP integration
4. **Platinum Tier**: Cloud deployment, multiple work zones

---

**Need Help?**
- Check logs in `logs/` folder
- Read `EMAIL_AUTO_PROCESSING_GUIDE.md`
- Run `bash scripts/run_email_system.sh --help`
