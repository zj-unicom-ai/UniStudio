import json
import argparse
import os
import sys
import urllib.request
import wave
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
REQUEST_PATH = PROJECT / "voice-requests.json"
VOICE_DIR = PROJECT / "assets" / "voice"
API_URL = os.environ.get("VOICE_API_URL", "http://localhost:3900/v1/audio/speech").strip()
API_KEY = os.environ.get("VOICE_API_KEY", "").strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "segments",
        nargs="*",
        help="Optional segment IDs to regenerate; omitted means all segments.",
    )
    args = parser.parse_args()
    request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = PROJECT / "voice-manifest.json"
    old_manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else []
    manifest_by_id = {item["id"]: item for item in old_manifest}
    requested_ids = set(args.segments)
    unknown_ids = requested_ids - {segment["id"] for segment in request["segments"]}
    if unknown_ids:
        parser.error(f"unknown segment ID(s): {', '.join(sorted(unknown_ids))}")
    selected = [
        segment
        for segment in request["segments"]
        if not requested_ids or segment["id"] in requested_ids
    ]
    for segment in selected:
        destination = VOICE_DIR / f"{segment['id']}.wav"
        payload = {
            key: value
            for key, value in request.items()
            if key not in {"segments"}
        }
        payload["input"] = segment["text"]
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            API_URL,
            data=body,
            headers={**{"Content-Type": "application/json"}, **({"Authorization": f"Bearer {API_KEY}"} if API_KEY else {})},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=600) as response:
            audio = response.read()
        if not audio.startswith(b"RIFF") or b"WAVE" not in audio[:16]:
            raise RuntimeError(
                f"VoiceStudio returned non-WAV data for {segment['id']}: "
                f"{audio[:120]!r}"
            )
        destination.write_bytes(audio)
        with wave.open(str(destination), "rb") as wav:
            duration = wav.getnframes() / wav.getframerate()
            sample_rate = wav.getframerate()
            channels = wav.getnchannels()
        manifest_by_id[segment["id"]] = {
                "id": segment["id"],
                "path": str(destination.relative_to(PROJECT)),
                "duration_s": round(duration, 3),
                "sample_rate": sample_rate,
                "channels": channels,
            }
        print(f"{segment['id']}: {duration:.2f}s, {sample_rate}Hz, {channels}ch")
    manifest = [manifest_by_id[segment["id"]] for segment in request["segments"] if segment["id"] in manifest_by_id]
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"voiceover generation failed: {exc}", file=sys.stderr)
        raise
