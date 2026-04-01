#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Setup Script - Configure Chrome profile and test LinkedIn connection.

This script helps you:
1. Find your Chrome profile path
2. Test LinkedIn login
3. Save your session for auto-posting

Usage:
    python setup_linkedin.py
"""

import os
import sys
from pathlib import Path


def find_chrome_profile():
    """Find Chrome profile paths on the system."""
    print("🔍 Searching for Chrome profiles...\n")

    # Common Chrome profile locations
    profile_locations = [
        # Windows (native)
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data"),
        os.path.expanduser(r"~\AppData\Roaming\Google\Chrome\User Data"),
        # WSL - Windows Chrome via /mnt/c
        "/mnt/c/Users/Saif/AppData/Local/Google/Chrome/User Data",
        "/mnt/c/Users/Saif/AppData/Roaming/Google/Chrome/User Data",
        # Linux
        os.path.expanduser("~/.config/google-chrome"),
        # macOS
        os.path.expanduser("~/Library/Application Support/Google/Chrome"),
    ]

    found_profiles = []

    for location in profile_locations:
        if os.path.exists(location):
            print(f"✓ Found Chrome User Data: {location}")

            # Look for profile directories
            try:
                for item in os.listdir(location):
                    if item in ['Default', 'Profile 1', 'Profile 2', 'Profile 3']:
                        profile_path = os.path.join(location, item)
                        if os.path.exists(os.path.join(profile_path, 'Web Data')):
                            found_profiles.append(profile_path)
                            print(f"  - Profile: {item}")
            except Exception as e:
                print(f"  Error listing profiles: {e}")
            print()

    return found_profiles


def test_linkedin_login():
    """Test LinkedIn login using Playwright."""
    print("🧪 Testing LinkedIn login...\n")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed!")
        print("   Run: pip install playwright")
        print("   Then: playwright install")
        return False

    # Find Chrome - Windows paths (for WSL)
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        # WSL paths to Windows Chrome
        "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
        "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        "/mnt/c/Users/Saif/AppData/Local/Google/Chrome/Application/chrome.exe",
    ]

    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break

    if not chrome_path:
        print("❌ Chrome not found! Please install Google Chrome.")
        return False

    print(f"✓ Using Chrome: {chrome_path}\n")

    # Chrome user data - WSL path
    chrome_user_data = "/mnt/c/Users/Saif/AppData/Local/Google/Chrome/User Data"

    print("=" * 60)
    print("IMPORTANT: A Chrome browser window will open.")
    print("1. If not already logged in, log in to LinkedIn manually")
    print("2. Navigate to https://www.linkedin.com/feed/")
    print("3. Confirm you can see your feed")
    print("4. Close the browser when done")
    print("=" * 60)
    print()

    input("Press Enter to continue...")

    try:
        with sync_playwright() as p:
            print("Launching Chrome with your profile...")

            browser = p.chromium.launch_persistent_context(
                user_data_dir=chrome_user_data,
                headless=False,
                executable_path=chrome_path,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--profile-directory=Default',
                ],
                ignore_default_args=['--enable-automation'],
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            print("Navigating to LinkedIn...")
            page.goto('https://www.linkedin.com/feed/', timeout=60000)

            print("\n" + "=" * 60)
            print("Waiting for you to log in (if needed)...")
            print("The browser will stay open for 120 seconds.")
            print("=" * 60)

            # Wait for login
            for i in range(60):
                page.wait_for_timeout(2000)
                current_url = page.url

                if 'feed' in current_url:
                    print(f"\n✓ SUCCESS! Logged in to LinkedIn")
                    print(f"  Current URL: {current_url}")
                    print("\nYour session is now saved. Future auto-posts will use this login.")
                    break
            else:
                print("\n⚠️ Timeout. Please ensure you're logged in.")

            browser.close()
            return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def create_config_file(profile_path: str):
    """Create a configuration file with the profile path."""
    config_path = Path(__file__).parent / 'linkedin_config.json'

    config = {
        'chrome_profile': profile_path,
        'auto_post_enabled': True,
    }

    import json
    config_path.write_text(json.dumps(config, indent=2))
    print(f"✓ Configuration saved to: {config_path}")


def main():
    print("=" * 60)
    print("  LinkedIn Auto-Post Setup")
    print("=" * 60)
    print()

    # Find profiles
    profiles = find_chrome_profile()

    if not profiles:
        print("❌ No Chrome profiles found!")
        print("   Please ensure Google Chrome is installed and you've logged in at least once.")
        sys.exit(1)

    print(f"Found {len(profiles)} Chrome profile(s)\n")

    # Test login
    success = test_linkedin_login()

    if success:
        print("\n" + "=" * 60)
        print("  ✓ Setup Complete!")
        print("=" * 60)
        print("\nYou can now use auto-post mode:")
        print("\n  # Create and publish immediately:")
        print("  python linkedin_poster.py auto --text \"Your post\" --hashtags \"AI,Business\"")
        print("\n  # Publish pending posts:")
        print("  python linkedin_poster.py publish --auto-post")
        print()

        # Save config
        if profiles:
            create_config_file(profiles[0])
    else:
        print("\n❌ Setup failed. Please try again.")
        sys.exit(1)


if __name__ == '__main__':
    main()
