#!/usr/bin/env python3
"""Create the optional HyperFrames voice manifest from WAVs in assets/audio."""
import json
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOICE_DIR = ROOT / "assets" / "audio"
MANIFEST = ROOT / "voice-manifest.json"


def main():
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    records = []
    for path in sorted(VOICE_DIR.glob("*.wav")):
        with wave.open(str(path), "rb") as wav:
            records.append({
                "id": path.stem,
                "path": path.relative_to(ROOT).as_posix(),
                "duration_s": round(wav.getnframes() / wav.getframerate(), 3),
                "sample_rate": wav.getframerate(),
                "channels": wav.getnchannels(),
            })
    if not records:
        raise SystemExit("No WAV files found in assets/audio; nothing to add.")
    MANIFEST.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"Wrote {len(records)} voice segment(s): {MANIFEST}")


if __name__ == "__main__":
    main()
