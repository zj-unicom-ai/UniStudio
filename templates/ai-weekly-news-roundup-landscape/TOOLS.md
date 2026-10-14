# Tools, environment, and included assets

This package is a local HTML video project. It does not call an AI model or a hosted rendering service. The generated sample can be built from the files in this folder once the listed local tools are available.

| Tool or asset | Purpose | Included or required |
| --- | --- | --- |
| HyperFrames `0.8.133` | Project validation, preview, timeline rendering, and MP4 export | Version pinned in `package.json`; Node.js/npm and first-run network access required for `npx` |
| Python 3 | Build pages, validate episode data, create a new project copy, measure WAV durations, and export a cover | Required; scripts use the Python standard library only |
| Chromium and FFmpeg | Browser-based frame rendering and MP4/PNG output | Install the runtime dependencies required by HyperFrames on the local computer |
| HTML, CSS, JavaScript, GSAP `3.14.2` | Page layout and seekable motion | Project source and `assets/vendor/gsap.min.js` are included |
| Noto Sans SC, ZCOOL QingKe HuangYou, JetBrains Mono | Chinese display/body text and compact labels | Font files and their OFL texts are included under `assets/fonts/` and `THIRD_PARTY_LICENSES/` |
| News photos, narration, music, sound effects | Optional episode-specific media | Not included. Add media you have rights to use and record its source and license |

The default project is silent and uses placeholder copy with no real news claims or photographs. `build.py` can add user-supplied narration from `assets/audio/` when a local `voice-manifest.json` is present. `make_voice_manifest.py` measures WAV duration; it does not generate speech. Choose and configure any TTS or recording tool separately. No local service URL, voice ID, account token, or author-specific media is required by this package.

The sample includes a horizontal video timeline at 1920 × 1080 and 30 fps. `compositions/cover-v.html` is a 1080 × 1920 cover artwork composition only; it is not a vertical full-video output.

## Third-party terms

- Template source: [MIT License](LICENSE).
- Noto Sans SC: [SIL Open Font License](THIRD_PARTY_LICENSES/Noto-Sans-SC-OFL.txt).
- ZCOOL QingKe HuangYou: [SIL Open Font License](THIRD_PARTY_LICENSES/ZCOOL-QingKe-HuangYou-OFL.txt).
- JetBrains Mono: [SIL Open Font License](THIRD_PARTY_LICENSES/JetBrains-Mono-OFL.txt).
- GSAP: [GSAP Standard License](https://gsap.com/community/standard-license/); the bundled file retains its upstream notice.

The template's MIT license does not replace the terms for bundled fonts or GSAP, nor does it grant rights to any photographs, audio, music, or other media added by a user.
