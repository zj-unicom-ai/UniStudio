# -*- coding: utf-8 -*-
from pathlib import Path
import json
import mimetypes
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "output/voice-m4"

for chapter_id in [f"S{i:02d}" for i in range(1, 10)]:
    audio_path = AUDIO_DIR / f"{chapter_id}.wav"
    output_path = AUDIO_DIR / f"{chapter_id}.transcript.json"
    if output_path.exists() and output_path.stat().st_mtime > audio_path.stat().st_mtime:
        print(f"Already transcribed: {chapter_id}", flush=True)
        continue
    boundary = "----VoiceStudioM4Boundary7MA4YWxkTrZu0gW"
    parts = []
    def add_field(name, value):
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
    add_field("model", "whisper-1")
    add_field("language", "zh")
    add_field("response_format", "verbose_json")
    add_field("timestamp_granularities[]", "segment")
    name = audio_path.name
    mime = mimetypes.guess_type(name)[0] or "audio/wav"
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\nContent-Type: {mime}\r\n\r\n".encode()
        + audio_path.read_bytes()
        + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    request = urllib.request.Request(
        "http://localhost:3900/v1/audio/transcriptions",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    print(f"Transcribing {chapter_id} ({audio_path.stat().st_size // 1024} KiB)", flush=True)
    with urllib.request.urlopen(request, timeout=900) as response:
        result = json.loads(response.read())
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    segments = result.get("segments") or []
    print(f"Saved {chapter_id}: {len(segments)} segments, transcript {len(result.get('text', ''))} chars", flush=True)
