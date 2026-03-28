---
name: approval-workflow
description: |
  Human-in-the-Loop (HITL) approval workflow for sensitive actions.
  Manages /Pending_Approval, /Approved, /Rejected folders.
  Tracks approval history and enforces permission boundaries.
---

# Approval Workflow

Human-in-the-Loop (HITL) pattern for sensitive actions.

## Overview

The Approval Workflow skill implements a file-based approval system where sensitive actions require human review before execution. Qwen Code creates approval request files, humans review and move them to `/Approved` or `/Rejected`, and the orchestrator executes approved actions.

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/     # Awaiting human review
├── Approved/             # Approved, ready to execute
├── Rejected/             # Declined actions
└── Approval_Logs/        # Historical approval records
```

## How It Works

### 1. Qwen Creates Approval Request

When a sensitive action is needed:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #123 payment
created: 2026-01-07T10:30:00
expires: 2026-01-08T10:30:00
status: pending
---

# Approval Required

## Action Details

- **Type:** Payment
- **Amount:** $500.00
- **Recipient:** Client A (Bank: XXXX1234)
- **Reason:** Invoice #123 payment
- **Due:** January 15, 2026

## Context

This payment is for January 2026 services rendered. Client A has been a customer since 2024.

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder with a comment explaining why.

## To Request Changes

Edit this file with questions, then move back to `Pending_Approval`.
```

### 2. Human Reviews

**Review Checklist:**
- [ ] Verify amount is correct
- [ ] Confirm recipient is legitimate
- [ ] Check supporting documentation
- [ ] Ensure within budget

### 3. Human Takes Action

**Approve:**
```bash
# Move file to Approved folder
mv "Pending_Approval/PAYMENT_Client_A.md" "Approved/"
```

**Reject:**
```bash
# Move to Rejected with comment
mv "Pending_Approval/PAYMENT_Client_A.md" "Rejected/"

# Add rejection reason to file
---
rejected: 2026-01-07T11:00:00
reason: Incorrect amount. Should be $450, not $500.
---
```

### 4. Orchestrator Executes

```bash
python3 scripts/orchestrator.py .
```

Orchestrator:
1. Scans `/Approved` folder
2. Executes approved actions
3. Logs to audit file
4. Moves to `/Done`

## Approval Types

### Email Send

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #123
has_attachment: true
---

## Email Details

**To:** client@example.com
**Subject:** Invoice #123 - January 2026
**Attachment:** invoice_123.pdf

**Preview:**
Dear Client,

Please find attached invoice for January 2026...
```

### Payment

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
method: bank_transfer
---

## Payment Details

**Amount:** $500.00
**Recipient:** Client A
**Method:** Bank Transfer
**Account:** XXXX1234

**Supporting Docs:**
- Invoice: /Vault/Invoices/invoice_123.pdf
- Contract: /Vault/Clients/Client_A_Contract.md
```

### Social Media Post

```markdown
---
type: approval_request
action: social_post
platform: linkedin
scheduled_time: 2026-01-08T09:00:00
---

## Post Content

**Platform:** LinkedIn
**Scheduled:** January 08, 2026 at 9:00 AM

**Content:**
🚀 Exciting news! Our new AI service...

#AI #Automation
```

### File Movement

```markdown
---
type: approval_request
action: file_move
source: /Vault/Inbox/sensitive_doc.pdf
destination: /Vault/Archive/Confidential/
---

## File Movement

**From:** /Vault/Inbox/sensitive_doc.pdf
**To:** /Vault/Archive/Confidential/

**Reason:** Archiving confidential document per retention policy.
```

## Permission Boundaries

### Auto-Approve Thresholds

Actions below certain thresholds can be auto-approved:

```python
# In orchestrator.py or config

AUTO_APPROVE_LIMITS = {
    'payment': 50.00,      # Payments under $50 auto-approved
    'email': True,         # All emails auto-approved (risky!)
    'file_move': True,     # File moves auto-approved
    'social_post': False   # Social posts always need approval
}
```

### Always Require Approval

```python
ALWAYS_APPROVE = [
    'payment_over_500',
    'new_recipient_payment',
    'contract_signing',
    'legal_documents',
    'sensitive_data_access'
]
```

## Approval Log

Track all approvals for audit:

```markdown
---
type: approval_log
original_file: PAYMENT_Client_A_2026-01-07.md
action: payment
amount: 500.00
---

# Approval Log

## Timeline

| Date | Action | By | Notes |
|------|--------|----|-------|
| 2026-01-07 10:30 | Created | Qwen | Invoice #123 |
| 2026-01-07 11:00 | Approved | Human | Verified |
| 2026-01-07 11:05 | Executed | System | Payment sent |

## Outcome

✅ Payment successfully sent to Client A
Transaction ID: TXN_12345
```

## Usage

### Create Approval Request

```bash
cat > AI_Employee_Vault/Pending_Approval/ACTION_name.md << 'EOF'
---
type: approval_request
action: your_action_type
status: pending
created: 2026-01-07T10:30:00
---

# Approval Required

## Details
...

## To Approve
Move to /Approved
EOF
```

### Process Approved Actions

```bash
cd AI_Employee_Vault
python3 scripts/orchestrator.py .
```

### View Pending Approvals

```bash
ls Pending_Approval/
```

### Approval Dashboard

```markdown
## Pending Approvals (3)

| File | Type | Amount | Created | Expires |
|------|------|--------|---------|---------|
| PAYMENT_Client_A.md | Payment | $500 | 10:30 AM | 10:30 AM Tomorrow |
| EMAIL_Invoice_123.md | Email | - | 10:35 AM | - |
| POST_Linkedin_01.md | Social | - | 10:40 AM | - |
```

## Best Practices

1. **Clear descriptions** - Explain what, why, and impact
2. **Set expiry** - Time-sensitive approvals should expire
3. **Track history** - Log all approvals for audit
4. **Define thresholds** - Auto-approve low-risk actions
5. **Review rejected** - Understand why actions were rejected

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not executed | Check file is in /Approved, not /Pending_Approval |
| Duplicate approvals | Add unique ID to approval request filename |
| Expired approvals | Set up reminder to review pending approvals |
| Missing context | Include all relevant details in approval request |

## Security

- Never auto-approve payments to new recipients
- Always require approval for legal/contract actions
- Log all approvals with timestamps
- Regular audit of approval history
- Rotate approval authorities periodically
