// Editable episode content lives in data/sample-episode.json.
import fs from "node:fs";
import path from "node:path";
const file = path.resolve(process.env.EPISODE_DATA || "data/sample-episode.json");
const data = JSON.parse(fs.readFileSync(file, "utf8"));
export const EPISODE = data.episode;
export const PAGES = data.pages;
