#!/usr/bin/env python3
"""Build approved-timing.json from the measured narration durations.

Every page slot is driven by the real WAV length, so re-running the voice
pass and then this script keeps the whole film in sync.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INTRO_VOICE_START = 0.80   # veil has lifted and the headline is on its way in
COVER_HOLD = 0.75          # silence after the last word, before the turn
PAGE_LEAD = 0.70           # page lands, then the voice starts
PAGE_TAIL = 0.90           # voice ends, page holds, then the next turn
TURN_OVERLAP = 0.62        # the peel overlaps the outgoing page (whoosh is 0.575s)
BRAND_DURATION = 6.00      # the series outro sub-composition is fixed at 6s


def main() -> None:
    manifest = {i["id"]: i["duration_s"] for i in json.loads((ROOT / "voice-manifest.json").read_text(encoding="utf-8"))}
    stories = json.loads((ROOT / "data" / "sample-episode.json").read_text(encoding="utf-8"))["stories"]

    intro = manifest["00-intro"]
    cover_duration = round(INTRO_VOICE_START + intro + COVER_HOLD, 3)

    starts, voice_starts, ends = [], [], []
    cursor = cover_duration
    for story in stories:
        start = round(cursor - TURN_OVERLAP, 3)
        voice = round(start + PAGE_LEAD, 3)
        end = round(voice + manifest[story["voice"]] + PAGE_TAIL, 3)
        starts.append(start)
        voice_starts.append(voice)
        ends.append(end)
        cursor = end

    brand_start = ends[-1]
    outro_voice = round(brand_start + PAGE_LEAD, 3)
    total = round(brand_start + BRAND_DURATION, 3)

    timing = {
        "cover_duration": cover_duration,
        "intro_voice_start": INTRO_VOICE_START,
        "story_starts": starts,
        "story_voice_starts": voice_starts,
        "story_ends": ends,
        "brand_start": brand_start,
        "brand_visual_start": round(brand_start - TURN_OVERLAP, 3),
        "outro_voice_start": outro_voice,
        "turn_overlap": TURN_OVERLAP,
        "total_duration": total,
    }
    (ROOT / "approved-timing.json").write_text(json.dumps(timing, indent=2) + "\n", encoding="utf-8")
    for k, v in timing.items():
        print(f"{k:22s} {v}")


if __name__ == "__main__":
    main()
