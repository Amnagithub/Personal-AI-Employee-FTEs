# Silver Tier Skills - Complete Guide

**Tagline:** *Functional Assistant with Multiple Watchers, MCP Integration, and Human-in-the-Loop*

**Estimated Time:** 20-30 hours

---

## Overview

Silver Tier builds on Bronze by adding:
- ✅ **Multiple Watchers** (Gmail + WhatsApp + File System)
- ✅ **Email MCP Integration** (Send/draft emails)
- ✅ **LinkedIn Auto-Posting** (Business promotion)
- ✅ **Planner System** (Multi-step task breakdown)
- ✅ **Approval Workflow** (Human-in-the-Loop)
- ✅ **Scheduler** (Cron/Task Scheduler integration)

---

## Skills Created

### 1. Email MCP (`email-mcp`)

**Purpose:** Send, draft, and manage emails via Gmail

**Location:** `.qwen/skills/email-mcp/`

**Files:**
```
.qwen/skills/email-mcp/
├── SKILL.md
├── scripts/
│   ├── mcp-client.py
│   ├── start-server.sh
│   ├── stop-server.sh
│   └── verify.py
└── references/
```

**Setup:**
```bash
# 1. Enable Gmail API at Google Cloud Console
# 2. Download credentials.json
mkdir -p ~/.ai_employee
cp credentials.json ~/.ai_employee/gmail_credentials.json

# 3. Start server
bash .qwen/skills/email-mcp/scripts/start-server.sh

# 4. Verify
python3 .qwen/skills/email-mcp/scripts/verify.py
```

**Usage:**
```bash
# Send email
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "client@example.com", "subject": "Invoice", "body": "..."}'
```

---

### 2. Gmail Watcher (`gmail-watcher`)

**Purpose:** Monitor Gmail for new important emails

**Location:** `.qwen/skills/gmail-watcher/` + `AI_Employee_Vault/scripts/watchers/gmail_watcher.py`

**Setup:**
```bash
# Install dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Run once (test)
python3 AI_Employee_Vault/scripts/watchers/gmail_watcher.py . --once

# Run continuously
python3 AI_Employee_Vault/scripts/watchers/gmail_watcher.py . --interval 120
```

**Output:** Creates `.md` files in `Needs_Action/` for each new email

---

### 3. WhatsApp Watcher (`whatsapp-watcher`)

**Purpose:** Monitor WhatsApp Web for urgent messages

**Location:** `.qwen/skills/whatsapp-watcher/`

**Setup:**
```bash
# Requires Playwright MCP running
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Run watcher
python3 AI_Employee_Vault/scripts/watchers/whatsapp_watcher.py . --interval 30
```

**Keywords Monitored:** urgent, asap, invoice, payment, help, emergency

---

### 4. LinkedIn Poster (`linkedin-poster`)

**Purpose:** Auto-post business updates to LinkedIn

**Location:** `.qwen/skills/linkedin-poster/`

**Workflow:**
1. Qwen creates draft → `Pending_Approval/LINKEDIN_post_*.md`
2. Human reviews content
3. Move to `Approved/` to publish
4. Orchestrator posts via Playwright

**Example Post:**
```markdown
---
type: linkedin_post
status: draft
hashtags: AI, Automation, Business
---

🚀 Exciting news! Our new AI Employee service...

#AI #Automation #Business
```

---

### 5. Planner (`planner`)

**Purpose:** Create Plan.md files for multi-step tasks

**Location:** `.qwen/skills/planner/`

**Example Plan:**
```markdown
---
type: plan
objective: Send invoice to Client A
created: 2026-01-07T10:30:00
status: in_progress
---

# Plan: Send Invoice

## Steps
- [x] Identify client
- [x] Calculate amount
- [ ] Generate invoice PDF
- [ ] Create email draft (APPROVAL REQUIRED)
- [ ] Send after approval
- [ ] Log transaction
```

---

### 6. Approval Workflow (`approval-workflow`)

**Purpose:** Human-in-the-Loop for sensitive actions

**Location:** `.qwen/skills/approval-workflow/`

**Folder Structure:**
```
AI_Employee_Vault/
├── Pending_Approval/    # Awaiting review
├── Approved/            # Ready to execute
├── Rejected/            # Declined
└── Approval_Logs/       # History
```

**Example Approval Request:**
```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A
- Reason: Invoice #123

## To Approve
Move to /Approved folder.
```

---

### 7. Scheduler (`scheduler`)

**Purpose:** Schedule recurring tasks

**Location:** `.qwen/skills/scheduler/`

**Common Schedules:**

**Daily Briefing (8 AM):**
```bash
# Cron
0 8 * * * cd /path/to/vault && python3 scripts/orchestrator.py . --briefing
```

**Weekly Audit (Monday 9 AM):**
```bash
# Cron
0 9 * * 1 cd /path/to/vault && python3 scripts/orchestrator.py . --weekly-audit
```

**Gmail Watcher (Every 5 min):**
```bash
# Cron
*/5 * * * * cd /path/to/vault && python3 scripts/watchers/gmail_watcher.py . --once
```

---

## Complete Silver Tier Setup

### Step 1: Install Dependencies

```bash
cd AI_Employee_Vault

# Python dependencies
pip install \
  google-auth \
  google-auth-oauthlib \
  google-auth-httplib2 \
  google-api-python-client \
  playwright \
  watchdog

# Playwright browsers
playwright install chromium
```

### Step 2: Configure Credentials

```bash
# Gmail API
mkdir -p ~/.ai_employee
cp /path/to/gmail_credentials.json ~/.ai_employee/

# LinkedIn (session via browser)
# Manual login at linkedin.com when Playwright starts
```

### Step 3: Start MCP Servers

```bash
# Email MCP
bash .qwen/skills/email-mcp/scripts/start-server.sh

# Playwright MCP (for WhatsApp, LinkedIn)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify
python3 .qwen/skills/email-mcp/scripts/verify.py
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py
```

### Step 4: Start Watchers

```bash
# Terminal 1: Gmail Watcher
python3 AI_Employee_Vault/scripts/watchers/gmail_watcher.py . --interval 120

# Terminal 2: WhatsApp Watcher
python3 AI_Employee_Vault/scripts/watchers/whatsapp_watcher.py . --interval 30

# Terminal 3: Filesystem Watcher
python3 AI_Employee_Vault/scripts/watchers/filesystem_watcher.py .
```

### Step 5: Set Up Scheduler

```bash
# Edit crontab
crontab -e

# Add Silver Tier schedules
0 8 * * * cd /path/to/vault && python3 scripts/orchestrator.py . --briefing
0 9 * * 1 cd /path/to/vault && python3 scripts/orchestrator.py . --weekly-audit
*/5 * * * * cd /path/to/vault && python3 scripts/watchers/gmail_watcher.py . --once
```

### Step 6: Run Qwen Code

```bash
cd AI_Employee_Vault
qwen
```

**Prompt:**
```
Check the Needs_Action folder for new items from watchers.
For each item:
1. Read and understand the content
2. Create a Plan.md if it's a multi-step task
3. Execute simple tasks directly
4. Create approval requests for sensitive actions
5. Move completed items to Done folder
```

---

## Silver Tier Checklist

- [ ] Email MCP server running
- [ ] Gmail Watcher monitoring inbox
- [ ] WhatsApp Watcher monitoring messages
- [ ] Filesystem Watcher monitoring Inbox folder
- [ ] LinkedIn Poster skill configured
- [ ] Planner system creating Plan.md files
- [ ] Approval Workflow folders created
- [ ] Scheduler configured (cron/Task Scheduler)
- [ ] Qwen Code processing action files
- [ ] Human reviewing approvals daily

---

## Testing Silver Tier

### Test 1: Email Arrival

1. Send yourself a test email
2. Wait 2-5 minutes
3. Check `Needs_Action/` for new EMAIL_*.md file
4. Run Qwen Code to process it

### Test 2: WhatsApp Message

1. Have someone message you with "urgent" keyword
2. Wait 1 minute
3. Check `Needs_Action/` for new WHATSAPP_*.md file
4. Run Qwen Code to process it

### Test 3: Email Sending

1. Qwen creates email draft approval request
2. Review in `Pending_Approval/`
3. Move to `Approved/`
4. Run orchestrator to send
5. Check email sent successfully

### Test 4: LinkedIn Post

1. Qwen creates post draft
2. Review content and timing
3. Approve by moving to `Approved/`
4. Orchestrator posts to LinkedIn

### Test 5: Daily Briefing

1. Wait for scheduled time (8 AM)
2. Check `Briefings/` for new briefing file
3. Review revenue, tasks, and suggestions

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Gmail Watcher not detecting emails | Check OAuth token, re-authenticate |
| Email MCP won't send | Verify Gmail API enabled |
| WhatsApp Watcher crashes | Restart Playwright MCP server |
| LinkedIn post fails | Re-login at linkedin.com |
| Plans not created | Check Qwen Code prompt instructions |
| Approvals not executing | Verify file in /Approved not /Pending_Approval |
| Scheduler not running | Check cron/Task Scheduler logs |

---

## Next Steps: Gold Tier

After mastering Silver Tier, upgrade to Gold:
- ✅ Odoo Accounting Integration
- ✅ Facebook/Instagram Posting
- ✅ Twitter (X) Integration
- ✅ Weekly CEO Briefing
- ✅ Ralph Wiggum Loop (Persistence)
- ✅ Comprehensive Audit Logging

---

## Resources

- [Main Hackathon Blueprint](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Email MCP Skill](./.qwen/skills/email-mcp/SKILL.md)
- [Gmail Watcher](./.qwen/skills/gmail-watcher/SKILL.md)
- [WhatsApp Watcher](./.qwen/skills/whatsapp-watcher/SKILL.md)
- [LinkedIn Poster](./.qwen/skills/linkedin-poster/SKILL.md)
- [Planner](./.qwen/skills/planner/SKILL.md)
- [Approval Workflow](./.qwen/skills/approval-workflow/SKILL.md)
- [Scheduler](./.qwen/skills/scheduler/SKILL.md)
