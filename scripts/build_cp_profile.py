#!/usr/bin/env python3
"""
CP Profile Dashboard Generator
Generates a retro terminal-style competitive programming SVG dashboard.
Fetches live data from Codeforces, LeetCode, CodeChef, and GitHub APIs.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────────────────────

GITHUB_USERNAME = "uvv-01"
CODEFORCES_USERNAME = None  # No CF account found
ATCODER_USERNAME = None     # No AtCoder account found
CODECHEF_USERNAME = "uvv_0000"
LEETCODE_USERNAME = "TUS8Mufpy3"
KATTIS_USERNAME = None      # No Kattis account found

# ─── API Helpers ─────────────────────────────────────────────────────────────

def fetch_json(url, timeout=15):
    """Fetch JSON from a URL with error handling."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CP-Profile-Generator/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  [WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def fetch_codeforces(handle):
    """Fetch Codeforces user data via official API."""
    print(f"  Fetching Codeforces data for {handle}...")
    data = fetch_json(f"https://codeforces.com/api/user.info?handles={handle}")
    if not data or data.get("status") != "OK" or not data.get("result"):
        return None
    user = data["result"][0]
    return {
        "rating": user.get("rating", 0),
        "max_rating": user.get("maxRating", 0),
        "rank": user.get("rank", "unrated"),
        "handle": user.get("handle", handle),
    }


def fetch_codeforces_solved(handle):
    """Count unique problems solved on Codeforces."""
    data = fetch_json(f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=10000")
    if not data or data.get("status") != "OK":
        return 0
    problems = set()
    for sub in data.get("result", []):
        if sub.get("verdict") == "OK":
            prob = sub.get("problem", {})
            key = (prob.get("contestId"), prob.get("index"))
            problems.add(key)
    return len(problems)


def fetch_codeforces_contests(handle):
    """Count rated contests on Codeforces."""
    data = fetch_json(f"https://codeforces.com/api/user.rating?handle={handle}")
    if not data or data.get("status") != "OK":
        return 0
    return len(data.get("result", []))


def fetch_github(username):
    """Fetch GitHub user data."""
    print(f"  Fetching GitHub data for {username}...")
    data = fetch_json(f"https://api.github.com/users/{username}")
    if not data:
        return None
    return {
        "repos": data.get("public_repos", 0),
        "followers": data.get("followers", 0),
        "following": data.get("following", 0),
    }


def fetch_github_contributions(username):
    """Fetch contribution count from contributions API."""
    data = fetch_json(f"https://github-contributions-api.jogruber.de/v4/{username}?y=last")
    if not data:
        return 0
    return sum(c.get("count", 0) for c in data.get("contributions", []))


def fetch_github_languages(username):
    """Fetch top languages from recent repos."""
    data = fetch_json(f"https://api.github.com/users/{username}/repos?per_page=30&sort=updated")
    if not data:
        return {}
    lang_counts = {}
    for repo in data:
        lang = repo.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    return dict(sorted(lang_counts.items(), key=lambda x: -x[1])[:5])


def fetch_github_stars(username):
    """Fetch total stars across repos."""
    data = fetch_json(f"https://api.github.com/users/{username}/repos?per_page=100")
    if not data:
        return 0
    return sum(r.get("stargazers_count", 0) for r in data)


def fetch_leetcode(username):
    """Fetch LeetCode stats from unofficial API."""
    print(f"  Fetching LeetCode data for {username}...")
    data = fetch_json(f"https://leetcode-stats-api.vercel.app/{username}")
    if not data or "totalSolved" not in data:
        return None
    return {
        "solved": data.get("totalSolved", 0),
        "easy": data.get("easySolved", 0),
        "medium": data.get("mediumSolved", 0),
        "hard": data.get("hardSolved", 0),
        "ranking": data.get("ranking", 0),
    }


def fetch_codechef(username):
    """Fetch CodeChef data by scraping profile page."""
    print(f"  Fetching CodeChef data for {username}...")
    try:
        import re
        req = urllib.request.Request(
            f"https://www.codechef.com/users/{username}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")

        # Extract from Drupal.settings JSON embedded in page
        rating = 0
        highest = 0
        contests = 0

        # Find date_versus_rating data
        match = re.search(r'"date_versus_rating":\{"all":(\[.*?])', html)
        if match:
            history = json.loads(match.group(1))
            contests = len(history)
            if history:
                ratings = [int(e.get("rating", 0)) for e in history]
                rating = ratings[-1] if ratings else 0
                highest = max(ratings) if ratings else 0

        # Extract problems solved from text
        solved = 0
        solved_match = re.search(r'Total Problems Solved:\s*(\d+)', html)
        if solved_match:
            solved = int(solved_match.group(1))

        return {
            "rating": rating,
            "max_rating": highest,
            "contests": contests,
            "solved": solved,
        }
    except Exception as e:
        print(f"  [WARN] CodeChef fetch failed: {e}", file=sys.stderr)
        return None


# ─── SVG Generation ──────────────────────────────────────────────────────────

# Color palette (dark terminal theme)
BG = "#0d1117"
BG_LIGHT = "#161b22"
BORDER = "#30363d"
GREEN = "#00ff41"
GREEN_DIM = "#00cc33"
AMBER = "#ffb000"
CYAN = "#00d4ff"
RED = "#ff4444"
WHITE = "#e6edf3"
GRAY = "#8b949e"
DIM = "#484f58"

# SVG dimensions
WIDTH = 900
PADDING = 24
InnerW = WIDTH - 2 * PADDING


def svg_header():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} __HEIGHT__" width="{WIDTH}">
<defs>
  <style>
    @font-face {{
      font-family: 'Mono';
      src: local('Courier New'), local('Consolas'), local('monospace');
    }}
    text {{ font-family: 'Courier New', Consolas, monospace; }}
  </style>
  <filter id="glow">
    <feGaussianBlur stdDeviation="1.5" result="blur"/>
    <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
'''


def text(x, y, content, color=GREEN, size=13, anchor="start", weight="normal", filter_attr=""):
    f = f' filter="url(#glow)"' if filter_attr else ""
    w = f' font-weight="{weight}"' if weight != "normal" else ""
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}"{w}{f}>{content}</text>\n'


def line(x1, y1, x2, y2, color=BORDER, width=1, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d}/>\n'


def rect(x, y, w, h, fill=BG_LIGHT, stroke=BORDER, rx=4, sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"/>\n'


def progress_bar(x, y, w, h, fraction, bar_color=GREEN, bg_color="#21262d"):
    filled = max(0, min(1, fraction)) * w
    return (
        rect(x, y, w, h, fill=bg_color, stroke="none", rx=2, sw=0)
        + f'<rect x="{x}" y="{y}" width="{filled}" height="{h}" fill="{bar_color}" rx="2"/>\n'
    )


class SVGBuilder:
    def __init__(self):
        self.elements = []
        self.y = 0

    def add(self, element):
        self.elements.append(element)

    def advance(self, dy):
        self.y += dy

    def get_y(self):
        return self.y

    def set_y(self, y):
        self.y = y

    def build(self):
        # Calculate total height
        max_y = self.y + PADDING
        header = svg_header().replace('__HEIGHT__', str(max_y))
        bg_rect = f'<rect width="{WIDTH}" height="{max_y}" fill="{BG}" rx="8"/>\n'
        return header + bg_rect + "".join(self.elements) + "</svg>"


def build_dashboard(data):
    """Build the main dashboard SVG."""
    svg = SVGBuilder()

    svg.set_y(PADDING)

    # ─── Title Bar ───
    y = svg.get_y()
    svg.add(rect(PADDING, y, InnerW, 36, fill="#161b22", stroke=BORDER, rx=6))
    # Title dots (decorative)
    svg.add(f'<circle cx="{PADDING + 14}" cy="{y + 18}" r="5" fill="#ff5f56"/>\n')
    svg.add(f'<circle cx="{PADDING + 30}" cy="{y + 18}" r="5" fill="#ffbd2e"/>\n')
    svg.add(f'<circle cx="{PADDING + 46}" cy="{y + 18}" r="5" fill="#27c93f"/>\n')
    svg.add(text(PADDING + 60, y + 23, "uvv-01@cp-dashboard ~ $ ./profile.sh", GREEN_DIM, 12))
    svg.add(text(PADDING + InnerW - 8, y + 23, "ONLINE", GREEN, 11, anchor="end", weight="bold"))
    svg.advance(50)

    # ─── Separator ───
    y = svg.get_y()
    svg.add(line(PADDING, y, PADDING + InnerW, y, BORDER))
    svg.advance(12)

    # ─── Two-column layout ───
    col_split = 280
    left_w = col_split - PADDING
    right_x = col_split + 12
    right_w = PADDING + InnerW - right_x

    top_y = svg.get_y()

    # ─── LEFT COLUMN: Profile ───
    ly = top_y
    svg.add(text(PADDING, ly + 16, "PROFILE", AMBER, 11, weight="bold"))
    ly += 28

    # Avatar placeholder (terminal-style)
    avatar_size = 80
    svg.add(rect(PADDING, ly, avatar_size, avatar_size, fill="#0d1117", stroke=GREEN_DIM, rx=4, sw=2))
    svg.add(text(PADDING + avatar_size // 2, ly + avatar_size // 2 - 8, "[", GRAY, 28, anchor="middle"))
    svg.add(text(PADDING + avatar_size // 2, ly + avatar_size // 2 + 18, "IMG", GRAY, 12, anchor="middle"))
    svg.add(text(PADDING + avatar_size // 2, ly + avatar_size // 2 + 32, "]", GRAY, 28, anchor="middle"))
    ly += avatar_size + 14

    # Profile info
    svg.add(text(PADDING, ly + 14, "USER:", GRAY, 11))
    svg.add(text(PADDING + 52, ly + 14, "yuvraj", WHITE, 11, weight="bold"))
    ly += 20
    svg.add(text(PADDING, ly + 14, "STATUS:", GRAY, 11))
    svg.add(text(PADDING + 62, ly + 14, "CODING", GREEN, 11, weight="bold"))
    ly += 20
    svg.add(text(PADDING, ly + 14, "FOCUS:", GRAY, 11))
    svg.add(text(PADDING + 54, ly + 14, "CP / OSS / Backend", CYAN, 11))
    ly += 20
    svg.add(text(PADDING, ly + 14, "LINKS:", GRAY, 11))
    ly += 20

    # Profile links
    links = [
        ("GITHUB", f"https://github.com/{GITHUB_USERNAME}", GREEN),
        ("LINKEDIN", "https://linkedin.com/in/yuvraj-singh-b70670356", CYAN),
        ("EMAIL", "mailto:yuvrajsinghdnb2006@gmail.com", AMBER),
    ]
    for label, url, color in links:
        svg.add(text(PADDING + 8, ly + 12, f"  > {label}", color, 10))
        ly += 16

    ly += 8

    # ─── RIGHT COLUMN: Contest Database ───
    ry = top_y
    svg.add(text(right_x, ry + 16, "CONTEST DATABASE", AMBER, 11, weight="bold"))
    ry += 30

    # Platform cards
    platforms = []

    if data.get("codeforces"):
        cf = data["codeforces"]
        platforms.append({
            "name": "CODEFORCES",
            "color": "#445f9d",
            "fields": [
                ("RATING", str(cf["rating"]), GREEN if cf["rating"] >= 1400 else WHITE),
                ("MAX", str(cf["max_rating"]), AMBER),
                ("RANK", cf["rank"].upper(), CYAN),
                ("SOLVED", str(data.get("cf_solved", "?")), WHITE),
                ("CONTESTS", str(data.get("cf_contests", "?")), WHITE),
            ],
        })

    if data.get("codechef"):
        cc = data["codechef"]
        platforms.append({
            "name": "CODECHEF",
            "color": "#5B4638",
            "fields": [
                ("RATING", str(cc["rating"]), GREEN if cc["rating"] >= 1400 else WHITE),
                ("MAX", str(cc["max_rating"]), AMBER),
                ("CONTESTS", str(cc.get("contests", "?")), WHITE),
            ],
        })

    if data.get("leetcode"):
        lc = data["leetcode"]
        platforms.append({
            "name": "LEETCODE",
            "color": "#FFA116",
            "fields": [
                ("SOLVED", str(lc["solved"]), GREEN),
                ("EASY", str(lc["easy"]), GREEN_DIM),
                ("MED", str(lc["medium"]), AMBER),
                ("HARD", str(lc["hard"]), RED),
                ("RANK", f"#{lc['ranking']:,}" if lc["ranking"] else "—", GRAY),
            ],
        })

    for plat in platforms:
        # Platform header
        svg.add(rect(right_x, ry, right_w, 20, fill=plat["color"], stroke="none", rx=3, sw=0))
        svg.add(text(right_x + 8, ry + 14, plat["name"], WHITE, 10, weight="bold"))
        ry += 26

        # Fields
        for label, value, color in plat["fields"]:
            svg.add(text(right_x + 4, ry + 12, label, GRAY, 10))
            svg.add(text(right_x + 72, ry + 12, value, color, 10, weight="bold"))
            ry += 16

        ry += 8

    # ─── Separator ───
    sep_y = max(ly, ry) + 4
    svg.add(line(PADDING, sep_y, PADDING + InnerW, sep_y, BORDER))
    svg.set_y(sep_y + 12)

    # ─── GitHub System Section ───
    y = svg.get_y()
    svg.add(text(PADDING, y + 16, "GITHUB SYSTEM", AMBER, 11, weight="bold"))
    y += 30

    gh = data.get("github", {})
    gh_stats = [
        ("REPOS", str(gh.get("repos", 0))),
        ("STARS", str(data.get("gh_stars", 0))),
        ("FOLLOWERS", str(gh.get("followers", 0))),
        ("CONTRIBUTIONS", f"{data.get('gh_contributions', 0)} (1yr)"),
    ]

    # Stats boxes
    box_w = (InnerW - 3 * 8) // 4
    for i, (label, value) in enumerate(gh_stats):
        bx = PADDING + i * (box_w + 8)
        svg.add(rect(bx, y, box_w, 44, fill=BG_LIGHT, stroke=BORDER, rx=4))
        svg.add(text(bx + box_w // 2, y + 18, label, GRAY, 9, anchor="middle"))
        svg.add(text(bx + box_w // 2, y + 36, value, GREEN, 14, anchor="middle", weight="bold"))
    y += 56

    # Languages
    langs = data.get("gh_languages", {})
    if langs:
        svg.add(text(PADDING, y + 12, "LANGUAGES:", GRAY, 10))
        lx = PADDING + 80
        lang_colors = {
            "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6",
            "Java": "#b07219", "C++": "#f34b7d", "HTML": "#e34c26",
            "CSS": "#563d7c", "Shell": "#89e051", "PHP": "#4F5D95",
        }
        for lang, count in list(langs.items())[:5]:
            color = lang_colors.get(lang, GRAY)
            svg.add(f'<circle cx="{lx}" cy="{y + 8}" r="4" fill="{color}"/>\n')
            svg.add(text(lx + 8, y + 12, lang, WHITE, 10))
            lx += len(lang) * 7 + 20
        y += 24

    # ─── Contribution Snake ───
    svg.add(line(PADDING, y, PADDING + InnerW, y, BORDER))
    y += 12
    svg.add(text(PADDING, y + 14, "CONTRIBUTION GRID", AMBER, 11, weight="bold"))
    y += 22

    # Snake placeholder - using a text-based representation
    snake_url_dark = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_USERNAME}/output/github-contribution-grid-snake-dark.svg"
    snake_url_light = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_USERNAME}/output/github-contribution-grid-snake.svg"
    svg.add(f'<foreignObject x="{PADDING}" y="{y}" width="{InnerW}" height="160">\n')
    svg.add(f'  <div xmlns="http://www.w3.org/1999/xhtml" style="width:100%;overflow:hidden;">\n')
    svg.add(f'    <picture>\n')
    svg.add(f'      <source media="(prefers-color-scheme: dark)" srcset="{snake_url_dark}"/>\n')
    svg.add(f'      <source media="(prefers-color-scheme: light)" srcset="{snake_url_light}"/>\n')
    svg.add(f'      <img src="{snake_url_light}" style="width:100%;max-width:{InnerW}px;" alt="Contribution Snake"/>\n')
    svg.add(f'    </picture>\n')
    svg.add(f'  </div>\n')
    svg.add(f'</foreignObject>\n')
    y += 165

    # ─── Footer ───
    svg.add(line(PADDING, y, PADDING + InnerW, y, BORDER))
    y += 14
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    svg.add(text(PADDING, y + 12, f"LAST SYNC: {now}", DIM, 9))
    svg.add(text(PADDING + InnerW, y + 12, "SYSTEM READY", GREEN, 9, anchor="end"))
    y += 20

    # ─── Minecraft Footer ───
    y += 8
    svg.add(rect(PADDING, y, InnerW, 32, fill=BG_LIGHT, stroke=BORDER, rx=4))
    svg.add(text(PADDING + InnerW // 2, y + 21,
                 "Mining algorithms, crafting projects, one commit at a time.",
                 GRAY, 10, anchor="middle"))
    y += 40

    svg.set_y(y)
    return svg


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("CP Profile Dashboard Generator")
    print("=" * 40)

    data = {}

    # Fetch all data with graceful degradation
    if CODEFORCES_USERNAME:
        data["codeforces"] = fetch_codeforces(CODEFORCES_USERNAME)
        if data["codeforces"]:
            data["cf_solved"] = fetch_codeforces_solved(CODEFORCES_USERNAME)
            time.sleep(2.5)  # Rate limit
            data["cf_contests"] = fetch_codeforces_contests(CODEFORCES_USERNAME)
    else:
        print("  [INFO] No Codeforces username configured, skipping.")

    if CODECHEF_USERNAME:
        data["codechef"] = fetch_codechef(CODECHEF_USERNAME)
    else:
        print("  [INFO] No CodeChef username configured, skipping.")

    if LEETCODE_USERNAME:
        data["leetcode"] = fetch_leetcode(LEETCODE_USERNAME)
    else:
        print("  [INFO] No LeetCode username configured, skipping.")

    # GitHub data
    data["github"] = fetch_github(GITHUB_USERNAME)
    data["gh_contributions"] = fetch_github_contributions(GITHUB_USERNAME)
    data["gh_languages"] = fetch_github_languages(GITHUB_USERNAME)
    data["gh_stars"] = fetch_github_stars(GITHUB_USERNAME)

    print("\nGenerating SVG...")
    svg_builder = build_dashboard(data)
    svg_content = svg_builder.build()

    # Write output
    output_path = os.path.join(os.path.dirname(__file__), "..", "assets", "cp-profile.svg")
    output_path = os.path.normpath(output_path)

    # Check if content changed
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            old_content = f.read()
        if old_content == svg_content:
            print("No changes detected. Skipping commit.")
            return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"SVG written to {output_path}")
    print(f"File size: {len(svg_content)} bytes")
    return True


if __name__ == "__main__":
    changed = main()
    sys.exit(0 if changed else 1)
