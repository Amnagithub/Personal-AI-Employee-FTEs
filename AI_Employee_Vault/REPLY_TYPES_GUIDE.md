# ✅ EMAIL REPLY TYPES - Complete Guide

## All Reply Types Now Supported

The intelligent reply generator now detects and responds to **6 different email types**:

---

## 1. 🍽️ Invitations (Lunch, Coffee, Meetup)

**Detected Keywords:**
- lunch, dinner, breakfast, coffee
- "join me", "interested in", "would you like"
- "are you free", "want to", "let's meet"

**Example Email:**
```
Subject: (empty)
Body: Hello, I have a plane for lunch today. Are you interested in joining me?
```

**Reply:**
```
Hi Amna Kh,

Thanks for the invitation! I'd love to join you for lunch today.

What time and place did you have in mind? Let me know the details and I'll make sure I'm available.

Looking forward to it!

Best
```

---

## 2. 👋 Casual Greetings

**Detected When:**
- Very short messages (< 30 chars)
- Just "hi", "hello", "hey"
- No questions or invitations

**Example Email:**
```
Subject: hi
Body: How are you?
```

**Reply:**
```
Hi Amna Kh,

Hey! I'm doing great, thanks for asking! 😊

Hope you're doing well too. What's new with you?

Best
```

---

## 3. 📧 Forwarded Emails

**Detected When:**
- Subject contains "Fwd:" or "forward"

**Example Email:**
```
Subject: Fwd: Google Developer Program Update
Body: (forwarded content)
```

**Reply:**
```
Hi Amna Kh,

Thanks for forwarding this to me. I've reviewed the information you shared.

I'll look through the details and get back to you if I have any questions or if there's anything I need to follow up on.

I appreciate you keeping me in the loop.

Best regards
```

---

## 4. 📅 Scheduling Requests (Formal)

**Detected Keywords:**
- meeting, schedule, calendar
- appointment, time slot, conference

**Example Email:**
```
Subject: Meeting Request
Body: Are you available for a meeting next week to discuss the project?
```

**Reply:**
```
Hi Amna Kh,

Thanks for reaching out about scheduling. I'd be happy to set up a time to connect.

Let me check my calendar and I'll get back to you shortly with some available time slots that work for me.

I'll respond within the next few hours with my availability.

Talk soon,
```

---

## 5. ❓ Questions

**Detected When:**
- Contains "?" 
- "can you", "could you", "would you"
- "please let me know"

**Example Email:**
```
Subject: Project Update
Body: Can you review the attached report and provide feedback by Friday?
```

**Reply:**
```
Hi John,

Thank you for your email. I appreciate you reaching out.

Regarding your questions:

1. Can you review the attached report and provide feedback by Friday?

I'm looking into these and will get back to you with detailed answers as soon as possible.

Thank you for your patience.

Best regards
```

---

## 6. 📰 Newsletters/Program Updates

**Detected Keywords:**
- google, developer, program, newsletter
- update, build, development

**Example Email:**
```
Subject: The Monthly Build - Google Developer Program - April 2026
Body: (newsletter content)
```

**Reply:**
```
Hi Amna Kh,

Thank you for sharing this update. I've received the information and appreciate you keeping me informed about the program.

I'll review the details and take advantage of the resources and opportunities mentioned.

Thanks again for the update!

Best regards
```

---

## 7. 📨 General Emails (Fallback)

**Used When:**
- Doesn't match any specific type above
- Professional/business emails

**Example Email:**
```
Subject: Project Inquiry
Body: I wanted to reach out regarding the new project...
```

**Reply:**
```
Hi Amna Kh,

Thank you for your email regarding "Project Inquiry".

I've received your message and am reviewing the details. I'll get back to you with a comprehensive response shortly.

Best regards
```

---

## Detection Priority Order

The system checks in this order:

1. **Invitations** (lunch, coffee, meetup) ← Highest priority
2. **Casual Greetings** (short "hi", "hello")
3. **Forwarded Emails** (Fwd:)
4. **Scheduling Requests** (meeting, calendar)
5. **Questions** (? marks)
6. **Newsletters** (google, developer)
7. **General** (everything else) ← Fallback

---

## Test Examples

### Test 1: Lunch Invitation ✅
```
Input: "I have a plane for lunch today. Are you interested in joining me?"
Output: "Thanks for the invitation! I'd love to join you for lunch today..."
```

### Test 2: Coffee Invitation ✅
```
Input: "Want to grab coffee this afternoon?"
Output: "Thanks for the invitation! I'd love to join you for coffee today..."
```

### Test 3: Simple Greeting ✅
```
Input: "Hi, how are you?"
Output: "Hey! I'm doing great, thanks for asking! 😊..."
```

### Test 4: Meeting Request ✅
```
Input: "Can we schedule a meeting for next week?"
Output: "Thanks for reaching out about scheduling..."
```

---

## Current Status

✅ **All Systems Running:**
- Gmail Watcher: Active (120s interval)
- Email Auto-Processor: Active (60s interval)
- Intelligent Replies: **Enabled**
- Use Qwen: **True**
- Reply Types: **7 types detected**

---

**Your AI Employee now understands context and writes appropriate replies for any email type!** 🎉
