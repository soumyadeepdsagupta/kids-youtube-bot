"""
script_generator.py
Uses Groq's OpenAI-compatible API (llama-3.3-70b-versatile) to generate
structured JSON scripts for kids YouTube videos.
Rotates through 8 content types and alternates 30s / 60s daily.
"""
import json
from datetime import datetime
from openai import OpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL    = "llama-3.3-70b-versatile"

# ── Content rotation ─────────────────────────────────────────────────────────

CONTENT_TYPES = [
    "bedtime_story",
    "nursery_rhyme",
    "animal_facts",
    "counting_numbers",
    "alphabet_letters",
    "colors_and_shapes",
    "science_facts",
    "nature_facts",
]

CONTENT_NAMES = {
    "bedtime_story":     "Bedtime Story",
    "nursery_rhyme":     "Nursery Rhyme",
    "animal_facts":      "Animal Facts",
    "counting_numbers":  "Counting Fun",
    "alphabet_letters":  "ABC Fun",
    "colors_and_shapes": "Colors & Shapes",
    "science_facts":     "Fun Science",
    "nature_facts":      "Nature Facts",
}

# ── Visual theme per content type ─────────────────────────────────────────────

THEME_COLORS = {
    "bedtime_story":     {"bg1": (20,  20,  80),  "bg2": (80,  20, 100), "text": (255, 230, 100), "accent": (180, 150, 255)},
    "nursery_rhyme":     {"bg1": (210, 50, 110),  "bg2": (255, 150,  40), "text": (255, 255, 255), "accent": (100, 220, 255)},
    "animal_facts":      {"bg1": (25,  95,  25),  "bg2": (75, 145,  35), "text": (255, 255, 200), "accent": (255, 200,  80)},
    "counting_numbers":  {"bg1": (35,  35, 175),  "bg2": (175, 35, 175), "text": (255, 255, 100), "accent": (100, 255, 180)},
    "alphabet_letters":  {"bg1": (195, 35,  35),  "bg2": (250, 135,  35), "text": (255, 255, 255), "accent": (100, 255, 120)},
    "colors_and_shapes": {"bg1": (75,   0, 175),  "bg2": (  0, 135, 215), "text": (255, 255, 100), "accent": (255, 160,  50)},
    "science_facts":     {"bg1": (  0,  15,  55),  "bg2": (  0,  75, 125), "text": (160, 220, 255), "accent": (255, 200,  50)},
    "nature_facts":      {"bg1": (  0,  95,  45),  "bg2": (35, 135, 195), "text": (255, 255, 200), "accent": (255, 150,  80)},
}

# ── Per-type prompts ──────────────────────────────────────────────────────────

TOPIC_PROMPTS = {
    "bedtime_story":     "a sweet, calming bedtime story with a simple moral for kids aged 3-6",
    "nursery_rhyme":     "a brand-new fun rhyming nursery rhyme for kids aged 2-5",
    "animal_facts":      "amazing, surprising animal facts for kids aged 4-8",
    "counting_numbers":  "a fun, engaging counting lesson for kids aged 2-5",
    "alphabet_letters":  "a playful alphabet / letter recognition lesson for kids aged 3-6",
    "colors_and_shapes": "a vibrant lesson about colors and shapes for kids aged 2-5",
    "science_facts":     "simple, mind-blowing science facts explained for kids aged 5-8",
    "nature_facts":      "wonderful nature and earth facts for kids aged 4-8",
}

# ─────────────────────────────────────────────────────────────────────────────

def get_todays_plan():
    day = datetime.now().timetuple().tm_yday          # 1-365
    content_type = CONTENT_TYPES[day % len(CONTENT_TYPES)]
    duration     = 30 if day % 2 == 0 else 60
    num_slides   = 3  if duration == 30 else 5
    return content_type, duration, num_slides


def generate_script(groq_api_key: str) -> dict:
    content_type, duration, num_slides = get_todays_plan()
    client = OpenAI(api_key=groq_api_key, base_url=GROQ_BASE_URL)

    prompt = f"""Create content for a {duration}-second kids YouTube video about {TOPIC_PROMPTS[content_type]}.

Return ONLY valid JSON — no markdown fences, no extra text — with EXACTLY {num_slides} slides:
{{
  "video_title": "Catchy YouTube title under 60 chars, include 1-2 relevant emojis",
  "description": "Engaging YouTube video description, 120-150 characters",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6"],
  "slides": [
    {{
      "text": "Short on-screen text — max 10 words",
      "narration": "Warm, fun narrator speech for this slide — 1 to 2 sentences"
    }}
  ]
}}

Slide rules:
  • Slide 1  : Exciting title / intro slide
  • Middle   : Main educational content — fun and varied
  • Last slide: text = "Subscribe for more fun every day!" narration = warm goodbye
Keep ALL content safe, joyful, and age-appropriate."""

    last_error = None
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional children's YouTube content creator. "
                            "ALWAYS return ONLY valid JSON, nothing else whatsoever."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=950,
                temperature=0.85,
            )

            raw = response.choices[0].message.content.strip()

            # Strip accidental markdown code fences
            if "```" in raw:
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else parts[0]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()

            script = json.loads(raw)

            # Validate required keys
            assert "video_title" in script
            assert "slides" in script
            assert len(script["slides"]) >= 1

            script["content_type"]  = content_type
            script["duration"]      = duration
            script["theme"]         = THEME_COLORS[content_type]
            script["content_name"]  = CONTENT_NAMES[content_type]
            return script

        except (json.JSONDecodeError, AssertionError, KeyError) as e:
            last_error = e
            print(f"   Script attempt {attempt + 1} failed: {e}. Retrying…")

    raise RuntimeError(f"Failed to generate a valid script after 3 attempts: {last_error}")
