#!/usr/bin/env node
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..")
const root = path.join(repoRoot, "artifacts/acceptance")

const rank = { FAIL: 4, BLOCKED: 3, SKIPPED: 2, PASS: 1 }
let worst = "PASS"
const byGate = {
  "G-DOC": [],
  "G-BROWSER": [],
  "G-PACKAGE": [],
  "G-PROTOCOL": [],
  "G-DEPLOY": [],
  "G-LIVE": [],
  "G-FI": []
}

if (fs.existsSync(root)) {
  for (const ac of fs.readdirSync(root)) {
    if (!fs.statSync(path.join(root, ac)).isDirectory()) continue
    const runs = fs.readdirSync(path.join(root, ac)).filter((r) =>
      fs.statSync(path.join(root, ac, r)).isDirectory()
    )
    if (!runs.length) continue
    const latest = runs
      .map((r) => ({ r, mtime: fs.statSync(path.join(root, ac, r)).mtimeMs }))
      .sort((a, b) => a.mtime - b.mtime)
      .at(-1).r
    const payload = JSON.parse(fs.readFileSync(path.join(root, ac, latest, "run.json"), "utf8"))
    if (rank[payload.status] > rank[worst]) worst = payload.status
    if (ac.startsWith("A-EVID-001")) byGate["G-DOC"].push(payload.status)
    if (ac.startsWith("A-UI") || ac.startsWith("A-COMPAT") || ac.startsWith("A-CONTEXT")) byGate["G-BROWSER"].push(payload.status)
    if (ac.startsWith("A-PACKAGE") || ac.startsWith("A-HOST")) byGate["G-PACKAGE"].push(payload.status)
    if (ac.startsWith("A-AUTH") || ac.startsWith("A-THREAD") || ac.startsWith("A-TURN")) byGate["G-PROTOCOL"].push(payload.status)
    if (ac.startsWith("A-DEPLOY") || ac.startsWith("A-UPGRADE")) byGate["G-DEPLOY"].push(payload.status)
    if (ac === "A-EVID-003") byGate["G-LIVE"].push(payload.status)
    if (ac.startsWith("FI-")) byGate["G-FI"].push(payload.status)
  }
}

const gRelease = worst === "PASS" ? "PASS" : worst
const report = { worst, gRelease, byGate, note: "BLOCKED live/systemd evidence is honest and does not count as PASS" }
const dest = path.join(repoRoot, "artifacts/acceptance/G-RELEASE.json")
fs.mkdirSync(path.dirname(dest), { recursive: true })
fs.writeFileSync(dest, JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
process.exit(gRelease === "FAIL" ? 1 : gRelease === "BLOCKED" ? 2 : gRelease === "SKIPPED" ? 3 : 0)
