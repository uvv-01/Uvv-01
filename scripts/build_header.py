#!/usr/bin/env python3
"""
Header SVG Generator
Refined professional header preserving the original double-box identity:
╔══════════════════════════════════════════════════════╗
║             Y U V R A J   S I N G H                  ║
║         Competitive Programmer · Developer           ║
╚══════════════════════════════════════════════════════╝
Uses realistic lighting, subtle depth, restrained highlights, and clean typography.
"""

import os

def generate_header_svg():
    width = 960
    height = 148

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <!-- Subtle linear gradient for deep matte slate background -->
    <linearGradient id="header-bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#121720"/>
      <stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>

    <!-- Subtle bevel top highlight -->
    <linearGradient id="bevel-highlight" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#30363d" stop-opacity="0.3"/>
      <stop offset="50%" stop-color="#484f58" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#30363d" stop-opacity="0.3"/>
    </linearGradient>

    <linearGradient id="line-divider" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#21262d" stop-opacity="0"/>
      <stop offset="30%" stop-color="#30363d" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#484f58" stop-opacity="1"/>
      <stop offset="70%" stop-color="#30363d" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#21262d" stop-opacity="0"/>
    </linearGradient>

    <!-- Controlled, subtle depth shadow -->
    <filter id="subtle-shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>

  <style>
    .name-title {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'SF Pro Display', Roboto, 'Inter', sans-serif;
      font-size: 26px;
      font-weight: 700;
      letter-spacing: 12px;
      fill: #f0f6fc;
    }}
    .sub-title {{
      font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', monospace;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: 3px;
      fill: #8b949e;
    }}
    .box-char {{
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 13px;
      fill: #484f58;
    }}
  </style>

  <!-- Panel Base with Controlled Shadow -->
  <rect x="8" y="8" width="{width - 16}" height="{height - 16}" rx="8" fill="url(#header-bg)" filter="url(#subtle-shadow)"/>
  <rect x="8" y="8" width="{width - 16}" height="{height - 16}" rx="8" fill="none" stroke="#21262d" stroke-width="1"/>

  <!-- Top Bevel Highlight Edge -->
  <line x1="24" y1="9" x2="{width - 24}" y2="9" stroke="url(#bevel-highlight)" stroke-width="1"/>

  <!-- Architectural Double-Frame (Tribute to original ╔══╗ terminal box) -->
  <!-- Outer Box -->
  <rect x="22" y="20" width="{width - 44}" height="{height - 40}" rx="4" fill="none" stroke="#30363d" stroke-width="1.25"/>
  <!-- Inner Box -->
  <rect x="27" y="25" width="{width - 54}" height="{height - 50}" rx="2" fill="none" stroke="#21262d" stroke-width="1"/>

  <!-- Corner Double-Line Node Details (╔ ╗ ╚ ╝) -->
  <!-- Top Left -->
  <line x1="22" y1="20" x2="38" y2="20" stroke="#8b949e" stroke-width="1.5"/>
  <line x1="22" y1="20" x2="22" y2="36" stroke="#8b949e" stroke-width="1.5"/>
  <!-- Top Right -->
  <line x1="{width - 38}" y1="20" x2="{width - 22}" y2="20" stroke="#8b949e" stroke-width="1.5"/>
  <line x1="{width - 22}" y1="20" x2="{width - 22}" y2="36" stroke="#8b949e" stroke-width="1.5"/>
  <!-- Bottom Left -->
  <line x1="22" y1="{height - 20}" x2="38" y2="{height - 20}" stroke="#8b949e" stroke-width="1.5"/>
  <line x1="22" y1="{height - 36}" x2="22" y2="{height - 20}" stroke="#8b949e" stroke-width="1.5"/>
  <!-- Bottom Right -->
  <line x1="{width - 38}" y1="{height - 20}" x2="{width - 22}" y2="{height - 20}" stroke="#8b949e" stroke-width="1.5"/>
  <line x1="{width - 22}" y1="{height - 36}" x2="{width - 22}" y2="{height - 20}" stroke="#8b949e" stroke-width="1.5"/>

  <!-- Center Text Group -->
  <!-- Main Name -->
  <text x="480" y="68" text-anchor="middle" class="name-title">Y U V R A J   S I N G H</text>

  <!-- Refined Center Divider Line -->
  <line x1="320" y1="88" x2="640" y2="88" stroke="url(#line-divider)" stroke-width="1"/>
  <polygon points="480,86 482,88 480,90 478,88" fill="#484f58"/>

  <!-- Subtitle matching original identity -->
  <text x="480" y="112" text-anchor="middle" class="sub-title">Competitive Programmer · Developer</text>
</svg>'''

    out_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'header.svg')
    out_path = os.path.normpath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Header refined at: {out_path} ({len(svg)} bytes)")

if __name__ == '__main__':
    generate_header_svg()
