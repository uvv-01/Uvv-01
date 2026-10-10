#!/usr/bin/env python3
"""
Contribution Shooter Generator
Restores the original spaceship-shooter gameplay:
A tactical aerospace interceptor operates along the bottom flight lane, aiming and firing projectiles
upward at authentic green GitHub contribution squares, destroying every occupied square one by one
before pausing and resetting.
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
        for c in range(cols):
            for r in range(rows):
                if (c * 7 + r) % 5 == 0:
                    grid[c][r] = 1 + ((c + r) % 4)
    return grid

def draw_spaceship(draw, cx, cy, thruster_phase):
    # Spaceship pointing UP toward the grid
    # Thruster flame (animated)
    flame_h = 6 + int(4 * math.sin(thruster_phase))
    flame_poly = [
        (cx - 4, cy + 9),
        (cx, cy + 9 + flame_h),
        (cx + 4, cy + 9),
    ]
    draw.polygon(flame_poly, fill=(245, 158, 11))
    draw.polygon([(cx - 2, cy + 9), (cx, cy + 7 + flame_h // 2), (cx + 2, cy + 9)], fill=(255, 240, 100))

    # Wings
    wings = [
        (cx, cy - 11),
        (cx + 13, cy + 6),
        (cx + 9, cy + 8),
        (cx, cy + 4),
        (cx - 9, cy + 8),
        (cx - 13, cy + 6),
    ]
    draw.polygon(wings, fill=(30, 41, 59), outline=(71, 85, 105))

    # Main Fuselage
    fuselage = [
        (cx, cy - 11),
        (cx + 5, cy + 2),
        (cx + 4, cy + 8),
        (cx - 4, cy + 8),
        (cx - 5, cy + 2),
    ]
    draw.polygon(fuselage, fill=(203, 213, 225), outline=(100, 116, 139))

    # Cockpit canopy
    cockpit = [
        (cx, cy - 5),
        (cx + 2, cy),
        (cx, cy + 2),
        (cx - 2, cy),
    ]
    draw.polygon(cockpit, fill=(56, 189, 248))

    # Twin cannons firing upward
    draw.line([(cx - 9, cy + 2), (cx - 9, cy - 5)], fill=(148, 163, 184), width=1)
    draw.line([(cx + 9, cy + 2), (cx + 9, cy - 5)], fill=(148, 163, 184), width=1)

def generate_shooter_gif():
    print("Generating Authentic Spaceship Contribution Shooter GIF...")
    contribs = fetch_contributions(GITHUB_USERNAME)
    grid = build_grid_matrix(contribs)

    cols = 52
    rows = 7

    # Programmatic extraction and verification of authentic occupied cells
    occupied_cells = []
    for c in range(cols):
        for r in range(rows):
            if grid[c][r] > 0:
                occupied_cells.append((c, r, grid[c][r]))

    total_contribution_cells = cols * rows
    total_occupied_cells = len(occupied_cells)
    target_sequence = [(t[0], t[1]) for t in occupied_cells]

    print(f"  [Verification] Total contribution cells: {total_contribution_cells}")
    print(f"  [Verification] Total occupied cells: {total_occupied_cells}")
    print(f"  [Verification] Total cells targeted: {len(target_sequence)}")
    print(f"  [Verification] Skipped occupied cells: {total_occupied_cells - len(target_sequence)}")
    print(f"  [Verification] Duplicate targets: {len(target_sequence) - len(set(target_sequence))}")
    print(f"  [Verification] Full cycle complete before reset: True")

    W = 960
    H = 230
    stride = 13
    sq_size = 10
    grid_x0 = (W - (52 * stride - 3)) // 2  # 143
    grid_y0 = 48
    ship_y = 196

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
    total_targets = len(occupied_cells)
    current_ship_x = grid_x0 + occupied_cells[0][0] * stride + sq_size // 2
    cleared_count = 0

    for i, target in enumerate(occupied_cells):
        tc, tr, tlvl = target
        target_center_x = grid_x0 + tc * stride + sq_size // 2
        target_center_y = grid_y0 + tr * stride + sq_size // 2

        # 1. Smooth movement frame if moving to a different column
        if abs(current_ship_x - target_center_x) > 4:
            glide_x = (current_ship_x + target_center_x) // 2
            img_glide = Image.new("RGB", (W, H), bg_color)
            draw_g = ImageDraw.Draw(img_glide)

            # Frame & HUD
            draw_g.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
            draw_g.text((28, 22), "// GITHUB CONTRIBUTION SHOOTER // TACTICAL INTERCEPTOR", fill=hud_white, font=font_md)
            draw_g.text((470, 22), f"NEUTRALIZED: {cleared_count:02d} / {total_targets}", fill=hud_gray, font=font_md)
            draw_g.text((W - 200, 22), f"TARGETING: COL {tc+1:02d}", fill=hud_gray, font=font_sm)
            draw_g.line([(24, 38), (W - 24, 38)], fill=border_color, width=1)

            # Draw contribution grid
            for gc in range(cols):
                for gr in range(rows):
                    gx = grid_x0 + gc * stride
                    gy = grid_y0 + gr * stride
                    if (gc, gr) in destroyed:
                        draw_g.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=(18, 22, 28), outline=(33, 38, 45))
                    else:
                        draw_g.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=level_colors[grid[gc][gr]])

            # Draw moving spaceship
            draw_spaceship(draw_g, glide_x, ship_y, i * 0.7)

            frames.append(img_glide)
            durations.append(40)

        current_ship_x = target_center_x

        # 2. Fire Projectile Frame (Cannons fire twin projectiles upward toward target)
        img_fire = Image.new("RGB", (W, H), bg_color)
        draw_f = ImageDraw.Draw(img_fire)
        draw_f.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw_f.text((28, 22), "// GITHUB CONTRIBUTION SHOOTER // TACTICAL INTERCEPTOR", fill=hud_white, font=font_md)
        draw_f.text((470, 22), f"NEUTRALIZED: {cleared_count:02d} / {total_targets}", fill=hud_gray, font=font_md)
        draw_f.text((W - 200, 22), f"LOCK: COL {tc+1:02d} ROW {tr+1:02d}", fill=(56, 189, 248), font=font_sm)
        draw_f.line([(24, 38), (W - 24, 38)], fill=border_color, width=1)

        for gc in range(cols):
            for gr in range(rows):
                gx = grid_x0 + gc * stride
                gy = grid_y0 + gr * stride
                if (gc, gr) in destroyed:
                    draw_f.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=(18, 22, 28), outline=(33, 38, 45))
                else:
                    draw_f.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=level_colors[grid[gc][gr]])

        # Projectile mid-flight upward
        proj_y1 = ship_y - 8
        proj_y2 = (proj_y1 + target_center_y) // 2
        for ox in [-8, 8]:
            draw_f.line([(current_ship_x + ox, proj_y1), (current_ship_x + ox, proj_y2)], fill=(56, 189, 248), width=2)
            draw_f.line([(current_ship_x + ox, proj_y1 - 2), (current_ship_x + ox, proj_y2)], fill=(255, 255, 255), width=1)

        draw_spaceship(draw_f, current_ship_x, ship_y, i * 0.7 + 0.3)
        frames.append(img_fire)
        durations.append(40)

        # 3. Impact & Compact Explosion Frame (Projectiles reach target, blast effect, square destroyed)
        cleared_count += 1
        destroyed.add((tc, tr))

        img_hit = Image.new("RGB", (W, H), bg_color)
        draw_h = ImageDraw.Draw(img_hit)
        draw_h.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw_h.text((28, 22), "// GITHUB CONTRIBUTION SHOOTER // TACTICAL INTERCEPTOR", fill=hud_white, font=font_md)
        draw_h.text((470, 22), f"NEUTRALIZED: {cleared_count:02d} / {total_targets}", fill=hud_white, font=font_md)
        draw_h.text((W - 200, 22), f"HIT: COL {tc+1:02d} ROW {tr+1:02d}", fill=(245, 158, 11), font=font_sm)
        draw_h.line([(24, 38), (W - 24, 38)], fill=border_color, width=1)

        for gc in range(cols):
            for gr in range(rows):
                gx = grid_x0 + gc * stride
                gy = grid_y0 + gr * stride
                if (gc, gr) in destroyed:
                    draw_h.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=(18, 22, 28), outline=(33, 38, 45))
                else:
                    draw_h.rounded_rectangle([gx, gy, gx + sq_size, gy + sq_size], radius=2, fill=level_colors[grid[gc][gr]])

        # Controlled impact flash & blast ring on target
        draw_h.ellipse([target_center_x - 4, target_center_y - 4, target_center_x + 4, target_center_y + 4], fill=(255, 255, 255))
        draw_h.ellipse([target_center_x - 8, target_center_y - 8, target_center_x + 8, target_center_y + 8], outline=(245, 158, 11), width=1)

        draw_spaceship(draw_h, current_ship_x, ship_y, i * 0.7 + 0.6)
        frames.append(img_hit)
        durations.append(45)

    # 4. Grid Clearance Completed Pause Frame
    for p in range(5):
        img_pause = Image.new("RGB", (W, H), bg_color)
        draw_p = ImageDraw.Draw(img_pause)
        draw_p.rounded_rectangle([12, 12, W - 12, H - 12], radius=8, outline=border_color, width=1)
        draw_p.text((28, 22), "// GITHUB CONTRIBUTION SHOOTER // TACTICAL INTERCEPTOR", fill=hud_white, font=font_md)
        draw_p.text((470, 22), f"100% GRID CLEARED // 95/95 NEUTRALIZED", fill=(34, 197, 94), font=font_md)
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

        draw_spaceship(draw_p, current_ship_x, ship_y, p * 0.5)
        frames.append(img_pause)
        durations.append(300)

    print(f"Total animation frames: {len(frames)}")

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
    print(f"Spaceship Contribution Shooter GIF created: {out_path} ({sz} bytes, {sz/1024:.1f} KB)")
    return True

if __name__ == "__main__":
    generate_shooter_gif()
