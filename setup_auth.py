"""
setup_auth.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run this script ONCE on your own computer to get the YouTube
refresh token.  After that, everything runs automatically on GitHub.

Prerequisites (run once):
    pip install google-auth-oauthlib

Usage:
    python setup_auth.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

SETUP_INSTRUCTIONS = """
How to get your Client ID and Client Secret
────────────────────────────────────────────
1. Go to  https://console.cloud.google.com
2. Click "Select a project" → "New Project" → name it "Kids YouTube Bot" → Create
3. Left menu → "APIs & Services" → "Library"
   Search "YouTube Data API v3" → click it → Enable
4. Left menu → "APIs & Services" → "Credentials"
   Click "+ Create Credentials" → "OAuth client ID"
   • If prompted to configure consent screen:
       - User Type: External → Create
       - App name: Kids YouTube Bot  |  add your email  → Save
       - Scopes: skip → Save
       - Test users: add your Gmail → Save
   Back to Credentials → "+ Create Credentials" → "OAuth client ID"
   • Application type: Desktop app → Name: kids-bot → Create
5. Copy the Client ID and Client Secret shown
"""


def main():
    print("=" * 62)
    print("  YouTube One-Time Authentication Setup")
    print("=" * 62)
    print(SETUP_INSTRUCTIONS)

    client_id     = input("Paste your Client ID     → ").strip()
    client_secret = input("Paste your Client Secret → ").strip()

    if not client_id or not client_secret:
        print("\n❌  Client ID / Secret cannot be empty. Exiting.")
        return

    client_config = {
        "installed": {
            "client_id":      client_id,
            "client_secret":  client_secret,
            "auth_uri":       "https://accounts.google.com/o/oauth2/auth",
            "token_uri":      "https://oauth2.googleapis.com/token",
            "redirect_uris":  ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }

    print("\n🌐  A browser window will open — log in with your YouTube account.")
    print("    If it doesn't open, copy the URL printed in the terminal.\n")

    flow  = InstalledAppFlow.from_client_config(client_config, SCOPES)
    creds = flow.run_local_server(port=0)

    print("\n" + "=" * 62)
    print("  ✅  Authentication successful!")
    print("  Add these 4 values as GitHub Secrets:")
    print("=" * 62)
    print()
    print(f"  Name: GROQ_API_KEY")
    print(f"  Value: <your Groq API key from console.groq.com>\n")
    print(f"  Name: YOUTUBE_CLIENT_ID")
    print(f"  Value: {client_id}\n")
    print(f"  Name: YOUTUBE_CLIENT_SECRET")
    print(f"  Value: {client_secret}\n")
    print(f"  Name: YOUTUBE_REFRESH_TOKEN")
    print(f"  Value: {creds.refresh_token}\n")
    print("=" * 62)
    print()
    print("  Where to add them:")
    print("  Your GitHub Repo → Settings → Secrets and variables")
    print("  → Actions → New repository secret")
    print()
    print("  Once all 4 secrets are added, the bot runs automatically")
    print("  every day at 10:00 AM UTC. You're done!")
    print("=" * 62)


if __name__ == "__main__":
    main()
