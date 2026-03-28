# Silver Tier Setup Guide
## Gmail Watcher + LinkedIn Poster - Complete Implementation

**Status:** ✅ Ready to Use
**Time:** 30-60 minutes for initial setup

---

## Quick Start Checklist

- [ ] Install Python dependencies
- [ ] Set up Gmail API credentials
- [ ] Authenticate Gmail OAuth
- [ ] Test Gmail Watcher
- [ ] Install Playwright browsers
- [ ] Test LinkedIn Poster
- [ ] Configure Qwen Code integration

---

## Step 1: Install Dependencies

### Install Python Packages

```bash
cd AI_Employee_Vault

# Using pip
pip install -r requirements.txt

# Or using uv (faster)
uv pip install -r requirements.txt
```

### Install Playwright Browsers

```bash
# Install Chromium browser for Playwright
playwright install chromium

# (Optional) Install system dependencies
playwright install-deps chromium
```

---

## Step 2: Set Up Gmail API Credentials

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** or select existing project
3. Name it: `AI Employee`
4. Click **"Create"**

### 2.2 Enable Gmail API

1. In your project, go to **"APIs & Services" > "Library"**
2. Search for **"Gmail API"**
3. Click on it and press **"Enable"**

### 2.3 Create OAuth Credentials

1. Go to **"APIs & Services" > "Credentials"**
2. Click **"+ CREATE CREDENTIALS" > "OAuth client ID"**
3. If prompted, configure **OAuth consent screen**:
   - User Type: **External**
   - App name: **AI Employee**
   - User support email: Your email
   - Developer contact: Your email
   - Click **"Save and Continue"**
   - Scopes: Skip this step
   - Test users: Add your email address
   - Click **"Save and Continue"**

4. Back to **Create OAuth Client ID**:
   - Application type: **Desktop app**
   - Name: **AI Employee Gmail**
   - Click **"Create"**

5. Download the credentials:
   - Click **"Download JSON"**
   - Save as `credentials.json`

### 2.4 Place Credentials File

```bash
# Option 1: In your home directory (recommended)
mkdir -p ~/.ai_employee
cp /path/to/credentials.json ~/.ai_employee/gmail_credentials.json

# Option 2: In your vault (for testing)
cp credentials.json AI_Employee_Vault/credentials.json
```

**⚠️ SECURITY:** Never commit `credentials.json` to Git!

---

## Step 3: Authenticate Gmail OAuth

### Run OAuth Setup

```bash
cd AI_Employee_Vault

# Run the OAuth setup script
python3 scripts/watchers/setup_gmail_oauth.py \
  ~/.ai_employee/gmail_credentials.json \
  .
```

### What Happens:

1. Browser opens automatically
2. Sign in to your Google account
3. Grant permissions to Gmail API
4. Token is saved to `AI_Employee_Vault/token.json`
5. Connection is tested

### Expected Output:

```
============================================================
Gmail OAuth Setup for AI Employee
============================================================

Credentials: /home/user/.ai_employee/gmail_credentials.json
Token will be saved to: ./token.json

Opening browser for authentication...

============================================================
✓ Authentication successful!
============================================================

Token saved to: ./token.json

You can now run the Gmail Watcher:
  python scripts/watchers/gmail_watcher.py . --interval 120

Testing connection to Gmail API...
✓ Connected to Gmail API
  Account: your.email@gmail.com
```

---

## Step 4: Test Gmail Watcher

### Run Once (Test Mode)

```bash
cd AI_Employee_Vault

# Check for new emails once
python3 scripts/watchers/gmail_watcher.py . --once --verbose
```

### Expected Output:

```
2026-01-07 10:30:00 - gmail_watcher - INFO - Starting GmailWatcher
2026-01-07 10:30:00 - gmail_watcher - INFO - Vault path: /path/to/vault
2026-01-07 10:30:00 - gmail_watcher - INFO - Checking for existing unread emails...
2026-01-07 10:30:01 - gmail_watcher - INFO - Connected to Gmail API
2026-01-07 10:30:02 - gmail_watcher - INFO - Found 2 new email(s)
2026-01-07 10:30:02 - gmail_watcher - INFO - Created action file: EMAIL_Project_Inquiry_20260107_103002.md
2026-01-07 10:30:02 - gmail_watcher - INFO - Created action file: EMAIL_Invoice_Request_20260107_103002.md
Processed 2 new email(s)
```

### Check Action Files

```bash
# List created action files
ls Needs_Action/

# View content of one
cat Needs_Action/EMAIL_*.md
```

### Run Continuously

```bash
# Run in background (checks every 2 minutes)
python3 scripts/watchers/gmail_watcher.py . --interval 120
```

**To stop:** Press `Ctrl+C`

---

## Step 5: Test LinkedIn Poster

### Create a Test Post Draft

```bash
cd AI_Employee_Vault

# Create a draft post
python3 scripts/linkedin_poster.py create \
  --text "Excited to share that I'm building an AI Employee system! 🚀

This autonomous agent handles email triage, social media posting, and business automation 24/7.

Key features:
✅ Gmail monitoring
✅ LinkedIn auto-posting  
✅ Human-in-the-loop approvals
✅ Multi-step task planning

#AI #Automation #Productivity #Innovation" \
  --hashtags "AI,Automation,Productivity,Innovation" \
  --vault .
```

### Expected Output:

```
✓ Draft created: /path/to/vault/Pending_Approval/LINKEDIN_POST_20260107_103000.md
  Location: /path/to/vault/Pending_Approval/LINKEDIN_POST_20260107_103000.md
  Status: Pending approval

To approve: Move file to Approved folder
To publish: python linkedin_poster.py publish --vault .
```

### Review the Draft

```bash
# View the draft
cat Pending_Approval/LINKEDIN_POST_*.md

# Or list all pending posts
python3 scripts/linkedin_poster.py list-pending --vault .
```

### Approve the Post

```bash
# Move to Approved folder (on Linux/Mac)
mv Pending_Approval/LINKEDIN_POST_*.md Approved/

# On Windows PowerShell
Move-Item Pending_Approval/LINKEDIN_POST_*.md Approved/
```

### Publish the Post

```bash
# Publish all approved posts
python3 scripts/linkedin_poster.py publish --vault .
```

### What Happens:

1. Browser opens (or uses existing session)
2. Navigates to LinkedIn
3. Creates new post
4. Fills in your content
5. Clicks "Post" button
6. Moves published post to `Done/` folder

**Note:** First time you'll need to log in to LinkedIn manually. The session is saved for future posts.

---

## Step 6: Configure Qwen Code Integration

### Create Company Handbook Entry

Add this to your `Company_Handbook.md`:

```markdown
## LinkedIn Posting Rules

- All posts must be reviewed before publishing
- Posts should be professional and value-adding
- Use 3-5 relevant hashtags
- No controversial topics
- Post frequency: 3-5 times per week
- Best times: 9-11 AM on weekdays

## Email Processing Rules

- Respond to client inquiries within 24 hours
- Flag payments over $500 for approval
- Archive newsletters after reading
- Forward technical issues to support queue
```

### Create Qwen Code Prompt Template

Create `AI_Employee_Vault/prompts/process_email.md`:

```markdown
# Process Incoming Email

You are an AI Employee. Process this email according to the Company Handbook.

## Steps

1. **Read and Understand**
   - Who sent it?
   - What do they want?
   - Is it urgent?

2. **Categorize**
   - Client inquiry → Draft reply
   - Invoice request → Generate invoice
   - Newsletter → Archive
   - Spam → Delete

3. **Take Action**
   - Simple reply → Draft email (requires approval)
   - Complex task → Create Plan.md
   - Payment → Create approval request

4. **Update Status**
   - Mark email as processed
   - Move to appropriate folder

## Output

- Draft email in Pending_Approval/ OR
- Plan.md in Plans/ OR
- Approval request in Pending_Approval/
```

---

## Step 7: Set Up Scheduling (Optional)

### Linux/Mac (Cron)

```bash
# Edit crontab
crontab -e

# Add these lines:

# Gmail Watcher - Every 5 minutes
*/5 * * * * cd /path/to/AI_Employee_Vault && python3 scripts/watchers/gmail_watcher.py . --once

# LinkedIn Post Scheduler - Daily at 9 AM
0 9 * * 1-5 cd /path/to/AI_Employee_Vault && python3 scripts/linkedin_poster.py publish --vault .
```

### Windows (Task Scheduler)

```powershell
# Open Task Scheduler
taskschd.msc

# Create Basic Task: "Gmail Watcher"
# Trigger: Daily
# Repeat task every: 5 minutes
# Action: Start a program
# Program: python3
# Arguments: scripts/watchers/gmail_watcher.py . --once
# Start in: C:\path\to\AI_Employee_Vault
```

---

## Troubleshooting

### Gmail Watcher Issues

**Problem:** `ModuleNotFoundError: No module named 'google'`

**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** `Credentials file not found`

**Solution:**
```bash
# Check file exists
ls ~/.ai_employee/gmail_credentials.json

# If not found, copy it there
cp /path/to/credentials.json ~/.ai_employee/gmail_credentials.json
```

**Problem:** `Token expired`

**Solution:**
```bash
# Delete old token
rm AI_Employee_Vault/token.json

# Re-run OAuth setup
python3 scripts/watchers/setup_gmail_oauth.py ~/.ai_employee/gmail_credentials.json .
```

**Problem:** `No emails detected`

**Solution:**
- Check Gmail query in `gmail_watcher.py` (line 33)
- Verify emails are marked as unread
- Check if they're in Inbox (not Spam/Other folders)

### LinkedIn Poster Issues

**Problem:** `playwright not installed`

**Solution:**
```bash
pip install playwright
playwright install chromium
```

**Problem:** `Not logged in to LinkedIn`

**Solution:**
- Browser will open and wait for you to log in
- Log in manually (first time only)
- Session is saved for future use

**Problem:** `Post button not found`

**Solution:**
- LinkedIn UI may have changed
- Try manual posting for now
- Check for script updates

---

## Testing Checklist

### Gmail Watcher

- [ ] OAuth authentication successful
- [ ] Token saved to `token.json`
- [ ] Test email sent to your account
- [ ] Gmail Watcher detects email
- [ ] Action file created in `Needs_Action/`
- [ ] Qwen Code processes action file
- [ ] Reply drafted and approved
- [ ] Email sent successfully

### LinkedIn Poster

- [ ] Draft created successfully
- [ ] Content formatted correctly
- [ ] Hashtags added
- [ ] Draft moved to `Approved/`
- [ ] Browser opens on publish command
- [ ] LinkedIn login successful
- [ ] Post published to LinkedIn
- [ ] File moved to `Done/`

---

## Next Steps

After Silver Tier is working:

1. **Monitor for a week** - Ensure watchers are catching all emails
2. **Refine Company Handbook** - Add more specific rules
3. **Add WhatsApp Watcher** - Similar to Gmail Watcher
4. **Upgrade to Gold Tier** - Add Odoo accounting, more integrations

---

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Playwright Documentation](https://playwright.dev/python/)
- [LinkedIn Brand Guidelines](https://brand.linkedin.com/policies)
- [Main Hackathon Blueprint](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review logs in `AI_Employee_Vault/logs/`
- Read the skill documentation in `.qwen/skills/`
