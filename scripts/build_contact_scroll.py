#!/usr/bin/env python3
"""
Contact Scroll GIF Generator
Generates an authentic animated GIF of a realistic ancient parchment scroll.
Begins closed, unrolls vertically from top to bottom, reveals contact information,
holds for comfortable readability, and loops cleanly.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

CONTACT_INFO = {
    "name": "Yuvraj Singh",
    "github": "github.com/uvv-01",
    "linkedin": "linkedin.com/in/yuvraj-singh-b70670356/",
    "email": "yuvrajsinghdnb2006@gmail.com",
}

def draw_wooden_roller(draw, x1, y, x2, h=14):
    # Turned aged walnut wood spindle with brass end-caps
    # Spindle body
    for row in range(h):
        t = row / max(1, h - 1)
        # Cylindrical shading
        if t < 0.3:
            col = (74, 46, 27)
        elif t < 0.7:
            col = (50, 28, 14)
        else:
            col = (31, 16, 7)
        draw.line([(x1 + 6, y + row), (x2 - 6, y + row)], fill=col)

    # Brass end-caps
    cap_w = 8
    cap_h = h + 4
    cap_y = y - 2
    # Left brass cap
    draw.rounded_rectangle([x1 - cap_w, cap_y, x1 + 6, cap_y + cap_h], radius=2, fill=(184, 134, 11), outline=(100, 70, 5))
    draw.line([(x1 - cap_w + 2, cap_y + 2), (x1 - cap_w + 2, cap_y + cap_h - 2)], fill=(220, 180, 50))
    # Right brass cap
    draw.rounded_rectangle([x2 - 6, cap_y, x2 + cap_w, cap_y + cap_h], radius=2, fill=(184, 134, 11), outline=(100, 70, 5))
    draw.line([(x2 + 2, cap_y + 2), (x2 + 2, cap_y + cap_h - 2)], fill=(220, 180, 50))

def generate_contact_scroll_gif():
    print("Generating Realistic Ancient Parchment Contact Scroll GIF...")
    W = 960
    H = 280

    bg_color = (13, 17, 23)
    border_color = (48, 54, 61)
    hud_gray = (139, 148, 158)
    hud_white = (240, 246, 252)

    parch_w = 640
    parch_x1 = (W - parch_w) // 2
    parch_x2 = parch_x1 + parch_w
    center_y = 50
    full_h = 190

    # Fonts
    try:
        font_sm = ImageFont.truetype("consola.ttf", 10)
        font_md = ImageFont.truetype("consola.ttf", 11)
        font_header = ImageFont.truetype("georgia.ttf", 12)
        font_name = ImageFont.truetype("georgia.ttf", 17)
        font_meta = ImageFont.truetype("consola.ttf", 12)
        font_link = ImageFont.truetype("consola.ttf", 12)
    except Exception:
        font_sm = ImageFont.load_default()
        font_md = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_meta = ImageFont.load_default()
        font_link = ImageFont.load_default()

    frames = []
    durations = []

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 1: CLOSED SCROLL (Held closed for ~1.2 seconds = 6 frames @ 200ms)
    # ─────────────────────────────────────────────────────────────────────────
    for c in range(6):
        img = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(img)

        # Panel Border & Header
        draw.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw.text((28, 22), "CONTACT DISPATCH // ARCHIVE RECORD", fill=hud_white, font=font_sm)
        draw.text((W - 200, 22), "STATUS: SEALED MANUSCRIPT", fill=hud_gray, font=font_sm)
        draw.line([(24, 36), (W - 24, 36)], fill=border_color, width=1)

        closed_y = H // 2 - 12
        # Drop shadow beneath closed roll
        draw.ellipse([parch_x1 + 10, closed_y + 18, parch_x2 - 10, closed_y + 36], fill=(5, 7, 10))

        # Rolled parchment cylinder body
        for row in range(24):
            t = row / 23.0
            if t < 0.2:
                col = (184, 143, 88)
            elif t < 0.6:
                col = (237, 217, 182)
            elif t < 0.85:
                col = (245, 231, 203)
            else:
                col = (154, 114, 62)
            draw.line([(parch_x1 + 16, closed_y + row), (parch_x2 - 16, closed_y + row)], fill=col)

        # Weathered tie band
        draw.rectangle([W//2 - 6, closed_y, W//2 + 6, closed_y + 24], fill=(85, 54, 24))

        # Top and bottom roller spindles
        draw_wooden_roller(draw, parch_x1, closed_y - 8, parch_x2, h=10)
        draw_wooden_roller(draw, parch_x1, closed_y + 22, parch_x2, h=10)

        # Closed scroll prompt
        draw.text((W // 2 - 110, closed_y + 48), "✦ ANCIENT CORRESPONDENCE ARCHIVE ✦", fill=(184, 143, 88), font=font_sm)
        draw.text((28, H - 24), "DISPATCH TELEMETRY: READY", fill=hud_gray, font=font_sm)

        frames.append(img)
        durations.append(200)

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 2: UNROLLING PROGRESSIVELY FROM TOP TO BOTTOM (~0.9s = 9 frames @ 100ms)
    # ─────────────────────────────────────────────────────────────────────────
    unroll_steps = 9
    for u in range(1, unroll_steps + 1):
        progress = u / float(unroll_steps)
        # Natural ease-out
        t_ease = math.sin(progress * math.pi / 2)
        cur_h = int(full_h * t_ease)

        img = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw.text((28, 22), "CONTACT DISPATCH // ARCHIVE RECORD", fill=hud_white, font=font_sm)
        draw.text((W - 200, 22), "STATUS: UNROLLING MANUSCRIPT", fill=(217, 119, 6), font=font_sm)
        draw.line([(24, 36), (W - 24, 36)], fill=border_color, width=1)

        top_y = center_y
        bot_y = top_y + cur_h

        # Soft shadow behind unrolling parchment
        draw.rectangle([parch_x1 + 10, top_y + 4, parch_x2 - 10, bot_y + 12], fill=(5, 7, 10))

        # Parchment background expanding downward
        draw.rectangle([parch_x1 + 14, top_y + 6, parch_x2 - 14, bot_y + 2], fill=(236, 217, 181), outline=(184, 145, 93))

        # Worn aged borders and subtle creasing
        draw.line([(parch_x1 + 16, top_y + 6), (parch_x1 + 16, bot_y + 2)], fill=(160, 120, 70))
        draw.line([(parch_x2 - 16, top_y + 6), (parch_x2 - 16, bot_y + 2)], fill=(160, 120, 70))

        # Content becomes progressively visible as parchment expands
        if cur_h > 60:
            draw.text((W // 2 - 65, top_y + 16), "CONTACT DISPATCH", fill=(124, 88, 53), font=font_header)
            draw.line([(parch_x1 + 40, top_y + 34), (parch_x2 - 40, top_y + 34)], fill=(196, 164, 120), width=1)

        if cur_h > 100:
            draw.text((W // 2 - 55, top_y + 40), CONTACT_INFO["name"], fill=(44, 26, 14), font=font_name)

        if cur_h > 140:
            # GitHub line
            draw.text((parch_x1 + 50, top_y + 72), "GITHUB", fill=(109, 76, 43), font=font_meta)
            draw.text((parch_x1 + 140, top_y + 72), CONTACT_INFO["github"], fill=(31, 18, 10), font=font_link)

        if cur_h > 170:
            # LinkedIn line
            draw.text((parch_x1 + 50, top_y + 98), "LINKEDIN", fill=(109, 76, 43), font=font_meta)
            draw.text((parch_x1 + 140, top_y + 98), CONTACT_INFO["linkedin"], fill=(31, 18, 10), font=font_link)

        # Top and bottom rollers
        draw_wooden_roller(draw, parch_x1, top_y, parch_x2, h=10)
        draw_wooden_roller(draw, parch_x1, bot_y, parch_x2, h=10)

        draw.text((28, H - 24), "DISPATCH TELEMETRY: REVEALING", fill=hud_gray, font=font_sm)

        frames.append(img)
        durations.append(100)

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 3: FULLY OPENED CONTACT INFORMATION (Held for ~5.0 seconds = 10 frames @ 500ms)
    # ─────────────────────────────────────────────────────────────────────────
    for o in range(10):
        img = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw.text((28, 22), "CONTACT DISPATCH // ARCHIVE RECORD", fill=hud_white, font=font_md)
        draw.text((W - 200, 22), "STATUS: DISPATCH REVEALED", fill=(34, 197, 94), font=font_sm)
        draw.line([(24, 36), (W - 24, 36)], fill=border_color, width=1)

        top_y = center_y
        bot_y = top_y + full_h

        # Drop shadow behind open parchment
        draw.rectangle([parch_x1 + 10, top_y + 4, parch_x2 - 10, bot_y + 12], fill=(5, 7, 10))

        # Aged yellowish-beige parchment body with sepia texture
        draw.rectangle([parch_x1 + 14, top_y + 6, parch_x2 - 14, bot_y + 2], fill=(236, 217, 181), outline=(184, 145, 93))
        # Inner fine border
        draw.rectangle([parch_x1 + 22, top_y + 12, parch_x2 - 22, bot_y - 4], outline=(204, 174, 130), width=1)

        # Subtle parchment aging gradients & deckle edges
        draw.line([(parch_x1 + 16, top_y + 6), (parch_x1 + 16, bot_y + 2)], fill=(160, 120, 70), width=1)
        draw.line([(parch_x2 - 16, top_y + 6), (parch_x2 - 16, bot_y + 2)], fill=(160, 120, 70), width=1)

        # Header Title
        draw.text((W // 2 - 65, top_y + 16), "CONTACT DISPATCH", fill=(124, 88, 53), font=font_header)
        draw.line([(parch_x1 + 40, top_y + 34), (parch_x2 - 40, top_y + 34)], fill=(196, 164, 120), width=1)

        # Name
        draw.text((W // 2 - 55, top_y + 40), CONTACT_INFO["name"], fill=(44, 26, 14), font=font_name)

        # Contact Details Rows (Clear, prominent, readable)
        row_y = top_y + 72
        # GitHub
        draw.rounded_rectangle([parch_x1 + 40, row_y - 3, parch_x2 - 40, row_y + 18], radius=3, fill=(245, 232, 207), outline=(210, 180, 140))
        draw.text((parch_x1 + 52, row_y + 1), "GITHUB", fill=(109, 76, 43), font=font_meta)
        draw.text((parch_x1 + 140, row_y + 1), CONTACT_INFO["github"], fill=(31, 18, 10), font=font_link)

        # LinkedIn
        row_y += 28
        draw.rounded_rectangle([parch_x1 + 40, row_y - 3, parch_x2 - 40, row_y + 18], radius=3, fill=(245, 232, 207), outline=(210, 180, 140))
        draw.text((parch_x1 + 52, row_y + 1), "LINKEDIN", fill=(109, 76, 43), font=font_meta)
        draw.text((parch_x1 + 140, row_y + 1), CONTACT_INFO["linkedin"], fill=(31, 18, 10), font=font_link)

        # Email
        row_y += 28
        draw.rounded_rectangle([parch_x1 + 40, row_y - 3, parch_x2 - 40, row_y + 18], radius=3, fill=(245, 232, 207), outline=(210, 180, 140))
        draw.text((parch_x1 + 52, row_y + 1), "EMAIL", fill=(109, 76, 43), font=font_meta)
        draw.text((parch_x1 + 140, row_y + 1), CONTACT_INFO["email"], fill=(31, 18, 10), font=font_link)

        # Footer note on parchment
        draw.text((W // 2 - 160, bot_y - 20), "Available for engineering collaborations & algorithmic discussion", fill=(140, 105, 65), font=font_sm)

        # Top and bottom wooden roller spindles
        draw_wooden_roller(draw, parch_x1, top_y, parch_x2, h=10)
        draw_wooden_roller(draw, parch_x1, bot_y, parch_x2, h=10)

        # Status text
        draw.text((28, H - 24), "DISPATCH TELEMETRY: COMPLETE (CLICK TO VISIT PROFILE)", fill=(34, 197, 94), font=font_sm)

        frames.append(img)
        durations.append(500)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    out_path = os.path.join(out_dir, "contact-scroll.gif")
    out_path = os.path.normpath(out_path)
    os.makedirs(out_dir, exist_ok=True)

    p_frames = [f.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for f in frames]
    p_frames[0].save(
        out_path,
        save_all=True,
        append_images=p_frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    sz = os.path.getsize(out_path)
    print(f"Contact Scroll GIF created: {out_path} ({sz} bytes, {sz/1024:.1f} KB)")
    return True

if __name__ == "__main__":
    generate_contact_scroll_gif()
