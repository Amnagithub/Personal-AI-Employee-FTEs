# Facebook/Instagram MCP Integration

**Purpose:** Post to Facebook Pages and Instagram Business accounts, generate social media summaries

**Location:** `.qwen/skills/facebook-mcp/`

---

## Setup

### Prerequisites

1. Facebook Developer Account
2. Facebook Page (for business)
3. Instagram Business Account (linked to Facebook Page)
4. Facebook App with permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_manage_comments`

### Get Facebook Access Token

1. Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your App
3. Request permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_manage_comments`
4. Generate Page Access Token (not User Token)
5. Token should be long-lived (60 days)

### Update .env File

```env
# Facebook/Instagram Configuration
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_long_lived_token
INSTAGRAM_ACCOUNT_ID=your_ig_business_account_id
```

### Get Page ID and Instagram Account ID

```bash
# Get your Page ID
curl -G https://graph.facebook.com/v19.0/me \
  -d access_token=YOUR_TOKEN

# Get Instagram Account ID (linked to Page)
curl -G https://graph.facebook.com/v19.0/{page-id}/instagram_accounts \
  -d access_token=YOUR_TOKEN
```

---

## Usage

### Start Facebook MCP Server

```bash
python .qwen/skills/facebook-mcp/scripts/facebook_mcp_server.py --port 8811
```

### Test Connection

```bash
python .qwen/skills/facebook-mcp/scripts/test-connection.py
```

---

## Available MCP Tools

### 1. `facebook_create_post`

Create a post on Facebook Page.

**Parameters:**
```json
{
  "message": "Exciting business update! #AI #Automation",
  "link": "https://example.com",
  "photo_url": "https://example.com/image.jpg"
}
```

**Returns:**
```json
{
  "success": true,
  "post_id": "123456789_987654321",
  "permalink": "https://facebook.com/yourpage/posts/987654321"
}
```

### 2. `facebook_get_posts`

Get recent posts from Page.

**Parameters:**
```json
{
  "limit": 10
}
```

### 3. `facebook_get_insights`

Get engagement metrics (likes, comments, shares).

**Parameters:**
```json
{
  "post_id": "123456789_987654321"
}
```

### 4. `instagram_create_post`

Create a post on Instagram Business.

**Parameters:**
```json
{
  "caption": "Business update! #AI #Automation #Growth",
  "image_url": "https://example.com/image.jpg"
}
```

**Returns:**
```json
{
  "success": true,
  "post_id": "123456789",
  "status": "published"
}
```

### 5. `instagram_create_reel`

Create a reel on Instagram.

**Parameters:**
```json
{
  "caption": "Behind the scenes! #BTS #Business",
  "video_url": "https://example.com/video.mp4"
}
```

### 6. `instagram_get_posts`

Get recent Instagram posts.

**Parameters:**
```json
{
  "limit": 10
}
```

### 7. `facebook_get_summary`

Get Page summary for CEO briefing.

**Parameters:**
```json
{
  "period": "week",
  "date_from": "2026-04-07",
  "date_to": "2026-04-14"
}
```

**Returns:**
```json
{
  "success": true,
  "period": {"from": "2026-04-07", "to": "2026-04-14"},
  "posts_count": 5,
  "total_likes": 150,
  "total_comments": 23,
  "total_shares": 45,
  "top_post": {
    "id": "123_456",
    "message": "Best performing post",
    "likes": 80
  }
}
```

---

## Approval Workflow

For social media posts:

1. Qwen creates draft → `Pending_Approval/FACEBOOK_POST_*.md`
2. Human reviews and moves to `Approved/`
3. MCP publishes post
4. File moved to `Done/` with post ID

---

## Error Handling

- **Invalid token:** Refresh token in .env (tokens expire after 60 days)
- **Page not found:** Verify PAGE_ID is correct
- **Rate limit:** Facebook limits to 200 posts/hour
- **Instagram API:** Only supports image/video posts (no links)

---

## Integration Examples

### Auto-Post Business Updates

```python
# 1. Qwen detects milestone in Business_Goals.md
# 2. Creates Facebook post draft
# 3. Human approves
# 4. Post published
```

### Weekly Social Summary

```python
# 1. Scheduled task runs Sunday
# 2. Calls facebook_get_summary, instagram_get_posts
# 3. Includes in CEO Briefing
# 4. Saves to Briefings/ folder
```

---

## Security Notes

1. Never commit access tokens to git
2. Use long-lived tokens (60 days) and refresh monthly
3. All posts require approval before publishing
4. Audit log tracks all posts
5. Rate limit: Max 5 posts/hour

---

## Resources

- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Page Access Tokens](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/page)
