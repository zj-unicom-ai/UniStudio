# Usage

## Requirements

- Node.js/npm. HyperFrames `0.8.145` is pinned in `package.json` and fetched through `npx` on first use.
- Python 3 only for optional replacement narration generation.
- HyperFrames-supported Chromium/FFmpeg runtime for preview and rendering.

Run commands from this template directory. Edit `data/sample-episode.json`, not generated `index.html`.

## Edit episode content

The JSON contains `episode` metadata and an ordered `pages` array. Keep page IDs unique and stable because they map to audio filenames and timing entries.

- `episode.title`, `show`, `slogan`, `outro`, `no`, and `chapters` set the cover, series branding, outro text, and chapter labels. `opening.welcome` and `opening.bridge` configure the spoken welcome and transition.
- Each page has `id`, `ch` (chapter index), `type`, and fields used by that layout. Page types include `opening`, `point`, `quote`, `ledger`, `grid4`, and `ending`.
- `say` is narration. `title`, `label`, `rows`, `cols`, `quote`, `subs`, `ask`, and `formula` control the visible copy.
- Put emphasis in square brackets, for example `[重点]`. Timed row/subtitle cues should be exact phrases from `say`, or a number from 0 to 1 for a relative position.
- `illus` selects an SVG key in `source/illus.mjs`.
- `timing.json` overrides page duration in seconds. Regenerating narration updates it from measured WAV duration.

The sample is a complete episode rather than a minimal schema. Preserve each field's type and align narration with visible cues. The source package flags several recalled historical quotations for verification; see SOURCES.md before publishing unchanged demo copy.

## Replace narration

Replace corresponding files under `assets/audio/` and update `voice-manifest.json` with each segment's `id`, relative `path`, `duration_s`, sample rate, and channel count. Keep `welcome.wav` and `bridge.wav` for the sample opening, or update the manifest and opening timeline together.

Optional TTS generation uses an OpenAI-compatible VoiceStudio endpoint. Configure your own authorized voice in the shell; values are read from environment variables and are not written as credentials into source:

```bash
export VOICESTUDIO_BASE_URL='http://127.0.0.1:3900'
export VOICESTUDIO_VOICE_ID='your-authorized-voice-id'
python3 scripts/generate_voiceover.py
npm run build
```

The service, voice and permission to use generated speech are the operator's responsibility. The helper defaults to model `omnivoice`; `VOICESTUDIO_MODEL` and `VOICESTUDIO_SPEED` are configurable. It reads `EPISODE_DATA` or `data/sample-episode.json`.

## Build, inspect, and render

```bash
npm run build
npm run check
npm run preview
npx hyperframes preview --list
```

Open the preview URL. Inspect the opening, a middle explanation page, a practice page, the outro, and audio transitions. Stop the preview service after review with the HyperFrames preview stop command.

```bash
npm run render
```

The package script writes `out/demo.mp4`; `out/` and generated `dist/` are Git-ignored. When publishing, use a fully visible opening frame as the cover.

## Common problems

- **Timed text does not appear:** ensure each string cue occurs verbatim in its page's `say`; the builder reports missing cue text.
- **Audio mismatch:** check unique page IDs, WAV paths, and matching manifest entries.
- **Wrong pacing:** regenerate `timing.json` from actual speech durations or edit seconds values, then rebuild.
- **Font differences:** keep bundled fonts in place and verify font loading in preview.
- **TTS request fails:** check endpoint reachability, authorized voice ID, model support, and WAV response format.
- **Render fails:** run `npm run check`, confirm browser/FFmpeg runtime, and inspect CLI diagnostics.
