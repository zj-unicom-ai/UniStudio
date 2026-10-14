# Tools, environment, and bundled assets

| Tool or asset | Version / purpose | Included or required |
| --- | --- | --- |
| HyperFrames | `0.8.145`; check, preview, render | Pinned in `package.json`; Node.js/npm and first-run network access required |
| HTML, CSS, JavaScript | Timeline and animated pages | Original project source in `source/` |
| GSAP | `3.15.0`; seekable animation | `vendor/gsap.min.js`; subject to the [GSAP Standard License](https://gsap.com/standard-license/) |
| Python 3 | Optional narration helper | Standard library only |
| VoiceStudio-compatible API | Optional speech generation | Not bundled; provide your own endpoint and authorized voice |
| Chromium and FFmpeg | HyperFrames preview/render | Install requirements for HyperFrames CLI on your system |
| Noto Sans SC / Noto Serif SC | Chinese typography | Variable WOFF2 and OFL texts in `fonts/` |
| Narration WAVs | Bundled demo audio | In `assets/audio/`; rights described in SOURCES.md |
| Cover art and illustrations | Episode visuals | Cover image and SVG source included; see SOURCES.md |

The sample rebuild works with bundled audio and does not call a speech service. The package contains no AI model, speech-model weights, API credentials, or private voice ID.

## License boundaries

- Original template code: [MIT](LICENSE).
- Noto fonts: SIL Open Font License texts are included in `fonts/`.
- GSAP: upstream notice is embedded in `vendor/gsap.min.js`; see the linked Standard License.
- Demo text, cover art, illustrations, narration, and rendered sample are not relicensed by MIT. See [SOURCES.md](SOURCES.md).
