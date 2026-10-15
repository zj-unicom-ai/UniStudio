import { readFile, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { referenceBackground, referenceAmbient } from "./reference-background.mjs";

const root = process.cwd();
const configPath = path.join(root, "data/episode.json");
const templatePath = path.join(root, "templates/index.template");
const config = JSON.parse(await readFile(configPath, "utf8"));
const template = await readFile(templatePath, "utf8");
const envelopePath = config.story.narration.envelopePath;
const audioPath = config.story.narration.audioPath;
const envelope = JSON.parse(await readFile(path.join(root, envelopePath), "utf8"));

function fail(message) {
  console.error(`Build failed: ${message}`);
  process.exit(1);
}

function escapeHtml(value) {
  return String(value).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}

function safeJson(value) {
  return JSON.stringify(value).replaceAll("<", "\\u003c").replaceAll(">", "\\u003e").replaceAll("&", "\\u0026");
}

function wavDuration(buffer) {
  if (buffer.toString("ascii", 0, 4) !== "RIFF" || buffer.toString("ascii", 8, 12) !== "WAVE") fail(`${audioPath} is not a WAV file.`);
  let sampleRate = 0;
  let channels = 0;
  let bits = 0;
  let dataBytes = 0;
  for (let offset = 12; offset + 8 <= buffer.length;) {
    const id = buffer.toString("ascii", offset, offset + 4);
    const size = buffer.readUInt32LE(offset + 4);
    const start = offset + 8;
    if (id === "fmt " && size >= 16) {
      channels = buffer.readUInt16LE(start + 2);
      sampleRate = buffer.readUInt32LE(start + 4);
      bits = buffer.readUInt16LE(start + 14);
    }
    if (id === "data") dataBytes = size;
    offset = start + size + (size % 2);
  }
  if (!sampleRate || !channels || !bits || !dataBytes) fail(`Could not read duration fields from ${audioPath}.`);
  return dataBytes / (sampleRate * channels * (bits / 8));
}

function validate() {
  if (!/^\d{4}\.\d{2}\.\d{2}$/.test(config.brand.publishDate)) fail("publishDate must be YYYY.MM.DD.");
  if (config.video.width !== 1080 || config.video.height !== 1920 || config.video.fps !== 30) fail("Video format must remain 1080x1920 at 30 fps.");
  if (config.video.showProgress || config.video.showTimeOfDay || config.video.showImageIndex || config.video.showCountdown) fail("Progress, time of day, image index, and countdown displays must stay disabled.");
  if (!Array.isArray(config.story.imageAssets) || config.story.imageAssets.length < 4) fail("Each video requires at least four image assets.");
  if (config.story.imageTimeline.length !== config.story.imageAssets.length) fail("Each image asset needs one semantic timeline entry.");
  if (new Set(config.story.imageAssets.map(asset => asset.id)).size !== config.story.imageAssets.length || new Set(config.story.imageTimeline.map(entry => entry.assetId)).size !== config.story.imageAssets.length) fail("Each video must show at least four separately registered images.");
  if (config.story.summarySegments.length < 3 || config.story.summarySegments.length > 6) fail("Add three to six summary segments.");
  if (!config.story.narration || !existsSync(path.join(root, audioPath))) fail(`Narration audio is missing: ${audioPath}`);
  if (!existsSync(path.join(root, envelopePath)) || !Array.isArray(envelope.values) || !envelope.values.length) fail(`RMS envelope is missing or empty: ${envelopePath}`);
  if (config.story.titleParts.length < 1 || config.story.titleParts.length > 2) fail("The title must use one or two lines.");
  for (const asset of config.story.imageAssets) if (!existsSync(path.join(root, asset.path))) fail(`Image asset is missing: ${asset.path}`);
  if (config.visualStyle?.backgroundPath && !existsSync(path.join(root, config.visualStyle.backgroundPath))) fail("The reference background plate is missing.");
}

validate();
const audioDuration = wavDuration(await readFile(path.join(root, audioPath)));
const audioStart = config.story.narration.startsAtSec;
const duration = Number((audioStart + audioDuration + config.motion.endHoldSec).toFixed(3));
if (duration > 120) fail(`Narration produces a ${duration.toFixed(1)} second video, above the 120 second limit.`);
if (Math.abs(envelope.durationSec - audioDuration) > 0.12) fail("RMS envelope duration does not match the narration WAV.");

let previous = -1;
for (const item of config.story.imageTimeline) {
  if (!Number.isFinite(item.startSec) || item.startSec < 0 || item.startSec <= previous || item.startSec >= audioDuration) fail("Image timeline starts must be ordered within the narration duration.");
  previous = item.startSec;
}
previous = -1;
for (const item of config.story.summarySegments) {
  if (!Number.isFinite(item.startSec) || item.startSec < 0 || item.startSec <= previous || item.startSec >= audioDuration) fail("Summary starts must be ordered within the narration duration.");
  if (item.text.length > 75) fail(`Summary segment is longer than 75 characters: ${item.kicker}`);
  previous = item.startSec;
}

const weightOf = text => [...text].reduce((sum, char) => sum + (char.charCodeAt(0) < 128 ? .58 : 1), 0);
const totalTitleWeight = config.story.titleParts.reduce((sum, part) => sum + weightOf(part.text), 0);
const singleLineTitleSize = Math.min(100, Math.floor(904 / totalTitleWeight));
const multiline = singleLineTitleSize < 60;
const titleFontSize = multiline ? Math.min(90, ...config.story.titleParts.map(part => Math.floor(928 / weightOf(part.text)))) : singleLineTitleSize;
if (titleFontSize < 60) fail("Title will not fit at the 60 px minimum; shorten the headline.");
const titleLines = config.story.titleParts.map(part => `<span class="title-line${part.accent ? " accent" : ""}">${escapeHtml(part.text)}</span>`).join("");
const subtitleWeight = [...config.story.subtitle].reduce((sum, char) => sum + (char.charCodeAt(0) < 128 ? 0.56 : 1), 0);
const subtitleSize = Math.min(multiline ? 40 : 62, Math.floor(929 / subtitleWeight));
if (subtitleSize < 30) fail("Subtitle is too long for the fixed title area; shorten it before building.");

const imageLookup = new Map(config.story.imageAssets.map((asset) => [asset.id, asset]));
const imageTransition = config.motion.imageTransitionSec;
const heroScenes = config.story.imageTimeline.map((entry, index) => {
  const asset = imageLookup.get(entry.assetId);
  if (!asset) fail(`No image asset matches timeline id ${entry.assetId}.`);
  const next = config.story.imageTimeline[index + 1]?.startSec;
  const sceneDuration = next === undefined ? duration - entry.startSec : next - entry.startSec + imageTransition;
  return `<img id="hero-${escapeHtml(asset.id)}" class="hero-scene clip" data-start="${entry.startSec}" data-duration="${sceneDuration.toFixed(3)}" data-track-index="${index + 1}" data-layout-allow-overflow src="${escapeHtml(asset.path)}" alt="${escapeHtml(asset.alt)}" />`;
}).join("\n        ");

const summaryScenes = config.story.summarySegments.map((entry, index) => {
  const next = config.story.summarySegments[index + 1]?.startSec;
  const sceneDuration = next === undefined ? duration - entry.startSec : next - entry.startSec + config.motion.summaryTransitionSec;
  return `<p id="summary-segment-${index + 1}" class="summary-scene clip summary-text" data-start="${entry.startSec}" data-duration="${sceneDuration.toFixed(3)}" data-track-index="${index + config.story.imageAssets.length + 1}" data-layout-allow-overlap>${escapeHtml(entry.text)}</p>`;
}).join("\n      ");

const ambient = referenceAmbient(config);
const brandChars = [...config.brand.name];
const brandHtml = `${escapeHtml(brandChars.slice(0, -2).join(""))}<span class="accent">${escapeHtml(brandChars.slice(-2).join(""))}</span>`;
const replacements = {
  "{{DURATION}}": duration.toFixed(3),
  "{{AUDIO_DURATION}}": audioDuration.toFixed(3),
  "{{AUDIO_START}}": audioStart.toFixed(3),
  "{{AUDIO_PATH}}": escapeHtml(audioPath),
  "{{BRAND}}": brandHtml,
  "{{DATE}}": escapeHtml(config.brand.publishDate),
  "{{TITLE_LINES}}": titleLines,
  "{{TITLE_LAYOUT_CLASS}}": multiline ? "is-multiline" : "",
  "{{HEADLINE_STYLE}}": `font-size:${titleFontSize}px`,
  "{{SUBTITLE_STYLE}}": `font-size:${subtitleSize}px;${multiline ? "top:420px" : ""}`,
  "{{SUBTITLE}}": escapeHtml(config.story.subtitle),
  "{{HERO_SCENES}}": heroScenes,
  "{{SUMMARY_SCENES}}": summaryScenes,
  "{{FIRST_KICKER}}": escapeHtml(config.story.summarySegments[0].kicker),
  "{{REFERENCE_BACKGROUND}}": referenceBackground(duration.toFixed(3), config.visualStyle?.backgroundPath),
  "{{REFERENCE_WAVE_TEXTURE}}": config.visualStyle?.backgroundPath ? `<div id="reference-wave-flow" class="clip" data-start="0" data-duration="${duration.toFixed(3)}" data-track-index="10" data-layout-allow-overflow style="background-image:url(&quot;${escapeHtml(config.visualStyle.backgroundPath)}&quot;)" aria-hidden="true"></div>` : "",
  "{{WAVE_PATHS}}": ambient.wavePaths,
  "{{WAVE_GLOWS}}": ambient.waveGlows,
  "{{WAVE_REFLECTIONS}}": ambient.waveReflections,
  "{{AUDIO_BARS}}": ambient.audioBars,
  "{{BAR_GLOWS}}": ambient.barGlows,
  "{{BAR_REFLECTIONS}}": ambient.barReflections,
  "{{PARTICLES}}": ambient.particles,
  "{{PARTICLE_GLOWS}}": ambient.particleGlows,
  "{{ISSUE_JSON}}": safeJson(config),
  "{{ENVELOPE_JSON}}": safeJson(envelope),
};

let html = template;
for (const [token, value] of Object.entries(replacements)) html = html.replaceAll(token, value);
if (/\{\{[A-Z_]+\}\}/.test(html)) fail("An unresolved template token remains in index.html.");
await writeFile(path.join(root, "index.html"), html, "utf8");
console.log(JSON.stringify({ output: "index.html", audioDurationSec: Number(audioDuration.toFixed(3)), totalDurationSec: duration, imageCount: heroScenes ? config.story.imageAssets.length : 0 }));
