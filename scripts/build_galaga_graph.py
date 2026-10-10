#!/usr/bin/env python3
"""
Galaga Contribution Graph Generator
Builds authentic Galaga arcade animated SVGs for GitHub profile README
based on the reference implementation from abozanona/pacman-contribution-graph.
Connects directly to uvv-01's authentic GitHub contribution graph.

Uses 100% pure SVG vector geometry for the rocket ship, thruster fire,
twin plasma cannons, and laser projectiles to guarantee full visibility
and bypass GitHub Camo proxy raster sanitization.
"""

import json
import math
import os
import re
import sys
import urllib.request

USERNAME = "uvv-01"

CELL_SIZE = 20
GAP_SIZE = 2
GRID_WIDTH = 53
GRID_HEIGHT = 7
DELTA_TIME = 200

# Spaceship positioned in the lower flight corridor
SHIP_Y = 9.5
SHIP_SPEED = 0.45
SHIP_HALF_WIDTH = 1.0

BULLET_SPEED = 0.65
MAX_BULLETS = 10
FIRE_RATE = 2
EXPLOSION_FRAMES = 7

THEMES = {
    "github-dark": {
        "empty_cell": "#161b22",
        "empty_border": "#21262d",
        "levels": ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    },
    "github": {
        "empty_cell": "#ebedf0",
        "empty_border": "#d0d7de",
        "levels": ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
    },
}

def to_svg_x(gx):
    return gx * (CELL_SIZE + GAP_SIZE)

def to_svg_y(gy):
    return gy * (CELL_SIZE + GAP_SIZE) + 15

def fetch_authentic_contributions(username):
    # Method 1: jogruber API
    url_api = f"https://github-contributions-api.jogruber.de/v4/{username}?y=last"
    try:
        req = urllib.request.Request(url_api, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            contribs = data.get("contributions", [])
            if len(contribs) >= 350:
                return contribs
    except Exception as e:
        print(f"  [Notice] API fetch notice: {e}", file=sys.stderr)

    # Method 2: Direct GitHub user contributions HTML scrape
    url_html = f"https://github.com/users/{username}/contributions"
    try:
        req = urllib.request.Request(url_html, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")
            days = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d+)"', html)
            if len(days) >= 350:
                return [{"date": d[0], "count": int(d[1]), "level": int(d[1])} for d in days]
    except Exception as e:
        print(f"  [Notice] HTML scrape notice: {e}", file=sys.stderr)

    return None

def build_grid_and_labels(contribs):
    grid = [[{"commitsCount": 0, "level": 0} for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
    month_labels = [""] * GRID_WIDTH
    recent = contribs[-371:] if len(contribs) >= 371 else contribs
    last_month = ""
    for idx, c in enumerate(recent):
        col = idx // 7
        row = idx % 7
        if col < GRID_WIDTH and row < GRID_HEIGHT:
            lvl = int(c.get("level", 0))
            cnt = int(c.get("count", 0))
            grid[col][row] = {
                "commitsCount": cnt if cnt > 0 else (1 if lvl > 0 else 0),
                "level": lvl
            }
            date_str = c.get("date", "")
            if date_str:
                month_num = int(date_str.split("-")[1])
                months_abbr = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                m_abbr = months_abbr[month_num]
                if m_abbr != last_month:
                    month_labels[col] = m_abbr
                    last_month = m_abbr
    return grid, month_labels

def run_galaga_sim(initial_grid):
    grid = [[dict(cell) for cell in col] for col in initial_grid]
    ship = {"x": GRID_WIDTH / 2.0}
    bullets = []
    next_bullet_id = 0
    game_history = []
    cell_events = []
    explosion_events = []
    
    def score_col(x):
        return sum(grid[x][r]["level"] for r in range(GRID_HEIGHT))
    
    def find_target_col(exclude=-1):
        ship_col = int(round(ship["x"] - 0.5))
        for radius in range(2, GRID_WIDTH + 1):
            best_col = -1
            best_score = 0
            for offset in range(-radius, radius + 1):
                x = ship_col + offset
                if 0 <= x < GRID_WIDTH and x != exclude:
                    s = score_col(x)
                    if s > best_score:
                        best_score = s
                        best_col = x
            if best_col != -1:
                return best_col
        for x in range(GRID_WIDTH):
            if x != exclude and any(grid[x][r]["commitsCount"] > 0 for r in range(GRID_HEIGHT)):
                return x
        return GRID_WIDTH // 2

    current_target_col = find_target_col()
    frames_shooting = 0
    frames_allowed = 6

    # 480 frames yields a smooth 48-second loop with rich action
    MAX_SIM_FRAMES = 480
    
    for frame_idx in range(MAX_SIM_FRAMES):
        new_bullets = []
        for b in bullets:
            b["y"] -= BULLET_SPEED
            if b["y"] < -1:
                continue
            col = int(round(b["x"] - 0.5))
            row = int(math.floor(b["y"]))
            hit = False
            if 0 <= col < GRID_WIDTH and 0 <= row < GRID_HEIGHT:
                if grid[col][row]["commitsCount"] > 0:
                    prev_lvl = grid[col][row]["level"]
                    new_lvl = max(0, prev_lvl - 1)
                    grid[col][row]["level"] = new_lvl
                    if new_lvl == 0:
                        grid[col][row]["commitsCount"] = 0
                        explosion_events.append({
                            "frameIndex": frame_idx,
                            "x": col,
                            "y": row,
                            "level": prev_lvl
                        })
                    cell_events.append({
                        "frameIndex": frame_idx,
                        "x": col,
                        "y": row,
                        "level": new_lvl
                    })
                    hit = True
            if not hit:
                new_bullets.append(b)
        bullets = new_bullets
        
        if not any(grid[current_target_col][r]["commitsCount"] > 0 for r in range(GRID_HEIGHT)):
            current_target_col = find_target_col()
            frames_shooting = 0
            frames_allowed = 5 + (frame_idx % 4)
            
        target_x = current_target_col + 0.5
        dx = target_x - ship["x"]
        if abs(dx) > SHIP_SPEED:
            ship["x"] += math.copysign(SHIP_SPEED, dx)
        else:
            ship["x"] = target_x
        ship["x"] = max(SHIP_HALF_WIDTH, min(GRID_WIDTH - SHIP_HALF_WIDTH, ship["x"]))
        
        aligned = abs(ship["x"] - target_x) < 0.5
        col_has_enemies = any(grid[current_target_col][r]["commitsCount"] > 0 for r in range(GRID_HEIGHT))
        if aligned and col_has_enemies:
            if frames_shooting >= frames_allowed:
                current_target_col = find_target_col(exclude=current_target_col)
                frames_shooting = 0
                frames_allowed = 5 + ((frame_idx + 1) % 4)
            else:
                if frame_idx % FIRE_RATE == 0 and len(bullets) < MAX_BULLETS:
                    bullets.append({
                        "id": next_bullet_id,
                        "x": target_x,
                        "y": SHIP_Y - 0.8
                    })
                    next_bullet_id += 1
                frames_shooting += 1
                
        game_history.append({
            "ship": {"x": ship["x"]},
            "bullets": [dict(b) for b in bullets]
        })
        
    return game_history, cell_events, explosion_events

def extract_bullet_flights(game_history):
    flights = []
    active = {}
    for f_idx, frame in enumerate(game_history):
        current_bullets = frame["bullets"]
        current_ids = {b["id"] for b in current_bullets}
        
        for bid in list(active.keys()):
            if bid not in current_ids:
                fl = active.pop(bid)
                flights.append({
                    "id": bid,
                    "x": fl["x"],
                    "startFrame": fl["startFrame"],
                    "endFrame": f_idx - 1,
                    "yPositions": fl["yPositions"]
                })
        for b in current_bullets:
            bid = b["id"]
            if bid not in active:
                active[bid] = {"x": b["x"], "startFrame": f_idx, "yPositions": [b["y"]]}
            else:
                active[bid]["yPositions"].append(b["y"])
                
    for bid, fl in active.items():
        flights.append({
            "id": bid,
            "x": fl["x"],
            "startFrame": fl["startFrame"],
            "endFrame": len(game_history) - 1,
            "yPositions": fl["yPositions"]
        })
    return flights

def get_cell_animation_data(x, y, initial_level, cell_events, total_frames, theme_levels):
    initial_color = theme_levels[initial_level]
    events = [e for e in cell_events if e["x"] == x and e["y"] == y]
    
    if not events:
        init_val = "transparent" if initial_level == 0 else initial_color
        return "0;1", f"{init_val};{init_val}"
        
    k_times = [0.0]
    k_values = [initial_color if initial_level > 0 else "transparent"]
    
    for ev in events:
        t = round(ev["frameIndex"] / max(total_frames - 1, 1), 4)
        c = theme_levels[ev["level"]] if ev["level"] > 0 else "transparent"
        if t != k_times[-1]:
            k_times.append(t)
            k_values.append(c)
        else:
            k_values[-1] = c
            
    if k_times[-1] != 1.0:
        k_times.append(1.0)
        k_values.append(k_values[-1])
        
    return ";".join(str(t) for t in k_times), ";".join(k_values)

def build_changing_values_animation(values, total_frames):
    if total_frames == 0:
        return "0;1", f"{values[0]};{values[0]}"
    key_times = []
    key_values = []
    last_val = None
    last_idx = None
    
    for idx, curr in enumerate(values):
        if curr != last_val:
            if last_val is not None and last_idx is not None and idx - 1 != last_idx:
                key_times.append(round((idx - 1) / (total_frames - 1), 4))
                key_values.append(last_val)
            key_times.append(round(idx / (total_frames - 1), 4))
            key_values.append(curr)
            last_val = curr
            last_idx = idx
            
    if not key_times or key_times[-1] != 1.0:
        if not key_times:
            key_times = [0.0, 1.0]
            key_values = [values[0], values[-1]]
        else:
            key_times.append(1.0)
            key_values.append(last_val or values[-1])
            
    return ";".join(str(t) for t in key_times), ";".join(key_values)

def generate_svg(initial_grid, month_labels, game_history, cell_events, explosion_events, theme_key):
    theme_cfg = THEMES[theme_key]
    theme_levels = theme_cfg["levels"]
    empty_cell = theme_cfg["empty_cell"]
    empty_border = theme_cfg["empty_border"]
    
    svg_width = GRID_WIDTH * (CELL_SIZE + GAP_SIZE) # 1166
    svg_height = 260
    total_frames = len(game_history)
    total_dur = max(int(total_frames * DELTA_TIME / 2), 1000)
    ship_svg_y = to_svg_y(SHIP_Y) # 224.0
    
    svg = f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<desc>Generated with galaga-contribution-graph</desc>'
    svg += '<rect width="100%" height="100%" fill="#000000"/>'
    
    # 1. Galaxy starfield
    star_seed = 12345
    def star_rng():
        nonlocal star_seed
        star_seed = (star_seed * 1664525 + 1013904223) & 0xFFFFFFFF
        return star_seed / 0xFFFFFFFF

    for _ in range(120):
        scx = f"{star_rng() * svg_width:.1f}"
        sr = f"{0.4 + star_rng() * 1.6:.1f}"
        sop = f"{0.3 + star_rng() * 0.7:.2f}"
        spd = int(2500 + star_rng() * 5500)
        sph = int(star_rng() * spd)
        svg += f'<circle cx="{scx}" cy="0" r="{sr}" fill="white" opacity="{sop}"><animate attributeName="cy" from="-2" to="{svg_height + 2}" dur="{spd}ms" begin="-{sph}ms" repeatCount="indefinite"/></circle>'
        
    # 2. Month labels
    last_m = ""
    for col_idx in range(GRID_WIDTH):
        m_txt = month_labels[col_idx]
        if m_txt and m_txt != last_m:
            x_pos = col_idx * (CELL_SIZE + GAP_SIZE) + CELL_SIZE / 2
            svg += f'<text x="{x_pos}" y="10" text-anchor="middle" font-size="10" fill="#aaaaaa">{m_txt}</text>'
            last_m = m_txt
            
    # 3. Base grid slots (unoccupied background slots clearly outlining the authentic GitHub contribution grid)
    for col in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            cx = to_svg_x(col)
            cy = to_svg_y(row)
            svg += f'<rect x="{cx}" y="{cy}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="3" fill="{empty_cell}" stroke="{empty_border}" stroke-width="0.5" opacity="0.45"/>'

    # 4. Active Contribution Cells (animated enemy formation)
    for col in range(GRID_WIDTH):
        for row in range(GRID_HEIGHT):
            cx = to_svg_x(col)
            cy = to_svg_y(row)
            init_lvl = initial_grid[col][row]["level"]
            kt, vals = get_cell_animation_data(col, row, init_lvl, cell_events, total_frames, theme_levels)
            svg += f'''<rect x="{cx}" y="{cy}" width="{CELL_SIZE}" height="{CELL_SIZE}" rx="3" fill="transparent">
\t\t\t\t<animate attributeName="fill" calcMode="discrete" dur="{total_dur}ms" repeatCount="indefinite"
\t\t\t\t\tvalues="{vals}" keyTimes="{kt}"/>
\t\t\t</rect>'''
            
    # 5. Dual Plasma Lasers (Pure vector rectangles with glowing cyan aura and white plasma core)
    flights = extract_bullet_flights(game_history)
    for flight in flights:
        svg_x = to_svg_x(flight["x"])
        t_start = round(flight["startFrame"] / (total_frames - 1), 4)
        t_end_next = round(min(flight["endFrame"] + 1, total_frames - 1) / (total_frames - 1), 4)
        
        if t_start <= 0 and t_end_next >= 1:
            op_kt, op_vals = "0;1", "1;1"
        elif t_start <= 0:
            op_kt, op_vals = f"0;{t_end_next};{t_end_next};1", "1;1;0;0"
        elif t_end_next >= 1:
            op_kt, op_vals = f"0;{t_start};{t_start};1", "0;0;1;1"
        else:
            op_kt, op_vals = f"0;{t_start};{t_start};{t_end_next};{t_end_next};1", "0;0;1;1;0;0"
            
        pos_kt = []
        pos_vals = []
        first_y = f"{to_svg_y(flight['yPositions'][0]):.1f}"
        last_y = f"{to_svg_y(flight['yPositions'][-1]):.1f}"
        
        if flight["startFrame"] > 0:
            pos_kt.append(0.0)
            pos_vals.append(f"{svg_x:.1f},{first_y}")
            
        for i, y_pos in enumerate(flight["yPositions"]):
            frame_idx = flight["startFrame"] + i
            t = round(frame_idx / (total_frames - 1), 4)
            svg_y = f"{to_svg_y(y_pos):.1f}"
            if not pos_kt or t != pos_kt[-1]:
                pos_kt.append(t)
                pos_vals.append(f"{svg_x:.1f},{svg_y}")
                
        if pos_kt[-1] != 1.0:
            pos_kt.append(1.0)
            pos_vals.append(f"{svg_x:.1f},{last_y}")
            
        pos_kt_str = ";".join(str(t) for t in pos_kt)
        pos_vals_str = ";".join(pos_vals)
        
        svg += f'''<g opacity="0">
\t\t\t\t<animate attributeName="opacity" calcMode="discrete" dur="{total_dur}ms" repeatCount="indefinite"
\t\t\t\t\tkeyTimes="{op_kt}" values="{op_vals}"/>
\t\t\t\t<animateTransform attributeName="transform" type="translate" calcMode="linear"
\t\t\t\t\tdur="{total_dur}ms" repeatCount="indefinite"
\t\t\t\t\tkeyTimes="{pos_kt_str}" values="{pos_vals_str}"/>
\t\t\t\t<rect x="-10" y="-12" width="2.5" height="12" rx="1.2" fill="#38bdf8"/>
\t\t\t\t<rect x="-9.5" y="-10" width="1.5" height="8" rx="0.7" fill="#ffffff"/>
\t\t\t\t<rect x="7.5" y="-12" width="2.5" height="12" rx="1.2" fill="#38bdf8"/>
\t\t\t\t<rect x="8" y="-10" width="1.5" height="8" rx="0.7" fill="#ffffff"/>
\t\t\t</g>'''
        
    # 6. Explosions (Expanding rings and 4 flying sparks)
    for exp in explosion_events:
        cx = f"{to_svg_x(exp['x']) + CELL_SIZE / 2:.1f}"
        cy = f"{to_svg_y(exp['y']) + CELL_SIZE / 2:.1f}"
        t_s = round(exp["frameIndex"] / (total_frames - 1), 4)
        t_e = round(min(exp["frameIndex"] + EXPLOSION_FRAMES, total_frames - 1) / (total_frames - 1), 4)
        if t_e <= t_s:
            continue
        kt = f"0;{t_s};{t_s};{t_e};1"
        op_vals = "0;0;1;0;0"
        exp_color = theme_levels[exp["level"]]
        
        svg += f'''<circle cx="{cx}" cy="{cy}" r="2" fill="none" stroke="{exp_color}" stroke-width="3" opacity="0">
\t\t\t\t<animate attributeName="r" calcMode="linear" dur="{total_dur}ms" repeatCount="indefinite" keyTimes="{kt}" values="2;2;2;{CELL_SIZE};{CELL_SIZE}"/>
\t\t\t\t<animate attributeName="stroke-width" calcMode="linear" dur="{total_dur}ms" repeatCount="indefinite" keyTimes="{kt}" values="3;3;3;0;0"/>
\t\t\t\t<animate attributeName="opacity" calcMode="linear" dur="{total_dur}ms" repeatCount="indefinite" keyTimes="{kt}" values="{op_vals}"/>
\t\t\t</circle>'''
        
        for dx, dy in [(0, -11), (0, 11), (-11, 0), (11, 0)]:
            tx = f"{float(cx) + dx:.1f}"
            ty = f"{float(cy) + dy:.1f}"
            svg += f'''<circle cx="{cx}" cy="{cy}" r="2.5" fill="{exp_color}" opacity="0">
\t\t\t\t<animate attributeName="cx" calcMode="linear" dur="{total_dur}ms" repeatCount="indefinite" keyTimes="{kt}" values="{cx};{cx};{cx};{tx};{tx}"/>
\t\t\t\t<animate attributeName="cy" calcMode="linear" dur="{total_dur}ms" repeatCount="indefinite" keyTimes="{kt}" values="{cy};{cy};{cy};{ty};{ty}"/>
\t\t\t\t<animate attributeName="r" calcMode="linear" dur="{total_dur}ms" repeatCount="indefinite" keyTimes="{kt}" values="2.5;2.5;2.5;0;0"/>
\t\t\t\t<animate attributeName="opacity" calcMode="linear" dur="{total_dur}ms" repeatCount="indefinite" keyTimes="{kt}" values="{op_vals}"/>
\t\t\t</circle>'''
            
    # 7. Pure Vector Galaga Fighter Rocket (Visible on all browsers and GitHub Camo)
    ship_positions = [f"{to_svg_x(f['ship']['x']):.1f},{ship_svg_y:.1f}" for f in game_history]
    ship_kt, ship_vals = build_changing_values_animation(ship_positions, total_frames)
    
    svg += f'''<g id="galaga-rocket">
\t\t<animateTransform attributeName="transform" type="translate" calcMode="linear"
\t\t\tdur="{total_dur}ms" repeatCount="indefinite"
\t\t\tkeyTimes="{ship_kt}"
\t\t\tvalues="{ship_vals}"/>
\t\t<!-- Animated Thruster Flame -->
\t\t<polygon points="-4,10 0,22 4,10" fill="#f59e0b">
\t\t\t<animate attributeName="points" dur="200ms" repeatCount="indefinite"
\t\t\t\tvalues="-4,10 0,22 4,10; -4,10 0,16 4,10; -4,10 0,24 4,10; -4,10 0,19 4,10; -4,10 0,22 4,10"/>
\t\t</polygon>
\t\t<polygon points="-2,10 0,16 2,10" fill="#fef08a">
\t\t\t<animate attributeName="points" dur="200ms" repeatCount="indefinite"
\t\t\t\tvalues="-2,10 0,16 2,10; -2,10 0,12 2,10; -2,10 0,17 2,10; -2,10 0,14 2,10; -2,10 0,16 2,10"/>
\t\t</polygon>
\t\t<!-- Aerodynamic Swept Wings -->
\t\t<polygon points="0,-12 17,8 13,12 0,5 -13,12 -17,8" fill="#1e293b" stroke="#475569" stroke-width="1"/>
\t\t<!-- Wingtips: Galaga Red Accents -->
\t\t<polygon points="12,4 17,8 13,12" fill="#ef4444"/>
\t\t<polygon points="-12,4 -17,8 -13,12" fill="#ef4444"/>
\t\t<!-- Main Fuselage -->
\t\t<polygon points="0,-18 7,-2 5,10 -5,10 -7,-2" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1"/>
\t\t<!-- Galaga Center Fin & Intake -->
\t\t<polygon points="0,-14 3,-2 0,4 -3,-2" fill="#ef4444"/>
\t\t<!-- Glowing Cyan Cockpit Canopy -->
\t\t<polygon points="0,-7 3,0 0,3 -3,0" fill="#38bdf8" stroke="#0ea5e9" stroke-width="0.5"/>
\t\t<!-- Twin Plasma Cannons with Charged Muzzle Tips -->
\t\t<line x1="-11" y1="2" x2="-11" y2="-8" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
\t\t<line x1="11" y1="2" x2="11" y2="-8" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
\t\t<circle cx="-11" cy="-8" r="1.5" fill="#38bdf8"/>
\t\t<circle cx="11" cy="-8" r="1.5" fill="#38bdf8"/>
\t</g>'''
    
    svg += '</svg>'
    return svg

def main():
    print("=== Generating Authentic Galaga Contribution Graph SVGs ===")
    print(f"Fetching live contribution data for GitHub user: '{USERNAME}'...")
    contribs = fetch_authentic_contributions(USERNAME)
    if not contribs:
        print("[ERROR] Could not fetch contributions for user", file=sys.stderr)
        sys.exit(1)
        
    occupied_count = sum(1 for c in contribs if c.get("count", 0) > 0)
    print(f"  [Verified] Total days: {len(contribs)}")
    print(f"  [Verified] Authentic occupied contribution days: {occupied_count}")
    
    initial_grid, month_labels = build_grid_and_labels(contribs)
    grid_occ = sum(1 for col in initial_grid for cell in col if cell["level"] > 0)
    print(f"  [Verified] Grid occupied cells mapped: {grid_occ}")
    
    print("Simulating Galaga arcade mission...")
    game_history, cell_events, explosion_events = run_galaga_sim(initial_grid)
    print(f"  [Simulation] Total frames: {len(game_history)}")
    print(f"  [Simulation] Cell impacts: {len(cell_events)}")
    print(f"  [Simulation] Neutralization explosions: {len(explosion_events)}")
    
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.join(repo_root, "assets")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Dark theme SVG
    dark_svg = generate_svg(initial_grid, month_labels, game_history, cell_events, explosion_events, "github-dark")
    dark_path = os.path.join(out_dir, "galaga-contribution-graph-dark.svg")
    with open(dark_path, "w", encoding="utf-8") as f:
        f.write(dark_svg)
    sz_dark = os.path.getsize(dark_path)
    print(f"  -> Generated {os.path.basename(dark_path)} ({sz_dark} bytes, {sz_dark/1024:.1f} KB)")
    
    # 2. Light theme SVG
    light_svg = generate_svg(initial_grid, month_labels, game_history, cell_events, explosion_events, "github")
    light_path = os.path.join(out_dir, "galaga-contribution-graph.svg")
    with open(light_path, "w", encoding="utf-8") as f:
        f.write(light_svg)
    sz_light = os.path.getsize(light_path)
    print(f"  -> Generated {os.path.basename(light_path)} ({sz_light} bytes, {sz_light/1024:.1f} KB)")
    
    print("[SUCCESS] Authentic Galaga contribution graphs successfully built with pure vector rocket.")

if __name__ == "__main__":
    main()
