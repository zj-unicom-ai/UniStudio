#!/usr/bin/env python3
"""Build the cover lip-sync input for local MuseTalk v1.5 inference.

The presenter only appears on the cover, so this script pads the intro
narration out to the cover slot and resamples it to the 16 kHz mono WAV that
MuseTalk expects. The leading silence matters: the composition starts the
intro audio at `intro_voice_start`, so the lip-sync clip has to carry the same
offset or the mouth runs early.

Outputs:
    assets/voice/cover-musetalk-input.wav
    assets/voice/cover-musetalk-input-16k.wav
"""
from array import array
import json
from pathlib import Path
import subprocess
import sys
import wave

ROOT = Path(__file__).resolve().parents[1]
RATE = 24_000


def read_pcm(path: Path) -> array:
    with wave.open(str(path), "rb") as wav:
        if (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) != (RATE, 1, 2):
            raise ValueError(f"Expected 24 kHz mono 16-bit PCM: {path}")
        samples = array("h", wav.readframes(wav.getnframes()))
    if sys.byteorder != "little":
        samples.byteswap()
    return samples


def write_pcm(path: Path, samples: array) -> None:
    out = array("h", samples)
    if sys.byteorder != "little":
        out.byteswap()
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(out.tobytes())


def resample_for_musetalk(source: Path, destination: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(source), "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(destination)],
        check=True,
    )


manifest = {item["id"]: item for item in json.loads((ROOT / "voice-manifest.json").read_text(encoding="utf-8"))}
timing = json.loads((ROOT / "approved-timing.json").read_text(encoding="utf-8"))

intro_start = timing["intro_voice_start"]
cover_duration = timing["cover_duration"]
intro = read_pcm(ROOT / manifest["00-intro"]["path"])

cover = array("h", [0]) * round(intro_start * RATE)
cover.extend(intro)
slot = round(cover_duration * RATE)
if len(cover) < slot:
    cover.extend([0] * (slot - len(cover)))

cover_pcm = ROOT / "assets" / "voice" / "cover-musetalk-input.wav"
cover_16k = ROOT / "assets" / "voice" / "cover-musetalk-input-16k.wav"
write_pcm(cover_pcm, cover)
resample_for_musetalk(cover_pcm, cover_16k)

print(f"Cover lip-sync audio: {len(cover) / RATE:.3f}s (intro {len(intro) / RATE:.2f}s placed at +{intro_start}s, cover slot {cover_duration}s).")
