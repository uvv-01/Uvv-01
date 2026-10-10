#!/usr/bin/env python3
"""
Contact Scroll Generator
Generates an animated GIF of a glowing rolled scroll that begins closed,
pulses for ~2 seconds, unrolls smoothly, and reveals authentic contact details.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

CONTACT_INFO = {
    "name": "Yuvraj Singh",
    "email": "yuvrajsinghdnb2006@gmail.com",
    "github": "github.com/uvv-01",
    "linkedin": "linkedin.com/in/yuvraj-singh-b70670356",
}

def generate_contact_scroll_gif():
    print("Generating Glowing Contact Scroll GIF...")
    W = 960
    H = 280

    bg_color = (7, 10, 19)
    border_color = (30, 41, 59)
    gold_primary = (251, 191, 36)      # #fbbf24
    gold_dim = (180, 130, 20)
    cyan_neon = (0, 240, 255)
    text_white = (248, 250, 252)
    text_muted = (148, 163, 184)

    # Fonts
    try:
        font_title = ImageFont.truetype("consola.ttf", 15)
        font_name = ImageFont.truetype("consola.ttf", 16)
        font_body = ImageFont.truetype("consola.ttf", 12)
        font_sm = ImageFont.truetype("consola.ttf", 10)
    except Exception:
        font_title = ImageFont.load_default()
        font_name = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_sm = ImageFont.load_default()

    frames = []
    durations = []

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 1: CLOSED SCROLL (~2.0 seconds = 10 frames @ 200ms each)
    # ─────────────────────────────────────────────────────────────────────────
    closed_frames_count = 10
    center_y = H // 2
    scroll_w = 420
    scroll_x1 = (W - scroll_w) // 2
    scroll_x2 = scroll_x1 + scroll_w

    for i in range(closed_frames_count):
        img = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(img)

        # Outer HUD Card Border
        draw.rounded_rectangle([16, 16, W - 16, H - 16], radius=10, outline=border_color, width=1)
        # Chamfer corner accents
        draw.line([(16, 32), (32, 16)], fill=gold_primary, width=2)
        draw.line([(W - 32, 16), (W - 16, 32)], fill=gold_primary, width=2)
        draw.line([(16, H - 32), (32, H - 16)], fill=gold_primary, width=2)
        draw.line([(W - 32, H - 16), (W - 16, H - 32)], fill=gold_primary, width=2)

        # Top HUD Status
        draw.text((36, 26), "// CONTACT PROTOCOL //", fill=gold_primary, font=font_sm)
        draw.text((W - 200, 26), "STATUS: SEALED SCROLL", fill=text_muted, font=font_sm)

        # Pulsing glow intensity (sine wave over 2 seconds)
        glow_pulse = math.sin((i / closed_frames_count) * math.pi * 2)
        glow_rad = 18 + int(6 * glow_pulse)
        seal_glow_alpha = 150 + int(80 * glow_pulse)

        # Ambient glow behind closed scroll
        for r in range(glow_rad, 0, -3):
            alpha_col = (int(30 + r * 1.5), int(20 + r), 5)
            draw.rounded_rectangle(
                [scroll_x1 - r, center_y - 20 - r//2, scroll_x2 + r, center_y + 20 + r//2],
                radius=14, fill=alpha_col
            )

        # Closed scroll cylinder body
        scroll_rect = [scroll_x1, center_y - 18, scroll_x2, center_y + 18]
        draw.rounded_rectangle(scroll_rect, radius=8, fill=(28, 22, 14), outline=gold_primary, width=2)

        # Decorative scroll bindings (ribbon bands)
        for rx in [scroll_x1 + 60, scroll_x2 - 60]:
            draw.line([(rx, center_y - 18), (rx, center_y + 18)], fill=cyan_neon, width=3)

        # Ornate Roller End-caps (Spindles)
        # Left spindle
        draw.rounded_rectangle([scroll_x1 - 18, center_y - 24, scroll_x1, center_y + 24], radius=4, fill=(45, 34, 18), outline=gold_primary, width=2)
        draw.ellipse([scroll_x1 - 24, center_y - 10, scroll_x1 - 16, center_y + 10], fill=gold_primary)
        # Right spindle
        draw.rounded_rectangle([scroll_x2, center_y - 24, scroll_x2 + 18, center_y + 24], radius=4, fill=(45, 34, 18), outline=gold_primary, width=2)
        draw.ellipse([scroll_x2 + 16, center_y - 10, scroll_x2 + 24, center_y + 10], fill=gold_primary)

        # Glowing Cyber Crest / Seal in center
        seal_cx = W // 2
        draw.ellipse([seal_cx - 18, center_y - 18, seal_cx + 18, center_y + 18], fill=(60, 42, 12), outline=gold_primary, width=2)
        draw.text((seal_cx - 6, center_y - 8), "✦", fill=gold_primary, font=font_title)

        # Prompt hint
        draw.text((W // 2 - 120, center_y + 44), "✦ TRANSMISSION SECURED · DECRYPTING... ✦", fill=gold_primary, font=font_sm)

        # Bottom HUD
        draw.text((36, H - 36), "DATA ACCESS: AWAITING REVEAL", fill=(80, 95, 115), font=font_sm)

        frames.append(img)
        durations.append(200)  # 10 * 200ms = 2000ms (2.0s)

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 2: UNROLLING ANIMATION (~0.8 seconds = 8 frames @ 100ms each)
    # ─────────────────────────────────────────────────────────────────────────
    unroll_frames_count = 8
    target_unroll_w = 680
    target_unroll_h = 180
    unroll_x1 = (W - target_unroll_w) // 2
    unroll_x2 = unroll_x1 + target_unroll_w

    for j in range(unroll_frames_count):
        img = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(img)

        # Outer HUD Card Border
        draw.rounded_rectangle([16, 16, W - 16, H - 16], radius=10, outline=border_color, width=1)
        draw.line([(16, 32), (32, 16)], fill=gold_primary, width=2)
        draw.line([(W - 32, 16), (W - 16, 32)], fill=gold_primary, width=2)
        draw.line([(16, H - 32), (32, H - 16)], fill=gold_primary, width=2)
        draw.line([(W - 32, H - 16), (W - 16, H - 32)], fill=gold_primary, width=2)

        draw.text((36, 26), "// CONTACT PROTOCOL //", fill=gold_primary, font=font_sm)
        draw.text((W - 200, 26), "STATUS: UNROLLING TRANSMISSION", fill=cyan_neon, font=font_sm)

        t = (j + 1) / unroll_frames_count
        # Smooth ease-out
        t_ease = math.sin(t * math.pi / 2)
        cur_w = int(scroll_w + (target_unroll_w - scroll_w) * t_ease)
        cur_h = int(36 + (target_unroll_h - 36) * t_ease)
        cur_x1 = (W - cur_w) // 2
        cur_x2 = cur_x1 + cur_w
        cur_y1 = center_y - cur_h // 2
        cur_y2 = center_y + cur_h // 2

        # Parchment background expanding
        draw.rounded_rectangle([cur_x1, cur_y1, cur_x2, cur_y2], radius=6, fill=(18, 22, 34), outline=gold_primary, width=2)

        # Top and bottom roller bars gliding apart
        # Top roller
        draw.rounded_rectangle([cur_x1 - 12, cur_y1 - 10, cur_x2 + 12, cur_y1 + 10], radius=5, fill=(45, 34, 18), outline=gold_primary, width=2)
        # Bottom roller
        draw.rounded_rectangle([cur_x1 - 12, cur_y2 - 10, cur_x2 + 12, cur_y2 + 10], radius=5, fill=(45, 34, 18), outline=gold_primary, width=2)

        # Light burst particles during unrolling
        burst_r = int(24 + 40 * t)
        draw.ellipse([W//2 - burst_r, center_y - burst_r, W//2 + burst_r, center_y + burst_r], outline=cyan_neon, width=1)

        draw.text((36, H - 36), "DATA ACCESS: DECRYPTING CIPHER", fill=cyan_neon, font=font_sm)

        frames.append(img)
        durations.append(100)  # 8 * 100ms = 800ms

    # ─────────────────────────────────────────────────────────────────────────
    # PHASE 3: REVEALED CONTACT INFORMATION (7.0 seconds = 14 frames @ 500ms)
    # ─────────────────────────────────────────────────────────────────────────
    revealed_frames_count = 14
    parch_x1 = unroll_x1
    parch_x2 = unroll_x2
    parch_y1 = center_y - target_unroll_h // 2
    parch_y2 = center_y + target_unroll_h // 2

    for k in range(revealed_frames_count):
        img = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(img)

        # Outer HUD Card Border
        draw.rounded_rectangle([16, 16, W - 16, H - 16], radius=10, outline=border_color, width=1)
        draw.line([(16, 32), (32, 16)], fill=gold_primary, width=2)
        draw.line([(W - 32, 16), (W - 16, 32)], fill=gold_primary, width=2)
        draw.line([(16, H - 32), (32, H - 16)], fill=gold_primary, width=2)
        draw.line([(W - 32, H - 16), (W - 16, H - 32)], fill=gold_primary, width=2)

        draw.text((36, 26), "// CONTACT PROTOCOL //", fill=gold_primary, font=font_sm)
        draw.text((W - 200, 26), "STATUS: TRANSMISSION REVEALED", fill=(34, 197, 94), font=font_sm)

        # Parchment background (Cyber-parchment)
        draw.rounded_rectangle([parch_x1, parch_y1, parch_x2, parch_y2], radius=8, fill=(15, 20, 32), outline=gold_primary, width=2)
        # Inner runic border
        draw.rectangle([parch_x1 + 8, parch_y1 + 8, parch_x2 - 8, parch_y2 - 8], outline=(30, 45, 68), width=1)

        # Top & Bottom Roller Handles
        draw.rounded_rectangle([parch_x1 - 14, parch_y1 - 10, parch_x2 + 14, parch_y1 + 8], radius=5, fill=(45, 34, 18), outline=gold_primary, width=2)
        draw.rounded_rectangle([parch_x1 - 14, parch_y2 - 8, parch_x2 + 14, parch_y2 + 10], radius=5, fill=(45, 34, 18), outline=gold_primary, width=2)
        # Spindle knobs
        draw.ellipse([parch_x1 - 20, parch_y1 - 7, parch_x1 - 12, parch_y1 + 5], fill=gold_primary)
        draw.ellipse([parch_x2 + 12, parch_y1 - 7, parch_x2 + 20, parch_y1 + 5], fill=gold_primary)
        draw.ellipse([parch_x1 - 20, parch_y2 - 5, parch_x1 - 12, parch_y2 + 7], fill=gold_primary)
        draw.ellipse([parch_x2 + 12, parch_y2 - 5, parch_x2 + 20, parch_y2 + 7], fill=gold_primary)

        # Scroll Content - Decrypted Contact Information
        # Header banner inside scroll
        draw.text((W // 2 - 160, parch_y1 + 18), "✦ TRANSMISSION DECRYPTED // CONTACT HUD ✦", fill=gold_primary, font=font_title)
        draw.line([(parch_x1 + 40, parch_y1 + 38), (parch_x2 - 40, parch_y1 + 38)], fill=(40, 55, 80), width=1)

        # Contact Details Columns
        left_col_x = parch_x1 + 40
        right_col_x = W // 2 + 30

        # Identity Row
        draw.text((left_col_x, parch_y1 + 52), "IDENTITY", fill=cyan_neon, font=font_sm)
        draw.text((left_col_x, parch_y1 + 68), CONTACT_INFO["name"], fill=text_white, font=font_name)

        # Email Row
        draw.text((left_col_x, parch_y1 + 96), "EMAIL DIRECT", fill=cyan_neon, font=font_sm)
        draw.text((left_col_x, parch_y1 + 112), CONTACT_INFO["email"], fill=gold_primary, font=font_body)

        # GitHub Profile
        draw.text((right_col_x, parch_y1 + 52), "GITHUB NETWORK", fill=cyan_neon, font=font_sm)
        draw.text((right_col_x, parch_y1 + 68), CONTACT_INFO["github"], fill=text_white, font=font_body)

        # LinkedIn Profile
        draw.text((right_col_x, parch_y1 + 96), "LINKEDIN NETWORK", fill=cyan_neon, font=font_sm)
        draw.text((right_col_x, parch_y1 + 112), CONTACT_INFO["linkedin"], fill=text_white, font=font_body)

        # Footer tagline inside scroll
        draw.line([(parch_x1 + 40, parch_y1 + 140), (parch_x2 - 40, parch_y1 + 140)], fill=(40, 55, 80), width=1)
        draw.text((W // 2 - 140, parch_y1 + 148), "// AVAILABLE FOR COLLABORATION & INQUIRIES //", fill=text_muted, font=font_sm)

        # Outer Card Bottom Status
        draw.text((36, H - 36), "DATA ACCESS: VERIFIED & ACTIVE", fill=(34, 197, 94), font=font_sm)

        frames.append(img)
        durations.append(500)  # 14 * 500ms = 7000ms (7.0s)

    # Save animated GIF
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    out_path = os.path.join(out_dir, "contact-scroll.gif")
    out_path = os.path.normpath(out_path)
    os.makedirs(out_dir, exist_ok=True)

    p_frames = []
    for f in frames:
        p_frame = f.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        p_frames.append(p_frame)

    p_frames[0].save(
        out_path,
        save_all=True,
        append_images=p_frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Contact Scroll GIF created: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate_contact_scroll_gif()
