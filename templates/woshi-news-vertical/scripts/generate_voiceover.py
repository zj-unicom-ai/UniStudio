#!/usr/bin/env python3
"""Generate narration using the saved 女播报快节奏 VoiceStudio profile."""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def multipart(fields: dict[str, str]) -> tuple[str, bytes]:
    boundary = "----CodexVoiceStudio20261015Boundary"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
            value.encode("utf-8"),
            b"\r\n",
        ])
    chunks.append(f"--{boundary}--\r\n".encode())
    return boundary, b"".join(chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="content/narration.txt")
    parser.add_argument("--output", default="assets/audio/voiceover-female-news-fast.wav")
    parser.add_argument("--base-url", default="http://localhost:3900")
    parser.add_argument("--profile-id", default="c5a1e453")
    parser.add_argument("--profile-name", default="女播报快节奏")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=20261015)
    args = parser.parse_args()

    source = Path(args.input)
    target = Path(args.output)
    text = source.read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit(f"Narration text is empty: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)

    with urllib.request.urlopen(args.base_url.rstrip("/") + "/profiles", timeout=30) as response:
        profiles = json.load(response)
    profile = next((p for p in profiles if p["id"] == args.profile_id), None)
    if profile is None or profile["name"] != args.profile_name:
        raise SystemExit("Requested saved VoiceStudio profile was not found; no fallback voice was used.")

    fields = {
        "text": text,
        "language": "Chinese",
        "profile_id": args.profile_id,
        "speed": str(args.speed),
        "seed": str(args.seed),
        "effect_preset": "broadcast",
        "engine": "omnivoice",
    }
    boundary, body = multipart(fields)
    request = urllib.request.Request(
        args.base_url.rstrip("/") + "/generate",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=1800) as response:
            wav = response.read()
            headers = response.headers
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")[:1200]
        raise SystemExit(f"VoiceStudio returned HTTP {exc.code}: {details}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SystemExit(f"Could not reach local VoiceStudio at {args.base_url}: {exc}") from exc

    if headers.get_content_type() != "audio/wav" or not wav.startswith(b"RIFF"):
        raise SystemExit("VoiceStudio response was not a WAV file; output was not saved.")
    target.write_bytes(wav)
    metadata = {
        "provider": "VoiceStudio local API",
        "voiceStudioVersion": "0.5.6",
        "engine": "omnivoice",
        "language": "Chinese",
        "profileId": args.profile_id,
        "profileName": args.profile_name,
        "profileKind": profile["kind"],
        "speed": args.speed,
        "effectPreset": "broadcast",
        "seed": args.seed,
        "audioId": headers.get("X-Audio-Id"),
        "generationSeconds": float(headers.get("X-Gen-Time", "0")),
        "durationSeconds": float(headers.get("X-Audio-Duration", "0")),
        "sampleRate": 24000,
        "scriptPath": str(source),
        "audioPath": str(target),
        "profileSaved": False,
    }
    meta_path = target.with_name("voiceover-metadata.json")
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audioPath": str(target), **metadata}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit("Cancelled; no replacement voiceover was written.")
