#!/usr/bin/env python3
"""
Gaming Coding Profile Dashboard Generator
Generates a realistic, professional competitive player-statistics screen for LeetCode, Codeforces, and CodeChef.
Uses restrained visual effects, believable panel depth, fine borders, and authentic data.
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

# Authentic cached fallbacks
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
    "codeforces": None
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
        print(f"  [Notice] API notice for {url}: {e}", file=sys.stderr)
        return None

def get_leetcode_data(username):
    if not username:
        return None
    print(f"Fetching LeetCode data for {username}...")
    res = dict(FALLBACK_DATA["leetcode"])
    res["handle"] = username

    stats = fetch_json(f"https://leetcode-stats-api.vercel.app/{username}")
    if stats and "totalSolved" in stats:
        res["solved"] = stats.get("totalSolved", res["solved"])
        res["easy"] = stats.get("easySolved", res["easy"])
        res["medium"] = stats.get("mediumSolved", res["medium"])
        res["hard"] = stats.get("hardSolved", res["hard"])

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
    if not history or len(history) < 2:
        return ""

    min_val = min(history)
    max_val = max(history)
    val_range = max_val - min_val if max_val != min_val else 1

    padding_x = 8
    padding_y = 10
    draw_w = w - 2 * padding_x
    draw_h = h - 2 * padding_y

    pts = []
    n = len(history)
    for i, val in enumerate(history):
        px = x + padding_x + (i / (n - 1)) * draw_w
        py = y + h - padding_y - ((val - min_val) / val_range) * draw_h
        pts.append((px, py))

    d_path = f"M {pts[0][0]:.1f} {pts[0][1]:.1f}"
    for px, py in pts[1:]:
        d_path += f" L {px:.1f} {py:.1f}"

    d_fill = f"{d_path} L {pts[-1][0]:.1f} {y + h - 1} L {pts[0][0]:.1f} {y + h - 1} Z"

    svg_parts = []
    # Subtle horizontal grid line in well
    svg_parts.append(f'<line x1="{x}" y1="{y + h // 2}" x2="{x + w}" y2="{y + h // 2}" stroke="#21262d" stroke-width="1" stroke-dasharray="2 3"/>')
    svg_parts.append(f'<line x1="{x}" y1="{y + h - 1}" x2="{x + w}" y2="{y + h - 1}" stroke="#21262d" stroke-width="1"/>')

    # Restrained gradient fill (under 12% opacity)
    svg_parts.append(f'<path d="{d_fill}" fill="url(#{grad_id})" opacity="0.12"/>')
    # Clean, crisp stroke line
    svg_parts.append(f'<path d="{d_path}" fill="none" stroke="{line_color}" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"/>')

    # Data points
    for i, (px, py) in enumerate(pts):
        if i == n - 1 or history[i] == max_val:
            svg_parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="2.5" fill="#f0f6fc" stroke="{line_color}" stroke-width="1.25"/>')
        else:
            svg_parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.5" fill="{line_color}" opacity="0.8"/>')

    # Labels for min and max
    svg_parts.append(f'<text x="{x + 6}" y="{y + 11}" fill="#6e7681" font-size="8.5" font-family="Consolas, monospace">PEAK {max_val}</text>')
    svg_parts.append(f'<text x="{x + w - 6}" y="{y + h - 5}" text-anchor="end" fill="#6e7681" font-size="8.5" font-family="Consolas, monospace">MIN {min_val}</text>')

    return "\n".join(svg_parts)

def build_dashboard_svg(lc_data, cf_data, cc_data):
    W = 960
    H = 416

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="100%" height="{H}">
  <defs>
    <!-- Dark matte slate panel gradients -->
    <linearGradient id="main-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#121720"/>
      <stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>

    <linearGradient id="card-panel-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#181e28"/>
      <stop offset="100%" stop-color="#121720"/>
    </linearGradient>

    <!-- Restrained graph fills -->
    <linearGradient id="lc-fill" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#f59e0b" stop-opacity="0.0"/>
    </linearGradient>

    <linearGradient id="cf-fill" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#94a3b8" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#94a3b8" stop-opacity="0.0"/>
    </linearGradient>

    <linearGradient id="cc-fill" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#d97706" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#d97706" stop-opacity="0.0"/>
    </linearGradient>

    <!-- Controlled physical drop shadow -->
    <filter id="panel-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <style>
    .header-label {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 2px;
      fill: #8b949e;
    }}
    .platform-name {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', sans-serif;
      font-size: 15px;
      font-weight: 700;
      letter-spacing: 1px;
      fill: #f0f6fc;
    }}
    .stat-label {{
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 9px;
      font-weight: 600;
      letter-spacing: 1.5px;
      fill: #8b949e;
    }}
    .rating-val {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', sans-serif;
      font-size: 32px;
      font-weight: 700;
      fill: #f0f6fc;
    }}
    .meta-val {{
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 11px;
      fill: #8b949e;
    }}
    .meta-highlight {{
      font-weight: 700;
      fill: #f0f6fc;
    }}
    .card-shell {{
      transition: transform 0.2s ease, stroke 0.2s ease;
    }}
    .card-shell:hover {{
      transform: translateY(-2px);
    }}
  </style>

  <!-- Container Base -->
  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="8" fill="url(#main-bg)" filter="url(#panel-shadow)"/>
  <rect x="8" y="8" width="{W - 16}" height="{H - 16}" rx="8" fill="none" stroke="#21262d" stroke-width="1"/>

  <!-- Top Bevel Highlight Edge -->
  <line x1="20" y1="9" x2="{W - 20}" y2="9" stroke="#30363d" stroke-width="1" stroke-opacity="0.6"/>

  <!-- Header Row -->
  <g transform="translate(24, 28)">
    <text x="0" y="0" class="header-label">COMPETITIVE STATISTICS</text>
    <text x="{W - 48}" y="0" text-anchor="end" class="header-label">VERIFIED TELEMETRY</text>
  </g>
  <line x1="24" y1="38" x2="{W - 24}" y2="38" stroke="#21262d" stroke-width="1"/>
'''

    card_w = 288
    card_h = 352
    gap = 18
    cards_x = [24, 24 + card_w + gap, 24 + 2 * (card_w + gap)]
    card_y = 48

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
        x1 + 14, card_y + 138, card_w - 28, 86,
        "#f59e0b", "lc-fill"
    )

    svg += f'''
  <!-- CARD 1: LEETCODE -->
  <g class="card-shell">
    <rect x="{x1}" y="{card_y}" width="{card_w}" height="{card_h}" rx="6" fill="url(#card-panel-bg)" stroke="#30363d" stroke-width="1"/>
    <!-- Controlled top accent line -->
    <line x1="{x1+6}" y1="{card_y}" x2="{x1+card_w-6}" y2="{card_y}" stroke="#f59e0b" stroke-width="2"/>

    <!-- Header & User -->
    <text x="{x1+16}" y="{card_y+26}" class="platform-name">LEETCODE</text>
    <text x="{x1+card_w-16}" y="{card_y+26}" text-anchor="end" class="meta-val">id: {lc_data.get('handle', 'TUS8Mufpy3')}</text>

    <!-- Rating Section -->
    <rect x="{x1+14}" y="{card_y+40}" width="{card_w-28}" height="86" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    <text x="{x1+26}" y="{card_y+58}" class="stat-label">CURRENT RATING</text>
    <text x="{x1+26}" y="{card_y+94}" class="rating-val">{lc_rating}</text>
    
    <text x="{x1+card_w-26}" y="{card_y+76}" text-anchor="end" class="meta-val">Peak: <tspan class="meta-highlight">{lc_peak}</tspan></text>
    <text x="{x1+card_w-26}" y="{card_y+96}" text-anchor="end" class="meta-val">Contests: <tspan class="meta-highlight">{lc_contests}</tspan></text>

    <!-- Rating History Chart -->
    <rect x="{x1+14}" y="{card_y+138}" width="{card_w-28}" height="86" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    {sparkline_lc}

    <!-- Solved Breakdown -->
    <g transform="translate({x1+14}, {card_y+236})">
      <rect x="0" y="0" width="{card_w-28}" height="102" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
      <text x="12" y="20" class="stat-label">PROBLEMS SOLVED ({lc_solved})</text>
      
      <!-- Progress Bar Breakdown -->
      <g transform="translate(12, 32)">
        <text x="0" y="14" fill="#238636" font-size="10" font-family="Consolas, monospace" font-weight="600">EASY</text>
        <text x="45" y="14" class="meta-highlight" font-size="10" font-family="Consolas, monospace">{lc_easy}</text>
        <rect x="80" y="6" width="{card_w-136}" height="8" rx="2" fill="#21262d"/>
        <rect x="80" y="6" width="{int((card_w-136) * (lc_easy/lc_solved)) if lc_solved else 0}" height="8" rx="2" fill="#238636"/>

        <text x="0" y="34" fill="#d29922" font-size="10" font-family="Consolas, monospace" font-weight="600">MED</text>
        <text x="45" y="34" class="meta-highlight" font-size="10" font-family="Consolas, monospace">{lc_med}</text>
        <rect x="80" y="26" width="{card_w-136}" height="8" rx="2" fill="#21262d"/>
        <rect x="80" y="26" width="{int((card_w-136) * (lc_med/lc_solved)) if lc_solved else 0}" height="8" rx="2" fill="#d29922"/>

        <text x="0" y="54" fill="#da3633" font-size="10" font-family="Consolas, monospace" font-weight="600">HARD</text>
        <text x="45" y="54" class="meta-highlight" font-size="10" font-family="Consolas, monospace">{lc_hard}</text>
        <rect x="80" y="46" width="{card_w-136}" height="8" rx="2" fill="#21262d"/>
        <rect x="80" y="46" width="{int((card_w-136) * (lc_hard/lc_solved)) if lc_solved else 0}" height="8" rx="2" fill="#da3633"/>
      </g>
    </g>
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
            x2 + 14, card_y + 138, card_w - 28, 86,
            "#94a3b8", "cf-fill"
        )
        cf_bottom = f'''
        <g transform="translate({x2+14}, {card_y+236})">
          <rect x="0" y="0" width="{card_w-28}" height="102" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
          <text x="14" y="22" class="stat-label">COMPETITIVE METRICS</text>
          <text x="14" y="46" class="meta-val">Rank: <tspan class="meta-highlight">{cf_rank}</tspan></text>
          <text x="14" y="68" class="meta-val">Max Rating: <tspan class="meta-highlight">{cf_peak}</tspan></text>
          <text x="14" y="90" class="meta-val">Rated Contests: <tspan class="meta-highlight">{cf_contests}</tspan></text>
        </g>
        '''
    else:
        cf_rating = "—"
        sparkline_cf = f'''
        <g opacity="0.6">
          <line x1="{x2+24}" y1="{card_y+181}" x2="{x2+card_w-24}" y2="{card_y+181}" stroke="#21262d" stroke-width="1" stroke-dasharray="3 3"/>
          <text x="{x2+card_w//2}" y="{card_y+176}" text-anchor="middle" fill="#8b949e" font-size="11" font-family="-apple-system, sans-serif" font-weight="600">Account Unlinked</text>
          <text x="{x2+card_w//2}" y="{card_y+194}" text-anchor="middle" fill="#6e7681" font-size="9" font-family="Consolas, monospace">Set handle in config to sync graph</text>
        </g>
        '''
        cf_bottom = f'''
        <g transform="translate({x2+14}, {card_y+236})">
          <rect x="0" y="0" width="{card_w-28}" height="102" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
          <text x="14" y="22" class="stat-label">STATUS</text>
          <text x="14" y="46" class="meta-val">Status: <tspan fill="#d29922" font-weight="600">Pending Setup</tspan></text>
          <text x="14" y="66" fill="#8b949e" font-size="10" font-family="-apple-system, sans-serif">Provide Codeforces handle to</text>
          <text x="14" y="82" fill="#8b949e" font-size="10" font-family="-apple-system, sans-serif">display live competitive statistics.</text>
        </g>
        '''

    svg += f'''
  <!-- CARD 2: CODEFORCES -->
  <g class="card-shell">
    <rect x="{x2}" y="{card_y}" width="{card_w}" height="{card_h}" rx="6" fill="url(#card-panel-bg)" stroke="#30363d" stroke-width="1"/>
    <line x1="{x2+6}" y1="{card_y}" x2="{x2+card_w-6}" y2="{card_y}" stroke="#64748b" stroke-width="2"/>

    <!-- Header & User -->
    <text x="{x2+16}" y="{card_y+26}" class="platform-name">CODEFORCES</text>
    <text x="{x2+card_w-16}" y="{card_y+26}" text-anchor="end" class="meta-val">{'id: ' + cf_data['handle'] if cf_data else '[unlinked]'}</text>

    <!-- Rating Section -->
    <rect x="{x2+14}" y="{card_y+40}" width="{card_w-28}" height="86" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    <text x="{x2+26}" y="{card_y+58}" class="stat-label">CURRENT RATING</text>
    <text x="{x2+26}" y="{card_y+94}" class="rating-val" fill="#8b949e">{cf_rating}</text>
    
    <text x="{x2+card_w-26}" y="{card_y+76}" text-anchor="end" class="meta-val">Status: <tspan class="meta-highlight">{'Linked' if cf_data else 'Unlinked'}</tspan></text>
    <text x="{x2+card_w-26}" y="{card_y+96}" text-anchor="end" class="meta-val">Rank: <tspan class="meta-highlight">{'Active' if cf_data else 'None'}</tspan></text>

    <!-- Rating History Chart / Empty Well -->
    <rect x="{x2+14}" y="{card_y+138}" width="{card_w-28}" height="86" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    {sparkline_cf}

    <!-- Bottom Stat Block -->
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
        x3 + 14, card_y + 138, card_w - 28, 86,
        "#d97706", "cc-fill"
    )

    svg += f'''
  <!-- CARD 3: CODECHEF -->
  <g class="card-shell">
    <rect x="{x3}" y="{card_y}" width="{card_w}" height="{card_h}" rx="6" fill="url(#card-panel-bg)" stroke="#30363d" stroke-width="1"/>
    <line x1="{x3+6}" y1="{card_y}" x2="{x3+card_w-6}" y2="{card_y}" stroke="#d97706" stroke-width="2"/>

    <!-- Header & User -->
    <text x="{x3+16}" y="{card_y+26}" class="platform-name">CODECHEF</text>
    <text x="{x3+card_w-16}" y="{card_y+26}" text-anchor="end" class="meta-val">id: {cc_data.get('handle', 'uvv_0000')}</text>

    <!-- Rating Section -->
    <rect x="{x3+14}" y="{card_y+40}" width="{card_w-28}" height="86" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    <text x="{x3+26}" y="{card_y+58}" class="stat-label">CURRENT RATING</text>
    <text x="{x3+26}" y="{card_y+94}" class="rating-val">{cc_rating}</text>
    
    <text x="{x3+card_w-26}" y="{card_y+76}" text-anchor="end" class="meta-val">Peak: <tspan class="meta-highlight">{cc_peak}</tspan></text>
    <text x="{x3+card_w-26}" y="{card_y+96}" text-anchor="end" class="meta-val">Contests: <tspan class="meta-highlight">{cc_contests}</tspan></text>

    <!-- Rating History Chart -->
    <rect x="{x3+14}" y="{card_y+138}" width="{card_w-28}" height="86" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
    {sparkline_cc}

    <!-- Bottom Stat Block -->
    <g transform="translate({x3+14}, {card_y+236})">
      <rect x="0" y="0" width="{card_w-28}" height="102" rx="4" fill="#0d1117" stroke="#21262d" stroke-width="1"/>
      <text x="14" y="22" class="stat-label">STARTERS TELEMETRY</text>
      <text x="14" y="46" class="meta-val">Tier: <tspan class="meta-highlight">{cc_div}</tspan></text>
      <text x="14" y="68" class="meta-val">Star Rating: <tspan class="meta-highlight">{cc_stars}</tspan></text>
      <text x="14" y="90" class="meta-val">Logged Contests: <tspan class="meta-highlight">{cc_contests} Contests</tspan></text>
    </g>
  </g>
</svg>'''

    return svg

def main():
    print("Generating Refined Competitive Gaming Coding Profile...")
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
