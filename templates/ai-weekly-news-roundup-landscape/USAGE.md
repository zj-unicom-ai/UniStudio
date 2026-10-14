# Usage

## 1. Prepare a working copy

Install Python 3, Node.js, and npm. From the template folder, create a separate project folder so generated compositions and episode data stay together:

```bash
python3 scripts/new_project.py ../my-ai-weekly-episode
cd ../my-ai-weekly-episode
cp data/sample-episode.json data/my-episode.json
```

The copy script refuses to overwrite an existing directory. It omits render output, caches, user-added photographs/audio, and private voice manifests.

The `npm` scripts pin HyperFrames to `0.8.133`. On first use, `npx` downloads that version, so network access is required. Preview and rendering also need the browser and FFmpeg environment described in [TOOLS.md](TOOLS.md).

## 2. Write and source the episode

Edit `data/my-episode.json`. Keep `SOURCES.md` for the episode-specific research ledger, or create a separate dated source file beside the JSON. Verify claims against primary sources when available, record publication dates and links, and distinguish confirmed facts from estimates or commentary. The package's default sample uses fictional placeholder stories and illustrative chart values; never present them as reporting.

Each episode contains `date`, `weekday`, `episode`, `branding`, `items`, and `recap`:

- `branding` controls the show name, cover text, ticker, commentary label, and closing copy. Keep the title compact and preview any longer replacement.
- `items` holds 3–10 stories. IDs should be unique and use letters, numbers, and hyphens. Every story needs `category`, `headline`, `toc_title`, `summary`, `source`, `comment`, and `layout`.
- `headline` should stay within 30 characters, `toc_title` within 14, `summary` within 70, `comment` within 45, and the displayed `source` within 12. The validator reports overlong text instead of shrinking it.
- `highlight` is optional and, when present, must be an exact continuous part of the headline.
- Every story uses layout `B`. Add `C` for a three-part explainer and provide `explain.what`, `explain.why`, and `explain.you` (up to 40 characters each). Add `D` for a data card and provide `data.big`, `data.title`, `data.note`, and two `data.bars` values from 0 to 100. A story cannot combine `C` and `D` on the same page entry.
- `recap` must contain one short line per story; each line is limited to 14 characters. Directory and recap spacing adjusts for 3–10 stories.

To add a photograph, place a licensed image in `assets/shots/` and set that story's `image` to its filename, such as `story-01.jpg`. Leave it `null` to show the designed placeholder. Record image source, license, and required credit in the episode's source ledger.

## 3. Build and check

```bash
python3 scripts/build.py all --data data/my-episode.json
python3 tests/edge_cases.py
npm run check
```

`all` rebuilds the root timeline, its story/page compositions, and their standalone review pages. Run it again whenever episode data or page source changes. Other supported targets are `cover`, `core`, and `pages`; see `python3 scripts/build.py --help` for the full list.

## 4. Preview, render, and export the cover

Start the preview server and check the important views before rendering:

```bash
npm run dev -- --background
npx --yes hyperframes@0.8.133 preview --status
# Review the complete opening, contents, a story, any C/D cards, and the closing.
npx --yes hyperframes@0.8.133 preview --stop
```

Render the full horizontal video, then export a separate PNG from the settled opening frame. This gives platforms a complete cover image instead of relying on a player thumbnail taken mid-animation:

```bash
mkdir -p out
npm run render -- --output out/my-episode.mp4
python3 scripts/export_cover.py out/my-episode.mp4 --output out/my-episode-cover.png
```

The cover extractor samples 1.6 seconds by default, after the title and date card have entered. Use `--at SECONDS` if your edited cover needs a different settled frame. It preserves the full 1920 × 1080 frame.

To render one page for review, for example the contents page:

```bash
npm run render -- --composition standalone/a-toc.html --output out/contents.mp4
```

The base sample is silent. Narration is optional: place your own WAV recordings in `assets/audio/` using the generated composition IDs as filenames (for example `b-news-01.wav`), then run `python3 scripts/make_voice_manifest.py`. The script writes `voice-manifest.json` with measured durations; rebuild and check the timeline before rendering. The package does not generate speech or include a TTS provider.

## Common issues

- **The preview still shows old copy:** rebuild with the intended `--data` file, then restart or refresh the preview.
- **A photograph is missing:** verify its filename and location under `assets/shots/`.
- **Text does not fit:** shorten it to the stated field limit and rebuild; do not hide overflow by shrinking all type.
- **Audio is missing or cut off:** confirm the WAV name matches a generated composition ID, regenerate the voice manifest, and check that the composition duration leaves enough room for the spoken line.
- **A vertical export is expected:** this package provides only a vertical cover composition. The full video timeline is landscape; a vertical program needs its own storyboard and layout review.
