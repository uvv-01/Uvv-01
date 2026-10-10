#!/usr/bin/env python3
"""
Build Galaga Contribution Graph SVG
Generates arcade Galaga SVG animations based on abozanona/pacman-contribution-graph.
Produces:
  - assets/galaga-contribution-graph-dark.svg (GitHub Dark theme)
  - assets/galaga-contribution-graph.svg (GitHub Light theme)
"""

import os
import re
import sys
import subprocess

USERNAME = "uvv-01"

def add_viewbox_if_missing(svg_path):
    """Ensure SVG has viewBox for responsive scaling in GitHub READMEs."""
    if not os.path.exists(svg_path):
        return
    with open(svg_path, "r", encoding="utf-8") as f:
        content = f.read()

    # If viewBox already present, nothing to do
    if 'viewBox="' in content or "viewbox=" in content.lower():
        return

    # Look for root <svg width="1166" height="259"
    m = re.search(r'<svg width="(\d+)" height="(\d+)"', content)
    if m:
        w, h = m.group(1), m.group(2)
        content = content.replace(
            f'<svg width="{w}" height="{h}"',
            f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"',
            1
        )
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [viewBox] Added viewBox='0 0 {w} {h}' to {os.path.basename(svg_path)}")

def build_galaga_svg(theme, output_filename):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_dir = os.path.join(repo_root, "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, output_filename)

    cmd = [
        "npx", "pacman-contribution-graph",
        "--game", "galaga",
        "--platform", "github",
        "--username", USERNAME,
        "--gameTheme", theme,
        "-o", out_path
    ]

    print(f"Generating Galaga SVG for theme '{theme}' -> {output_filename}...")
    res = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, shell=True)
    if res.returncode != 0:
        print(f"Error running pacman-contribution-graph: {res.stderr}")
        return False

    add_viewbox_if_missing(out_path)
    sz = os.path.getsize(out_path)
    print(f"  -> Generated {output_filename} ({sz} bytes, {sz/1024:.1f} KB)")
    return True

def main():
    print("=== Building Galaga Contribution Graph SVGs ===")
    ok_dark = build_galaga_svg("github-dark", "galaga-contribution-graph-dark.svg")
    ok_light = build_galaga_svg("github", "galaga-contribution-graph.svg")
    if ok_dark and ok_light:
        print("[SUCCESS] Galaga contribution graph SVGs successfully generated.")
    else:
        print("[ERROR] Failed to generate one or more Galaga SVGs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
