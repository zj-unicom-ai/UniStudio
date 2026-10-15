# -*- coding: utf-8 -*-
"""Transcribe M5 chapter WAVs through VoiceStudio, splitting long files to fit its ASR timeout."""
from pathlib import Path
import json
import mimetypes
import tempfile
import wave
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "output/voice-m5"
CHUNK_SECONDS = 75.0
ENDPOINT = "http://localhost:3900/v1/audio/transcriptions"


def transcribe(path):
    boundary = "----VoiceStudioM5Boundary7MA4YWxkTrZu0gW"
    parts = []

    def add_field(name, value):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())

    add_field("model", "whisper-1")
    add_field("language", "zh")
    add_field("response_format", "verbose_json")
    add_field("timestamp_granularities[]", "segment")
    mime = mimetypes.guess_type(path.name)[0] or "audio/wav"
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
        + path.read_bytes()
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    request = urllib.request.Request(
        ENDPOINT,
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        return json.loads(response.read())


def split_wav(source_path, directory):
    with wave.open(str(source_path), "rb") as source:
        params = source.getparams()
        if params.sampwidth != 2 or params.nchannels != 1:
            raise SystemExit(f"Expected mono 16-bit WAV: {source_path} has {params}")
        frames_per_chunk = int(CHUNK_SECONDS * params.framerate)
        total_frames = params.nframes
        for part_no, first in enumerate(range(0, total_frames, frames_per_chunk), 1):
            count = min(frames_per_chunk, total_frames - first)
            source.setpos(first)
            audio = source.readframes(count)
            path = directory / f"{source_path.stem}.part{part_no:02d}.wav"
            with wave.open(str(path), "wb") as output:
                output.setparams((params.nchannels, params.sampwidth, params.framerate, 0, "NONE", "not compressed"))
                output.writeframes(audio)
            yield path, first / params.framerate, count / params.framerate


manifest = json.loads((AUDIO_DIR / "manifest.json").read_text())
durations = {item["id"]: float(item["duration_seconds"]) for item in manifest["chapters"]}
for chapter_id in [f"S{i:02d}" for i in range(1, 10)]:
    audio_path = AUDIO_DIR / f"{chapter_id}.wav"
    output_path = AUDIO_DIR / f"{chapter_id}.transcript.json"
    if output_path.exists() and output_path.stat().st_mtime > audio_path.stat().st_mtime:
        print(f"Already transcribed: {chapter_id}", flush=True)
        continue

    segments, texts = [], []
    with tempfile.TemporaryDirectory(prefix="m5-asr-") as temp_dir:
        chunks = list(split_wav(audio_path, Path(temp_dir)))
        for part_no, (chunk_path, offset, duration) in enumerate(chunks, 1):
            print(f"Transcribing {chapter_id} part {part_no}/{len(chunks)} ({duration:.1f}s)", flush=True)
            result = transcribe(chunk_path)
            texts.append(result.get("text", "").strip())
            for index, item in enumerate(result.get("segments") or []):
                start = min(duration, max(0.0, float(item.get("start", 0.0))))
                end = min(duration, max(start, float(item.get("end", start))))
                text = item.get("text", "").strip()
                if not text:
                    continue
                segments.append({
                    "id": len(segments),
                    "start": round(offset + start, 3),
                    "end": round(offset + end, 3),
                    "text": text,
                })
            print(f"Saved {chapter_id} part {part_no}: {len(result.get('segments') or [])} segments", flush=True)

    full_text = "".join(texts).strip()
    if not segments or "\ufffd" in full_text:
        raise SystemExit(f"Invalid transcript for {chapter_id}; output not written.")
    output = {
        "task": "transcribe",
        "language": "zh",
        "duration": durations[chapter_id],
        "text": full_text,
        "segments": segments,
        "chunk_seconds": CHUNK_SECONDS,
    }
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"Saved {chapter_id}: {len(segments)} segments, transcript {len(full_text)} chars", flush=True)
