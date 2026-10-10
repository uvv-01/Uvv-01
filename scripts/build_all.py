#!/usr/bin/env python3
"""
Master Asset Build Script
Builds all visual assets for the GitHub Profile:
1. Name Header SVG (assets/header.svg)
2. Gaming Coding Profile Dashboard SVG (assets/coding-profile.svg)
3. Rocket Spaceship Contribution Shooter GIF (assets/contribution-shooter.gif)
4. Glowing Contact Scroll Reveal GIF (assets/contact-scroll.gif)
"""

import sys
import subprocess

def run_script(script_name):
    print(f"\n[BUILD] Running {script_name}...")
    res = subprocess.run([sys.executable, f"scripts/{script_name}"], check=True)
    return res.returncode == 0

def main():
    scripts = [
        "build_header.py",
        "build_coding_profile.py",
        "build_contribution_shooter.py",
        "build_contact_scroll.py",
    ]
    for s in scripts:
        run_script(s)
    print("\n[SUCCESS] All profile assets successfully generated.")

if __name__ == "__main__":
    main()
