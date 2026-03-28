---
name: linkedin-poster
description: |
  Automatically post updates to LinkedIn for business promotion and lead generation.
  Uses Playwright for browser automation. Creates drafts for human approval before posting.
  Supports text posts, images, and hashtags.
---

# LinkedIn Poster

Automate LinkedIn posts for business promotion and lead generation.

## Overview

LinkedIn Poster automates posting to LinkedIn using Playwright browser automation. All posts are created as drafts first, requiring human approval before publishing.

## Prerequisites

1. **Playwright MCP Server** running
2. **LinkedIn session** authenticated
3. **Python dependencies**: playwright

```bash
# Start Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh
```

## Quick Start

### Create Post Draft

```bash
python3 .qwen/skills/linkedin-poster/scripts/create_draft.py \
  --text "Excited to announce our new AI automation service!" \
  --hashtags "AI #Automation #Business"
```

### Review and Approve

1. Check `/Pending_Approval/LINKEDIN_post_*.md`
2. Review content
3. Move to `/Approved` to publish

### Publish Approved Post

```bash
python3 scripts/linkedin_poster.py . --publish-approved
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

## Configuration

### Posting Schedule

```bash
# Post at specific times
python3 scripts/linkedin_poster.py . --schedule "09:00"
```

### Hashtag Strategy

```python
HASHTAGS = [
    '#AI',
    '#Automation',
    '#Business',
    '#Productivity',
    '#Tech'
]
```

## Workflow

1. **Qwen creates draft** → Based on business goals
2. **Draft saved** → /Pending_Approval
3. **Human reviews** → Content, timing, tone
4. **Approve** → Move to /Approved
5. **Post published** → Via Playwright
6. **Logged** → To audit file

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login failed | Re-authenticate LinkedIn manually |
| Post not publishing | Check character limit (3000) |
| Hashtags not working | Use spaces, not commas |
| Image upload fails | Use supported formats (JPG, PNG) |

## Best Practices

1. **Post consistently** - 3-5 times per week
2. **Use engaging content** - Questions, stories, insights
3. **Include hashtags** - 3-5 relevant tags
4. **Timing matters** - Post during business hours
5. **Always approve** - Never auto-publish without review
