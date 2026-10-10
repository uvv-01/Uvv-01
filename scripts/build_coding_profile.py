#!/usr/bin/env python3
"""
Gaming Coding Profile Dashboard Generator
Generates a competitive video game player-statistics HUD for LeetCode, Codeforces, and CodeChef.
Fetches authentic real-time data with reliable fallbacks and non-breaking error handling.
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error

# ─── Configuration ───────────────────────────────────────────────────────────
LEETCODE_USERNAME = os.environ.get("LEETCODE_USERNAME", "TUS8Mufpy3")
CODECHEF_USERNAME = os.environ.get("CODECHEF_USERNAME", "uvv_0000")
CODEFORCES_USERNAME = os.environ.get("CODEFORCES_USERNAME", None)  # None until configured

# Authentic cached fallbacks in case APIs are temporarily unreachable or rate-limited
FALLBACK_DATA = {
    "leetcode": {
        "handle": "TUS8Mufpy3",
        "current_rating": 1390,
        "peak_rating": 1492,
        "contests": 10,
        "rating_history": [1461, 1492, 1447, 1408, 1411, 1435, 1435, 1421, 1413, 1390],
        "solved": 169,
        "easy": 101,
        "medium": 66,
        "hard": 2,
        "rank": "764,774",
    },
    "codechef": {
        "handle": "uvv_0000",
        "current_rating": 1162,
        "peak_rating": 1202,
        "contests": 11,
        "rating_history": [849, 878, 943, 1024, 1097, 1120, 1154, 1164, 1202, 1183, 1162],
        "stars": "1★",
        "division": "Div 4",
    },
    "codeforces": None  # Genuinely unconfigured
}

def fetch_json(url, headers=None, data=None, timeout=8):
    try:
        h = {"User-Agent": "Mozilla/5.0"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, data=data, headers=h)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [Notice] API fetch notice for {url}: {e}", file=sys.stderr)
        return None

def get_leetcode_data(username):
    if not username:
        return None
    print(f"Fetching LeetCode data for {username}...")
    res = dict(FALLBACK_DATA["leetcode"])
    res["handle"] = username

    # Fetch stats
    stats = fetch_json(f"https://leetcode-stats-api.vercel.app/{username}")
    if stats and "totalSolved" in stats:
        res["solved"] = stats.get("totalSolved", res["solved"])
        res["easy"] = stats.get("easySolved", res["easy"])
        res["medium"] = stats.get("mediumSolved", res["medium"])
        res["hard"] = stats.get("hardSolved", res["hard"])

    # Fetch contest ranking and history via official GraphQL
    query = """
    query userContestRankingInfo($username: String!) {
      userContestRanking(username: $username) {
        attendedContestsCount
        rating
        globalRanking
      }
      userContestRankingHistory(username: $username) {
        attended
        rating
      }
    }
    """
    gql_data = json.dumps({"query": query, "variables": {"username": username}}).encode("utf-8")
    gql = fetch_json(
        "https://leetcode.com/graphql",
        headers={"Content-Type": "application/json"},
        data=gql_data
    )
    if gql and "data" in gql:
        ucr = gql["data"].get("userContestRanking")
        if ucr:
            res["current_rating"] = round(ucr.get("rating", res["current_rating"]))
            res["contests"] = ucr.get("attendedContestsCount", res["contests"])
            if ucr.get("globalRanking"):
                res["rank"] = f"{ucr['globalRanking']:,}"

        uch = gql["data"].get("userContestRankingHistory")
        if uch:
            history = [round(item["rating"]) for item in uch if item.get("attended") and item.get("rating")]
            if history:
                res["rating_history"] = history
                res["peak_rating"] = max(history)

    return res

def get_codechef_data(username):
    if not username:
        return None
    print(f"Fetching CodeChef data for {username}...")
    res = dict(FALLBACK_DATA["codechef"])
    res["handle"] = username

    try:
        req = urllib.request.Request(
            f"https://www.codechef.com/users/{username}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")

        idx = html.find('"date_versus_rating":')
        if idx != -1:
            arr_idx = html.find('"all":[', idx)
            if arr_idx != -1:
                arr_end = html.find(']', arr_idx) + 1
                arr_str = html[arr_idx+6:arr_end]
                history_json = json.loads(arr_str)
                if history_json:
                    ratings = [int(h.get("rating", 0)) for h in history_json if h.get("rating")]
                    if ratings:
                        res["rating_history"] = ratings
                        res["current_rating"] = ratings[-1]
                        res["peak_rating"] = max(ratings)
                        res["contests"] = len(ratings)

        rating_match = re.search(r'<div class="rating-number">(\d+)</div>', html)
        if rating_match:
            res["current_rating"] = int(rating_match.group(1))

        stars_match = re.search(r'<span class="rating">(\d+&#9733;|\d+★|\d+\s*★)</span>', html)
        if stars_match:
            res["stars"] = stars_match.group(1).replace("&#9733;", "★")
    except Exception as e:
        print(f"  [Notice] CodeChef scraping notice: {e}", file=sys.stderr)

    return res

def get_codeforces_data(handle):
    if not handle:
        return None
    print(f"Fetching Codeforces data for {handle}...")
    info = fetch_json(f"https://codeforces.com/api/user.info?handles={handle}")
    if not info or info.get("status") != "OK" or not info.get("result"):
        return None
    user = info["result"][0]
    res = {
        "handle": user.get("handle", handle),
        "current_rating": user.get("rating", 0),
        "peak_rating": user.get("maxRating", 0),
        "rank": user.get("rank", "unrated").title(),
        "contests": 0,
        "rating_history": [],
    }

    rating_data = fetch_json(f"https://codeforces.com/api/user.rating?handle={handle}")
    if rating_data and rating_data.get("status") == "OK":
        contests = rating_data.get("result", [])
        res["contests"] = len(contests)
        res["rating_history"] = [c.get("newRating") for c in contests]

    return res

# ─── SVG Construction ────────────────────────────────────────────────────────

def build_sparkline(history, x, y, w, h, line_color, grad_id):
    """Generate SVG sparkline path and dots for rating history."""
    if not history or len(history) < 2:
        return ""

    min_val = min(history)
    max_val = max(history)
    val_range = max_val - min_val if max_val != min_val else 1

    padding_x = 10
    padding_y = 12
    draw_w = w - 2 * padding_x
    draw_h = h - 2 * padding_y

    pts = []
    n = len(history)
    for i, val in enumerate(history):
        px = x + padding_x + (i / (n - 1)) * draw_w
        py = y + h - padding_y - ((val - min_val) / val_range) * draw_h
        pts.append((px, py))

    # Path string
    d_path = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for px, py in pts[1:]:
        d_path += f" L {px:.1f} {py:.1f}"

    # Gradient fill area
    d_fill = f"{d_path} L {pts[-1][0]:.1f} {y + h - 2} L {pts[0][0]:.1f} {y + h - 2} Z"

    svg_parts = []
    # Grid lines inside sparkline box
    svg_parts.append(f'<line x1="{x}" y1="{y + h // 2}" x2="{x + w}" y2="{y + h // 2}" stroke="#1e293b" stroke-width="1" stroke-dasharray="3 3"/>')
    svg_parts.append(f'<line x1="{x}" y1="{y + h - 2}" x2="{x + w}" y2="{y + h - 2}" stroke="#1e293b" stroke-width="1"/>')

    # Filled area
    svg_parts.append(f'<path d="{d_fill}" fill="url(#{grad_id})" opacity="0.3"/>')
    # Glowing line
    svg_parts.append(f'<path d="{d_path}" fill="none" stroke="{line_color}" stroke-width="2.5" filter="url(#neon-glow)" stroke-linecap="round"/>')
    svg_parts.append(f'<path d="{d_path}" fill="none" stroke="{line_color}" stroke-width="2" stroke-linecap="round"/>')

    # Data points
    for i, (px, py) in enumerate(pts):
        if i == 0 or i == n - 1 or history[i] == max_val:
            svg_parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="#ffffff" stroke="{line_color}" stroke-width="1.5"/>')
        else:
            svg_parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.5" fill="{line_color}"/>')

    # Labels for min and max
    svg_parts.append(f'<text x="{x + 6}" y="{y + 12}" fill="#64748b" font-size="9" font-family="Consolas, monospace">PEAK: {max_val}</text>')
    svg_parts.append(f'<text x="{x + w - 6}" y="{y + h - 6}" text-anchor="end" fill="#64748b" font-size="9" font-family="Consolas, monospace">BASE: {min_val}</text>')

    return "\n".join(svg_parts)

def build_dashboard_svg(lc_data, cf_data, cc_data):
    W = 960
    H = 460

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="{H}">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="db-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#060913"/>
      <stop offset="50%" stop-color="#0a101d"/>
      <stop offset="100%" stop-color="#070a14"/>
    </linearGradient>

    <!-- Card Gradients -->
    <linearGradient id="card-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#121829" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#0b101d" stop-opacity="0.95"/>
    </linearGradient>

    <linearGradient id="lc-area" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffa116" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#ffa116" stop-opacity="0.0"/>
    </linearGradient>

    <linearGradient id="cf-area" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#00f0ff" stop-opacity="0.0"/>
    </linearGradient>

    <linearGradient id="cc-area" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.0"/>
    </linearGradient>

    <!-- Glow Filters -->
    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="hud-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <style>
    @keyframes pulse-dot {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.3; }}
    }}
    .live-dot {{
      animation: pulse-dot 2s ease-in-out infinite;
    }}
    .hud-title {{
      font-family: 'Rajdhani', 'Orbitron', 'Segoe UI', system-ui, sans-serif;
      font-weight: 700;
      letter-spacing: 2px;
    }}
    .mono {{
      font-family: 'Consolas', 'Courier New', monospace;
    }}
    .card-wrap {{
      transition: transform 0.3s ease, filter 0.3s ease;
    }}
    .card-wrap:hover {{
      transform: translateY(-4px);
    }}
  </style>

  <!-- Outer Background Container -->
  <rect x="0" y="0" width="{W}" height="{H}" rx="12" fill="url(#db-bg)"/>
  <rect x="1" y="1" width="{W-2}" height="{H-2}" rx="11" fill="none" stroke="#1e293b" stroke-width="1.5"/>

  <!-- Top HUD Status Header -->
  <path d="M 24 16 L 36 16 M {W-36} 16 L {W-24} 16" stroke="#00f0ff" stroke-width="2"/>
  <g transform="translate(24, 28)">
    <text x="0" y="0" fill="#00f0ff" font-size="11" class="mono" font-weight="700" letter-spacing="2">
      // COMPETITIVE GAMING DASHBOARD // TELEMETRY: SYNCHRONIZED
    </text>
  </g>
  <g transform="translate({W-160}, 28)">
    <circle cx="0" cy="-3" r="4" fill="#00ff88" class="live-dot" filter="url(#neon-glow)"/>
    <text x="12" y="0" fill="#00ff88" font-size="10" class="mono" font-weight="600" letter-spacing="1">LIVE HUD STATS</text>
  </g>

  <line x1="24" y1="42" x2="{W-24}" y2="42" stroke="#1e293b" stroke-width="1"/>
'''

    # Layout for 3 cards
    card_w = 286
    card_h = 390
    gap = 21
    cards_x = [24, 24 + card_w + gap, 24 + 2 * (card_w + gap)]
    card_y = 52

    # ══════════════════════════════════════════════════════════════════════════
    # CARD 1: LEETCODE
    # ══════════════════════════════════════════════════════════════════════════
    x1 = cards_x[0]
    lc_rating = lc_data["current_rating"] if lc_data else "—"
    lc_peak = lc_data["peak_rating"] if lc_data else "—"
    lc_contests = lc_data["contests"] if lc_data else 0
    lc_solved = lc_data.get("solved", 0) if lc_data else 0
    lc_easy = lc_data.get("easy", 0) if lc_data else 0
    lc_med = lc_data.get("medium", 0) if lc_data else 0
    lc_hard = lc_data.get("hard", 0) if lc_data else 0

    sparkline_lc = build_sparkline(
        lc_data.get("rating_history", []) if lc_data else [],
        x1 + 16, card_y + 160, card_w - 32, 95,
        "#ffa116", "lc-area"
    )

    svg += f'''
  <!-- CARD 1: LEETCODE -->
  <g class="card-wrap">
    <!-- Card Frame -->
    <rect x="{x1}" y="{card_y}" width="{card_w}" height="{card_h}" rx="10" fill="url(#card-grad)" stroke="#27354f" stroke-width="1.5"/>
    <!-- Top Accent Bar -->
    <path d="M {x1+8} {card_y} L {x1+card_w-8} {card_y}" stroke="#ffa116" stroke-width="3" stroke-linecap="round" filter="url(#neon-glow)"/>
    
    <!-- Platform Badge -->
    <rect x="{x1+16}" y="{card_y+16}" width="78" height="22" rx="4" fill="#ffa116" fill-opacity="0.15" stroke="#ffa116" stroke-width="1"/>
    <text x="{x1+55}" y="{card_y+31}" text-anchor="middle" fill="#ffa116" font-size="10" class="mono" font-weight="700">PLATFORM</text>
    <text x="{x1+card_w-16}" y="{card_y+31}" text-anchor="end" fill="#64748b" font-size="10" class="mono">ID: {lc_data.get('handle', 'TUS8Mufpy3')}</text>

    <!-- Platform Name -->
    <text x="{x1+16}" y="{card_y+62}" fill="#ffffff" font-size="18" class="hud-title">LEETCODE</text>
    <text x="{x1+16}" y="{card_y+78}" fill="#94a3b8" font-size="10" class="mono">CONTEST RATING TELEMETRY</text>

    <!-- Rating Section -->
    <rect x="{x1+16}" y="{card_y+88}" width="{card_w-32}" height="60" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
    <text x="{x1+28}" y="{card_y+106}" fill="#64748b" font-size="9" class="mono" font-weight="600">CURRENT RATING</text>
    <text x="{x1+28}" y="{card_y+136}" fill="#ffa116" font-size="28" class="hud-title" font-weight="800" filter="url(#neon-glow)">{lc_rating}</text>
    
    <text x="{x1+card_w-28}" y="{card_y+114}" text-anchor="end" fill="#94a3b8" font-size="10" class="mono">PEAK: <tspan fill="#ffffff" font-weight="700">{lc_peak}</tspan></text>
    <text x="{x1+card_w-28}" y="{card_y+134}" text-anchor="end" fill="#94a3b8" font-size="10" class="mono">CONTESTS: <tspan fill="#ffa116" font-weight="700">{lc_contests}</tspan></text>

    <!-- Rating Graph Area -->
    <rect x="{x1+16}" y="{card_y+160}" width="{card_w-32}" height="95" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
    {sparkline_lc}

    <!-- Statistics Section -->
    <rect x="{x1+16}" y="{card_y+268}" width="{card_w-32}" height="106" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
    <text x="{x1+26}" y="{card_y+286}" fill="#64748b" font-size="9" class="mono" font-weight="600">SOLVED PROBLEMS: {lc_solved}</text>
    
    <!-- Easy Bar -->
    <text x="{x1+26}" y="{card_y+306}" fill="#22c55e" font-size="10" class="mono">EASY</text>
    <text x="{x1+75}" y="{card_y+306}" fill="#ffffff" font-size="10" class="mono" font-weight="700">{lc_easy}</text>
    <rect x="{x1+110}" y="{card_y+298}" width="{card_w-150}" height="8" rx="3" fill="#1e293b"/>
    <rect x="{x1+110}" y="{card_y+298}" width="{int((card_w-150) * (lc_easy/lc_solved)) if lc_solved else 0}" height="8" rx="3" fill="#22c55e"/>

    <!-- Medium Bar -->
    <text x="{x1+26}" y="{card_y+328}" fill="#f59e0b" font-size="10" class="mono">MED</text>
    <text x="{x1+75}" y="{card_y+328}" fill="#ffffff" font-size="10" class="mono" font-weight="700">{lc_med}</text>
    <rect x="{x1+110}" y="{card_y+320}" width="{card_w-150}" height="8" rx="3" fill="#1e293b"/>
    <rect x="{x1+110}" y="{card_y+320}" width="{int((card_w-150) * (lc_med/lc_solved)) if lc_solved else 0}" height="8" rx="3" fill="#f59e0b"/>

    <!-- Hard Bar -->
    <text x="{x1+26}" y="{card_y+350}" fill="#ef4444" font-size="10" class="mono">HARD</text>
    <text x="{x1+75}" y="{card_y+350}" fill="#ffffff" font-size="10" class="mono" font-weight="700">{lc_hard}</text>
    <rect x="{x1+110}" y="{card_y+342}" width="{card_w-150}" height="8" rx="3" fill="#1e293b"/>
    <rect x="{x1+110}" y="{card_y+342}" width="{int((card_w-150) * (lc_hard/lc_solved)) if lc_solved else 0}" height="8" rx="3" fill="#ef4444"/>
  </g>
'''

    # ══════════════════════════════════════════════════════════════════════════
    # CARD 2: CODEFORCES
    # ══════════════════════════════════════════════════════════════════════════
    x2 = cards_x[1]
    if cf_data:
        cf_rating = str(cf_data.get("current_rating", 0))
        cf_peak = str(cf_data.get("peak_rating", 0))
        cf_rank = cf_data.get("rank", "Unrated")
        cf_contests = cf_data.get("contests", 0)
        sparkline_cf = build_sparkline(
            cf_data.get("rating_history", []),
            x2 + 16, card_y + 160, card_w - 32, 95,
            "#00f0ff", "cf-area"
        )
        cf_bottom = f'''
        <text x="{x2+28}" y="{card_y+300}" fill="#94a3b8" font-size="11" class="mono">RANK: <tspan fill="#00f0ff" font-weight="700">{cf_rank}</tspan></text>
        <text x="{x2+28}" y="{card_y+326}" fill="#94a3b8" font-size="11" class="mono">CONTESTS: <tspan fill="#ffffff" font-weight="700">{cf_contests}</tspan></text>
        <text x="{x2+28}" y="{card_y+352}" fill="#94a3b8" font-size="11" class="mono">MAX RATING: <tspan fill="#00f0ff" font-weight="700">{cf_peak}</tspan></text>
        '''
    else:
        # Authentic Unlinked / Placeholder State
        cf_rating = "—"
        sparkline_cf = f'''
        <!-- Holographic Standby Radar -->
        <g opacity="0.7">
          <circle cx="{x2 + card_w//2}" cy="{card_y + 160 + 47}" r="32" fill="none" stroke="#00f0ff" stroke-width="1" stroke-dasharray="4 4"/>
          <circle cx="{x2 + card_w//2}" cy="{card_y + 160 + 47}" r="16" fill="none" stroke="#00f0ff" stroke-width="0.75"/>
          <line x1="{x2 + card_w//2 - 40}" y1="{card_y + 160 + 47}" x2="{x2 + card_w//2 + 40}" y2="{card_y + 160 + 47}" stroke="#00f0ff" stroke-width="0.75" stroke-dasharray="2 4"/>
          <line x1="{x2 + card_w//2}" y1="{card_y + 160 + 10}" x2="{x2 + card_w//2}" y2="{card_y + 160 + 85}" stroke="#00f0ff" stroke-width="0.75" stroke-dasharray="2 4"/>
          <text x="{x2 + card_w//2}" y="{card_y + 160 + 51}" text-anchor="middle" fill="#00f0ff" font-size="9" class="mono" font-weight="700">STANDBY</text>
        </g>
        '''
        cf_bottom = f'''
        <!-- Awaiting Configuration Notice -->
        <g transform="translate({x2+16}, {card_y+268})">
          <rect x="0" y="0" width="{card_w-32}" height="106" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
          <text x="14" y="24" fill="#38bdf8" font-size="10" class="mono" font-weight="700">// TELEMETRY STANDBY</text>
          <text x="14" y="44" fill="#94a3b8" font-size="10" class="mono">Status: Awaiting CF Handle</text>
          <text x="14" y="64" fill="#64748b" font-size="9" class="mono">Set in build_cp_profile.py</text>
          <text x="14" y="80" fill="#64748b" font-size="9" class="mono">to unlock live telemetry.</text>
          <rect x="14" y="88" width="{card_w-60}" height="4" rx="2" fill="#1e293b"/>
          <rect x="14" y="88" width="40" height="4" rx="2" fill="#00f0ff" opacity="0.6"/>
        </g>
        '''

    svg += f'''
  <!-- CARD 2: CODEFORCES -->
  <g class="card-wrap">
    <!-- Card Frame -->
    <rect x="{x2}" y="{card_y}" width="{card_w}" height="{card_h}" rx="10" fill="url(#card-grad)" stroke="#27354f" stroke-width="1.5"/>
    <!-- Top Accent Bar -->
    <path d="M {x2+8} {card_y} L {x2+card_w-8} {card_y}" stroke="#00f0ff" stroke-width="3" stroke-linecap="round" filter="url(#neon-glow)"/>

    <!-- Platform Badge -->
    <rect x="{x2+16}" y="{card_y+16}" width="78" height="22" rx="4" fill="#00f0ff" fill-opacity="0.15" stroke="#00f0ff" stroke-width="1"/>
    <text x="{x2+55}" y="{card_y+31}" text-anchor="middle" fill="#00f0ff" font-size="10" class="mono" font-weight="700">PLATFORM</text>
    <text x="{x2+card_w-16}" y="{card_y+31}" text-anchor="end" fill="#64748b" font-size="10" class="mono">{'ID: ' + cf_data['handle'] if cf_data else '[UNLINKED]'}</text>

    <!-- Platform Name -->
    <text x="{x2+16}" y="{card_y+62}" fill="#ffffff" font-size="18" class="hud-title">CODEFORCES</text>
    <text x="{x2+16}" y="{card_y+78}" fill="#94a3b8" font-size="10" class="mono">COMPETITIVE ARENA</text>

    <!-- Rating Section -->
    <rect x="{x2+16}" y="{card_y+88}" width="{card_w-32}" height="60" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
    <text x="{x2+28}" y="{card_y+106}" fill="#64748b" font-size="9" class="mono" font-weight="600">CURRENT RATING</text>
    <text x="{x2+28}" y="{card_y+136}" fill="#00f0ff" font-size="28" class="hud-title" font-weight="800" filter="url(#neon-glow)">{cf_rating}</text>
    
    <text x="{x2+card_w-28}" y="{card_y+114}" text-anchor="end" fill="#94a3b8" font-size="10" class="mono">STATUS: <tspan fill="{'#00ff88' if cf_data else '#38bdf8'}" font-weight="700">{'LINKED' if cf_data else 'PENDING'}</tspan></text>
    <text x="{x2+card_w-28}" y="{card_y+134}" text-anchor="end" fill="#94a3b8" font-size="10" class="mono">TIER: <tspan fill="#00f0ff" font-weight="700">{'ARENA' if cf_data else 'UNSET'}</tspan></text>

    <!-- Rating Graph Area -->
    <rect x="{x2+16}" y="{card_y+160}" width="{card_w-32}" height="95" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
    {sparkline_cf}

    <!-- Statistics Section -->
    {cf_bottom}
  </g>
'''

    # ══════════════════════════════════════════════════════════════════════════
    # CARD 3: CODECHEF
    # ══════════════════════════════════════════════════════════════════════════
    x3 = cards_x[2]
    cc_rating = cc_data["current_rating"] if cc_data else "—"
    cc_peak = cc_data["peak_rating"] if cc_data else "—"
    cc_contests = cc_data["contests"] if cc_data else 0
    cc_stars = cc_data.get("stars", "1★") if cc_data else "1★"
    cc_div = cc_data.get("division", "Div 4") if cc_data else "Div 4"

    sparkline_cc = build_sparkline(
        cc_data.get("rating_history", []) if cc_data else [],
        x3 + 16, card_y + 160, card_w - 32, 95,
        "#f59e0b", "cc-area"
    )

    svg += f'''
  <!-- CARD 3: CODECHEF -->
  <g class="card-wrap">
    <!-- Card Frame -->
    <rect x="{x3}" y="{card_y}" width="{card_w}" height="{card_h}" rx="10" fill="url(#card-grad)" stroke="#27354f" stroke-width="1.5"/>
    <!-- Top Accent Bar -->
    <path d="M {x3+8} {card_y} L {x3+card_w-8} {card_y}" stroke="#f59e0b" stroke-width="3" stroke-linecap="round" filter="url(#neon-glow)"/>

    <!-- Platform Badge -->
    <rect x="{x3+16}" y="{card_y+16}" width="78" height="22" rx="4" fill="#f59e0b" fill-opacity="0.15" stroke="#f59e0b" stroke-width="1"/>
    <text x="{x3+55}" y="{card_y+31}" text-anchor="middle" fill="#f59e0b" font-size="10" class="mono" font-weight="700">PLATFORM</text>
    <text x="{x3+card_w-16}" y="{card_y+31}" text-anchor="end" fill="#64748b" font-size="10" class="mono">ID: {cc_data.get('handle', 'uvv_0000')}</text>

    <!-- Platform Name -->
    <text x="{x3+16}" y="{card_y+62}" fill="#ffffff" font-size="18" class="hud-title">CODECHEF</text>
    <text x="{x3+16}" y="{card_y+78}" fill="#94a3b8" font-size="10" class="mono">RATED STARTERS TELEMETRY</text>

    <!-- Rating Section -->
    <rect x="{x3+16}" y="{card_y+88}" width="{card_w-32}" height="60" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
    <text x="{x3+28}" y="{card_y+106}" fill="#64748b" font-size="9" class="mono" font-weight="600">CURRENT RATING</text>
    <text x="{x3+28}" y="{card_y+136}" fill="#f59e0b" font-size="28" class="hud-title" font-weight="800" filter="url(#neon-glow)">{cc_rating}</text>
    
    <text x="{x3+card_w-28}" y="{card_y+114}" text-anchor="end" fill="#94a3b8" font-size="10" class="mono">PEAK: <tspan fill="#ffffff" font-weight="700">{cc_peak}</tspan></text>
    <text x="{x3+card_w-28}" y="{card_y+134}" text-anchor="end" fill="#94a3b8" font-size="10" class="mono">CONTESTS: <tspan fill="#f59e0b" font-weight="700">{cc_contests}</tspan></text>

    <!-- Rating Graph Area -->
    <rect x="{x3+16}" y="{card_y+160}" width="{card_w-32}" height="95" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
    {sparkline_cc}

    <!-- Statistics Section -->
    <g transform="translate({x3+16}, {card_y+268})">
      <rect x="0" y="0" width="{card_w-32}" height="106" rx="6" fill="#070d18" stroke="#1e293b" stroke-width="1"/>
      <text x="14" y="24" fill="#f59e0b" font-size="10" class="mono" font-weight="700">// CONTEST TELEMETRY</text>
      <text x="14" y="46" fill="#94a3b8" font-size="11" class="mono">DIVISION: <tspan fill="#ffffff" font-weight="700">{cc_div}</tspan></text>
      <text x="14" y="68" fill="#94a3b8" font-size="11" class="mono">RATING STARS: <tspan fill="#f59e0b" font-weight="700">{cc_stars}</tspan></text>
      <text x="14" y="90" fill="#94a3b8" font-size="11" class="mono">STARTERS LOGGED: <tspan fill="#ffffff" font-weight="700">{cc_contests} Contests</tspan></text>
    </g>
  </g>
</svg>'''

    return svg

def main():
    print("Generating Gaming Coding Profile Dashboard...")
    lc_data = get_leetcode_data(LEETCODE_USERNAME)
    cf_data = get_codeforces_data(CODEFORCES_USERNAME)
    cc_data = get_codechef_data(CODECHEF_USERNAME)

    svg_content = build_dashboard_svg(lc_data, cf_data, cc_data)

    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "coding-profile.svg")
    out_path = os.path.normpath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Coding Profile Dashboard written to: {out_path} ({len(svg_content)} bytes)")
    return True

if __name__ == "__main__":
    main()
