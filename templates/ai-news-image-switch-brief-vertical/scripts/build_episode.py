#!/usr/bin/env python3
"""Build index.html from an episode JSON file using only Python's standard library."""

from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "index.template.html"
DEFAULT_DATA = ROOT / "data" / "sample-episode.json"


def fail(message: str) -> None:
    raise SystemExit(f"Episode data error: {message}")


def local_asset(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{label} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        fail(f"{label} must stay inside the template directory")
    if not (ROOT / path).is_file():
        fail(f"{label} file does not exist: {value}")
    return value


def main() -> None:
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DATA
    if not data_path.is_absolute():
        data_path = (Path.cwd() / data_path).resolve()
    try:
        episode = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {data_path.name}: {exc}")

    duration = episode.get("duration")
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        fail("duration must be a positive number of seconds")
    duration_text = f"{duration:g}"
    for field in ("title", "subtitle", "footerKicker"):
        if not isinstance(episode.get(field), str) or not episode[field].strip():
            fail(f"{field} must be a non-empty string")
    if len(episode["title"]) > 12:
        fail("title should be 12 characters or fewer to fit the fixed title plate")
    if len(episode["subtitle"]) > 16:
        fail("subtitle should be 16 characters or fewer to fit the fixed subtitle plate")
    footer_lines = episode.get("footerLines")
    if not isinstance(footer_lines, list) or not 1 <= len(footer_lines) <= 3:
        fail("footerLines must contain one to three lines")
    if any(not isinstance(line, str) or not line.strip() for line in footer_lines):
        fail("each footerLines entry must be a non-empty string")
    if any(len(line) > 21 for line in footer_lines):
        fail("each footer line should be 21 characters or fewer to fit the summary panel")

    background = local_asset(episode.get("background"), "background")
    bgm = local_asset(episode.get("bgm"), "bgm")
    bgm_duration = episode.get("bgmDuration")
    if not isinstance(bgm_duration, (int, float)) or not math.isfinite(bgm_duration) or bgm_duration <= 0:
        fail("bgmDuration must be the positive duration of the music file")
    images = episode.get("images")
    beats = episode.get("beats")
    if not isinstance(images, list) or not 1 <= len(images) <= 8:
        fail("images must contain between one and eight image objects")
    if not isinstance(beats, list) or not beats:
        fail("beats must contain at least one image beat")
    image_ids = [image.get("id") for image in images if isinstance(image, dict)]
    if len(image_ids) != len(images) or any(not isinstance(item, str) or not item for item in image_ids):
        fail("every image needs a non-empty id")
    if len(set(image_ids)) != len(image_ids):
        fail("image ids must be unique")
    image_index = {image_id: index for index, image_id in enumerate(image_ids)}

    layers = []
    for index, image in enumerate(images):
        path = local_asset(image.get("path"), f"images[{index}].path")
        alt = html.escape(str(image.get("alt", "")), quote=True)
        layers.append(
            f'      <div id="shot-{index}" class="image-layer clip" data-start="0" '
            f'data-duration="{duration_text}" data-track-index="{5 + index}">'
            f'<img src="{html.escape(path, quote=True)}" alt="{alt}" /></div>'
        )

    previous_start = -1.0
    for index, beat in enumerate(beats):
        if not isinstance(beat, dict) or beat.get("image") not in image_index:
            fail(f"beats[{index}].image must reference an image id")
        start = beat.get("start")
        if not isinstance(start, (int, float)) or not math.isfinite(start) or start < 0 or start >= duration:
            fail(f"beats[{index}].start must be between 0 and duration")
        if start <= previous_start:
            fail("beat start times must be strictly increasing")
        previous_start = start
    if beats[0]["start"] != 0:
        fail("the first beat must start at 0 seconds")

    deck = episode.get("transitionDeck")
    transition_count = max(1, len(beats) - 1)
    if not isinstance(deck, list) or len(deck) < transition_count:
        fail(f"transitionDeck needs at least {transition_count} entries")
    if any(effect not in {"zoom", "push", "tilt"} for effect in deck):
        fail('transitionDeck entries must be "zoom", "push", or "tilt"')
    seed = episode.get("transitionSeed", 1)
    if not isinstance(seed, int):
        fail("transitionSeed must be an integer")

    config = dict(episode)
    config["background"] = background
    config["bgm"] = bgm
    audio_clips = []
    audio_start = 0.0
    clip_index = 0
    while audio_start < duration - 1e-9:
        clip_duration = min(bgm_duration, duration - audio_start)
        audio_clips.append(
            f'    <audio id="bgm-{clip_index}" class="clip" '
            f'src="{html.escape(bgm, quote=True)}" data-start="{audio_start:g}" '
            f'data-duration="{clip_duration:g}" data-media-start="0" '
            f'data-track-index="{41 + clip_index}"></audio>'
        )
        audio_start += clip_duration
        clip_index += 1
    rendered = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "@@DURATION@@": duration_text,
        "@@BACKGROUND@@": html.escape(background, quote=True),
        "@@BGM_CLIPS@@": "\n".join(audio_clips),
        "@@IMAGE_LAYERS@@": "\n".join(layers),
        "@@TITLE@@": html.escape(episode["title"]),
        "@@SUBTITLE@@": html.escape(episode["subtitle"]),
        "@@FOOTER_KICKER@@": html.escape(episode["footerKicker"]),
        "@@FOOTER_LINES@@": "<br />".join(html.escape(line) for line in footer_lines),
        "@@EPISODE_JSON@@": json.dumps(config, ensure_ascii=False).replace("</", "<\\/"),
    }
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    if re.search(r"@@[A-Z_]+@@", rendered):
        fail("template contains an unfilled placeholder")
    (ROOT / "index.html").write_text(rendered, encoding="utf-8")
    print(f"Built index.html from {data_path.name} ({len(beats)} beats, {duration_text}s).")


if __name__ == "__main__":
    main()
