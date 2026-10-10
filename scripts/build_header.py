#!/usr/bin/env python3
"""
Header SVG Generator
Generates a gaming HUD name banner for Yuvraj Singh.
"""

import os

def generate_header_svg():
    width = 960
    height = 180

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#070a13"/>
      <stop offset="50%" stop-color="#0b1220"/>
      <stop offset="100%" stop-color="#080c16"/>
    </linearGradient>
    <linearGradient id="text-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffffff"/>
      <stop offset="40%" stop-color="#00f0ff"/>
      <stop offset="70%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
    <linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#00f0ff" stop-opacity="0"/>
      <stop offset="30%" stop-color="#00f0ff" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="#38bdf8" stop-opacity="1"/>
      <stop offset="70%" stop-color="#c084fc" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#c084fc" stop-opacity="0"/>
    </linearGradient>
    <filter id="neon-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur1"/>
      <feGaussianBlur stdDeviation="8" result="blur2"/>
      <feMerge>
        <feMergeNode in="blur2"/>
        <feMergeNode in="blur1"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="soft-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <pattern id="grid-pattern" width="24" height="24" patternUnits="userSpaceOnUse">
      <path d="M 24 0 L 0 0 0 24" fill="none" stroke="#1e293b" stroke-width="0.75" stroke-opacity="0.4"/>
    </pattern>
  </defs>

  <style>
    @keyframes pulse-glow {{
      0%, 100% {{ opacity: 0.8; filter: drop-shadow(0 0 6px #00f0ff); }}
      50% {{ opacity: 1; filter: drop-shadow(0 0 14px #00f0ff); }}
    }}
    @keyframes scanline {{
      0% {{ transform: translateY(0); }}
      100% {{ transform: translateY(180px); }}
    }}
    .glow-title {{
      font-family: 'Rajdhani', 'Orbitron', 'Montserrat', 'Segoe UI', system-ui, sans-serif;
      font-weight: 800;
      letter-spacing: 14px;
      animation: pulse-glow 4s ease-in-out infinite;
    }}
    .hud-label {{
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 10px;
      letter-spacing: 2px;
      fill: #64748b;
    }}
    .hud-val {{
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 10px;
      letter-spacing: 2px;
      font-weight: 600;
      fill: #00f0ff;
    }}
  </style>

  <!-- Background Base -->
  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="url(#bg-grad)"/>
  <rect x="0" y="0" width="{width}" height="{height}" rx="12" fill="url(#grid-pattern)"/>

  <!-- Radial Glow Behind Name -->
  <circle cx="480" cy="90" r="140" fill="#00f0ff" opacity="0.07" filter="url(#neon-glow)"/>

  <!-- Outer HUD Frame Chamfered Border -->
  <path d="M 24 16 L 80 16 M {width - 80} 16 L {width - 24} 16 M {width - 16} 24 L {width - 16} 60 M {width - 16} {height - 60} L {width - 16} {height - 24} M {width - 24} {height - 16} L {width - 80} {height - 16} M 80 {height - 16} L 24 {height - 16} M 16 {height - 24} L 16 {height - 60} M 16 60 L 16 24" 
        stroke="#00f0ff" stroke-width="2" stroke-linecap="round" fill="none" opacity="0.8"/>

  <!-- Inner HUD Border Lines -->
  <rect x="20" y="20" width="{width - 40}" height="{height - 40}" rx="6" fill="none" stroke="#1e293b" stroke-width="1" stroke-dasharray="8 6"/>

  <!-- Corner Brackets -->
  <path d="M 22 36 L 22 22 L 36 22" stroke="#00f0ff" stroke-width="2.5" fill="none"/>
  <path d="M {width - 36} 22 L {width - 22} 22 L {width - 22} 36" stroke="#00f0ff" stroke-width="2.5" fill="none"/>
  <path d="M 22 {height - 36} L 22 {height - 22} L 36 {height - 22}" stroke="#00f0ff" stroke-width="2.5" fill="none"/>
  <path d="M {width - 36} {height - 22} L {width - 22} {height - 22} L {width - 22} {height - 36}" stroke="#00f0ff" stroke-width="2.5" fill="none"/>

  <!-- HUD Top Header Info -->
  <g transform="translate(36, 38)">
    <circle cx="4" cy="0" r="3" fill="#22c55e"/>
    <text x="14" y="3" class="hud-label">STATUS: <tspan class="hud-val">ONLINE</tspan></text>
    <text x="150" y="3" class="hud-label">SYS.ID: <tspan class="hud-val">UVV-01</tspan></text>
  </g>
  <g transform="translate({width - 240}, 38)">
    <text x="0" y="3" class="hud-label">MODE: <tspan class="hud-val">COMPETITIVE</tspan></text>
    <text x="130" y="3" class="hud-label">LVL: <tspan class="hud-val">99</tspan></text>
  </g>

  <!-- Crosshairs -->
  <g opacity="0.6">
    <line x1="480" y1="24" x2="480" y2="34" stroke="#00f0ff" stroke-width="1"/>
    <line x1="475" y1="29" x2="485" y2="29" stroke="#00f0ff" stroke-width="1"/>
  </g>

  <!-- Name Header -->
  <g transform="translate(480, 102)" text-anchor="middle">
    <!-- Glow Under-layer -->
    <text x="0" y="0" font-size="44" fill="#00f0ff" class="glow-title" opacity="0.5" filter="url(#neon-glow)">YUVRAJ SINGH</text>
    <!-- Sharp Foreground Text -->
    <text x="0" y="0" font-size="44" fill="url(#text-grad)" class="glow-title" filter="url(#soft-glow)">YUVRAJ SINGH</text>
  </g>

  <!-- Cyber Subtitle / Underline -->
  <line x1="180" y1="126" x2="{width - 180}" y2="126" stroke="url(#line-grad)" stroke-width="2"/>
  
  <!-- Reticle Diamonds on Line -->
  <polygon points="480,123 483,126 480,129 477,126" fill="#00f0ff"/>
  <polygon points="280,124 282,126 280,128 278,126" fill="#00f0ff" opacity="0.6"/>
  <polygon points="680,124 682,126 680,128 678,126" fill="#c084fc" opacity="0.6"/>

  <!-- Subtitle Tagline -->
  <text x="480" y="148" text-anchor="middle" font-family="'Consolas', 'Courier New', monospace" font-size="11" letter-spacing="4" fill="#94a3b8">
    // COMPETITIVE PROGRAMMING HUD // ARCHITECTURE &amp; SYSTEMS
  </text>
</svg>'''

    out_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'header.svg')
    out_path = os.path.normpath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f"Header generated at: {out_path} ({len(svg)} bytes)")

if __name__ == '__main__':
    generate_header_svg()
