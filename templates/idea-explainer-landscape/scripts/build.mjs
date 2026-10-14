import { spawnSync } from "node:child_process";
import path from "node:path";
const data = process.argv[2] ? path.resolve(process.argv[2]) : path.resolve("data/sample-episode.json");
const env = { ...process.env, EPISODE_DATA: data };
for (const args of [["source/build.mjs"], ["scripts/modularize.mjs"]]) {
  const result = spawnSync(process.execPath, args, { stdio: "inherit", env });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
for (const [from, to] of [["dist/index.html","index.html"],["dist/preview.html","preview.html"],["dist/pages.json","pages.json"],["dist/shotlist.csv","shotlist.csv"]]) {
  const result = spawnSync("cp", [from, to], { stdio: "inherit" });
  if (result.status !== 0) process.exit(result.status ?? 1);
}
