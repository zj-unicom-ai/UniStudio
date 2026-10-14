---
name: idea-explainer-landscape
description: Create a Chinese-language long-form landscape explainer from a sourced concept using the bundled HyperFrames project and editable episode data.
---

# Concept Explainer — Landscape Skill

Use for horizontal narrated explainers connecting an abstract idea to everyday situations and practical exercises.

## Workflow

1. Read this template's README, USAGE, TOOLS, and SOURCES. Treat the supplied episode as demo material, not verified research for new work.
2. Prepare a sourced outline: relatable opening, concrete scenarios, explanation, practical application, recap, and concise outro. Preserve supplied wording as requested. Record factual and historical sources in the new project's SOURCES.md.
3. Copy this entire template directory to a separate project. Do not build, render, or store generated output inside the shared template.
4. Edit `data/sample-episode.json`. Keep narration, screen text, cue phrases, page IDs, illustration keys, and chapter indexes aligned. Record provenance for added media.
5. Reuse bundled WAVs only for the sample. For new narration, use user-provided or authorized voice settings. The helper reads its endpoint and voice identifier from environment variables; never write credentials or private IDs into source.
6. Run `npm run build` and `npm run check`. Preview opening, representative explanation and practice pages, audio transitions, and outro; fix issues before rendering.
7. Render with `npm run render`. Check duration, sound, opening cover, closing card, and output path.

## Deliverables

Provide the final MP4, cover image, editable project, source/rights ledger, and review notes. Report output format, duration, and any unverified facts or media rights.
