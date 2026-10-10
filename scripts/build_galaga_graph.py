#!/usr/bin/env python3
"""
Galaga Contribution Graph Generator
Builds authentic Galaga arcade animated SVGs for GitHub profile README
based on the reference implementation from abozanona/pacman-contribution-graph.
Connects directly to uvv-01's authentic GitHub contribution graph.
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

SHIP_Y = 10.5
SHIP_SPEED = 0.4
SHIP_HALF_WIDTH = 0.8

BULLET_SPEED = 0.6
MAX_BULLETS = 10
FIRE_RATE = 2
EXPLOSION_FRAMES = 7

BULLET_IMAGE_DATA = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAACACAMAAACMX59YAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAAByUExURQAAAP////7+/gBE/wBE/wBE/wBE/wBE/wBE/gBE/gBE/wBE/wBE/gBE/wBE/wBE/gBE/gBE/+cgMfUeJf8AAP8AAP4AAP4AAABE/wBE/hhW/y9m/y9n/yNd/4Sl/73O/7zO//8cHP4cHP8AAP4AAP///6QdcYAAAAAYdFJOUwAAAGbHk4W9hb1genq/3RYcHJPFhb2FvbKPFBsAAAABYktHRAH/Ai3eAAAACXBIWXMAAA7DAAAOwwHHb6hkAAAAB3RJTUUH6gUIFjcZmpji7QAAACV0RVh0ZGF0ZTpjcmVhdGUAMjAyNi0wNS0wOFQyMjo1NToyNSswMDowMDWlEL0AAAAldEVYdGRhdGU6bW9kaWZ5ADIwMjYtMDUtMDhUMjI6NTU6MjUrMDA6MDBE+KgBAAAAKHRFWHRkYXRlOnRpbWVzdGFtcAAyMDI2LTA1LTA4VDIyOjU1OjI1KzAwOjAwE+2J3gAAAk5JREFUaN7tVotWwyAMnahzvp2PSXxMZ/P/3+ggECija1N2ZDvuWmm17W1y82IyyeH0LIPzyXBMdQYXR4IjwZFATDAD0NoeYE/mT30pITBfNK/ZNx2TyAX3acvjL4QE2r/HFxIXptGHmUEkIkkXx0CmwczIl6KD4OqaccPnWx8BXtc/d9GDN/Twepmc6S5A7x1z3iCgDKJfoFxI7kEI7nrdYkGfWXQZE3DW5e2HrGM5C0Anj3aoATmCyH8XAr5B/05oxRpsYGcEvQ5vJwiFxzUAkDAlBUrpndWAshg09NsCO9TgPxEIamE8wZ5rMIzg7b2FD7t+CgiWJxl8lRJ8DyFwJbdUJ0rFLysm6AsjFFowVgMYQlBswX4TtLcSYAiUD59qhzEJGGwSmF5r80CFFAgW+JZND3ZO5zINYDgBbBFRjbdAV63GLQSqjwAghJMJXB4os7bL2e9C9iWVewlUN8H9g8OcYC8fVxY/qxhPc3rOH4T8Bvq5CUC/vgh26zEBYxQBugOrWVCNYOEVwKAE1nAB2YYxBBh/HQ8uCvUJFi7+VARIVwfmAqcBhmQWWoB1XdhFGNGFcb0cZBjjrszRLLWgkgbovJB2JJfKXIljUjlSEev0RJuArIF0vC84/AYNLX/sQtRIxoRxj4qpXkfiaeIm/J+HcbEDDSiRMRoQNV3AA8yDcgJM/G+EPdE3VUpFd5INV9+JXFMykLmAfjIjmyK0wLUj5NYkJKBx0sKrWIMEchGxsgVNsQVNCYEfLGEySrd5xSK6LArjdUwtDIrCL/JGvSI+ReIgAAAAAElFTkSuQmCC"
)

SHIP_IMAGE_DATA = (
    "data:image/png;base64,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"
)

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
        for radius in range(3, GRID_WIDTH + 1):
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

    # 480 frames yields a smooth ~48-second loop with extensive action
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
                        "y": SHIP_Y - 1.0
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
    svg_height = GRID_HEIGHT * (CELL_SIZE + GAP_SIZE) + 15 + 90 # 259
    total_frames = len(game_history)
    total_dur = max(int(total_frames * DELTA_TIME / 2), 1000)
    
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
            
    # 5. Bullets
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
        
        svg += f'''<image x="-5" y="-13" width="10" height="13" href="{BULLET_IMAGE_DATA}" opacity="0" preserveAspectRatio="xMidYMid meet">
\t\t\t\t<animate attributeName="opacity" calcMode="discrete" dur="{total_dur}ms" repeatCount="indefinite"
\t\t\t\t\tkeyTimes="{op_kt}" values="{op_vals}"/>
\t\t\t\t<animateTransform attributeName="transform" type="translate" calcMode="linear"
\t\t\t\t\tdur="{total_dur}ms" repeatCount="indefinite"
\t\t\t\t\tkeyTimes="{pos_kt_str}" values="{pos_vals_str}"/>
\t\t\t</image>'''
        
    # 6. Explosions
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
            
    # 7. Ship
    ship_positions = [f"{to_svg_x(f['ship']['x']):.1f},{to_svg_y(SHIP_Y):.1f}" for f in game_history]
    ship_kt, ship_vals = build_changing_values_animation(ship_positions, total_frames)
    svg += f'''<image x="-16" y="-35" width="32" height="35" href="{SHIP_IMAGE_DATA}" preserveAspectRatio="xMidYMid meet">
\t\t<animateTransform attributeName="transform" type="translate" calcMode="linear"
\t\t\tdur="{total_dur}ms" repeatCount="indefinite"
\t\t\tkeyTimes="{ship_kt}"
\t\t\tvalues="{ship_vals}"/>
\t</image>'''
    
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
    
    print("[SUCCESS] Authentic Galaga contribution graphs successfully built.")

if __name__ == "__main__":
    main()
