---
name: linkedin-poster
description: |
  Automatically post updates to LinkedIn for business promotion and lead generation.
  Uses Playwright for browser automation. Creates drafts for human approval before posting.
  Supports text posts, images, and hashtags. Fully autonomous - no manual intervention required.
---

# LinkedIn Poster

**Autonomous** LinkedIn posting for business promotion and lead generation.

## Overview

LinkedIn Poster automatically creates and publishes posts to LinkedIn using Playwright browser automation. All posts follow the approval workflow:

1. **Auto-created** → Based on business goals, achievements, or updates
2. **Draft saved** → `/Pending_Approval`
3. **Human reviews** → Content, timing, tone
4. **Approve** → Move to `/Approved`
5. **Post published** → Via Playwright (automatic)
6. **Logged** → Moved to `/Done`

## Prerequisites

1. **Playwright MCP Server** running
2. **LinkedIn session** authenticated (first-time manual login)
3. **Python dependencies**: playwright

```bash
# Start Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Install playwright
pip install playwright
playwright install chromium
```

## Quick Start

### Create Post Draft

```bash
python3 .qwen/skills/linkedin-poster/scripts/create_draft.py \
  --text "Excited to announce our new AI automation service!" \
  --hashtags "AI,Automation,Business"
```

### Review and Approve

1. Check `/Pending_Approval/LINKEDIN_post_*.md`
2. Review content
3. Move to `/Approved` to publish (automatic)

### Publish Approved Posts

```bash
python3 .qwen/skills/linkedin-poster/scripts/publish.py \
  --vault ./AI_Employee_Vault
```

## Automated Workflow

### How It Works

```
┌─────────────────┐
│ Business Goals  │
│ Company Events  │
│ Milestones      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Qwen Code       │
│ Creates Draft   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pending_Approval│ ◄── Human Review
└────────┬────────┘
         │
         ▼ (Move to Approved)
┌─────────────────┐
│ Approved        │ ◄── Auto-publish
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Posted to       │
│ LinkedIn        │
└─────────────────┘
```

### Qwen Code Integration

When Qwen Code is running, it will automatically:

1. **Monitor** business goals and achievements
2. **Create** LinkedIn post drafts when appropriate
3. **Save** to `/Pending_Approval`
4. **Publish** approved posts automatically

**Example Prompt:**
```
Review our Business_Goals.md and recent achievements.
Create LinkedIn post drafts for any noteworthy updates.
Save them to Pending_Approval for review.
Then publish any approved posts.
```

## Post Templates

### Business Update

```markdown
---
type: linkedin_post
status: draft
created: 2026-01-07T10:30:00
hashtags: AI, Automation, Business
---

# LinkedIn Post Draft

## Content

🚀 Exciting news!

We've just launched our new AI Employee service that helps businesses automate 80% of their routine tasks.

✅ Save 20+ hours per week
✅ Reduce operational costs
✅ 24/7 autonomous operation

Interested in learning more? DM me!

#AI #Automation #Business #Innovation

---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

### Weekly Achievement

```markdown
---
type: linkedin_post
status: draft
created: 2026-01-07T10:30:00
hashtags: Achievement, AI, Productivity
---

# LinkedIn Post Draft

## Content

This week our AI Employee helped clients:

📧 Process 500+ emails automatically
💬 Respond to 50+ urgent WhatsApp messages
📊 Generate 20+ CEO briefings
⏰ Save 100+ hours of manual work

Ready to automate your workflow? Let's talk!

#AI #Automation #Productivity #BusinessGrowth

---

## To Approve
Move this file to /Approved folder.
```

## Configuration

### Posting Schedule

Edit `Business_Goals.md` to set posting frequency:

```markdown
## LinkedIn Strategy
- Post frequency: 3x per week
- Best times: 9 AM, 12 PM, 5 PM
- Content mix: 40% insights, 40% achievements, 20% promotions
```

### Hashtag Strategy

```python
DEFAULT_HASHTAGS = [
    'AI',
    'Automation',
    'Business',
    'Productivity',
    'Tech'
]
```

## Scripts

### create_draft.py

Create a new LinkedIn post draft.

```bash
python3 .qwen/skills/linkedin-poster/scripts/create_draft.py \
  --text "Your post content" \
  --hashtags "AI,Automation,Business" \
  --vault ./AI_Employee_Vault
```

**Options:**
- `--text, -t`: Post content (required)
- `--hashtags, -H`: Comma-separated hashtags (without #)
- `--schedule, -s`: Scheduled publish time (ISO format)
- `--vault, -v`: Path to vault (default: current dir)

### publish.py

Publish all approved posts.

```bash
python3 .qwen/skills/linkedin-poster/scripts/publish.py \
  --vault ./AI_Employee_Vault
```

**Options:**
- `--vault, -v`: Path to vault (default: current dir)
- `--list-pending`: Show pending drafts
- `--list-approved`: Show approved posts

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Re-authenticate LinkedIn manually in browser |
| Post content not filling | Script will try 3 methods: direct insert, paste, then typing. Wait for it to complete. |
| Post not publishing | Check character limit (3000 max). Click the 'Post' button manually when prompted. |
| Hashtags not working | Use commas in frontmatter, spaces in content |
| Image upload fails | Use supported formats (JPG, PNG, GIF) |
| Browser won't launch | Run `playwright install chromium` |

## Best Practices

1. **Post consistently** - 3-5 times per week
2. **Use engaging content** - Questions, stories, insights
3. **Include hashtags** - 3-5 relevant tags
4. **Timing matters** - Post during business hours (9 AM - 5 PM)
5. **Always review** - Never skip human approval step
6. **Track performance** - Monitor engagement in `/Done` folder

## Example Session

```bash
# 1. Start Playwright server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# 2. Create a post draft
python3 .qwen/skills/linkedin-poster/scripts/create_draft.py \
  -t "Just completed our first Silver Tier deployment! 🎉" \
  -H "AI,Automation,Milestone" \
  -v ./AI_Employee_Vault

# 3. Review the draft
cat ./AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md

# 4. Approve (move to Approved folder)
mv ./AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md \
   ./AI_Employee_Vault/Approved/

# 5. Publish
python3 .qwen/skills/linkedin-poster/scripts/publish.py \
  -v ./AI_Employee_Vault
```

## Resources

- [Playwright MCP](../browsing-with-playwright/SKILL.md)
- [Approval Workflow](../approval-workflow/SKILL.md)
- [Silver Tier Guide](../../../SILVER_TIER_SKILLS.md)
