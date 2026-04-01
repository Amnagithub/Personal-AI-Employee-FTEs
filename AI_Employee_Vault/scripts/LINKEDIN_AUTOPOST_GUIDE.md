# LinkedIn Auto-Post Guide

## Quick Start

### Step 1: Setup (First Time Only)

```bash
# Run the setup script to configure Chrome and test login
python AI_Employee_Vault/scripts/setup_linkedin.py
```

This will:
- Find your Chrome profile
- Open LinkedIn in your Chrome browser
- Save your login session for future use

### Step 2: Auto-Post (One Command)

```bash
# Create and publish immediately
python AI_Employee_Vault/scripts/linkedin_poster.py auto \
  --text "Excited to announce our new AI automation service!" \
  --hashtags "AI,Automation,Business"
```

### Step 3: Or Use Approval Workflow

```bash
# Create draft (requires approval)
python AI_Employee_Vault/scripts/linkedin_poster.py create \
  --text "Your post content" \
  --hashtags "AI,Business"

# Review draft in: AI_Employee_Vault/Pending_Approval/

# Move file to Approved folder to publish

# Publish all approved posts
python AI_Employee_Vault/scripts/linkedin_poster.py publish --vault AI_Employee_Vault
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `auto` | Create and publish immediately (no approval) |
| `create` | Create draft for approval |
| `publish` | Publish approved posts |
| `list-pending` | Show pending drafts |
| `list-approved` | Show approved posts |

---

## Examples

### Auto-Post Mode (No Approval)

```bash
# Simple post
python AI_Employee_Vault/scripts/linkedin_poster.py auto \
  --text "Hello LinkedIn! This is an automated post." \
  --hashtags "AI,Automation"

# Post with scheduling
python AI_Employee_Vault/scripts/linkedin_poster.py auto \
  --text "Check out our latest product!" \
  --hashtags "Tech,Innovation" \
  --schedule "2026-04-01T09:00:00"
```

### Approval Workflow Mode

```bash
# Create draft
python AI_Employee_Vault/scripts/linkedin_poster.py create \
  --vault AI_Employee_Vault \
  --text "Big announcement coming soon!" \
  --hashtags "Business,Growth"

# Review the draft file in Pending_Approval folder
# Edit if needed, then move to Approved folder

# Publish
python AI_Employee_Vault/scripts/linkedin_poster.py publish \
  --vault AI_Employee_Vault
```

---

## Troubleshooting

### Browser Won't Open

```bash
# Ensure Playwright is installed
pip install playwright
playwright install
```

### Login Failed / Session Expired

```bash
# Re-run setup to re-authenticate
python AI_Employee_Vault/scripts/setup_linkedin.py
```

### Chrome Not Found

Make sure Google Chrome is installed at:
- Windows: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Linux: `/usr/bin/google-chrome`
- macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

### Post Not Publishing

1. Check character limit (max 3000)
2. Ensure you're logged in to LinkedIn
3. Try manual posting via LinkedIn website
4. Check for LinkedIn service outages

---

## Configuration

### Use Different Chrome Profile

Edit `AI_Employee_Vault/scripts/linkedin_poster.py`:

```python
# Line ~195
chrome_profile = "Profile 1"  # Change from "Default"
```

### Enable Auto-Post by Default

Add `--auto-post` flag to publish commands:

```bash
python AI_Employee_Vault/scripts/linkedin_poster.py publish \
  --vault AI_Employee_Vault \
  --auto-post
```

---

## Best Practices

1. **Test First**: Run setup script before first auto-post
2. **Review Content**: Even with auto-post, review drafts before publishing
3. **Timing**: Post during business hours (9 AM - 5 PM)
4. **Frequency**: 3-5 posts per week for optimal engagement
5. **Hashtags**: Use 3-5 relevant hashtags per post
6. **Monitor**: Check LinkedIn for comments and engagement

---

## Workflow Integration

### Daily Auto-Post

```bash
# Add to cron/scheduler
0 9 * * 1-5 cd /path/to/project && \
  python AI_Employee_Vault/scripts/linkedin_poster.py auto \
    --text "Daily business update..." \
    --hashtags "Business,Daily"
```

### Weekly Summary

```bash
# Every Monday at 10 AM
0 10 * * 1 cd /path/to/project && \
  python AI_Employee_Vault/scripts/linkedin_poster.py auto \
    --text "Weekly business summary..." \
    --hashtags "Weekly,Business"
```

---

## Support

For issues:
1. Check logs in browser window
2. Review error messages in terminal
3. Re-run setup script
4. Try manual posting on LinkedIn website
