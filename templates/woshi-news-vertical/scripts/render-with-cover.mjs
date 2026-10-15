import { spawnSync } from "node:child_process";
import { mkdir, readdir, rm, copyFile } from "node:fs/promises";
import path from "node:path";

const root = process.cwd();
const version = "0.8.158";
const args = process.argv.slice(2);
const outputIndex = args.findIndex((arg) => arg === "--output" || arg === "-o");
const outputEquals = args.find((arg) => arg.startsWith("--output="));
const output = outputIndex >= 0
  ? args[outputIndex + 1]
  : outputEquals?.slice("--output=".length) ?? "renders/沃资讯-日期版.mp4";
const renderArgs = outputIndex >= 0 || outputEquals
  ? args
  : [...args, "--output", output];

function run(commandArgs) {
  const result = spawnSync("npx", ["--yes", `hyperframes@${version}`, ...commandArgs], {
    cwd: root,
    stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}

async function collectPngs(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await collectPngs(fullPath));
    else if (entry.isFile() && entry.name.toLowerCase().endsWith(".png")) files.push(fullPath);
  }
  return files;
}

run(["render", ...renderArgs]);

const outputPath = path.resolve(root, output);
const extension = path.extname(outputPath).toLowerCase();
if (![".mp4", ".mov", ".webm", ".mkv", ".gif"].includes(extension)) {
  console.log(`Rendered ${output}; cover export skipped for ${extension || "unknown output"} format.`);
  process.exit(0);
}

const captureDirectory = path.join(root, ".hyperframes", "artifacts", "cover-export");
await rm(captureDirectory, { recursive: true, force: true });
await mkdir(path.dirname(outputPath), { recursive: true });
run(["snapshot", root, "--at=0", `--output=${captureDirectory}`, "--no-end", "--describe=false"]);

const pngs = await collectPngs(captureDirectory);
if (pngs.length !== 1) {
  throw new Error(`Expected one opening-frame PNG from HyperFrames snapshot, found ${pngs.length}.`);
}

const coverPath = path.join(path.dirname(outputPath), `${path.basename(outputPath, extension)}-封面.png`);
await copyFile(pngs[0], coverPath);
await rm(captureDirectory, { recursive: true, force: true });
console.log(`Cover exported: ${path.relative(root, coverPath)}`);
