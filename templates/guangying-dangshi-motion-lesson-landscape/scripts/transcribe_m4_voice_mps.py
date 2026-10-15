# -*- coding: utf-8 -*-
"""Fast local segment timing with the already-cached Whisper Turbo checkpoint.

The model path is explicit so this script never downloads weights. MPS uses
fp32 here: fp16 produced replacement characters in the first local comparison.
"""
from pathlib import Path
import json
import whisper

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "output/voice-m4"
CHECKPOINT = Path.home() / ".cache/whisper/large-v3-turbo.pt"
MANIFEST_PATH = AUDIO_DIR / "manifest.json"

if not CHECKPOINT.exists():
    raise SystemExit(f"Cached Whisper Turbo checkpoint not found: {CHECKPOINT}")
if not MANIFEST_PATH.exists():
    raise SystemExit("Missing voice manifest; run scripts/assemble_m4_audio.py first.")

manifest = json.loads(MANIFEST_PATH.read_text())
durations = {item["id"]: float(item["duration_seconds"]) for item in manifest["chapters"]}
model = whisper.load_model(str(CHECKPOINT), device="mps")

for chapter_id in [f"S{i:02d}" for i in range(1, 10)]:
    audio_path = AUDIO_DIR / f"{chapter_id}.wav"
    output_path = AUDIO_DIR / f"{chapter_id}.transcript.json"
    if output_path.exists() and output_path.stat().st_mtime > audio_path.stat().st_mtime:
        print(f"Already transcribed: {chapter_id}", flush=True)
        continue
    print(f"Transcribing {chapter_id} with cached Whisper Turbo on MPS", flush=True)
    result = model.transcribe(
        str(audio_path),
        language="zh",
        task="transcribe",
        verbose=False,
        word_timestamps=False,
        fp16=False,
    )
    text = result.get("text", "")
    segments = [
        {
            "id": item.get("id", index),
            "start": round(float(item.get("start", 0.0)), 3),
            "end": round(float(item.get("end", 0.0)), 3),
            "text": item.get("text", "").strip(),
        }
        for index, item in enumerate(result.get("segments", []))
    ]
    if "\ufffd" in text or not segments:
        raise SystemExit(f"Invalid transcript returned for {chapter_id}; output not written.")
    output = {
        "task": "transcribe",
        "language": result.get("language", "zh"),
        "duration": durations[chapter_id],
        "text": text.strip(),
        "segments": segments,
    }
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"Saved {chapter_id}: {len(segments)} segments, {len(text)} transcript chars", flush=True)
