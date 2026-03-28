---
name: planner
description: |
  Create Plan.md files for multi-step tasks. Qwen Code reasoning loop that breaks down
  complex tasks into actionable steps with checkboxes. Integrates with approval workflow.
---

# Planner

Create structured plans for multi-step tasks with Qwen Code reasoning.

## Overview

The Planner skill creates `Plan.md` files that break down complex tasks into manageable, trackable steps. Each plan includes objectives, step-by-step actions, approval requirements, and progress tracking.

## How It Works

### 1. Trigger

When Qwen Code detects a complex task in `/Needs_Action`, it creates a plan:

```bash
# Qwen Code prompt
Analyze the task in Needs_Action and create a Plan.md file with:
1. Clear objective
2. Required steps with checkboxes
3. Approval requirements
4. Success criteria
```

### 2. Plan Structure

```markdown
---
type: plan
objective: Send invoice to Client A
created: 2026-01-07T10:30:00
status: in_progress
priority: high
estimated_steps: 5
approvals_required: 1
---

# Plan: Send Invoice to Client A

## Objective

Generate and send January 2026 invoice to Client A for $1,500.

## Steps

- [x] Identify client details from database
- [x] Calculate amount based on contract
- [ ] Generate invoice PDF
- [ ] Create email draft (REQUIRES APPROVAL)
- [ ] Send email after approval
- [ ] Log transaction
- [ ] Move to Done

## Approval Requirements

| Step | Action | Approver |
|------|--------|----------|
| 4 | Send email | Human |

## Resources

- Client contract: `/Vault/Clients/Client_A_Contract.md`
- Invoice template: `/Vault/Templates/Invoice_Template.md`
- Accounting rates: `/Vault/Accounting/Rates.md`

## Notes

Client prefers PDF invoices. Payment terms: Net 15.

---

## Progress

**Created:** 2026-01-07 10:30 AM
**Started:** 2026-01-07 10:35 AM
**Estimated completion:** 2026-01-07 11:00 AM
```

### 3. Execution

Qwen Code processes the plan:

```bash
# Qwen Code prompt
Read Plan.md in Plans folder.
Execute next unchecked step.
Update plan with progress.
If step requires approval, create approval request file.
```

### 4. Approval Integration

When a step requires approval:

```markdown
---
type: approval_request
action: send_email
plan: PLAN_invoice_client_a
step: 4
status: pending
---

## Approval Required

**Plan:** Send Invoice to Client A
**Step 4:** Send email with invoice

**Email Details:**
- To: client@example.com
- Subject: Invoice #123 - January 2026
- Attachment: invoice_123.pdf

## To Approve
Move this file to /Approved folder.
```

## Usage

### Create Plan Manually

```bash
cat > AI_Employee_Vault/Plans/PLAN_custom_task.md << 'EOF'
---
type: plan
objective: Your objective here
created: 2026-01-07T10:30:00
status: pending
---

# Plan: Your Plan Name

## Objective
Clear description of what you want to achieve.

## Steps
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Approval Requirements
| Step | Action | Approver |
|------|--------|----------|
| 3 | Send email | Human |
EOF
```

### Process Plan with Qwen

```bash
cd AI_Employee_Vault
qwen
```

Prompt:
```
Read all plans in the Plans folder.
For each plan:
1. Check current status
2. Execute the next unchecked step
3. Update the plan with progress
4. Create approval requests for steps that need approval
5. Move completed plans to Done folder
```

## Integration with Other Skills

### + Email MCP

```yaml
# In Plan.md steps:
- [ ] Create email draft (email-mcp)
- [ ] Send after approval (email-mcp + approval-workflow)
```

### + Gmail Watcher

```yaml
# When Gmail Watcher detects email:
# Qwen creates plan:
- type: plan
  objective: Process incoming email
  steps:
    - [x] Read email content
    - [ ] Draft reply
    - [ ] Send after approval
```

### + Approval Workflow

```yaml
# Plan steps that need approval trigger:
- step: Send payment
  approval_type: payment
  approval_threshold: 500
```

## Plan Templates

### Simple Task

```markdown
---
type: plan
objective: Simple task objective
created: 2026-01-07T10:30:00
status: pending
---

# Plan: Task Name

## Objective
One sentence description.

## Steps
- [ ] Step 1
- [ ] Step 2
- [ ] Done

## Notes
Additional context here.
```

### Complex Multi-Approval

```markdown
---
type: plan
objective: Complex objective
created: 2026-01-07T10:30:00
status: pending
approvals_required: 3
---

# Plan: Complex Task

## Objective
Detailed description.

## Steps
- [ ] Research phase
- [ ] Draft creation
- [ ] Review (APPROVAL 1)
- [ ] Revision
- [ ] Final approval (APPROVAL 2)
- [ ] Execute (APPROVAL 3)
- [ ] Complete

## Approval History
| Date | Step | Approver | Decision |
|------|------|----------|----------|
| | | | |
```

## Best Practices

1. **Clear objectives** - One sentence, measurable outcome
2. **Atomic steps** - Each step should be independently actionable
3. **Explicit approvals** - Mark which steps need approval
4. **Track progress** - Update plan as steps complete
5. **Archive completed** - Move to Done when all steps checked

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan not progressing | Check for blocked approval steps |
| Too many steps | Break into sub-plans |
| Unclear ownership | Add assignee to plan metadata |
| Stale plans | Review weekly, archive if no longer relevant |
