# Silver Tier - Quick Start Reference

## ✅ What's Implemented

### Gmail Watcher
- ✅ Monitors Gmail every 2 minutes
- ✅ Creates action files in `Needs_Action/`
- ✅ OAuth 2.0 authentication
- ✅ Filters unread, important emails

### LinkedIn Poster
- ✅ Creates post drafts for approval
- ✅ Human-in-the-loop workflow
- ✅ Auto-publishes approved posts
- ✅ Saves LinkedIn session

---

## 🚀 Quick Commands

### Gmail Watcher

```bash
cd AI_Employee_Vault

# First time: Authenticate
python3 scripts/watchers/setup_gmail_oauth.py ~/.ai_employee/gmail_credentials.json .

# Test (run once)
python3 scripts/watchers/gmail_watcher.py . --once --verbose

# Run continuously (every 2 minutes)
python3 scripts/watchers/gmail_watcher.py . --interval 120
```

### LinkedIn Poster

```bash
cd AI_Employee_Vault

# Create a post draft
python3 scripts/linkedin_poster.py create \
  --text "Your post content here" \
  --hashtags "AI,Automation,Business" \
  --vault .

# List pending drafts
python3 scripts/linkedin_poster.py list-pending --vault .

# Approve (move to Approved folder)
# Windows: Move-Item Pending_Approval/LINKEDIN_*.md Approved/

# Publish approved posts
python3 scripts/linkedin_poster.py publish --vault .
```

---

## 📁 File Locations

```
AI_Employee_Vault/
├── scripts/
│   ├── watchers/
│   │   ├── gmail_watcher.py         # Gmail monitoring
│   │   ├── setup_gmail_oauth.py     # OAuth setup
│   │   └── filesystem_watcher.py    # File monitoring
│   └── linkedin_poster.py           # LinkedIn automation
├── Needs_Action/                     # New action items
├── Pending_Approval/                 # Awaiting approval
├── Approved/                         # Ready to execute
├── Done/                             # Completed
└── SILVER_TIER_SETUP.md              # Full setup guide
```

---

## 🔧 Troubleshooting

### Gmail Issues

**No emails detected:**
```bash
# Check token exists
ls token.json

# Re-authenticate
python3 scripts/watchers/setup_gmail_oauth.py ~/.ai_employee/gmail_credentials.json .
```

**Module not found:**
```bash
pip install -r requirements.txt
```

### LinkedIn Issues

**Browser won't open:**
```bash
# Reinstall Playwright
playwright install chromium
```

**Not logged in:**
- Browser will open and wait for you to log in
- Session saved after first login

---

## 📝 Example Workflow

### 1. Email Arrives

```
Gmail Watcher detects email
↓
Creates: Needs_Action/EMAIL_Inquiry_20260107_103000.md
↓
Qwen Code processes it
↓
Drafts reply in Pending_Approval/
↓
You approve (move to Approved/)
↓
Email sent
```

### 2. LinkedIn Post

```
Qwen creates post draft
↓
Saved to: Pending_Approval/LINKEDIN_POST_*.md
↓
You review content
↓
Move to Approved/
↓
Run: python3 scripts/linkedin_poster.py publish
↓
Post published to LinkedIn
```

---

## 🎯 Silver Tier Checklist

- [ ] Dependencies installed
- [ ] Gmail OAuth configured
- [ ] Test email detected
- [ ] Action file created
- [ ] LinkedIn post draft created
- [ ] Post published successfully
- [ ] Qwen Code processing items

---

## 📚 Documentation

- **Full Setup:** `SILVER_TIER_SETUP.md`
- **Skills:** `.qwen/skills/gmail-watcher/`, `.qwen/skills/linkedin-poster/`
- **Hackathon Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`

---

## 💡 Next Steps

1. **Test Gmail Watcher** - Send yourself a test email
2. **Test LinkedIn Poster** - Create and publish a test post
3. **Configure Qwen Code** - Set up prompts for processing
4. **Add Scheduling** - Set up cron/Task Scheduler

---

**Need Help?** See `SILVER_TIER_SETUP.md` for detailed instructions.
