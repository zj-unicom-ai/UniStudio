#!/usr/bin/env python3
"""Export a full-frame PNG from the settled opening of a rendered video."""
import argparse
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path, help="Rendered MP4 path")
    parser.add_argument("--output", type=Path, help="PNG destination (default: <video>-cover.png)")
    parser.add_argument("--at", type=float, default=1.6,
                        help="Frame time in seconds (default: 1.6, after the opening reveal)")
    args = parser.parse_args()

    source = args.video.expanduser().resolve()
    if not source.is_file():
        parser.error(f"video does not exist: {source}")
    if args.at < 0:
        parser.error("--at must be zero or greater")

    destination = (args.output.expanduser().resolve() if args.output else
                   source.with_name(f"{source.stem}-cover.png"))
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", str(args.at), "-i", str(source), "-frames:v", "1",
        "-update", "1", str(destination),
    ]
    subprocess.run(command, check=True)
    print(f"Cover exported: {destination}")


if __name__ == "__main__":
    main()
