// Bring the humans 03 — make.fun TikTok ad entry.
//
// This program does one small job: it takes VIDEO.json, the file that
// names the TikTok video this entry points at, and copies it into the
// output folder the grader reads. It touches nothing else, talks to no
// network, and reads no clock.
//
// Usage: node main.ts [VIDEO.json] [outdir]
//   VIDEO.json defaults to the file beside this program.
//   outdir defaults to "out".

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";

const source = process.argv[2] ?? join(dirname(process.argv[1]), "VIDEO.json");
const outdir = process.argv[3] ?? "out";

// Read the descriptor first so a broken file fails loudly here,
// before anything is written anywhere. A missing or empty "url"
// means the video has not been posted yet, which is also an error.
const raw = readFileSync(source, "utf8");
let descriptor: unknown;
try {
  descriptor = JSON.parse(raw);
} catch {
  console.error(`VIDEO.json at ${source} is not valid JSON`);
  process.exit(1);
}

if (
  typeof descriptor !== "object" ||
  descriptor === null ||
  typeof (descriptor as { url?: unknown }).url !== "string" ||
  (descriptor as { url: string }).url.length === 0
) {
  console.error(`VIDEO.json at ${source} has no "url" string`);
  process.exit(1);
}

mkdirSync(outdir, { recursive: true });
copyFileSync(source, join(outdir, "VIDEO.json"));
console.log(`Copied VIDEO.json to ${outdir}/VIDEO.json`);
