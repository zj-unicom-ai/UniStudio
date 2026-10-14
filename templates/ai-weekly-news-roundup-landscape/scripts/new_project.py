#!/usr/bin/env python3
"""Copy this template into a clean, independent episode project folder."""
import argparse
import shutil
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1]


def ignored(directory, names):
    current = Path(directory).resolve()
    relative = current.relative_to(SOURCE)
    excluded = {".DS_Store", ".git", "node_modules", "__pycache__", "out"}
    ignored_names = set(names) & excluded
    if relative == Path("."):
        ignored_names |= set(names) & {"voice-manifest.json"}
    if relative == Path("data"):
        ignored_names |= set(names) & {"my-episode.json"}
    if relative == Path("assets/audio"):
        ignored_names |= set(names)
    if relative == Path("assets/shots"):
        ignored_names |= {name for name in names if name != ".gitkeep"}
    if relative == Path("preview"):
        ignored_names |= {name for name in names
                          if name.startswith("work-") or
                          (name.startswith(".") and ".hf-transaction-" in name)}
    ignored_names |= {name for name in names if name.startswith(".tmp-")}
    return ignored_names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New project directory")
    args = parser.parse_args()
    destination = args.destination.expanduser().resolve()
    if destination == SOURCE or SOURCE in destination.parents:
        parser.error("destination must be outside the template folder")
    if destination.exists():
        parser.error(f"destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE, destination, ignore=ignored)
    print(f"Project copied to: {destination}")


if __name__ == "__main__":
    main()
