# 🎬 Kids YouTube Bot — Fully Automated

Generates and publishes a **new kids video every single day** to YouTube — completely automatically.  
All tools are **100% free**. After a 15-minute one-time setup, you never touch it again.

---

## What it does

| Step | Tool | Cost |
|------|------|------|
| Writes a fun kids script | Groq (Llama 3) | Free |
| Creates colourful slide images | Pillow (Python) | Free |
| Adds warm narration voice | Microsoft edge-tts | Free |
| Generates background music | NumPy sine waves | Free |
| Assembles the MP4 video | MoviePy + FFmpeg | Free |
| Uploads to YouTube daily | YouTube Data API v3 | Free |
| Runs on a schedule | GitHub Actions | Free |

**Content rotates automatically** through 8 types — alternating 30 s and 60 s videos:

> Bedtime Stories · Nursery Rhymes · Animal Facts · Counting · Alphabet ·  
> Colours & Shapes · Science Facts · Nature Facts

---

## One-time setup (~15 minutes)

### Step 1 — Create your GitHub repository

1. Go to [github.com](https://github.com) → **New repository**
2. Name it `kids-youtube-bot` → **Public** → Create
3. Upload all these project files (drag-and-drop in the GitHub UI, or use git)

### Step 2 — Set up YouTube API (Google Cloud — free)

1. Go to **[console.cloud.google.com](https://console.cloud.google.com)**
2. Click **"Select a project"** → **"New Project"**  
   Name: `Kids YouTube Bot` → **Create**
3. Left menu → **APIs & Services** → **Library**  
   Search **"YouTube Data API v3"** → Click it → **Enable**
4. Left menu → **APIs & Services** → **Credentials**  
   Click **"+ Create Credentials"** → **"OAuth client ID"**
   - If it asks you to configure the consent screen first:
     - User Type: **External** → Create
     - App name: `Kids YouTube Bot` | Add your email → Save & Continue (skip the rest)
     - Add yourself as a **Test user** → Save
   - Back on Credentials → **"+ Create Credentials"** → **"OAuth client ID"**
   - Application type: **Desktop app** → Name: `kids-bot` → **Create**
5. **Copy your Client ID and Client Secret** (you'll need them in Step 3)

### Step 3 — Get your YouTube refresh token (run once on your computer)

```bash
# Install the one dependency needed just for this step
pip install google-auth-oauthlib

# Run the setup script
python setup_auth.py
```

- Follow the prompts — paste your Client ID and Client Secret
- A browser window opens → log in with your YouTube channel account → Allow
- The script prints **4 values** — copy them all

### Step 4 — Add GitHub Secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

Add these 4 secrets (exact names, paste the values from Step 3):

| Secret Name | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys |
| `YOUTUBE_CLIENT_ID` | From setup_auth.py output |
| `YOUTUBE_CLIENT_SECRET` | From setup_auth.py output |
| `YOUTUBE_REFRESH_TOKEN` | From setup_auth.py output |

---

## ✅ Done! That's it.

The bot now runs **automatically every day at 10:00 AM UTC**.

- A new video is generated and published to your YouTube channel daily
- You can also trigger a manual run: GitHub repo → **Actions** tab → **Daily Kids Video** → **Run workflow**
- Check run logs: Actions tab → click the latest run

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `GROQ_API_KEY` error | Check the secret name is exact — no spaces |
| YouTube upload fails with 403 | Your OAuth app may still be in "testing" — add your account as a test user in Google Cloud Console |
| Font looks wrong | The workflow installs `fonts-dejavu-core` — it works on GitHub Actions Ubuntu |
| Video not appearing on YouTube | Check your YouTube Studio — it may be processing |

---

## Project structure

```
kids-youtube-bot/
├── .github/workflows/daily_video.yml   ← Runs every day automatically
├── main.py                              ← Pipeline orchestrator
├── script_generator.py                 ← Groq AI content writing
├── visual_generator.py                 ← Pillow slide images
├── audio_generator.py                  ← edge-tts narration
├── video_assembler.py                  ← MoviePy video assembly
├── youtube_uploader.py                 ← YouTube Data API upload
├── setup_auth.py                       ← One-time OAuth setup (local only)
└── requirements.txt                    ← Python dependencies
```

---

*100% free · no credit card · no paid APIs · runs forever automatically*
