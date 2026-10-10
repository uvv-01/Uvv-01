#!/usr/bin/env python3
"""
Contribution Shooter Generator
Generates an arcade animated GIF of a spaceship firing at authentic green GitHub contribution squares.
Preserves recognizable GitHub contribution grid aesthetics.
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
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            contribs = data.get("contributions", [])
            if len(contribs) >= 350:
                return contribs
    except Exception as e:
        print(f"  [Notice] Contribution API fetch notice: {e}", file=sys.stderr)
    return None

def build_grid_matrix(contribs):
    # GitHub grid is 52 or 53 weeks x 7 days
    # Each entry has: date, count, level (0-4)
    # Arrange into 52 columns x 7 rows
    cols = 52
    rows = 7
    matrix = [[0 for _ in range(rows)] for _ in range(cols)]
    
    if contribs:
        # Take the last 52*7 = 364 entries
        recent = contribs[- (cols * rows):]
        idx = 0
        for c in range(cols):
            for r in range(rows):
                if idx < len(recent):
                    matrix[c][r] = recent[idx].get("level", 0)
                    idx += 1
    else:
        # Fallback authentic distribution if offline
        for c in range(cols):
            for r in range(rows):
                if (c * 7 + r) % 5 == 0 or (c > 35 and (c + r) % 2 == 0):
                    matrix[c][r] = 1 + ((c + r) % 4)
    return matrix

def draw_spaceship(draw, cx, cy, thruster_phase):
    # Spaceship centered at (cx, cy)
    # Nose pointing up
    w = 26
    h = 24
    
    # Thruster flame (animated)
    flame_h = 8 + int(4 * math.sin(thruster_phase))
    flame_poly = [
        (cx - 5, cy + 10),
        (cx, cy + 10 + flame_h),
        (cx + 5, cy + 10),
    ]
    draw.polygon(flame_poly, fill=(255, 120, 0))
    inner_flame = [
        (cx - 2, cy + 10),
        (cx, cy + 8 + flame_h // 2),
        (cx + 2, cy + 10),
    ]
    draw.polygon(inner_flame, fill=(255, 240, 100))

    # Wings
    wings = [
        (cx, cy - 12),
        (cx + 14, cy + 8),
        (cx + 10, cy + 10),
        (cx, cy + 6),
        (cx - 10, cy + 10),
        (cx - 14, cy + 8),
    ]
    draw.polygon(wings, fill=(30, 41, 59), outline=(0, 240, 255))

    # Fuselage body
    fuselage = [
        (cx, cy - 12),
        (cx + 6, cy + 4),
        (cx + 4, cy + 9),
        (cx - 4, cy + 9),
        (cx - 6, cy + 4),
    ]
    draw.polygon(fuselage, fill=(226, 232, 240), outline=(0, 240, 255))

    # Cockpit windshield
    cockpit = [
        (cx, cy - 6),
        (cx + 3, cy),
        (cx, cy + 2),
        (cx - 3, cy),
    ]
    draw.polygon(cockpit, fill=(0, 240, 255))

    # Cannons
    draw.line([(cx - 10, cy + 2), (cx - 10, cy - 4)], fill=(0, 240, 255), width=2)
    draw.line([(cx + 10, cy + 2), (cx + 10, cy - 4)], fill=(0, 240, 255), width=2)

def generate_shooter_gif():
    print("Generating Rocket Spaceship Contribution Shooter GIF...")
    contribs = fetch_contributions(GITHUB_USERNAME)
    grid = build_grid_matrix(contribs)

    # Find candidate green squares (level >= 2) across the grid to shoot at
    targets = []
    # Search for active squares in distinct columns
    cols_search = [12, 22, 34, 46]
    for target_col in cols_search:
        found_r = None
        for r in range(7):
            if grid[target_col][r] >= 2:
                found_r = r
                break
        if found_r is None:
            # Pick any non-zero or set level 3
            for r in range(7):
                if grid[target_col][r] > 0:
                    found_r = r
                    break
        if found_r is None:
            found_r = 3
            grid[target_col][found_r] = 3
        targets.append((target_col, found_r))

    print(f"Target green squares: {targets}")

    # Canvas Setup
    W = 960
    H = 240
    sq_size = 10
    sq_gap = 3
    stride = sq_size + sq_gap
    grid_w = 52 * stride - sq_gap
    grid_h = 7 * stride - sq_gap
    grid_x0 = (W - grid_w) // 2
    grid_y0 = 50

    # Color definitions
    bg_color = (7, 10, 19)
    border_color = (30, 41, 59)
    hud_cyan = (0, 240, 255)
    hud_green = (0, 255, 136)
    hud_gray = (100, 116, 139)
    
    level_colors = {
        0: (22, 27, 34),       # #161b22
        1: (14, 68, 41),       # #0e4429
        2: (0, 109, 50),       # #006d32
        3: (38, 166, 65),      # #26a641
        4: (57, 211, 83),      # #39d353
    }

    # Font setup
    try:
        font_sm = ImageFont.truetype("consola.ttf", 10)
        font_md = ImageFont.truetype("consola.ttf", 12)
    except Exception:
        font_sm = ImageFont.load_default()
        font_md = ImageFont.load_default()

    frames = []
    total_frames = 54
    # State tracking: destroyed squares set
    destroyed_squares = set()
    current_score = 34700

    # Keyframes setup for 3 target shots:
    # Target 0: frames 0..17
    # Target 1: frames 18..35
    # Target 2: frames 36..53
    shots = [
        {"target": targets[0], "start_f": 0, "move_f": 5, "fire_f": 7, "hit_f": 11, "end_f": 17},
        {"target": targets[1], "start_f": 18, "move_f": 23, "fire_f": 25, "hit_f": 29, "end_f": 35},
        {"target": targets[2], "start_f": 36, "move_f": 41, "fire_f": 43, "hit_f": 47, "end_f": 53},
    ]

    ship_y = 195
    # Initial ship X
    prev_ship_x = grid_x0 + targets[0][0] * stride - 60

    for f in range(total_frames):
        img = Image.new("RGB", (W, H), bg_color)
        draw = ImageDraw.Draw(img)

        # 1. Outer Border & HUD Header
        draw.rounded_rectangle([12, 12, W - 12, H - 12], radius=10, outline=border_color, width=1)
        # Chamfer corner accents
        draw.line([(12, 28), (28, 12)], fill=hud_cyan, width=2)
        draw.line([(W - 28, 12), (W - 12, 28)], fill=hud_cyan, width=2)
        draw.line([(12, H - 28), (28, H - 12)], fill=hud_cyan, width=2)
        draw.line([(W - 28, H - 12), (W - 12, H - 28)], fill=hud_cyan, width=2)

        # Header Title
        draw.text((28, 22), "// ARCADE CONTRIB SHOOTER //", fill=hud_cyan, font=font_md)
        draw.text((320, 24), "SYSTEM: TARGETING ACTIVE", fill=hud_gray, font=font_sm)
        draw.text((W - 220, 22), f"SCORE: {current_score:06d}", fill=hud_green, font=font_md)

        # Separator line
        draw.line([(24, 40), (W - 24, 40)], fill=(20, 30, 48), width=1)

        # 2. Find active shot sequence
        active_shot = None
        for s in shots:
            if s["start_f"] <= f <= s["end_f"]:
                active_shot = s
                break

        target_col, target_row = active_shot["target"]
        target_center_x = grid_x0 + target_col * stride + sq_size // 2
        target_center_y = grid_y0 + target_row * stride + sq_size // 2

        # Compute spaceship position
        if f < active_shot["move_f"]:
            # Interpolate from prev position
            t = (f - active_shot["start_f"]) / max(1, (active_shot["move_f"] - active_shot["start_f"]))
            # Smooth ease-out
            t_ease = math.sin(t * math.pi / 2)
            ship_x = prev_ship_x + (target_center_x - prev_ship_x) * t_ease
        else:
            ship_x = target_center_x
            prev_ship_x = ship_x

        # Check projectile and explosion states
        projectile_active = False
        proj_y = None
        explosion_frame = None

        if active_shot["fire_f"] <= f < active_shot["hit_f"]:
            projectile_active = True
            progress = (f - active_shot["fire_f"]) / (active_shot["hit_f"] - active_shot["fire_f"])
            proj_y = (ship_y - 12) + (target_center_y - (ship_y - 12)) * progress

        if f >= active_shot["hit_f"]:
            explosion_frame = f - active_shot["hit_f"]
            if (target_col, target_row) not in destroyed_squares:
                destroyed_squares.add((target_col, target_row))
                current_score += 1000

        # 3. Draw Contribution Grid
        for c in range(52):
            for r in range(7):
                sx = grid_x0 + c * stride
                sy = grid_y0 + r * stride
                
                if (c, r) in destroyed_squares:
                    # Destroyed square: dark crater with charred border
                    draw.rounded_rectangle([sx, sy, sx + sq_size, sy + sq_size], radius=2, fill=(10, 14, 22), outline=(30, 41, 59))
                else:
                    lvl = grid[c][r]
                    col = level_colors.get(lvl, level_colors[0])
                    # If this is the currently locked target before impact, give it a subtle target pulse
                    if (c, r) == (target_col, target_row) and f < active_shot["hit_f"]:
                        draw.rounded_rectangle([sx, sy, sx + sq_size, sy + sq_size], radius=2, fill=col)
                        # Reticle brackets around target
                        draw.rectangle([sx - 2, sy - 2, sx + sq_size + 2, sy + sq_size + 2], outline=(0, 240, 255), width=1)
                    else:
                        draw.rounded_rectangle([sx, sy, sx + sq_size, sy + sq_size], radius=2, fill=col)

        # 4. Draw Projectile (Laser Bolt)
        if projectile_active and proj_y is not None:
            # Twin laser bolts from cannons
            for ox in [-8, 8]:
                bx = ship_x + ox
                # Laser bolt with neon core
                draw.line([(bx, proj_y + 10), (bx, proj_y - 6)], fill=(0, 240, 255), width=3)
                draw.line([(bx, proj_y + 8), (bx, proj_y - 4)], fill=(255, 255, 255), width=1)
                # Glowing flare head
                draw.ellipse([bx - 3, proj_y - 8, bx + 3, proj_y - 2], fill=(255, 255, 255))

        # 5. Draw Explosion Animation on Target
        if explosion_frame is not None and explosion_frame <= 5:
            ex = target_center_x
            ey = target_center_y
            ef = explosion_frame

            if ef == 0:
                # Stage 1: Intense Flash
                draw.ellipse([ex - 12, ey - 12, ex + 12, ey + 12], fill=(255, 255, 255))
            elif ef == 1:
                # Stage 2: Expanding Fireball + Shockwave Ring
                draw.ellipse([ex - 16, ey - 16, ex + 16, ey + 16], fill=(255, 220, 50))
                draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=(255, 255, 255))
                draw.ellipse([ex - 22, ey - 22, ex + 22, ey + 22], outline=(0, 240, 255), width=1)
            elif ef == 2:
                # Stage 3: Particle Debris Burst
                draw.ellipse([ex - 14, ey - 14, ex + 14, ey + 14], fill=(255, 100, 20))
                draw.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=(255, 200, 50))
                # 8 spark particles flying outwards
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    dist = 18
                    px = ex + int(dist * math.cos(rad))
                    py = ey + int(dist * math.sin(rad))
                    draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 240, 100))
            elif ef >= 3:
                # Stage 4: Lingering Smoke & Embers
                draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=(80, 30, 20))
                for angle in range(20, 380, 60):
                    rad = math.radians(angle)
                    dist = 22 + ef * 2
                    px = ex + int(dist * math.cos(rad))
                    py = ey + int(dist * math.sin(rad))
                    draw.point((px, py), fill=(255, 120, 50))

        # 6. Draw Spaceship
        thruster_phase = f * 0.6
        draw_spaceship(draw, int(ship_x), ship_y, thruster_phase)

        # 7. Bottom Arcade Status Bar
        draw.line([(24, H - 28), (W - 24, H - 28)], fill=(20, 30, 48), width=1)
        draw.text((28, H - 22), "STATUS: TARGET ACQUIRED // 60 FPS ARCADE RENDER", fill=hud_gray, font=font_sm)
        draw.text((W - 240, H - 22), f"TARGET LOCK: COL {target_col:02d} ROW {target_row:02d}", fill=hud_cyan, font=font_sm)

        frames.append(img)

    # Save animated GIF with palette quantization
    out_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    out_path = os.path.join(out_dir, "contribution-shooter.gif")
    out_path = os.path.normpath(out_path)
    os.makedirs(out_dir, exist_ok=True)

    # Convert frames to palette mode for compact GIF size
    p_frames = []
    for f in frames:
        p_frame = f.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        p_frames.append(p_frame)

    p_frames[0].save(
        out_path,
        save_all=True,
        append_images=p_frames[1:],
        duration=70,  # ~14 fps
        loop=0,
        optimize=True
    )
    print(f"Contribution Shooter GIF created: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate_shooter_gif()
