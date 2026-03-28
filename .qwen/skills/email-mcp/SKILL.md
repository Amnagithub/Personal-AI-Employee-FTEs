---
name: email-mcp
description: |
  Email integration via Gmail MCP. Send, draft, search, and manage emails.
  Use for sending invoices, replies, notifications, and email-based workflows.
  Requires Gmail API credentials and OAuth setup.
---

# Email MCP (Gmail Integration)

Send, draft, and manage emails via Gmail MCP server.

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable **Gmail API**: `APIs & Services > Library > Gmail API`
4. Create OAuth 2.0 credentials: `APIs & Services > Credentials > OAuth consent screen`
5. Download `credentials.json`

### 2. Store Credentials

```bash
# Save credentials securely
mkdir -p ~/.ai_employee
cp /path/to/credentials.json ~/.ai_employee/gmail_credentials.json

# Set environment variable
export GMAIL_CREDENTIALS="$HOME/.ai_employee/gmail_credentials.json"
```

**Never commit credentials to Git!**

## Server Lifecycle

### Start Server

```bash
# Start Email MCP server
bash .qwen/skills/email-mcp/scripts/start-server.sh
```

### Stop Server

```bash
# Stop Email MCP server
bash .qwen/skills/email-mcp/scripts/stop-server.sh
```

### Verify Server

```bash
python3 .qwen/skills/email-mcp/scripts/verify.py
```

Expected: `✓ Email MCP server running on port 8809`

## Quick Reference

### Send Email

```bash
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "client@example.com", "subject": "Invoice #123", "body": "Please find attached...", "attachments": ["/path/to/file.pdf"]}'
```

### Create Draft

```bash
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_draft_create \
  -p '{"to": "client@example.com", "subject": "Proposal", "body": "Hi..."}'
```

### Search Emails

```bash
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_search \
  -p '{"query": "is:unread from:client@example.com"}'
```

### Read Email

```bash
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_read \
  -p '{"message_id": "msg_12345"}'
```

### Mark as Read

```bash
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_mark_read \
  -p '{"message_id": "msg_12345"}'
```

### Archive Email

```bash
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_archive \
  -p '{"message_id": "msg_12345"}'
```

## Workflow: Send Invoice

1. **Generate invoice** (from accounting data)
2. **Create draft** for review
3. **Human approval** (move file to /Approved)
4. **Send email** with attachment
5. **Log action** to audit file

```bash
# Step 2: Create draft
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_draft_create \
  -p '{
    "to": "client@example.com",
    "subject": "Invoice #123 - January 2026",
    "body": "Dear Client,\n\nPlease find attached invoice for January 2026.\n\nAmount: $1,500\nDue: Feb 15, 2026\n\nBest regards",
    "attachments": ["/path/to/invoice_123.pdf"]
  }'

# Step 4: Send after approval
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_send_draft \
  -p '{"draft_id": "draft_123"}'
```

## Workflow: Email Triage

1. **Search unread emails**
2. **Filter by priority** (important, from clients)
3. **Create action files** in /Needs_Action
4. **Qwen processes** and suggests replies
5. **Send replies** after approval

```bash
# Search unread important emails
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_search \
  -p '{"query": "is:unread is:important"}'

# Read specific email
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_read \
  -p '{"message_id": "msg_12345"}'

# Reply after approval
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_send \
  -p '{
    "to": "client@example.com",
    "subject": "Re: Project Update",
    "body": "Hi,\n\nThanks for your email...\n\nBest regards",
    "in_reply_to": "msg_12345"
  }'
```

## Tool Reference

| Tool | Parameters | Description |
|------|------------|-------------|
| `email_send` | to, subject, body, attachments, cc, bcc | Send email immediately |
| `email_draft_create` | to, subject, body, attachments | Create draft for review |
| `email_draft_send` | draft_id | Send existing draft |
| `email_search` | query, max_results | Search Gmail |
| `email_read` | message_id | Read email content |
| `email_mark_read` | message_id | Mark as read |
| `email_archive` | message_id | Archive email |
| `email_delete` | message_id | Delete email (trash) |

## Human-in-the-Loop Pattern

For sensitive actions (sending emails), use approval workflow:

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #123
status: pending
---

## Email Details
- **To:** client@example.com
- **Subject:** Invoice #123 - January 2026
- **Attachment:** invoice_123.pdf

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

After approval, send the email:

```bash
python3 .qwen/skills/email-mcp/scripts/mcp-client.py call \
  -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "client@example.com", "subject": "Invoice #123", "body": "..."}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| OAuth error | Re-authenticate: delete token, run start-server.sh |
| 403 Forbidden | Enable Gmail API in Google Cloud Console |
| Server not starting | Check port 8809 not in use |
| Attachments fail | Use absolute file paths |
| Rate limit | Wait 1-2 minutes, retry |

## Security Best Practices

1. **Never commit** `credentials.json` or `token.json`
2. Use **environment variables** for paths
3. **Review drafts** before sending sensitive emails
4. **Log all sent emails** to audit file
5. **Rotate credentials** every 90 days

## Integration with Watchers

Gmail Watcher creates action files when new emails arrive:

```python
# gmail_watcher.py creates:
# /Vault/Needs_Action/EMAIL_msg_12345.md

---
type: email
from: client@example.com
subject: Project Inquiry
received: 2026-01-07T10:30:00
priority: high
status: pending
---

### Email Content
...

### Suggested Actions
- [ ] Reply to sender
- [ ] Forward to team
- [ ] Archive after processing
```

Qwen processes these files and creates email drafts for approval.

## Resources

- [Gmail API Docs](https://developers.google.com/gmail/api)
- [OAuth 2.0 Setup](https://developers.google.com/identity/protocols/oauth2)
- [Email MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/gmail)
