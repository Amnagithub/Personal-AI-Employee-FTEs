# Gold Tier Setup Guide

**Complete setup instructions for Odoo, Facebook/Instagram, Ralph Wiggum Loop, CEO Briefing, and Audit Logging**

---

## Prerequisites

Before starting Gold Tier setup, ensure you have:

1. ✅ **Silver Tier complete** (Gmail, WhatsApp, LinkedIn working)
2. ✅ **Docker Desktop** installed and running
3. ✅ **Python 3.13+** installed
4. ✅ **Facebook Developer Account** (or create one)

---

## Step 1: Install Dependencies

```cmd
cd AI_Employee_Vault

# Install/upgrade all dependencies
pip install -r requirements.txt

# Verify installation
python --version  # Should be 3.13+
```

---

## Step 2: Setup Odoo Community Edition

### 2.1 Start Odoo with Docker Compose

```cmd
cd AI_Employee_Vault\odoo

# Start Odoo and PostgreSQL
docker-compose up -d

# Wait for Odoo to be ready (takes ~30 seconds)
timeout 30

# Check if Odoo is running
docker ps | findstr odoo

# View logs if needed
docker logs odoo_community -f
```

**Expected output:**
```
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS         PORTS                    NAMES
abc123         odoo:19.0      "/entrypoint.sh odoo"    2 minutes ago   Up 2 minutes   0.0.0.0:8069->8069/tcp   odoo_community
def456         postgres:15    "docker-entrypoint.s…"   2 minutes ago   Up 2 minutes   5432/tcp                 odoo_postgres
```

### 2.2 Access Odoo Web Interface

1. Open browser: http://localhost:8069
2. Create new database:
   - **Master password:** `admin` (default in docker-compose)
   - **Database name:** `ai_employee`
   - **Email:** `admin@example.com`
   - **Password:** `admin`
   - **Language:** English
   - **Country:** Your country
   - ✅ Check "Demo data" (for testing)

3. Click **Create Database**

### 2.3 Install Required Odoo Modules

After database creation:

1. Go to **Apps** menu
2. Search and install:
   - **Invoicing** (or Accounting)
   - **Contacts**
   - **Products**

### 2.4 Create API User

1. Go to **Settings** → **Users & Companies** → **Users**
2. Click **New**
3. Fill in:
   - **Name:** AI Employee
   - **Email:** ai_employee@example.com
   - **Password:** ai_employee_api
4. Set access rights:
   - **Accounting/Invoicing:** Administrator
5. Click **Save**

### 2.5 Test Odoo Connection

```cmd
# Test Odoo is accessible
curl http://localhost:8069

# Should return HTML
```

---

## Step 3: Setup Facebook/Instagram Integration

### 3.1 Create Facebook Developer Account

1. Go to: https://developers.facebook.com/
2. Click **Get Started**
3. Accept terms
4. Verify account (if required)

### 3.2 Create Facebook App

1. Go to: https://developers.facebook.com/apps/
2. Click **Create App**
3. Select app type: **Business**
4. Fill in:
   - **App name:** AI Employee Social
   - **App contact email:** your email
5. Click **Create App**

### 3.3 Add Facebook Graph API

1. In your App dashboard, click **Add Product**
2. Find **Graph API** and click **Set Up**

### 3.4 Request Permissions

1. Go to **App Review** → **Permissions and Features**
2. Request advanced access for:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_manage_comments`
   - `pages_manage_engagement` (optional)

**Note:** For personal use, you don't need App Review approval. For production apps with other users, you'll need to submit for review.

### 3.5 Get Page Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your App from dropdown
3. Click **Generate Access Token**
4. Grant permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
5. Click **Generate Token**
6. Copy the **User Access Token**

### 3.6 Get Long-Lived Token

```cmd
# Exchange short-lived token for long-lived token (60 days)
curl -G "https://graph.facebook.com/v19.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

Copy the returned `access_token` (this is your long-lived token).

### 3.7 Get Page ID

```cmd
# Get your Page ID
curl -G "https://graph.facebook.com/v19.0/me/accounts" \
  -d "access_token=YOUR_LONG_LIVED_TOKEN"
```

Copy the `id` of your page.

### 3.8 Get Instagram Account ID

```cmd
# Get Instagram Business Account ID
curl -G "https://graph.facebook.com/v19.0/YOUR_PAGE_ID/instagram_accounts" \
  -d "access_token=YOUR_LONG_LIVED_TOKEN"
```

**Note:** Instagram account must be:
- Business type (not personal)
- Linked to your Facebook Page

### 3.9 Update .env File

Add these lines to `.env` in project root:

```env
# =============================================================================
# ODOO CONFIGURATION (Gold Tier)
# =============================================================================
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=ai_employee
ODOO_PASSWORD=ai_employee_api

# =============================================================================
# FACEBOOK/INSTAGRAM CONFIGURATION (Gold Tier)
# =============================================================================
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_ACCESS_TOKEN=your_long_lived_token_here
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id_here
```

---

## Step 4: Test MCP Servers

### 4.1 Start Odoo MCP Server

```cmd
# In new terminal
python .qwen\skills\odoo-mcp\scripts\odoo_mcp_server.py --port 8810

# Should see:
# Odoo MCP Server starting on localhost:8810
```

### 4.2 Test Odoo MCP

```cmd
# In another terminal
python .qwen\skills\odoo-mcp\scripts\test-connection.py

# Should see:
# ✅ Health check passed
# ✅ Contact created
# ✅ Financial summary retrieved
```

### 4.3 Start Facebook MCP Server

```cmd
# In new terminal
python .qwen\skills\facebook-mcp\scripts\facebook_mcp_server.py --port 8811

# Should see:
# Facebook/Instagram MCP Server starting on localhost:8811
```

### 4.4 Test Facebook MCP

```cmd
# In another terminal
python .qwen\skills\facebook-mcp\scripts\test-connection.py

# Should see:
# ✅ Health check passed
# ✅ Retrieved X Facebook posts
# ✅ Retrieved X Instagram posts
```

---

## Step 5: Test Ralph Wiggum Loop

```cmd
# Test Ralph Wiggum Loop
python AI_Employee_Vault\scripts\ralph_wiggum.py ^
  "Read Business_Goals.md and summarize the objectives" ^
  --max-iterations 3 ^
  --verbose

# Should see:
# 🚀 Starting Ralph Wiggum Loop
# 📍 Iteration 1/3
# 🤖 Running Qwen Code...
# ✅ Completion promise detected
```

---

## Step 6: Test CEO Briefing Generation

```cmd
# Generate CEO briefing
python AI_Employee_Vault\scripts\ceo_briefing.py --vault AI_Employee_Vault --verbose

# Should see:
# 📊 Generating CEO Briefing
# 📈 Fetching financial data from Odoo...
# 📋 Analyzing completed tasks...
# 📱 Fetching social media data...
# ✅ Briefing saved to: AI_Employee_Vault\Briefings\2026-04-14_Monday_Briefing.md
```

**View the briefing:**
```cmd
type AI_Employee_Vault\Briefings\2026-04-14_Monday_Briefing.md
```

---

## Step 7: Test Audit Logging

```cmd
# Generate audit report
python AI_Employee_Vault\scripts\audit_logger.py ^
  --vault AI_Employee_Vault ^
  --action report ^
  --days 7

# Should see formatted markdown report with:
# - Total actions
# - Success rate
# - Actions by actor
# - Errors (if any)
```

---

## Step 8: Start Master Orchestrator

### 8.1 Start Everything

```cmd
cd AI_Employee_Vault

# Start master orchestrator
python scripts\orchestrator.py . --verbose
```

**What orchestrator does:**
1. ✅ Starts Odoo via Docker Compose
2. ✅ Starts Odoo MCP server (port 8810)
3. ✅ Starts Facebook MCP server (port 8811)
4. ✅ Starts all watchers (Gmail, WhatsApp, File)
5. ✅ Schedules recurring tasks:
   - Daily briefing at 8:00 AM
   - Weekly CEO briefing on Monday 9:00 AM
   - Weekly audit on Sunday 11:00 PM
   - Log cleanup at midnight
   - Health check every 5 minutes

### 8.2 Verify All Processes

```cmd
# Check running Python processes
tasklist | findstr python

# Should see:
# - orchestrator.py
# - odoo_mcp_server.py
# - facebook_mcp_server.py
# - gmail_watcher.py
# - whatsapp_watcher.py
# - filesystem_watcher.py
```

### 8.3 Graceful Shutdown

```cmd
# Press Ctrl+C to stop orchestrator
# All processes will be stopped gracefully
```

---

## Step 9: Integration Testing

### 9.1 End-to-End Invoice Flow

**Test complete invoice workflow:**

1. **Create invoice via Odoo MCP:**
```cmd
curl -X POST http://localhost:8810 ^
  -H "Content-Type: application/json" ^
  -d "{\"tool\":\"odoo_create_invoice\",\"params\":{\"partner_name\":\"Test Client\",\"partner_email\":\"test@example.com\",\"invoice_lines\":[{\"name\":\"Consulting\",\"quantity\":10,\"price_unit\":150,\"account_id\":1}]}}"
```

2. **Check approval request created:**
```cmd
dir Pending_Approval\ODOO_*.md
```

3. **Approve invoice:**
```cmd
move Pending_Approval\ODOO_*.md Approved\
```

4. **Verify invoice posted in Odoo:**
   - Open http://localhost:8069
   - Login as admin
   - Go to Invoicing → Customer Invoices
   - Should see new invoice

### 9.2 Facebook Post Flow

**Test complete Facebook post workflow:**

1. **Qwen creates post draft:**
   - Qwen monitors business events
   - Creates `Pending_Approval/FACEBOOK_POST_*.md`

2. **Human approves:**
   - Review content
   - Move to `Approved/`

3. **MCP publishes post:**
   - Orchestrator detects approved file
   - Calls `facebook_create_post` via MCP
   - Post appears on Facebook Page

### 9.3 CEO Briefing Flow

**Test weekly briefing generation:**

1. **Manual trigger:**
```cmd
python AI_Employee_Vault\scripts\ceo_briefing.py --vault AI_Employee_Vault
```

2. **Verify briefing created:**
```cmd
dir AI_Employee_Vault\Briefings\
```

3. **Review in Obsidian:**
   - Open vault in Obsidian
   - Navigate to `Briefings/`
   - Open latest briefing

---

## Step 10: Configure Windows Task Scheduler

For automatic scheduling without running orchestrator 24/7:

### 10.1 Create Scheduled Tasks

**Daily Briefing (8:00 AM):**
```cmd
schtasks /create /tn "AI_Employee_Daily_Briefing" /tr "python AI_Employee_Vault\scripts\ceo_briefing.py --vault AI_Employee_Vault" /sc daily /st 08:00
```

**Weekly CEO Briefing (Monday 9:00 AM):**
```cmd
schtasks /create /tn "AI_Employee_Weekly_Briefing" /tr "python AI_Employee_Vault\scripts\ceo_briefing.py --vault AI_Employee_Vault --days 7" /sc weekly /d MON /st 09:00
```

**Weekly Audit (Sunday 11:00 PM):**
```cmd
schtasks /create /tn "AI_Employee_Weekly_Audit" /tr "python AI_Employee_Vault\scripts\audit_logger.py --vault AI_Employee_Vault --action report --days 7" /sc weekly /d SUN /st 23:00
```

### 10.2 Verify Scheduled Tasks

```cmd
# List all AI Employee tasks
schtasks /query | findstr AI_Employee

# Run task manually
schtasks /run /tn "AI_Employee_Daily_Briefing"
```

---

## Troubleshooting

### Odoo Won't Start

```cmd
# Check Docker
docker ps

# Check ports
netstat -an | findstr 8069

# Restart Odoo
cd AI_Employee_Vault\odoo
docker-compose down
docker-compose up -d

# Check logs
docker logs odoo_community
```

### Facebook Token Expired

```cmd
# Tokens expire after 60 days
# Generate new token at Graph API Explorer
# Update .env file
# Restart Facebook MCP server
```

### Ralph Wiggum Never Completes

```cmd
# Check state file
type \tmp\ralph_state.json

# Increase max iterations
python AI_Employee_Vault\scripts\ralph_wiggum.py "..." --max-iterations 20

# Use verbose mode
python AI_Employee_Vault\scripts\ralph_wiggum.py "..." --verbose
```

### CEO Briefing Empty

```cmd
# Check Odoo has transactions
# Check Done/ folder has files
# Check date range (use --days parameter)

python AI_Employee_Vault\scripts\ceo_briefing.py --days 30
```

### MCP Servers Won't Connect

```cmd
# Check servers are running
tasklist | findstr mcp

# Check ports
netstat -an | findstr 8810
netstat -an | findstr 8811

# Restart servers
# Check .env credentials are correct
```

---

## Verification Checklist

Use this checklist to verify Gold Tier is fully operational:

- [ ] Odoo running at http://localhost:8069
- [ ] Odoo MCP server on port 8810
- [ ] Facebook MCP server on port 8811
- [ ] Test connection scripts pass
- [ ] Ralph Wiggum Loop completes successfully
- [ ] CEO briefing generates correctly
- [ ] Audit logging captures actions
- [ ] Orchestrator starts all processes
- [ ] Scheduled tasks configured (optional)
- [ ] .env file has all credentials
- [ ] All watchers running (Gmail, WhatsApp, File)
- [ ] Approval workflow functional

---

## Next Steps

### Daily Operations

1. Start orchestrator in morning: `python scripts\orchestrator.py .`
2. Check `Pending_Approval/` for items needing review
3. Review `Briefings/` for CEO reports
4. Check `Logs/` for audit trail
5. Stop orchestrator at night: Ctrl+C

### Weekly Tasks

1. Review weekly CEO briefing
2. Check audit report for errors
3. Refresh Facebook token if needed (every 60 days)
4. Review and archive old logs

### Monthly Tasks

1. Backup vault folder
2. Backup Odoo data: `docker-compose exec db pg_dump -U odoo ai_employee > backup.sql`
3. Review and rotate credentials
4. Update dependencies: `pip install -r requirements.txt --upgrade`

---

## Resources

- [Gold Tier Complete Doc](../GOLD_TIER_COMPLETE.md)
- [Odoo MCP Skill](../.qwen/skills/odoo-mcp/SKILL.md)
- [Facebook MCP Skill](../.qwen/skills/facebook-mcp/SKILL.md)
- [Ralph Wiggum Skill](../.qwen/skills/ralph-wiggum/SKILL.md)
- [Main Hackathon Blueprint](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)

---

**🎉 Gold Tier Setup Complete!**

Your AI Employee now has full business intelligence capabilities:
- 💼 Odoo ERP for accounting
- 📱 Facebook + Instagram posting
- 🔄 Autonomous task completion
- 📊 Weekly CEO briefings
- 📝 Comprehensive audit logging

**Ready for production use!**
