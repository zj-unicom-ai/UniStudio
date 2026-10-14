// Keep this episode as one seekable composition; attach narration as independent audio clips.
import fs from "node:fs";
import { EPISODE } from "../source/storyboard.mjs";
const pages = JSON.parse(fs.readFileSync("dist/pages.json", "utf8"));
const voice = JSON.parse(fs.readFileSync("voice-manifest.json", "utf8"));
const audio = voice.segments.map((segment) => {
  const page = pages.find((entry) => entry.id === segment.id);
  if (!page && !["welcome", "bridge"].includes(segment.id)) throw new Error(`Missing audio page: ${segment.id}`);
  const welcome = voice.segments.find((entry) => entry.id === "welcome");
  const start = segment.id === "welcome" ? 0
    : segment.id === "bridge" ? Math.round((welcome.duration_s + 0.15) * 1000) / 1000
    : Math.round((page.start + 0.35) * 1000) / 1000;
  return `<audio id="voice-${segment.id}" src="${segment.path}" data-start="${start}" data-duration="${segment.duration_s}" data-track-index="10" data-volume="1"></audio>`;
}).join("\n");
const indexPath = "dist/index.html";
const index = fs.readFileSync(indexPath, "utf8");
fs.writeFileSync(indexPath, index.replace("</body>", `${audio}\n</body>`));
const previewPath = "dist/preview.html";
const preview = fs.readFileSync(previewPath, "utf8")
  .replace(` data-composition-id="${EPISODE.id}"`, "")
  .replace(/<div id="yinian-outro-host"[^>]*><\/div>/, "");
fs.writeFileSync(previewPath, preview);
console.log(`Built single composition with ${voice.segments.length} narration clips.`);
