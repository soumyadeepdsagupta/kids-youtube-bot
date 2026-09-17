"""
youtube_uploader.py
Uploads the finished video to YouTube using the Data API v3 (free quota).
Uses a stored refresh token — no browser interaction needed during automation.
"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


CATEGORY_EDUCATION = "27"


def upload_to_youtube(
    video_path:     str,
    title:          str,
    description:    str,
    tags:           list,
    client_id:      str,
    client_secret:  str,
    refresh_token:  str,
) -> str:
    """Upload video and return the public YouTube URL."""

    # Build credentials from stored refresh token (no browser needed)
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )
    creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)

    # Build the full description
    tag_line = "  ".join(f"#{t.replace(' ', '')}" for t in tags[:8])
    full_description = (
        f"{description}\n\n"
        "🌟 New fun video every single day! Subscribe so you never miss one! 🌟\n\n"
        f"{tag_line}\n"
        "#KidsVideos #ChildrenLearning #KidsEducation #Fun4Kids #Preschool"
    )

    # Merge user tags with generic kids tags (deduplicated)
    all_tags = list(dict.fromkeys(
        tags + ["kids", "children", "education", "learning",
                "preschool", "toddler", "fun", "KidsLearnFun"]
    ))

    body = {
        "snippet": {
            "title":           title,
            "description":     full_description,
            "tags":            all_tags,
            "categoryId":      CATEGORY_EDUCATION,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus":               "public",
            "madeForKids":                 True,
            "selfDeclaredMadeForKids":     True,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=2 * 1024 * 1024,   # 2 MB chunks
    )

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    print("   Uploading", end="", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"\r   Uploading {pct}% …", end="", flush=True)
    print("\r   Upload complete!      ")

    video_id = response["id"]
    return f"https://www.youtube.com/watch?v={video_id}"
