#!/usr/bin/env python3
"""Copy this self-contained template into a fresh project directory."""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", "node_modules", "out", "renders", "snapshots", ".hyperframes", ".transcode-cache", "__pycache__"}

def ignore(directory, names):
    return [name for name in names if name in SKIP or name == ".DS_Store"]

def main():
    parser = argparse.ArgumentParser(description="Create a clean project from this template.")
    parser.add_argument("destination", help="New, not-yet-existing project directory")
    args = parser.parse_args()
    destination = Path(args.destination).expanduser().resolve()
    if destination == ROOT or ROOT in destination.parents:
        parser.error("destination must be outside the template directory")
    if destination.exists():
        parser.error(f"destination already exists: {destination}")
    shutil.copytree(ROOT, destination, ignore=ignore)
    print(f"Created project: {destination}")
    print("Next: edit the episode data and local media, then run npm run build and npm run check.")

if __name__ == "__main__":
    main()
