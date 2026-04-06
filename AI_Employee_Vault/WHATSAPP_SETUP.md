# WhatsApp Watcher & Auto-Processor - Complete Setup Guide

## 📱 Overview

The WhatsApp system monitors WhatsApp Web for incoming messages containing specific keywords, creates action files, generates intelligent replies, and sends them automatically (with human-in-the-loop for sensitive messages).

### **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                  WHATSAPP SYSTEM FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. WhatsApp Watcher (every 30s)                           │
│     - Monitors WhatsApp Web via Playwright                  │
│     - Detects messages with keywords                        │
│     - Creates: Needs_Action/WHATSAPP_*.md                   │
│                                                            │
│  2. WhatsApp Auto-Processor (every 60s)                   │
│     - Scans Needs_Action/ for WHATSAPP_*.md                │
│     - Analyzes message type & sensitivity                  │
│     - Generates intelligent reply                          │
│                                                            │
│     ├─ Non-sensitive ──> Send immediately                │
│     │   └─ Via WhatsApp Web (Playwright)                  │
│     │   └─ Move to Done/                                   │
│     │                                                       │
│     └─ Sensitive ──> Create approval request             │
│         └─ Creates: Pending_Approval/WHATSAPP_APPROVAL_*.md│
│         └─ [WAITS FOR HUMAN]                              │
│             ├─ Move to Approved/ ──> Send & Done/         │
│             └─ Move to Rejected/ ──> Discard              │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### **Prerequisites**

| Component | Status | Purpose |
|-----------|--------|---------|
| Python 3.13+ | ✅ Required | Runtime |
| Playwright | ✅ Required | Browser automation |
| Chromium Browser | ✅ Required | WhatsApp Web |
| WhatsApp Account | ✅ Required | Message monitoring |

### **Step 1: Install Dependencies**

```bash
cd "C:\Users\Saif\Documents\GitHub\Personal AI Employee FTEs\AI_Employee_Vault"

# Install Python packages
pip install playwright

# Install Chromium browser for Playwright
playwright install chromium
```

### **Step 2: Start WhatsApp System**

**Option A - WhatsApp Only:**
```
Double-click: AI_Employee_Vault\start_whatsapp_system.bat
```

**Option B - All Systems (Email + WhatsApp):**
```
Double-click: AI_Employee_Vault\start_all_systems.bat
```

### **Step 3: First-Time Login**

When you run the WhatsApp Watcher for the first time:

1. A browser window will open to `web.whatsapp.com`
2. You'll see a **QR code**
3. Open WhatsApp on your phone
4. Go to **Settings > Linked Devices > Link a Device**
5. Scan the QR code
6. Session will be saved automatically for future use

**Expected Output:**
```
Starting WhatsApp Watcher...
Monitoring WhatsApp Web every 30 seconds...

[WhatsApp Watcher Terminal]
- WhatsAppWatcher - INFO - Starting Playwright...
- WhatsAppWatcher - INFO - Loading session from: .whatsapp_session
- WhatsAppWatcher - INFO - Navigating to WhatsApp Web...
- WhatsAppWatcher - INFO - ✓ Connected to WhatsApp Web (logged in)
- WhatsAppWatcher - INFO - Monitoring for new messages...
```

---

## 🔍 How It Works

### **Keyword Monitoring**

The WhatsApp Watcher monitors for these keywords (case-insensitive):

| Keyword | Use Case |
|---------|----------|
| `urgent` | Urgent requests requiring immediate attention |
| `asap` | Time-sensitive messages |
| `invoice` | Invoice requests from clients |
| `payment` | Payment-related inquiries |
| `help` | General help requests |
| `emergency` | Emergency situations |
| `pricing` | Pricing/cost inquiries |

**Example:** If someone sends "Hey, can you send me the invoice for January?", the watcher detects "invoice" keyword and creates an action file.

### **Message Analysis**

When a message is detected, the Auto-Processor analyzes it:

| Analysis Type | Categories |
|---------------|------------|
| **Message Type** | greeting, invoice_request, meeting_request, pricing_inquiry, urgent, gratitude, general |
| **Urgency** | low, medium, high |
| **Sensitivity** | low, medium, high |
| **Action Required** | Yes/No |

### **Reply Generation**

Based on the analysis, intelligent replies are generated:

**Invoice Request:**
```
Original: "Hey, can you send me the invoice for January?"
Reply: "Hi [Name], I've received your invoice request. Let me prepare that for you and send it over soon."
```

**Meeting Request:**
```
Original: "Can we schedule a call this week?"
Reply: "Hi [Name], I'd be happy to schedule a meeting. What time works best for you this week?"
```

**Pricing Inquiry:**
```
Original: "What's your pricing for the AI service?"
Reply: "Hi [Name], thanks for your interest! Let me get you the pricing details. I'll send that information shortly."
```

---

## 📁 File Structure

### **Action Files Created**

```
AI_Employee_Vault/
├── Needs_Action/
│   └── WHATSAPP_Amna_Kh_20260405_141530.md    # New detected message
│
├── Pending_Approval/
│   └── WHATSAPP_APPROVAL_Amna_Kh_20260405_141600.md  # Awaiting approval
│
├── Approved/
│   └── WHATSAPP_APPROVAL_*.md                  # Approved, ready to send
│
├── Done/
│   └── WHATSAPP_Amna_Kh_20260405_141530.md     # Completed
│
├── Rejected/
│   └── WHATSAPP_APPROVAL_*.md                  # Rejected messages
│
└── .whatsapp_session/                          # Browser session (DO NOT DELETE)
```

### **Action File Schema**

```markdown
---
type: whatsapp
from: Amna Kh
chat_name: Amna Kh
received: 2026-04-05T14:15:30
priority: high
status: pending
message_id: Amna_Kh_Hey_can_you_send_2026-04-05 14:15:00
is_group: false
---

# WhatsApp Message Received

## Message Details

- **From:** Amna Kh
- **Chat:** Amna Kh
- **Received:** 2026-04-05 14:15:30
- **Group Chat:** No

---

## Message Content

Hey, can you send me the invoice for January?

---

## Detected Keywords

invoice

---

## Suggested Actions

- [ ] Read and understand the message
- [ ] Check if reply is needed
- [ ] Draft response (requires approval for sensitive actions)
- [ ] Take any required action (create invoice, schedule meeting, etc.)
- [ ] Mark as complete
```

---

## 🎯 Usage Guide

### **Test WhatsApp Watcher (Single Run)**

```bash
cd "C:\Users\Saif\Documents\GitHub\Personal AI Employee FTEs\AI_Employee_Vault"

# Run once to test detection
python scripts\watchers\whatsapp_watcher.py . --once --verbose
```

**Expected Output:**
```
Processed 1 new message(s)
```

Check `Needs_Action/` for created file.

### **Run WhatsApp Watcher Continuously**

```bash
# Monitor every 30 seconds
python scripts\watchers\whatsapp_watcher.py . --interval 30
```

### **Run WhatsApp Auto-Processor**

```bash
# Test mode (no sending)
python scripts\whatsapp_processor.py . --verbose

# Auto-send mode (sends non-sensitive replies)
python scripts\whatsapp_processor.py . --auto-send --verbose

# Continuous loop (every 60 seconds)
python scripts\whatsapp_processor.py . --loop --loop-interval 60 --auto-send
```

---

## 👤 Human-in-the-Loop Workflow

### **When Approval is Required**

Approval requests are created for:
- Payment-related messages
- Invoice requests
- Meeting schedules
- Any sensitive content

### **Approve a Reply**

**PowerShell:**
```powershell
Move-Item "AI_Employee_Vault\Pending_Approval\WHATSAPP_APPROVAL_*.md" `
          "AI_Employee_Vault\Approved\"
```

### **Reject a Reply**

**PowerShell:**
```powershell
Move-Item "AI_Employee_Vault\Pending_Approval\WHATSAPP_APPROVAL_*.md" `
          "AI_Employee_Vault\Rejected\"
```

### **Edit Before Sending**

1. Open the approval file in `Pending_Approval/`
2. Edit the "Generated Reply" section
3. Move to `Approved/` to send

---

## 🔧 Configuration

### **Change Monitored Keywords**

Edit `scripts\watchers\whatsapp_watcher.py`, line ~50:

```python
# Keywords to monitor (case-insensitive)
self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'pricing']
```

Add or remove keywords as needed.

### **Change Check Interval**

**WhatsApp Watcher:**
```bash
# Change from 30 seconds to 60 seconds
python scripts\watchers\whatsapp_watcher.py . --interval 60
```

**WhatsApp Processor:**
```bash
# Change from 60 seconds to 120 seconds
python scripts\whatsapp_processor.py . --loop --loop-interval 120
```

### **Enable/Disable Headless Mode**

For production (no browser window):
```bash
python scripts\watchers\whatsapp_watcher.py . --interval 30 --headless
```

For testing (visible browser):
```bash
python scripts\watchers\whatsapp_watcher.py . --interval 30
```

---

## 📊 Monitoring & Debugging

### **Check Detected Messages**

```bash
# List action files
dir "AI_Employee_Vault\Needs_Action\WHATSAPP_*.md"

# List approval requests
dir "AI_Employee_Vault\Pending_Approval\WHATSAPP_APPROVAL_*.md"

# List completed
dir "AI_Employee_Vault\Done\WHATSAPP_*.md"
```

### **View Message Cache**

```bash
# Check processed messages
type "AI_Employee_Vault\.whatsapp_cache.json"
```

### **Clear Session (Re-login)**

If WhatsApp Web isn't working:

```bash
# Delete session
rmdir /s "AI_Employee_Vault\.whatsapp_session"

# Restart WhatsApp Watcher
python scripts\watchers\whatsapp_watcher.py . --interval 30
```

Browser will show QR code again for re-login.

---

## ⚠️ Important Notes

### **Terms of Service**

⚠️ **Be aware of WhatsApp's Terms of Service.** Automated access to WhatsApp Web may violate their policies. Use at your own risk.

### **Session Security**

- The `.whatsapp_session` folder contains your WhatsApp login
- **Never share or commit this folder**
- Keep it secure on your local machine
- If compromised, delete it and re-login

### **Rate Limiting**

- WhatsApp may rate-limit or block automated access
- Use reasonable check intervals (30-60 seconds recommended)
- Monitor for any issues or bans

### **Backup**

- Backup your `.whatsapp_session` folder regularly
- If session is corrupted, delete and re-login

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Browser won't open** | Run `playwright install chromium` |
| **QR code not showing** | Wait 10-20 seconds, refresh page |
| **Session expired** | Delete `.whatsapp_session` and re-login |
| **No messages detected** | Check if messages contain keywords |
| **Message not sending** | Ensure WhatsApp Web is logged in |
| **Playwright error** | Reinstall: `pip install playwright && playwright install chromium` |
| **Action files not created** | Check `Needs_Action/` folder exists |
| **Approval not processing** | Move file to `Approved/` folder correctly |

---

## 🔄 Complete Workflow Example

### **Scenario: Client Requests Invoice**

1. **Message Received:**
   - Client sends: "Hey, can you send me the invoice for January?"
   - WhatsApp Watcher detects "invoice" keyword

2. **Action File Created:**
   ```
   Needs_Action/WHATSAPP_Client_Name_20260405_141530.md
   ```

3. **Auto-Processor Runs:**
   - Reads the file
   - Analyzes: `invoice_request`, sensitivity: `high`
   - Generates reply
   - Creates approval request (sensitive content)

4. **Approval Request Created:**
   ```
   Pending_Approval/WHATSAPP_APPROVAL_Client_Name_20260405_141600.md
   ```

5. **Human Reviews:**
   - Opens approval file
   - Edits reply if needed
   - Moves to `Approved/`

6. **Auto-Processor Sends:**
   - Detects file in `Approved/`
   - Opens WhatsApp Web
   - Sends reply to client
   - Moves to `Done/`

7. **Complete:**
   - Client receives automated reply
   - File archived in `Done/`

---

## 📚 Integration with Other Systems

### **Email + WhatsApp Combined**

Use `start_all_systems.bat` to run:
- Gmail Watcher
- Email Auto-Processor
- WhatsApp Watcher
- WhatsApp Auto-Processor

All systems work independently and create action files in the same `Needs_Action/` folder.

### **Qwen Code Integration**

Qwen Code can process both email and WhatsApp action files:

```
Check the Needs_Action folder for new items from watchers.
For each item:
1. Read and understand the content
2. Create a Plan.md if it's a multi-step task
3. Execute simple tasks directly
4. Create approval requests for sensitive actions
5. Move completed items to Done folder
```

---

## 🎯 Next Steps

1. **Test with a real message** - Have someone send you a WhatsApp with "invoice" or "urgent"
2. **Monitor for 1 hour** - Ensure watcher catches all messages
3. **Refine keywords** - Add/remove based on your needs
4. **Customize replies** - Edit `WhatsAppReplyGenerator` in `whatsapp_processor.py`
5. **Set up scheduling** - Use Windows Task Scheduler for auto-start

---

## 📖 Additional Resources

- [WhatsApp Web](https://web.whatsapp.com)
- [Playwright Documentation](https://playwright.dev/python/)
- [Main Hackathon Blueprint](../Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md)
- [Email Setup Guide](./EMAIL_AUTO_PROCESSING_GUIDE.md)

---

## 💡 Pro Tips

1. **Keep browser visible initially** - Don't use `--headless` until you've confirmed login works
2. **Test with your own messages** - Send yourself WhatsApp messages with keywords to test
3. **Monitor logs** - Watch terminal output for any errors
4. **Backup session** - Copy `.whatsapp_session` to a safe location
5. **Use verbose mode** - Add `--verbose` flag when debugging

---

**Need Help?** Check the troubleshooting section or review logs in the terminal windows.
