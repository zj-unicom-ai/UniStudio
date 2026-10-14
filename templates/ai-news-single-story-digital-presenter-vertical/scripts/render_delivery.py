#!/usr/bin/env python3
"""Render through the pinned HyperFrames CLI and export a full cover and player page."""
import argparse
import html
import json
from fractions import Fraction
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.8.140"
DEFAULT_COVER_AT = 2.0

def fail(message):
    raise SystemExit(message)

def output_from(arguments):
    for index, item in enumerate(arguments):
        if item == "--output":
            if index + 1 >= len(arguments):
                fail("--output needs a path")
            return Path(arguments[index + 1]), None
        if item.startswith("--output="):
            return Path(item.split("=", 1)[1]), index
    return None, None

def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--cover-at", type=float, default=DEFAULT_COVER_AT, help="Seconds into the rendered video for the complete static cover.")
    options, forwarded = parser.parse_known_args()
    if options.cover_at < 0:
        parser.error("--cover-at must be zero or greater")

    output, output_index = output_from(forwarded)
    if output is None:
        output = Path("out/ai-news-single-story.mp4")
        forwarded.extend(["--output", str(output)])
    elif not output.is_absolute():
        output = (Path.cwd() / output).resolve()
        for i, arg in enumerate(forwarded):
            if arg == "--output" and i + 1 < len(forwarded):
                forwarded[i + 1] = str(output)
            elif arg.startswith("--output="):
                forwarded[i] = "--output=" + str(output)
    if output.suffix.lower() != ".mp4":
        parser.error("render output must use the .mp4 extension")
    output.parent.mkdir(parents=True, exist_ok=True)

    command = ["npx", "--yes", f"hyperframes@{VERSION}", "render", *forwarded]
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)
    if not output.is_absolute():
        output = (ROOT / output).resolve()
    if not output.is_file():
        fail(f"HyperFrames did not create the requested MP4: {output}")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        fail("MP4 rendered, but ffmpeg and ffprobe are required to validate and export the cover PNG and player page.")
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,width,height,r_frame_rate:format=duration",
        "-of", "json", str(output),
    ], capture_output=True, text=True, check=True)
    metadata = json.loads(probe.stdout)
    video = next((stream for stream in metadata.get("streams", []) if stream.get("codec_type") == "video"), None)
    has_audio = any(stream.get("codec_type") == "audio" for stream in metadata.get("streams", []))
    if video is None or (video.get("width"), video.get("height")) != (1080, 1920):
        fail("Rendered MP4 must contain a 1080x1920 video stream.")
    if Fraction(video.get("r_frame_rate", "0/1")) != 30:
        fail("Rendered MP4 must be 30 fps.")
    if not has_audio:
        fail("Rendered MP4 has no audio stream; this template requires its BGM or narration.")
    duration = float(metadata.get("format", {}).get("duration", 0))
    if duration <= options.cover_at:
        fail(f"Cover time {options.cover_at:g}s is outside the rendered video ({duration:.2f}s).")
    print(f"Verified MP4: 1080x1920, 30 fps, {duration:.2f}s, audio present.")

    cover = output.with_name(output.stem + "_封面.png")
    player = output.with_name(output.stem + "_播放页.html")
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{options.cover_at:g}", "-i", str(output),
        "-frames:v", "1", "-update", "1",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#07101f",
        str(cover),
    ], check=True)
    video_name = html.escape(output.name, quote=True)
    cover_name = html.escape(cover.name, quote=True)
    player.write_text(f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(output.stem)}</title>
<style>
html,body{{margin:0;min-height:100%;background:#07101f;color:#fff;font-family:system-ui,sans-serif}}
body{{display:grid;place-items:center;padding:24px;box-sizing:border-box}}
video{{display:block;width:min(100%,540px);max-height:92vh;aspect-ratio:9/16;background:#000;object-fit:contain}}
</style>
</head>
<body>
<video controls playsinline preload="metadata" poster="{cover_name}">
<source src="{video_name}" type="video/mp4">
</video>
</body>
</html>
""", encoding="utf-8")
    print(f"MP4: {output}")
    print(f"Cover PNG (1080x1920): {cover}")
    print(f"Player page: {player}")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"Command failed with exit status {error.returncode}", file=sys.stderr)
        raise
