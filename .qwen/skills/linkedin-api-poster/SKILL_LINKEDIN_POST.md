# LinkedIn API Poster

**Official LinkedIn API v2 integration for posting updates programmatically.**

## Overview

LinkedIn API Poster uses LinkedIn's official Sharing API (v2) to create posts with proper OAuth 2.0 authentication. Unlike browser automation, this approach:

- ✅ **Uses official API** - No risk of account suspension
- ✅ **Fully automated** - No manual login required
- ✅ **Supports images** - Upload via LinkedIn's Assets API
- ✅ **Respects rate limits** - Built-in quota management
- ✅ **Approval workflow** - Drafts saved for human review

## API Capabilities

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `oauth/v2/authorization` | GET | Authorize application |
| `oauth/v2/accessToken` | POST | Exchange code for token |
| `rest/posts` | POST | Create share/update |
| `rest/assets?action=registerUpload` | POST | Register image upload |
| `rest/assets/{assetId}` | PUT | Upload image binary |

## Prerequisites

1. **LinkedIn Developer Account** - https://developer.linkedin.com/
2. **LinkedIn App** - Create at https://www.linkedin.com/developers/apps
3. **Required Permissions**:
   - `w_member_social` - Post on behalf of member
   - `r_liteprofile` - Read member profile
   - `w_organization_social` - Post on behalf of organization (optional)

## Quick Start

### First-Time Setup: Get OAuth Credentials

1. **Create LinkedIn Developer Account**
   - Visit https://developer.linkedin.com/
   - Sign in with your LinkedIn account
   - Complete developer registration

2. **Create New App**
   - Go to https://www.linkedin.com/developers/apps
   - Click "Create App"
   - Fill in app details (name, company, etc.)

3. **Configure OAuth Settings**
   - Navigate to your app → "Auth" tab
   - Set **Redirect URL** to: `http://localhost:8000/callback`
   - Note your **Client ID** and **Client Secret**

4. **Get Authorization Code (Manual)**

   Open this URL in your browser (replace `{CLIENT_ID}`):

   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={CLIENT_ID}&redirect_uri=http://localhost:8000/callback&state=foo&scope=w_member_social%20r_liteprofile
   ```

5. **Authorize the App**
   - Click "Allow" on the LinkedIn consent screen
   - You'll be redirected to: `http://localhost:8000/callback?code={AUTH_CODE}&state=foo`
   - **Copy the `code` parameter** from the URL

6. **Exchange Code for Access Token**

   ```bash
   python3 .qwen/skills/linkedin-api-poster/linkedin_post.py get-token \
     --client-id "your_client_id" \
     --client-secret "your_client_secret" \
     --auth-code "authorization_code_from_url" \
     --redirect-uri "http://localhost:8000/callback"
   ```

7. **Save Credentials**
   - The script will output your `access_token` and `refresh_token`
   - Create `.env` file in the skill directory:

   ```env
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_ACCESS_TOKEN=your_access_token
   LINKEDIN_REFRESH_TOKEN=your_refresh_token
   LINKEDIN_REDIRECT_URI=http://localhost:8000/callback
   ```

### Create Post

```bash
# Simple text post
python3 .qwen/skills/linkedin-api-poster/linkedin_post.py post \
  --text "Exciting news! Just launched our AI Employee service!" \
  --vault ./AI_Employee_Vault

# Post with hashtags
python3 .qwen/skills/linkedin-api-poster/linkedin_post.py post \
  --text "AI automation is changing business operations" \
  --hashtags "AI,Automation,Business" \
  --vault ./AI_Employee_Vault

# Post to organization page
python3 .qwen/skills/linkedin-api-poster/linkedin_post.py post \
  --text "We're hiring!" \
  --organization-id "12345678" \
  --vault ./AI_Employee_Vault
```

### Refresh Access Token

Access tokens expire every 60 days. Refresh automatically:

```bash
python3 .qwen/skills/linkedin-api-poster/linkedin_post.py refresh-token \
  --client-id "your_client_id" \
  --client-secret "your_client_secret" \
  --refresh-token "your_refresh_token"
```

## Automated Workflow

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
│ API Posts to    │
│ LinkedIn        │
└─────────────────┘
```

## Post Templates

### Business Update

```markdown
---
type: linkedin_post
status: pending_approval
created: 2026-01-10T10:30:00
visibility: PUBLIC
author: person:urn:li:person:ABC123
---

# LinkedIn Post Draft

## Content

🚀 Exciting news!

We've just launched our new AI Employee service that helps businesses automate routine tasks.

✅ Save 20+ hours per week
✅ Reduce operational costs
✅ 24/7 autonomous operation

#AI #Automation #Business

---

## To Approve

Move this file to /Approved folder to publish via API.
```

## Error Handling

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | Token expired. Run `refresh-token` command |
| `403 Forbidden` | Check app permissions in LinkedIn Developer Console |
| `400 Bad Request` | Verify text format and character limit (3000 max) |
| `429 Too Many Requests` | Rate limited. Wait and retry (API allows ~100 posts/day) |

## API Reference

### Create Share (Text Post)

```http
POST https://api.linkedin.com/v2/rest/posts
Content-Type: application/json
Authorization: Bearer {access_token}
X-Restli-Protocol-Version: 2.0.0

{
  "author": "urn:li:person:ABC123",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Your post content here"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

### Create Share (Organization)

```json
{
  "author": "urn:li:organization:12345678",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Company announcement"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

## Best Practices

1. **Refresh tokens proactively** - Don't wait for expiration
2. **Use approval workflow** - Always review before posting
3. **Monitor rate limits** - Check response headers for `X-RateLimit-Remaining`
4. **Format content properly** - Use line breaks and emojis for engagement
5. **Track post IDs** - Store in metadata for analytics

## Configuration

### Environment Variables

Create `.env` file:

```env
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_REFRESH_TOKEN=your_refresh_token
LINKEDIN_REDIRECT_URI=http://localhost:8000/callback
```

### Token Auto-Refresh

Enable automatic token refresh when posting:

```bash
# Set in .env
LINKEDIN_AUTO_REFRESH=true
```

## Integration with Qwen Code

Qwen Code can automatically:

1. Monitor business goals and achievements
2. Create LinkedIn post drafts in `/Pending_Approval`
3. Publish approved posts via API
4. Log results in `/Done` folder

**Example Prompt:**

```
Review our Business_Goals.md and recent milestones.
Create LinkedIn post drafts for noteworthy updates.
Save to Pending_Approval for review.
Publish any approved posts via API.
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No redirect after authorization | Ensure redirect URL matches exactly in app settings |
| `invalid_grant` error | Auth code expired. Request new code and retry quickly |
| `insufficient_scope` | Re-authorize with correct permissions in OAuth URL |
| Token won't refresh | Verify client ID/secret are correct and not revoked |

## Resources

- [LinkedIn API Docs](https://learn.microsoft.com/en-us/linkedin/)
- [Sharing API Reference](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [OAuth 2.0 Guide](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/authentication)
- [Postman Collection](https://www.postman.com/linkedin-developers/linkedin-api/collection/4wq3j7g/linkedin-api)
