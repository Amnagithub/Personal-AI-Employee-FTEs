---
name: scheduler
description: |
  Schedule recurring tasks via cron (Linux/Mac) or Task Scheduler (Windows).
  Automate daily briefings, weekly audits, and periodic watcher execution.
  Includes templates for common scheduling patterns.
---

# Scheduler

Schedule recurring tasks for your AI Employee.

## Overview

The Scheduler skill provides cron and Task Scheduler configurations for running AI Employee tasks on a schedule. Use it for daily briefings, weekly audits, periodic watcher execution, and other time-based automation.

## Scheduling Patterns

### Pattern 1: Cron (Linux/Mac)

Edit crontab:
```bash
crontab -e
```

### Pattern 2: Windows Task Scheduler

Use PowerShell or GUI:
```powershell
# Open Task Scheduler
taskschd.msc
```

## Pre-configured Schedules

### Daily Briefing (8:00 AM)

Generate a daily summary every morning.

**Cron:**
```bash
# Daily briefing at 8:00 AM
0 8 * * * cd /path/to/AI_Employee_Vault && python3 scripts/orchestrator.py . --briefing
```

**Windows Task Scheduler:**
```powershell
$action = New-ScheduledTaskAction -Execute "python3" `
  -Argument "scripts/orchestrator.py . --briefing" `
  -WorkingDirectory "C:\path\to\AI_Employee_Vault"

$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

Register-ScheduledTask -TaskName "AI_Employee_Daily_Briefing" `
  -Action $action -Trigger $trigger -User "Saif"
```

### Weekly Audit (Monday 9:00 AM)

Generate weekly business audit and CEO briefing.

**Cron:**
```bash
# Weekly audit every Monday at 9:00 AM
0 9 * * 1 cd /path/to/AI_Employee_Vault && python3 scripts/orchestrator.py . --weekly-audit
```

**Windows:**
```powershell
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM

Register-ScheduledTask -TaskName "AI_Employee_Weekly_Audit" `
  -Action $action -Trigger $trigger -User "Saif"
```

### Gmail Watcher (Every 5 Minutes)

Check for new emails continuously.

**Cron:**
```bash
# Check Gmail every 5 minutes
*/5 * * * * cd /path/to/AI_Employee_Vault && python3 scripts/watchers/gmail_watcher.py . --once
```

**Windows:**
```powershell
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask -TaskName "AI_Employee_Gmail_Watcher" `
  -Action $action -Trigger $trigger -User "Saif"
```

### File Watcher (Continuous)

Run filesystem watcher in background.

**Systemd Service (Linux):**
```ini
# /etc/systemd/system/ai-employee-file-watcher.service
[Unit]
Description=AI Employee File Watcher
After=network.target

[Service]
Type=simple
User=saif
WorkingDirectory=/path/to/AI_Employee_Vault
ExecStart=/usr/bin/python3 scripts/watchers/filesystem_watcher.py .
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable ai-employee-file-watcher
sudo systemctl start ai-employee-file-watcher
```

### WhatsApp Watcher (Every 30 Seconds)

**Note:** Too frequent for cron. Run as background service instead.

```bash
# Start in background
nohup python3 scripts/watchers/whatsapp_watcher.py . --interval 30 > /tmp/whatsapp_watcher.log 2>&1 &
```

## Schedule Templates

### Full AI Employee Schedule

```bash
# AI Employee Cron Schedule
# Edit with: crontab -e

# Environment
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin

# Daily briefing (8:00 AM)
0 8 * * * cd /path/to/AI_Employee_Vault && python3 scripts/orchestrator.py . --briefing

# Weekly audit (Monday 9:00 AM)
0 9 * * 1 cd /path/to/AI_Employee_Vault && python3 scripts/orchestrator.py . --weekly-audit

# Gmail watcher (every 5 minutes)
*/5 * * * * cd /path/to/AI_Employee_Vault && python3 scripts/watchers/gmail_watcher.py . --once

# File watcher (every 2 minutes)
*/2 * * * * cd /path/to/AI_Employee_Vault && python3 scripts/watchers/filesystem_watcher.py . --once

# Cleanup old logs (Sunday 11:00 PM)
0 23 * * 0 cd /path/to/AI_Employee_Vault && python3 scripts/cleanup.py --days 30

# Backup vault (Daily 11:30 PM)
30 23 * * * cd /path/to/AI_Employee_Vault && bash scripts/backup.sh
```

### Windows Full Schedule (PowerShell)

```powershell
# AI Employee Scheduled Tasks
# Run as Administrator

$workingDir = "C:\path\to\AI_Employee_Vault"
$python = "python3"

# Daily Briefing
$action = New-ScheduledTaskAction -Execute $python `
  -Argument "scripts/orchestrator.py . --briefing" `
  -WorkingDirectory $workingDir
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "AI_Employee/Daily_Briefing" `
  -Action $action -Trigger $trigger -User "Saif"

# Weekly Audit
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM
Register-ScheduledTask -TaskName "AI_Employee/Weekly_Audit" `
  -Action $action -Trigger $trigger -User "Saif"

# Gmail Watcher
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Minutes 5)
$action = New-ScheduledTaskAction -Execute $python `
  -Argument "scripts/watchers/gmail_watcher.py . --once" `
  -WorkingDirectory $workingDir
Register-ScheduledTask -TaskName "AI_Employee/Gmail_Watcher" `
  -Action $action -Trigger $trigger -User "Saif"
```

## Orchestrator Flags

### Available Modes

```bash
# Standard run - process all pending actions
python3 scripts/orchestrator.py .

# Daily briefing mode
python3 scripts/orchestrator.py . --briefing

# Weekly audit mode
python3 scripts/orchestrator.py . --weekly-audit

# Process only emails
python3 scripts/orchestrator.py . --type email

# Process only payments
python3 scripts/orchestrator.py . --type payment

# Dry run (no changes)
python3 scripts/orchestrator.py . --dry-run

# Verbose logging
python3 scripts/orchestrator.py . --verbose
```

## Monitoring Scheduled Tasks

### Check Cron Jobs

```bash
# List all cron jobs
crontab -l

# Check cron logs
grep CRON /var/log/syslog
```

### Check Windows Tasks

```powershell
# List all AI Employee tasks
Get-ScheduledTask -TaskPath "\AI_Employee\"

# Check task status
Get-ScheduledTask -TaskName "AI_Employee_Daily_Briefing"

# View task history
Get-ScheduledTaskInfo -TaskName "AI_Employee_Daily_Briefing"
```

### View Logs

```bash
# Orchestrator logs
tail -f AI_Employee_Vault/logs/orchestrator.log

# Watcher logs
tail -f AI_Employee_Vault/logs/watchers.log

# System logs (Linux)
journalctl -u ai-employee-file-watcher -f
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check user permissions, working directory |
| Python not found | Use absolute path to python3 |
| File not found | Verify working directory in task config |
| Task runs but fails | Check logs, add --verbose flag |
| Multiple instances | Add lock file mechanism |

## Best Practices

1. **Stagger schedules** - Don't run all tasks at same time
2. **Add logging** - Always log output for debugging
3. **Handle failures** - Set up email alerts for failed tasks
4. **Review regularly** - Check task execution history weekly
5. **Backup configs** - Save cron/task scheduler configs to Git (without secrets)

## Resources

- [Cron Schedule Generator](https://crontab.guru/)
- [Windows Task Scheduler Reference](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [Systemd Service Templates](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
