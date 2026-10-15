#!/usr/bin/env python3
"""Create a seek-stable 100 ms RMS envelope from the issue voiceover WAV."""

import array
import argparse
import json
import math
import struct
import wave
from pathlib import Path


SOURCE = Path("assets/audio/voiceover.wav")
TARGET = Path("assets/audio/voice-envelope.json")
WINDOW_SECONDS = 0.1
SMOOTH_SECONDS = 0.18


def decode_frames(raw: bytes, width: int) -> list[float]:
    if width == 1:
        return [(sample - 128) / 128.0 for sample in raw]
    if width == 2:
        values = array.array("h")
        values.frombytes(raw)
        return [sample / 32768.0 for sample in values]
    if width == 3:
        values = []
        for offset in range(0, len(raw), 3):
            sample = int.from_bytes(raw[offset:offset + 3], "little", signed=False)
            if sample & 0x800000:
                sample -= 0x1000000
            values.append(sample / 8388608.0)
        return values
    if width == 4:
        count = len(raw) // 4
        return [value / 2147483648.0 for value in struct.unpack("<" + "i" * count, raw)]
    raise ValueError(f"Unsupported WAV sample width: {width} bytes")


def main() -> None:
    global SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="assets/audio/voiceover-female-news-fast.wav")
    SOURCE = Path(parser.parse_args().input)
    with wave.open(str(SOURCE), "rb") as audio:
        channels = audio.getnchannels()
        rate = audio.getframerate()
        width = audio.getsampwidth()
        frames = audio.getnframes()
        samples = decode_frames(audio.readframes(frames), width)

    samples_per_window = max(1, round(rate * WINDOW_SECONDS))
    samples_per_frame = channels
    amplitudes = []
    for start in range(0, len(samples), samples_per_window * samples_per_frame):
        block = samples[start:start + samples_per_window * samples_per_frame]
        if not block:
            continue
        rms = math.sqrt(sum(sample * sample for sample in block) / len(block))
        amplitudes.append(rms)

    ordered = sorted(amplitudes)
    reference = ordered[min(len(ordered) - 1, round((len(ordered) - 1) * 0.92))] or 1.0
    normalized = [min(1.0, amplitude / reference) for amplitude in amplitudes]
    radius = max(1, round(SMOOTH_SECONDS / WINDOW_SECONDS / 2))
    smoothed = []
    for index in range(len(normalized)):
        left = max(0, index - radius)
        right = min(len(normalized), index + radius + 1)
        value = sum(normalized[left:right]) / (right - left)
        smoothed.append(round(value, 4))

    duration = frames / rate
    payload = {
        "sampleIntervalSec": WINDOW_SECONDS,
        "smoothingSec": SMOOTH_SECONDS,
        "durationSec": round(duration, 4),
        "normalization": "92nd-percentile RMS; clamped and 180 ms centered moving average",
        "values": smoothed,
    }
    TARGET.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(TARGET), "durationSec": payload["durationSec"], "samples": len(smoothed)}))


if __name__ == "__main__":
    main()
