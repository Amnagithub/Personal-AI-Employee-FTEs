#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn API Poster - Official LinkedIn API v2 Integration

Posts to LinkedIn using official API with OAuth 2.0 authentication.
Supports text posts, images, and approval workflow.

Usage:
    # First-time token setup
    python3 linkedin_post.py get-token \
      --client-id "your_client_id" \
      --client-secret "your_client_secret" \
      --auth-code "auth_code" \
      --redirect-uri "http://localhost:8000/callback"

    # Create post with approval workflow
    python3 linkedin_post.py post \
      --text "Your post content" \
      --hashtags "AI,Automation,Business" \
      --vault ./AI_Employee_Vault

    # Publish approved posts
    python3 linkedin_post.py publish --vault ./AI_Employee_Vault

    # Refresh access token
    python3 linkedin_post.py refresh-token \
      --client-id "your_client_id" \
      --client-secret "your_client_secret" \
      --refresh-token "your_refresh_token"
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv


# LinkedIn API Configuration
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2"
LINKEDIN_OAUTH_TOKEN_URL = f"{LINKEDIN_AUTH_URL}/accessToken"


class LinkedInAPI:
    """LinkedIn API client for posting updates."""

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        redirect_uri: str = "http://localhost:8000/callback",
        auto_refresh: bool = True,
    ):
        """
        Initialize LinkedIn API client.

        Args:
            client_id: LinkedIn app client ID
            client_secret: LinkedIn app client secret
            access_token: OAuth access token
            refresh_token: OAuth refresh token
            redirect_uri: OAuth redirect URI
            auto_refresh: Auto-refresh expired tokens
        """
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.refresh_token = refresh_token or os.getenv("LINKEDIN_REFRESH_TOKEN")
        self.redirect_uri = redirect_uri or os.getenv(
            "LINKEDIN_REDIRECT_URI", "http://localhost:8000/callback"
        )
        self.auto_refresh = auto_refresh and os.getenv("LINKEDIN_AUTO_REFRESH", "true").lower() == "true"

        if not all([self.client_id, self.client_secret, self.access_token]):
            raise ValueError(
                "Missing LinkedIn credentials. Set environment variables or pass parameters."
            )

    def get_auth_url(self, scope: list = None) -> str:
        """
        Generate OAuth authorization URL for manual authorization.

        Args:
            scope: List of permission scopes

        Returns:
            Authorization URL to open in browser
        """
        if scope is None:
            scope = ["w_member_social", "r_liteprofile"]

        scope_str = "%20".join(scope)
        return (
            f"{LINKEDIN_AUTH_URL}/authorization?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"state=foo&"
            f"scope={scope_str}"
        )

    def exchange_code_for_token(self, auth_code: str) -> dict:
        """
        Exchange authorization code for access token.

        Args:
            auth_code: Authorization code from OAuth redirect

        Returns:
            Dictionary with access_token, refresh_token, and expires_in
        """
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(LINKEDIN_OAUTH_TOKEN_URL, data=payload)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")

        return token_data

    def refresh_access_token(self) -> dict:
        """
        Refresh expired access token using refresh token.

        Returns:
            Dictionary with new access_token and refresh_token
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available. Re-authorize manually.")

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(LINKEDIN_OAUTH_TOKEN_URL, data=payload)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")

        # Update environment file
        self._save_tokens(token_data)

        return token_data

    def get_member_urn(self) -> str:
        """
        Get the authenticated member's URN ID.

        Returns:
            Member URN (e.g., urn:li:person:ABC123)
        """
        url = f"{LINKEDIN_API_BASE}/userinfo"
        headers = {"Authorization": f"Bearer {self.access_token}"}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        user_info = response.json()
        return f"urn:li:person:{user_info.get('sub')}"

    def create_post(
        self,
        text: str,
        author_urn: str = None,
        organization_id: str = None,
        visibility: str = "PUBLIC",
    ) -> dict:
        """
        Create a post on LinkedIn using UGC API v2.

        Args:
            text: Post content (max 3000 characters)
            author_urn: Person or organization URN
            organization_id: Organization ID if posting to company page
            visibility: Post visibility (PUBLIC, CONNECTIONS, etc.)

        Returns:
            API response with post ID
        """
        if len(text) > 3000:
            raise ValueError(f"Post text exceeds 3000 character limit ({len(text)} chars)")

        # Determine author URN
        if author_urn is None:
            if organization_id:
                author_urn = f"urn:li:organization:{organization_id}"
            else:
                author_urn = self.get_member_urn()

        # Prepare post payload for UGC API
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            },
        }

        # Use UGC Posts API
        url = f"{LINKEDIN_API_BASE}/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        response = requests.post(url, json=post_data, headers=headers)

        # Handle token expiration
        if response.status_code == 401 and self.auto_refresh:
            print("Token expired. Refreshing...")
            self.refresh_access_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.post(url, json=post_data, headers=headers)

        response.raise_for_status()
        return response.json()

    def _save_tokens(self, token_data: dict):
        """Save tokens to .env file."""
        env_path = Path(__file__).parent / ".env"

        env_content = {}
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_content[key.strip()] = value.strip()

        env_content["LINKEDIN_ACCESS_TOKEN"] = token_data.get("access_token", "")
        env_content["LINKEDIN_REFRESH_TOKEN"] = token_data.get("refresh_token", "")

        with open(env_path, "w") as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")

        print(f"✓ Tokens saved to {env_path}")


def create_draft(
    text: str,
    hashtags: list = None,
    scheduled_time: str = None,
    visibility: str = "PUBLIC",
    vault_path: Path = None,
) -> Path:
    """
    Create a LinkedIn post draft for approval.

    Args:
        text: Post content
        hashtags: List of hashtags (without #)
        scheduled_time: Optional scheduled publish time
        visibility: Post visibility
        vault_path: Path to vault

    Returns:
        Path to created draft file
    """
    if vault_path is None:
        vault_path = Path.cwd()
    else:
        vault_path = Path(vault_path).resolve()

    pending_approval = vault_path / "Pending_Approval"
    pending_approval.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"LINKEDIN_POST_{timestamp}.md"
    filepath = pending_approval / filename

    # Format hashtags
    hashtag_text = ""
    if hashtags:
        hashtag_text = "\n\n" + " ".join([f"#{tag}" for tag in hashtags])

    # Full post content
    full_text = text + hashtag_text

    content = f"""---
type: linkedin_post
status: pending_approval
created: {datetime.now().isoformat()}
scheduled_time: {scheduled_time or 'immediate'}
visibility: {visibility}
hashtags: {', '.join(hashtags or [])}
character_count: {len(full_text)}
---

# LinkedIn Post Draft

## Content

{full_text}

## Details

- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Character Count:** {len(full_text)} (Max: 3000)
- **Hashtags:** {', '.join(hashtags or [])}
- **Visibility:** {visibility}
- **Scheduled:** {scheduled_time or 'Immediate'}

---

## To Approve

Move this file to `/Approved` folder to publish via LinkedIn API.

## To Reject

Move this file to `/Rejected` folder with a comment.

## To Request Changes

Edit the content above and save, or add comments below.

---

## Notes

<!-- Add any comments or feedback here -->

"""
    filepath.write_text(content, encoding="utf-8")
    return filepath


def publish_approved_posts(vault_path: Path, linkedin_api: LinkedInAPI) -> list:
    """
    Publish all approved LinkedIn posts.

    Args:
        vault_path: Path to vault
        linkedin_api: LinkedInAPI instance

    Returns:
        List of published post results
    """
    vault_path = Path(vault_path).resolve()
    approved_folder = vault_path / "Approved"

    if not approved_folder.exists():
        print("No Approved folder found")
        return []

    published = []
    for post_file in approved_folder.glob("LINKEDIN_POST_*.md"):
        print(f"\nPublishing: {post_file.name}")

        # Parse frontmatter
        text = post_file.read_text(encoding="utf-8")
        if "---" not in text:
            print(f"  ⚠ Invalid file format, skipping")
            continue

        # Extract metadata
        parts = text.split("---", 2)
        try:
            metadata = {}
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
        except Exception as e:
            print(f"  ⚠ Error parsing metadata: {e}")
            continue

        # Extract post content
        post_text = parts[2].strip()
        if "## Content" in post_text:
            post_text = post_text.split("## Content", 1)[1].strip()
            # Remove subsequent headers
            if "\n##" in post_text:
                post_text = post_text.split("\n##")[0].strip()

        try:
            # Publish via API
            result = linkedin_api.create_post(text=post_text)
            post_id = result.get("id", "unknown")

            # Move to Done folder
            done_folder = vault_path / "Done"
            done_folder.mkdir(parents=True, exist_ok=True)
            post_file.rename(done_folder / post_file.name)

            print(f"  ✓ Published successfully (ID: {post_id})")
            published.append({"file": post_file.name, "post_id": post_id})

        except Exception as e:
            print(f"  ✗ Failed to publish: {e}")

    return published


def main():
    parser = argparse.ArgumentParser(
        description="LinkedIn API Poster - Official API integration with OAuth 2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time setup
  python3 linkedin_post.py get-token \\
    --client-id "your_id" --client-secret "your_secret" --auth-code "code"

  # Create post draft
  python3 linkedin_post.py post -t "Your post content" -H "AI,Automation"

  # Publish approved posts
  python3 linkedin_post.py publish -v ./AI_Employee_Vault

  # Refresh token
  python3 linkedin_post.py refresh-token \\
    --client-id "your_id" --client-secret "your_secret" --refresh-token "token"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Get Token (First-time setup)
    get_token_parser = subparsers.add_parser(
        "get-token", help="Exchange authorization code for access token"
    )
    get_token_parser.add_argument("--client-id", required=True, help="LinkedIn app client ID")
    get_token_parser.add_argument(
        "--client-secret", required=True, help="LinkedIn app client secret"
    )
    get_token_parser.add_argument(
        "--auth-code", required=True, help="Authorization code from OAuth redirect"
    )
    get_token_parser.add_argument(
        "--redirect-uri",
        default="http://localhost:8000/callback",
        help="OAuth redirect URI (default: http://localhost:8000/callback)",
    )

    # Refresh Token
    refresh_parser = subparsers.add_parser(
        "refresh-token", help="Refresh expired access token"
    )
    refresh_parser.add_argument("--client-id", required=True, help="LinkedIn app client ID")
    refresh_parser.add_argument(
        "--client-secret", required=True, help="LinkedIn app client secret"
    )
    refresh_parser.add_argument("--refresh-token", required=True, help="Current refresh token")

    # Create Post Draft
    post_parser = subparsers.add_parser(
        "post", help="Create LinkedIn post draft for approval"
    )
    post_parser.add_argument("--text", "-t", required=True, help="Post text content")
    post_parser.add_argument(
        "--hashtags", "-H", help="Comma-separated hashtags (without #)"
    )
    post_parser.add_argument("--schedule", "-s", help="Scheduled time (ISO format)")
    post_parser.add_argument(
        "--visibility",
        default="PUBLIC",
        choices=["PUBLIC", "CONNECTIONS"],
        help="Post visibility",
    )
    post_parser.add_argument(
        "--vault", "-v", default=".", help="Path to vault (default: current dir)"
    )

    # Publish Approved Posts
    publish_parser = subparsers.add_parser(
        "publish", help="Publish all approved posts via LinkedIn API"
    )
    publish_parser.add_argument(
        "--vault", "-v", default=".", help="Path to vault (default: current dir)"
    )
    publish_parser.add_argument(
        "--client-id", help="LinkedIn app client ID (or use .env)"
    )
    publish_parser.add_argument(
        "--client-secret", help="LinkedIn app client secret (or use .env)"
    )
    publish_parser.add_argument(
        "--access-token", help="LinkedIn access token (or use .env)"
    )
    publish_parser.add_argument(
        "--refresh-token", help="LinkedIn refresh token (or use .env)"
    )
    publish_parser.add_argument(
        "--auto-refresh", action="store_true", help="Auto-refresh expired tokens"
    )

    args = parser.parse_args()

    if args.command == "get-token":
        # Exchange auth code for access token
        api = LinkedInAPI(
            client_id=args.client_id,
            client_secret=args.client_secret,
            redirect_uri=args.redirect_uri,
        )

        print("Exchanging authorization code for access token...")
        token_data = api.exchange_code_for_token(args.auth_code)

        print("\n✓ Successfully obtained access token!")
        print(f"Access Token: {token_data.get('access_token')}")
        print(f"Refresh Token: {token_data.get('refresh_token')}")
        print(f"Expires In: {token_data.get('expires_in')} seconds")

        # Save to .env
        api._save_tokens(token_data)

        print("\nNext steps:")
        print("1. Verify .env file is created in skill directory")
        print("2. Create a post draft: python3 linkedin_post.py post -t 'Your post'")

    elif args.command == "refresh-token":
        # Refresh access token
        api = LinkedInAPI(
            client_id=args.client_id,
            client_secret=args.client_secret,
            refresh_token=args.refresh_token,
        )

        print("Refreshing access token...")
        token_data = api.refresh_access_token()

        print("\n✓ Token refreshed successfully!")
        print(f"New Access Token: {token_data.get('access_token')}")
        print(f"New Refresh Token: {token_data.get('refresh_token')}")

    elif args.command == "post":
        # Create post draft
        hashtags = (
            [h.strip() for h in args.hashtags.split(",")] if args.hashtags else []
        )

        draft_path = create_draft(
            text=args.text,
            hashtags=hashtags,
            scheduled_time=args.schedule,
            visibility=args.visibility,
            vault_path=args.vault,
        )

        print(f"✓ Draft created: {draft_path.name}")
        print(f"  Location: {draft_path}")
        print(f"  Status: Pending approval")
        print(f"\nTo approve: Move file to Approved folder")
        print(f"To publish: python3 linkedin_post.py publish --vault {args.vault}")

    elif args.command == "publish":
        # Publish approved posts
        # Load .env from current working directory (project root)
        load_dotenv(Path.cwd() / ".env")
        # Also try loading from script directory as fallback
        load_dotenv(Path(__file__).parent / ".env", override=False)

        api = LinkedInAPI(
            client_id=args.client_id,
            client_secret=args.client_secret,
            access_token=args.access_token,
            refresh_token=args.refresh_token,
            auto_refresh=args.auto_refresh,
        )

        published = publish_approved_posts(args.vault, api)

        if published:
            print(f"\n✓ Published {len(published)} post(s) successfully!")
            for post in published:
                print(f"  - {post['file']} → {post['post_id']}")
        else:
            print("\nNo posts were published.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
