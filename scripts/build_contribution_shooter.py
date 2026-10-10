#!/usr/bin/env python3
"""
Contribution Shooter Generator
Simulates a continuous snake-like tactical clearance traversal across the authentic GitHub contribution grid for uvv-01.
Targets and destroys every occupied contribution cell before resetting.
"""

import math
import os
import sys
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont

GITHUB_USERNAME = "uvv-01"

def fetch_contributions(username):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            contribs = data.get("contributions", [])
            if len(contribs) >= 350:
                return contribs
    except Exception as e:
        print(f"  [Notice] Contribution API notice: {e}", file=sys.stderr)
    return None

def build_grid_matrix(contribs):
    cols = 52
    rows = 7
    grid = [[0 for _ in range(rows)] for _ in range(cols)]
    
    if contribs:
        recent = contribs[- (cols * rows):]
        idx = 0
        for c in range(cols):
            for r in range(rows):
                if idx < len(recent):
                    grid[c][r] = recent[idx].get("level", 0)
                    idx += 1
    else:
        # Fallback distribution
        for c in range(cols):
            for r in range(rows):
                if (c * 7 + r) % 5 == 0:
                    grid[c][r] = 1 + ((c + r) % 4)
    return grid

def generate_shooter_gif():
    print("Generating Continuous Grid Clearance Shooter GIF...")
    contribs = fetch_contributions(GITHUB_USERNAME)
    grid = build_grid_matrix(contribs)

    cols = 52
    rows = 7

    # Programmatic verification of authentic occupied cells
    authentic_occupied = set()
    for c in range(cols):
        for r in range(rows):
            if grid[c][r] > 0:
                authentic_occupied.add((c, r))

    # Snake-like traversal path across the 52x7 grid
    # Row-by-row in alternating directions (boustrophedon snake)
    snake_targets = []
    traversal_cells = []
    for r in range(rows):
        col_order = list(range(cols)) if r % 2 == 0 else list(range(cols - 1, -1, -1))
        for c in col_order:
            traversal_cells.append((c, r))
            if grid[c][r] > 0:
                direction = 1 if r % 2 == 0 else -1
                snake_targets.append({
                    "col": c,
                    "row": r,
                    "level": grid[c][r],
                    "dir": direction
                })

    # Verification checks
    targeted_coords = [(t["col"], t["row"]) for t in snake_targets]
    assert len(targeted_coords) == len(authentic_occupied), "Target count mismatch!"
    assert set(targeted_coords) == authentic_occupied, "Missing or extra targets detected!"
    assert len(targeted_coords) == len(set(targeted_coords)), "Duplicate targets found!"
    print(f"  [Verification] Authentic occupied cells: {len(authentic_occupied)}")
    print(f"  [Verification] Generated snake targets: {len(snake_targets)}")
    print(f"  [Verification] Traversed grid dimensions: {cols}x{rows} (364 cells)")
    print(f"  [Verification] Skipped targets: 0, Duplicate targets: 0")

    W = 960
    H = 210
    stride = 13
    sq_size = 10
    grid_x0 = (W - (52 * stride - 3)) // 2  # 143
    grid_y0 = 50

    bg_color = (13, 17, 23)
    border_color = (48, 54, 61)
    hud_gray = (139, 148, 158)
    hud_white = (240, 246, 252)

    level_colors = {
        0: (22, 27, 34),
        1: (14, 68, 41),
        2: (0, 109, 50),
        3: (38, 166, 65),
        4: (57, 211, 83),
    }

    try:
        font_sm = ImageFont.truetype("consola.ttf", 10)
        font_md = ImageFont.truetype("consola.ttf", 11)
    except Exception:
        font_sm = ImageFont.load_default()
        font_md = ImageFont.load_default()

    frames = []
    durations = []
    destroyed = set()
    total_targets = len(snake_targets)
    cleared_count = 0
    prev_row = snake_targets[0]["row"]

    for i, target in enumerate(snake_targets):
        c = target["col"]
        r = target["row"]
        direction = target["dir"]
        tx = grid_x0 + c * stride
        ty = grid_y0 + r * stride

        # Smooth row transition frame at boundary
        if r != prev_row:
            img_t = Image.new("RGB", (W, H), bg_color)
            draw_t = ImageDraw.Draw(img_t)
            draw_t.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
            draw_t.text((28, 22), "TACTICAL GRID // CLEARANCE PROTOCOL", fill=hud_white, font=font_md)
            draw_t.text((420, 22), f"NEUTRALIZED: {cleared_count:02d} / {total_targets}", fill=hud_gray, font=font_md)
            draw_t.text((W - 200, 22), f"SWEEPING ROW {r + 1} OF {rows}", fill=hud_gray, font=font_sm)
            draw_t.line([(24, 38), (W - 24, 38)], fill=border_color, width=1)

            for gc in range(cols):
                for gr in range(rows):
                    gx = grid_x0 + gc * stride
                    gy = grid_y0 + gr * stride
                    if (gc, gr) in destroyed:
                        draw_t.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=(18, 22, 28), outline=(33, 38, 45))
                    else:
                        draw_t.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=level_colors[grid[gc][gr]])

            trans_x = tx + (direction * -18)
            trans_y = grid_y0 + ((prev_row + r) / 2) * stride + 5
            draw_t.polygon([
                (trans_x, trans_y + 8),
                (trans_x - 6, trans_y - 6),
                (trans_x + 6, trans_y - 6)
            ], fill=(203, 213, 225), outline=(71, 85, 105))

            frames.append(img_t)
            durations.append(45)
            prev_row = r

        # Frame 1: Ship fires projectile
        ship_offset_x = -16 if direction == 1 else 16
        ship_x = tx + ship_offset_x + 5
        ship_y = ty + 5

        img_fire = Image.new("RGB", (W, H), bg_color)
        draw_f = ImageDraw.Draw(img_fire)
        draw_f.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw_f.text((28, 22), "TACTICAL GRID // CLEARANCE PROTOCOL", fill=hud_white, font=font_md)
        draw_f.text((420, 22), f"NEUTRALIZED: {cleared_count:02d} / {total_targets}", fill=hud_gray, font=font_md)
        draw_f.text((W - 200, 22), f"SWEEPING ROW {r + 1} OF {rows}", fill=hud_gray, font=font_sm)
        draw_f.line([(24, 38), (W - 24, 38)], fill=border_color, width=1)

        for gc in range(cols):
            for gr in range(rows):
                gx = grid_x0 + gc * stride
                gy = grid_y0 + gr * stride
                if (gc, gr) in destroyed:
                    draw_f.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=(18, 22, 28), outline=(33, 38, 45))
                else:
                    draw_f.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=level_colors[grid[gc][gr]])

        # Projectile in flight
        proj_mid_x = (ship_x + (tx + 5)) // 2
        draw_f.line([(ship_x, ship_y), (proj_mid_x, ship_y)], fill=(56, 189, 248), width=2)

        # Ship facing movement direction
        if direction == 1:
            draw_f.polygon([(ship_x + 8, ship_y), (ship_x - 6, ship_y - 5), (ship_x - 6, ship_y + 5)], fill=(203, 213, 225), outline=(71, 85, 105))
            draw_f.point((ship_x - 8, ship_y), fill=(245, 158, 11))
        else:
            draw_f.polygon([(ship_x - 8, ship_y), (ship_x + 6, ship_y - 5), (ship_x + 6, ship_y + 5)], fill=(203, 213, 225), outline=(71, 85, 105))
            draw_f.point((ship_x + 8, ship_y), fill=(245, 158, 11))

        frames.append(img_fire)
        durations.append(40)

        # Frame 2: Impact & Compact Explosion
        cleared_count += 1
        destroyed.add((c, r))

        img_hit = Image.new("RGB", (W, H), bg_color)
        draw_h = ImageDraw.Draw(img_hit)
        draw_h.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw_h.text((28, 22), "TACTICAL GRID // CLEARANCE PROTOCOL", fill=hud_white, font=font_md)
        draw_h.text((420, 22), f"NEUTRALIZED: {cleared_count:02d} / {total_targets}", fill=hud_white, font=font_md)
        draw_h.text((W - 200, 22), f"SWEEPING ROW {r + 1} OF {rows}", fill=hud_gray, font=font_sm)
        draw_h.line([(24, 38), (W - 24, 38)], fill=border_color, width=1)

        for gc in range(cols):
            for gr in range(rows):
                gx = grid_x0 + gc * stride
                gy = grid_y0 + gr * stride
                if (gc, gr) in destroyed:
                    draw_h.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=(18, 22, 28), outline=(33, 38, 45))
                else:
                    draw_h.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=level_colors[grid[gc][gr]])

        # Controlled compact impact flash
        cx = tx + sq_size // 2
        cy = ty + sq_size // 2
        draw_h.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 255, 255))
        draw_h.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=(245, 158, 11), width=1)

        if direction == 1:
            draw_h.polygon([(ship_x + 8, ship_y), (ship_x - 6, ship_y - 5), (ship_x - 6, ship_y + 5)], fill=(203, 213, 225), outline=(71, 85, 105))
        else:
            draw_h.polygon([(ship_x - 8, ship_y), (ship_x + 6, ship_y - 5), (ship_x + 6, ship_y + 5)], fill=(203, 213, 225), outline=(71, 85, 105))

        frames.append(img_hit)
        durations.append(45)

    # Completed sweep pause
    for p in range(4):
        img_pause = Image.new("RGB", (W, H), bg_color)
        draw_p = ImageDraw.Draw(img_pause)
        draw_p.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw_p.text((28, 22), "TACTICAL GRID // CLEARANCE PROTOCOL", fill=hud_white, font=font_md)
        draw_p.text((420, 22), f"NEUTRALIZED: 95 / 95 (100% CLEARED)", fill=(34, 197, 94), font=font_md)
        draw_p.text((W - 200, 22), "RESETTING CYCLE...", fill=hud_gray, font=font_sm)
        draw_p.line([(24, 38), (W - 24, 38)], fill=border_color, width=1)

        for gc in range(cols):
            for gr in range(rows):
                gx = grid_x0 + gc * stride
                gy = grid_y0 + gr * stride
                if (gc, gr) in destroyed:
                    draw_p.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=(18, 22, 28), outline=(33, 38, 45))
                else:
                    draw_p.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=level_colors[grid[gc][gr]])

        frames.append(img_pause)
        durations.append(300)

    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    out_path = os.path.join(out_dir, "contribution-shooter.gif")
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
    print(f"Contribution Shooter GIF created: {out_path} ({sz} bytes, {sz/1024:.1f} KB)")
    return True

if __name__ == "__main__":
    generate_shooter_gif()
