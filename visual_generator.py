"""
visual_generator.py
Creates colourful 1280×720 slide images for each video using Pillow + numpy.
No external APIs required — 100 % free.
"""
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720   # HD resolution — YouTube-ready


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_gradient(c1: tuple, c2: tuple) -> Image.Image:
    """Fast vertical gradient via numpy."""
    a = np.array(c1, dtype=np.float32)
    b = np.array(c2, dtype=np.float32)
    t = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]   # (H,1)
    strip = (a * (1.0 - t) + b * t).astype(np.uint8)           # (H,3)
    full  = np.broadcast_to(strip[:, None, :], (H, W, 3)).copy()
    return Image.fromarray(full, "RGB")


def star_points(cx, cy, r_outer, r_inner, n=5):
    pts = []
    for i in range(2 * n):
        angle = math.pi / n * i - math.pi / 2
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return pts


def get_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap_text(text: str, font, draw, max_width: int) -> list:
    words = text.split()
    lines, line = [], []
    for word in words:
        test = " ".join(line + [word])
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] > max_width and line:
            lines.append(" ".join(line))
            line = [word]
        else:
            line.append(word)
    if line:
        lines.append(" ".join(line))
    return lines


# ── Decorations (per content type) ────────────────────────────────────────────

def add_decorations(draw: ImageDraw.ImageDraw, content_type: str, accent: tuple, seed: int = 42):
    """Draw fun background decorations — all with partial alpha."""
    rng = random.Random(seed)

    def a(alpha=120):
        return accent + (alpha,)

    if content_type in ("bedtime_story", "science_facts"):
        # Scattered stars
        for _ in range(28):
            x, y = rng.randint(15, W - 15), rng.randint(15, H - 15)
            r = rng.randint(6, 20)
            alpha = rng.randint(50, 160)
            draw.polygon(star_points(x, y, r, r // 2), fill=accent + (alpha,))

    elif content_type == "nursery_rhyme":
        # Colourful outlined circles
        palette = [(255, 80, 80), (255, 180, 50), (80, 220, 80), (50, 180, 255), (200, 80, 255)]
        for i in range(20):
            x, y = rng.randint(0, W), rng.randint(0, H)
            r = rng.randint(12, 48)
            col = palette[i % len(palette)] + (rng.randint(100, 200),)
            draw.ellipse([x - r, y - r, x + r, y + r], outline=col, width=4)

    elif content_type == "animal_facts":
        # Leaf-shaped ellipses
        for _ in range(14):
            x, y = rng.randint(20, W - 20), rng.randint(20, H - 20)
            w2, h2 = rng.randint(12, 38), rng.randint(22, 58)
            draw.ellipse([x - w2, y - h2, x + w2, y + h2], fill=accent + (rng.randint(60, 130),))

    elif content_type == "counting_numbers":
        # Filled circles (counting dots)
        for _ in range(16):
            x, y = rng.randint(20, W - 20), rng.randint(20, H - 20)
            r = rng.randint(10, 32)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=accent + (rng.randint(70, 140),))

    elif content_type == "alphabet_letters":
        # Outlined squares / rectangles
        for _ in range(18):
            x, y = rng.randint(10, W - 60), rng.randint(10, H - 60)
            s = rng.randint(18, 48)
            draw.rectangle([x, y, x + s, y + s], outline=accent + (rng.randint(80, 160),), width=3)

    elif content_type == "colors_and_shapes":
        # Mix of circles, squares, triangles
        for i in range(16):
            x, y = rng.randint(20, W - 20), rng.randint(20, H - 20)
            r = rng.randint(14, 44)
            col = accent + (rng.randint(80, 160),)
            if i % 3 == 0:
                draw.ellipse([x - r, y - r, x + r, y + r], outline=col, width=3)
            elif i % 3 == 1:
                draw.rectangle([x - r, y - r, x + r, y + r], outline=col, width=3)
            else:
                draw.polygon([(x, y - r), (x + r, y + r), (x - r, y + r)], outline=col)

    elif content_type == "nature_facts":
        # Soft bubble circles
        for _ in range(22):
            x, y = rng.randint(20, W - 20), rng.randint(20, H - 20)
            r = rng.randint(6, 28)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=accent + (rng.randint(80, 160),), width=2)

    else:
        # Generic dots
        for _ in range(20):
            x, y = rng.randint(10, W - 10), rng.randint(10, H - 10)
            r = rng.randint(4, 16)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=accent + (rng.randint(60, 130),))


# ── Slide builder ─────────────────────────────────────────────────────────────

def create_slide(text: str, slide_idx: int, total_slides: int, theme: dict, content_type: str) -> Image.Image:
    accent     = tuple(theme["accent"])
    text_color = tuple(theme["text"])

    # 1. Gradient base
    base = make_gradient(tuple(theme["bg1"]), tuple(theme["bg2"]))

    # 2. RGBA overlay: decorations + semi-transparent card
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)

    add_decorations(ov_draw, content_type, accent, seed=slide_idx * 13 + 42)

    # Card background
    cx1, cy1 = 70, H // 4 - 10
    cx2, cy2 = W - 70, H * 3 // 4 + 10
    ov_draw.rectangle([cx1, cy1, cx2, cy2], fill=(0, 0, 0, 115))

    # Top accent bar
    ov_draw.rectangle([cx1, cy1, cx2, cy1 + 8], fill=accent + (200,))

    # Composite
    result = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    draw   = ImageDraw.Draw(result)

    # 3. Text — with automatic size reduction if needed
    max_w = cx2 - cx1 - 90
    for font_size in (74, 60, 48, 38):
        font  = get_font(font_size)
        lines = wrap_text(text, font, draw, max_w)
        if len(lines) <= 4:
            break

    bbox_ref = draw.textbbox((0, 0), "Ag", font=font)
    line_h   = (bbox_ref[3] - bbox_ref[1]) + 22
    total_h  = len(lines) * line_h
    start_y  = (cy1 + cy2) // 2 - total_h // 2

    for i, line in enumerate(lines):
        bx = draw.textbbox((0, 0), line, font=font)
        tw = bx[2] - bx[0]
        x  = (W - tw) // 2
        y  = start_y + i * line_h
        # Drop shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0))
        # Main text
        draw.text((x, y), line, font=font, fill=text_color)

    # 4. Progress dots
    if total_slides > 1:
        sp, r_big, r_sm = 30, 10, 6
        total_w = (total_slides - 1) * sp
        dx0 = (W - total_w) // 2
        dy  = H - 36
        for i in range(total_slides):
            cx = dx0 + i * sp
            if i == slide_idx:
                draw.ellipse([cx - r_big, dy - r_big, cx + r_big, dy + r_big], fill=text_color)
            else:
                draw.ellipse([cx - r_sm, dy - r_sm, cx + r_sm, dy + r_sm], fill=accent)

    # 5. Channel watermark
    wm_font = get_font(22)
    wm_text = "KidsLearnFun"
    wb = draw.textbbox((0, 0), wm_text, font=wm_font)
    draw.text((W - (wb[2] - wb[0]) - 18, H - 32), wm_text, font=wm_font,
              fill=tuple(max(0, c - 30) for c in text_color))

    return result


# ── Public API ────────────────────────────────────────────────────────────────

def generate_slides(script: dict, output_dir: str) -> list:
    os.makedirs(output_dir, exist_ok=True)
    paths  = []
    slides = script["slides"]
    for i, slide in enumerate(slides):
        img  = create_slide(slide["text"], i, len(slides), script["theme"], script["content_type"])
        path = os.path.join(output_dir, f"slide_{i:02d}.png")
        img.save(path, "PNG")
        paths.append(path)
        print(f"   Slide {i + 1}/{len(slides)}: {slide['text'][:50]}")
    return paths
