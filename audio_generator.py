"""
audio_generator.py
Generates narration audio using Microsoft edge-tts (completely free, no API key).
Neural voices — high quality, warm, kid-friendly.
"""
import asyncio
import os
import edge_tts

# Best voice per content type
VOICES = {
    "bedtime_story":     "en-US-JennyNeural",    # Soft, warm
    "nursery_rhyme":     "en-US-AriaNeural",      # Upbeat, playful
    "animal_facts":      "en-US-GuyNeural",       # Clear, friendly
    "counting_numbers":  "en-US-JennyNeural",
    "alphabet_letters":  "en-US-AriaNeural",
    "colors_and_shapes": "en-US-JennyNeural",
    "science_facts":     "en-US-GuyNeural",
    "nature_facts":      "en-US-AriaNeural",
}

FALLBACK_VOICES = [
    "en-US-JennyNeural",
    "en-US-AriaNeural",
    "en-US-GuyNeural",
    "en-GB-SoniaNeural",
]


async def _tts(text: str, voice: str, path: str):
    """Async TTS call via edge-tts."""
    communicate = edge_tts.Communicate(text, voice, rate="+5%", volume="+10%")
    await communicate.save(path)


def generate_slide_audio(narration: str, voice: str, path: str):
    """Generate audio for a single slide narration."""
    for v in [voice] + FALLBACK_VOICES:
        try:
            asyncio.run(_tts(narration, v, path))
            return
        except Exception as e:
            print(f"   Voice {v} failed: {e}. Trying next…")
    raise RuntimeError(f"All TTS voices failed for narration: {narration[:40]}")


def generate_all_audio(script: dict, output_dir: str) -> list:
    """Generate one audio file per slide. Returns list of paths."""
    os.makedirs(output_dir, exist_ok=True)
    voice  = VOICES.get(script["content_type"], "en-US-JennyNeural")
    paths  = []
    slides = script["slides"]

    for i, slide in enumerate(slides):
        path = os.path.join(output_dir, f"audio_{i:02d}.mp3")
        generate_slide_audio(slide["narration"], voice, path)
        paths.append(path)
        print(f"   Audio {i + 1}/{len(slides)}: OK")

    return paths
