"""
video_assembler.py
Assembles slide images + narration audio into an MP4 video.
Adds cheerful background music generated with numpy (no external music needed).
Uses MoviePy 1.0.3 + system FFmpeg — both free.
"""
import os
import numpy as np
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    CompositeAudioClip,
)
from moviepy.audio.AudioClip import AudioArrayClip

SAMPLE_RATE = 44100


# ── Background music generator ────────────────────────────────────────────────

def _make_music(duration: float) -> np.ndarray:
    """
    Generates a simple, cheerful pentatonic melody using sine waves.
    Returns a stereo float32 array of shape (n_samples, 2).
    """
    # C-major pentatonic: C4 D4 E4 G4 A4
    PENTATONIC = [261.63, 293.66, 329.63, 392.00, 440.00]
    MELODY     = [0, 2, 4, 3, 1, 4, 2, 0, 1, 3, 2, 4]   # index pattern
    NOTE_DUR   = 0.45   # seconds per note

    n_total = int(SAMPLE_RATE * duration)
    music   = np.zeros(n_total, dtype=np.float32)
    note_n  = int(SAMPLE_RATE * NOTE_DUR)

    for i in range(n_total // note_n + 1):
        freq  = PENTATONIC[MELODY[i % len(MELODY)]]
        start = i * note_n
        end   = min(start + note_n, n_total)
        if start >= n_total:
            break
        seg = end - start
        t   = np.linspace(0.0, seg / SAMPLE_RATE, seg, dtype=np.float32)

        # Fundamental + 2 harmonics for warmth
        wave = (
            np.sin(2 * np.pi * freq * t)
            + 0.45 * np.sin(2 * np.pi * freq * 2 * t)
            + 0.20 * np.sin(2 * np.pi * freq * 3 * t)
        )

        # Short attack / release envelope
        fade = min(int(0.04 * SAMPLE_RATE), seg // 4)
        env  = np.ones(seg, dtype=np.float32)
        env[:fade]  = np.linspace(0.0, 1.0, fade)
        env[-fade:] = np.linspace(1.0, 0.0, fade)

        music[start:end] = wave * env * 0.09   # low background volume

    # Stereo (L == R)
    return np.column_stack([music, music])


# ── Video assembly ────────────────────────────────────────────────────────────

def assemble_video(slide_paths: list, audio_paths: list, output_path: str) -> str:
    """
    Combine each slide image with its narration audio, concatenate,
    mix in background music, and write the final MP4.
    """
    clips = []
    for img_path, aud_path in zip(slide_paths, audio_paths):
        narr  = AudioFileClip(aud_path)
        dur   = narr.duration + 0.35   # slight pause between slides
        clip  = ImageClip(img_path).set_duration(dur).set_audio(narr)
        clips.append(clip)

    video      = concatenate_videoclips(clips, method="compose")
    total_dur  = video.duration

    # Add background music
    try:
        music_arr = _make_music(total_dur)
        bg_music  = AudioArrayClip(music_arr, fps=SAMPLE_RATE).volumex(0.30)
        mixed     = CompositeAudioClip([video.audio, bg_music])
        video     = video.set_audio(mixed)
    except Exception as e:
        print(f"   ⚠  Background music skipped: {e}")

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="/tmp/kids_temp_audio.m4a",
        remove_temp=True,
        logger=None,          # suppress verbose moviepy output
    )

    return output_path
