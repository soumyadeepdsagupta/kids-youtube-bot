"""
main.py — Kids YouTube Bot orchestrator
Runs the full pipeline:
  1. Generate script  (Groq — free)
  2. Create slides    (Pillow — free)
  3. Generate audio   (edge-tts — free)
  4. Assemble video   (MoviePy/FFmpeg — free)
  5. Upload to YouTube (Data API v3 — free quota)
"""
import os
import sys
import shutil
from datetime import datetime, timezone

# Allow imports from same directory when run as `python main.py`
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from script_generator import generate_script
from visual_generator  import generate_slides
from audio_generator   import generate_all_audio
from video_assembler   import assemble_video
from youtube_uploader  import upload_to_youtube

WORK_DIR = "/tmp/kids_video_pipeline"


def banner(msg: str):
    print(f"\n{'─' * 58}")
    print(f"  {msg}")
    print(f"{'─' * 58}")


def main():
    banner(f"Kids Video Bot  ·  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    # ── Load secrets from environment ─────────────────────────────────────────
    groq_key       = os.environ.get("GROQ_API_KEY")
    yt_client_id   = os.environ.get("YOUTUBE_CLIENT_ID")
    yt_client_sec  = os.environ.get("YOUTUBE_CLIENT_SECRET")
    yt_refresh     = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    missing = [k for k, v in {
        "GROQ_API_KEY":           groq_key,
        "YOUTUBE_CLIENT_ID":      yt_client_id,
        "YOUTUBE_CLIENT_SECRET":  yt_client_sec,
        "YOUTUBE_REFRESH_TOKEN":  yt_refresh,
    }.items() if not v]

    if missing:
        print(f"\n❌  Missing environment variables: {', '.join(missing)}")
        print("    Add them as GitHub Secrets (see README.md).")
        sys.exit(1)

    # ── Workspace ──────────────────────────────────────────────────────────────
    slides_dir = os.path.join(WORK_DIR, "slides")
    audio_dir  = os.path.join(WORK_DIR, "audio")
    video_path = os.path.join(WORK_DIR, "video.mp4")

    if os.path.exists(WORK_DIR):
        shutil.rmtree(WORK_DIR)
    os.makedirs(WORK_DIR)

    # ── Step 1: Script ─────────────────────────────────────────────────────────
    print("\n📝  [1/5] Generating script with Groq…")
    script = generate_script(groq_key)
    print(f"   Type    : {script['content_name']}  ({script['content_type']})")
    print(f"   Duration: {script['duration']}s  |  Slides: {len(script['slides'])}")
    print(f"   Title   : {script['video_title']}")

    # ── Step 2: Slide images ───────────────────────────────────────────────────
    print("\n🎨  [2/5] Creating slide images (Pillow)…")
    slide_paths = generate_slides(script, slides_dir)

    # ── Step 3: Narration audio ────────────────────────────────────────────────
    print("\n🎙   [3/5] Generating narration audio (edge-tts)…")
    audio_paths = generate_all_audio(script, audio_dir)

    # ── Step 4: Video assembly ─────────────────────────────────────────────────
    print("\n🎬  [4/5] Assembling video (MoviePy + FFmpeg)…")
    assemble_video(slide_paths, audio_paths, video_path)
    size_mb = os.path.getsize(video_path) / 1_048_576
    print(f"   Output  : {video_path}  ({size_mb:.1f} MB)")

    # ── Step 5: YouTube upload ─────────────────────────────────────────────────
    print("\n📺  [5/5] Uploading to YouTube…")
    url = upload_to_youtube(
        video_path=video_path,
        title=script["video_title"],
        description=script["description"],
        tags=script["tags"],
        client_id=yt_client_id,
        client_secret=yt_client_sec,
        refresh_token=yt_refresh,
    )

    banner(f"✅  Published → {url}")

    # ── Cleanup ────────────────────────────────────────────────────────────────
    shutil.rmtree(WORK_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()
