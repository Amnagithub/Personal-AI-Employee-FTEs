# Odoo MCP Server Integration

**Purpose:** Integrate with Odoo Community Edition for accounting, invoicing, and business management

**Location:** `.qwen/skills/odoo-mcp/`

---

## Setup

### Prerequisites

1. Docker Desktop installed and running
2. Odoo Community running on `localhost:8069`
3. Python 3.13+

### Odoo Configuration

1. Access Odoo at `http://localhost:8069`
2. Create database: `ai_employee`
3. Install modules:
   - Accounting
   - Invoicing
   - Contacts
   - Products

### Create API User

1. Go to Settings → Users & Companies → Users
2. Create user: `ai_employee`
3. Set password: `ai_employee_api`
4. Assign role: Accounting / Billing

### Update .env File

```env
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=ai_employee
ODOO_PASSWORD=ai_employee_api
```

---

## Usage

### Start Odoo MCP Server

```bash
# Start Odoo (if not running)
cd AI_Employee_Vault/odoo
docker-compose up -d

# Verify Odoo is running
curl http://localhost:8069

# Start MCP server
python .qwen/skills/odoo-mcp/scripts/start-server.py
```

### Test Connection

```bash
python .qwen/skills/odoo-mcp/scripts/test-connection.py
```

---

## Available MCP Tools

### 1. `odoo_create_invoice`

Create a new invoice in Odoo.

**Parameters:**
```json
{
  "partner_name": "Client A",
  "partner_email": "client@example.com",
  "invoice_lines": [
    {
      "name": "Consulting Services",
      "quantity": 10,
      "price_unit": 150.00,
      "account_id": 1
    }
  ],
  "payment_term": "30 days",
  "currency": "USD"
}
```

**Returns:**
```json
{
  "invoice_id": 42,
  "invoice_number": "INV/2026/00042",
  "status": "draft",
  "total_amount": 1500.00
}
```

### 2. `odoo_validate_invoice`

Validate and post an invoice (requires approval).

**Parameters:**
```json
{
  "invoice_id": 42
}
```

### 3. `odoo_register_payment`

Register payment for an invoice.

**Parameters:**
```json
{
  "invoice_id": 42,
  "amount": 1500.00,
  "payment_method": "bank_transfer",
  "journal_id": 1
}
```

### 4. `odoo_get_partners`

List all business partners (contacts).

**Parameters:**
```json
{
  "filter": "customer"
}
```

### 5. `odoo_get_invoices`

Retrieve invoices with optional filters.

**Parameters:**
```json
{
  "status": "draft",
  "date_from": "2026-01-01",
  "date_to": "2026-04-30"
}
```

### 6. `odoo_get_financial_summary`

Get accounting summary for CEO briefing.

**Parameters:**
```json
{
  "period": "monthly",
  "date_from": "2026-04-01",
  "date_to": "2026-04-30"
}
```

### 7. `odoo_create_contact`

Create a new business contact.

**Parameters:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "company": "Acme Corp",
  "type": "customer"
}
```

---

## Approval Workflow

For sensitive financial actions (validating invoices, registering payments):

1. Qwen creates approval request → `Pending_Approval/ODOO_*.md`
2. Human reviews and moves to `Approved/`
3. MCP executes the action
4. File moved to `Done/` with transaction ID

---

## Error Handling

- **Connection refused:** Check if Odoo is running: `docker ps | grep odoo`
- **Authentication failed:** Verify credentials in `.env`
- **Database error:** Check PostgreSQL: `docker ps | grep postgres`
- **API timeout:** Retry with exponential backoff

---

## Integration Examples

### Auto-Generate Invoice from Email

```python
# 1. Gmail Watcher detects invoice request
# 2. Qwen reads Needs_Action/EMAIL_*.md
# 3. Qwen calls odoo_create_invoice via MCP
# 4. Creates approval request
# 5. Human approves
# 6. Invoice sent via email
```

### Weekly Revenue Report

```python
# 1. Scheduled task runs Sunday night
# 2. Calls odoo_get_financial_summary
# 3. Generates CEO Briefing
# 4. Saves to Briefings/ folder
```

---

## Security Notes

1. Never expose Odoo admin password
2. Use separate API user with limited permissions
3. All financial actions require approval
4. Audit log tracks all MCP calls
5. Rate limit: Max 10 invoices/hour

---

## Resources

- [Odoo 19 External API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Odoo MCP Server Reference](https://github.com/AlanOgic/mcp-odoo-adv)
- [Docker Compose Docs](https://docs.docker.com/compose/)
