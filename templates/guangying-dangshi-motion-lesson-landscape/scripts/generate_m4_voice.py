# -*- coding: utf-8 -*-
from pathlib import Path
import json
import re
import sys
import time
import urllib.error
import urllib.request
import wave

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/voice-m4"
OUT.mkdir(parents=True, exist_ok=True)
SCRIPT = (ROOT / "content/EP01_SCRIPT_M4.md").read_text()
blocks = re.split(r"(?=^## S\d+)", SCRIPT, flags=re.M)
chapters = []
for block in blocks:
    match = re.match(r"## (S\d+)｜([^\n]+)", block)
    if not match:
        continue
    narration = re.split(r"\*\*口播\*\*[：:]\s*", block, maxsplit=1)[1]
    narration = re.split(r"\n(?:---|## )", narration, maxsplit=1)[0].strip()
    if not narration:
        continue
    chapter_id = match.group(1)
    (OUT / f"{chapter_id}.txt").write_text(narration + "\n")
    chapters.append({"id": chapter_id, "title": match.group(2), "text": narration})

if len(chapters) != 9:
    raise SystemExit(f"Expected 9 chapters, found {len(chapters)}")

requested = set(sys.argv[1:])
if requested:
    unknown = requested - {chapter["id"] for chapter in chapters}
    if unknown:
        raise SystemExit(f"Unknown chapter ids: {sorted(unknown)}")
    chapters = [chapter for chapter in chapters if chapter["id"] in requested]

for chapter in chapters:
    dest = OUT / f"{chapter['id']}.wav"
    request = urllib.request.Request(
        "http://localhost:3900/v1/audio/speech",
        data=json.dumps({
            "model": "omnivoice",
            "voice": "c36e2897",
            "input": chapter["text"],
            "response_format": "wav",
            "language": "zh",
        }, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print(f"Generating {chapter['id']}: {len(chapter['text'])} chars", flush=True)
    with urllib.request.urlopen(request, timeout=900) as response:
        data = response.read()
    dest.write_bytes(data)
    try:
        with wave.open(str(dest), "rb") as wf:
            duration = wf.getnframes() / wf.getframerate()
            info = {"sample_rate": wf.getframerate(), "channels": wf.getnchannels(), "frames": wf.getnframes(), "duration_seconds": round(duration, 3)}
    except Exception as exc:
        raise SystemExit(f"Voice endpoint returned an unreadable WAV for {chapter['id']}: {exc}; body starts {data[:100]!r}")
    chapter.update(info)
    print(f"Saved {dest.name}: {duration:.2f}s, {info['sample_rate']} Hz", flush=True)
    time.sleep(1.0)

manifest_path = OUT / "manifest.json"
old_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
merged_chapters = {chapter["id"]: chapter for chapter in old_manifest.get("chapters", [])}
merged_chapters.update({chapter["id"]: {key: value for key, value in chapter.items() if key != "text"} for chapter in chapters})
manifest = {
    "voice_profile_id": "c36e2897",
    "voice_profile_name": "国标视野",
    "engine": "VoiceStudio OmniVoice",
    "model_license": "CC-BY-NC; non-commercial use only",
    "publication_choice": "non-commercial",
    "chapters": [merged_chapters[key] for key in sorted(merged_chapters)],
}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(f"Generated {len(chapters)} chapters; total {sum(c['duration_seconds'] for c in chapters):.2f}s")
