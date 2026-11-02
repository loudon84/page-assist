#!/usr/bin/env node
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { collectSource } from "./source.mjs"

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..")
const output = process.argv[process.argv.indexOf("--output") + 1] || path.join(repoRoot, "artifacts/acceptance")
const files = ["run-index.json", "run-index-node.json"].map((name) => path.join(output, name)).filter((file) => fs.existsSync(file))
const runs = []
for (const file of files) {
  const payload = JSON.parse(fs.readFileSync(file, "utf8"))
  for (const row of payload.runs || []) {
    runs.push(row)
  }
}
const combined = {
  schema_version: 2,
  source: collectSource(repoRoot),
  runs
}
const dest = path.join(output, "run-index-combined.json")
fs.writeFileSync(dest, JSON.stringify(combined, null, 2))
console.log(dest)
