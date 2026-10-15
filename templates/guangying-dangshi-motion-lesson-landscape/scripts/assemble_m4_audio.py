# -*- coding: utf-8 -*-
"""Assemble chapter voice WAVs and make a deterministic, original ambient bed."""
from pathlib import Path
import json
import math
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VOICE_DIR = ROOT / "output/voice-m4"
VOICE_OUT = ROOT / "media/voice/EP01_M4_narration.wav"
MUSIC_OUT = ROOT / "media/audio/EP01_M4_music.wav"
GAP_SECONDS = 0.35

VOICE_OUT.parent.mkdir(parents=True, exist_ok=True)
MUSIC_OUT.parent.mkdir(parents=True, exist_ok=True)

chapter_data = []
sample_rate = None
channels = None
sample_width = None
offset = 0.0
with wave.open(str(VOICE_OUT), "wb") as merged:
    for number in range(1, 10):
        chapter_id = f"S{number:02d}"
        path = VOICE_DIR / f"{chapter_id}.wav"
        if not path.exists():
            raise SystemExit(f"Missing generated chapter: {path}")
        with wave.open(str(path), "rb") as source:
            params = source.getparams()
            if sample_rate is None:
                sample_rate, channels, sample_width = params.framerate, params.nchannels, params.sampwidth
                merged.setparams((channels, sample_width, sample_rate, 0, "NONE", "not compressed"))
            elif (params.framerate, params.nchannels, params.sampwidth) != (sample_rate, channels, sample_width):
                raise SystemExit(f"Incompatible audio parameters in {path}: {params}")
            duration = params.nframes / params.framerate
            text = (VOICE_DIR / f"{chapter_id}.txt").read_text().strip()
            chapter_data.append({"id": chapter_id, "start": round(offset, 4), "end": round(offset + duration, 4), "duration_seconds": round(duration, 4), "text": text})
            print(f"Append {chapter_id} at {offset:.2f}s, duration {duration:.2f}s", flush=True)
            merged.writeframes(source.readframes(params.nframes))
        offset += duration
        if number < 9:
            merged.writeframes(b"\x00" * int(sample_rate * GAP_SECONDS) * channels * sample_width)
            offset += GAP_SECONDS

if sample_width != 2 or channels != 1:
    raise SystemExit(f"Expected 16-bit mono chapter WAVs; got width={sample_width}, channels={channels}")

total_seconds = round(offset, 4)
manifest = json.loads((VOICE_DIR / "manifest.json").read_text()) if (VOICE_DIR / "manifest.json").exists() else {}
manifest.update({"sample_rate": sample_rate, "gap_seconds": GAP_SECONDS, "duration_seconds": total_seconds, "chapters": chapter_data})
(VOICE_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print(f"Narration: {VOICE_OUT} ({total_seconds:.2f}s, {sample_rate} Hz mono)", flush=True)

# Original, generated-in-code ambient pad: slow chord changes, no sampled music.
# Low amplitude leaves the narration intelligible; HyperFrames applies a voiceover carve.
music_rate = 24000
frames = int(round(total_seconds * music_rate))
progression = [
    (65.406, 77.782, 98.000, 130.813),   # C minor
    (51.913, 65.406, 77.782, 103.826),   # A-flat
    (77.782, 98.000, 116.541, 155.563),  # E-flat
    (58.270, 73.416, 87.307, 116.541),   # B-flat
    (43.654, 51.913, 65.406, 87.307),    # F minor
    (65.406, 77.782, 98.000, 130.813),   # C minor
    (51.913, 65.406, 77.782, 103.826),   # A-flat
    (49.000, 61.735, 73.416, 98.000),    # G
]
with wave.open(str(MUSIC_OUT), "wb") as music:
    music.setparams((2, 2, music_rate, 0, "NONE", "not compressed"))
    block = music_rate * 10
    for start_frame in range(0, frames, block):
        end_frame = min(frames, start_frame + block)
        t = np.arange(start_frame, end_frame, dtype=np.float64) / music_rate
        chord_index = np.floor(t / 24.0).astype(np.int64) % len(progression)
        within = np.mod(t, 24.0)
        breath = 0.80 + 0.20 * np.sin(2 * np.pi * t / 19.0 + 0.3)
        pad = np.zeros_like(t)
        for chord_no, notes in enumerate(progression):
            is_current = chord_index == chord_no
            is_previous = (within < 3.0) & (chord_index == ((chord_no + 1) % len(progression)))
            is_next = (within > 21.0) & (chord_index == ((chord_no - 1) % len(progression)))
            active = is_current | is_previous | is_next
            if not np.any(active):
                continue
            local_t = t[active]
            level = np.ones_like(local_t)
            active_within = within[active]
            active_index = chord_index[active]
            current_at_start = (active_index == chord_no) & (active_within < 3.0)
            previous_at_start = (active_index == ((chord_no + 1) % len(progression))) & (active_within < 3.0)
            current_at_end = (active_index == chord_no) & (active_within > 21.0)
            next_at_end = (active_index == ((chord_no - 1) % len(progression))) & (active_within > 21.0)
            theta_start = np.clip(active_within / 3.0, 0.0, 1.0) * np.pi / 2
            theta_end = np.clip((active_within - 21.0) / 3.0, 0.0, 1.0) * np.pi / 2
            level[current_at_start] = np.sin(theta_start[current_at_start]) ** 2
            level[previous_at_start] = np.cos(theta_start[previous_at_start]) ** 2
            level[current_at_end] = np.cos(theta_end[current_at_end]) ** 2
            level[next_at_end] = np.sin(theta_end[next_at_end]) ** 2
            level *= breath[active]
            for note_no, frequency in enumerate(notes):
                amp = (0.013, 0.009, 0.008, 0.0045)[note_no]
                tone = np.sin(2 * np.pi * frequency * local_t)
                tone += 0.18 * np.sin(4 * np.pi * frequency * local_t + 0.2 * note_no)
                pad[active] += amp * level * tone
        fade_in = np.clip(t / 4.0, 0, 1)
        fade_out = np.clip((total_seconds - t) / 6.0, 0, 1)
        pad *= fade_in * fade_out
        left = np.clip(pad * 0.97, -0.8, 0.8)
        right = np.clip(pad * 1.03, -0.8, 0.8)
        stereo = np.column_stack((left, right))
        pcm = np.clip(stereo * 32767, -32768, 32767).astype("<i2")
        music.writeframes(pcm.tobytes())

print(f"Original ambient bed: {MUSIC_OUT} ({total_seconds:.2f}s, {music_rate} Hz stereo)")
