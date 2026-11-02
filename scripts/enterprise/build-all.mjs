#!/usr/bin/env node
import { spawnSync } from "node:child_process"
import path from "node:path"
import { fileURLToPath } from "node:url"

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..")
const steps = [
  ["bun", ["run", "build:chrome"]],
  ["bun", ["run", "build:firefox"]],
  ["bun", ["run", "build:edge"]]
]

for (const [cmd, args] of steps) {
  const result = spawnSync(cmd, args, { cwd: repoRoot, stdio: "inherit", shell: true })
  const code = result.status ?? 1
  if (code !== 0) {
    console.error(`build step failed: ${cmd} ${args.join(" ")} exit=${code}`)
    process.exit(code)
  }
}
