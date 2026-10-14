---
name: ai-weekly-news-roundup
description: Use when creating or updating an AI technology weekly roundup with this landscape editorial template, including sourced stories, optional narration, a rendered MP4, and a separate complete cover image.
---

# AI 周见｜横版科技周报

Use the complete project in this package to make a 16:9 weekly AI news roundup. Keep the bundled visual system: deep-blue grid opening, yellow emphasis, clean story pages, optional explainer/data cards, short recap, and yellow transitions. The sample is for layout only; it is not factual reporting.

## Start with the package

1. Locate the directory containing this `SKILL.md`; it is the template root. Use the full package because the Skill depends on its fonts, GSAP file, Python generators, page sources, and HyperFrames compositions.
2. Read `README.md`, `USAGE.md`, `TOOLS.md`, and `SOURCES.md`. If the user's workspace has an `AGENTS.md` or existing brief, follow it and inspect the relevant episode materials.
3. Create an independent project folder with `python3 <template-root>/scripts/new_project.py <project-path>`. Run all subsequent commands from that copy. The helper keeps the bundled demo and omits generated output, user-added photos/audio, and local voice manifests.
4. Use the installed HyperFrames workflow skill if available. Otherwise follow this package's setup and commands. The project pins HyperFrames `0.8.133`; do not upgrade it as part of an episode.

## Research and script

- Use the user's article links, notes, script, or topic as the brief. If they ask for current-week news or provide claims without enough support, verify the material against primary sources when possible and consult independent reporting for context. Browse current information when freshness matters.
- Keep an episode-specific source ledger based on `SOURCES.md`. For every published claim or number, retain the source URL, date, and wording note. Mark estimates, disputed figures, and unconfirmed plans clearly; never fill gaps with invented facts.
- Preserve supplied wording and editorial intent unless asked to rewrite. Structure 3–10 stories, each with a concise headline, summary, source label, and short commentary. Add a `C` explainer or `D` data card only when the story benefits from it; all chart values must be sourced and normalized to 0–100.
- Use `data/sample-episode.json` as the schema, save the new episode under a new name such as `data/my-episode.json`, and observe the field limits in `USAGE.md`. Replace the demo date, episode number, brand copy, stories, and recap. The default demo stories and chart values are fictional placeholders.
- Put only licensed, episode-relevant images in `assets/shots/` and record their own image credits in the source ledger. Leaving `image` as `null` produces a designed placeholder.

## Optional narration

The package does not include recorded speech, a voice ID, service credentials, or a TTS engine. If the user supplies or requests narration and a configured local speech tool is available, generate or use their chosen audio through that tool. Save each WAV as `assets/audio/<composition-id>.wav`, run `python3 scripts/make_voice_manifest.py`, rebuild, and check the audio timing. If no narration is requested or available, keep the timeline silent. Do not claim a voice was rendered when it was not.

## Build, review, and deliver

Run these steps from the independent project folder:

```bash
python3 scripts/build.py all --data data/my-episode.json
python3 tests/edge_cases.py
npm run check
npm run dev -- --background
npx --yes hyperframes@0.8.133 preview --status
```

Review the opening after its reveal, contents page, at least one story page, every C/D page used, and the closing. Check title fit, image/source labels, transitions, subtitle-safe space, and any voice alignment. Stop the preview service when done:

```bash
npx --yes hyperframes@0.8.133 preview --stop
npm run render -- --output out/my-episode.mp4
python3 scripts/export_cover.py out/my-episode.mp4 --output out/my-episode-cover.png
```

The cover exporter captures the complete 1920 × 1080 opening at 1.6 seconds by default. Inspect the PNG to confirm the full title and date card have settled and remain inside the frame; change `--at` if the cover was redesigned. Do not use a mid-transition or cropped frame as the cover.

Deliver the MP4, separate complete cover PNG, final episode JSON, and dated sources/media ledger. State that the video is landscape; this package has an optional portrait cover but no vertical full-video timeline. If the preview service, dependencies, source verification, or rendering fails, report the exact limit and do not present an unchecked render as complete.
