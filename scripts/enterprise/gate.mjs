#!/usr/bin/env node
import crypto from "node:crypto"
import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { collectSource } from "./source.mjs"

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..")

const args = process.argv.slice(2)
const get = (flag, fallback) => {
  const i = args.indexOf(flag)
  return i >= 0 ? args[i + 1] : fallback
}

const requiredPath = get("--required", path.join(repoRoot, "contracts/octop-client/v1/required-acceptance.json"))
const runIndexPath = get("--run-index", "")
const manifestPath = get("--release-manifest", "")
const outputPath = get("--output", path.join(repoRoot, "artifacts/acceptance/G-RELEASE.json"))

const sha256 = (value) => crypto.createHash("sha256").update(value).digest("hex")
const readJson = (file) => JSON.parse(fs.readFileSync(file, "utf8"))

const fail = (reason, extra = {}) => {
  const report = {
    gRelease: "FAIL",
    exit_code: 1,
    reason,
    ...extra
  }
  fs.mkdirSync(path.dirname(outputPath), { recursive: true })
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2))
  console.log(JSON.stringify(report, null, 2))
  process.exit(1)
}

if (!requiredPath || !fs.existsSync(requiredPath)) {
  fail("REQUIRED_LIST_MISSING", { requiredPath })
}
if (!runIndexPath || !fs.existsSync(runIndexPath)) {
  fail("RUN_INDEX_MISSING", { runIndexPath })
}
if (!manifestPath || !fs.existsSync(manifestPath)) {
  fail("RELEASE_MANIFEST_MISSING", { manifestPath })
}

const required = readJson(requiredPath)
const runIndex = readJson(runIndexPath)
const manifest = readJson(manifestPath)
const source = collectSource(repoRoot)

if (required.schema_version !== 2) {
  fail("REQUIRED_SCHEMA_INVALID", { schema_version: required.schema_version })
}

const requiredTuples = []
for (const item of [...(required.acceptances || []), ...(required.failure_injections || [])]) {
  for (const mode of item.required_modes || []) {
    for (const parameterCase of item.parameter_cases || ["default"]) {
      requiredTuples.push({
        id: item.id,
        mode,
        parameter_case: parameterCase,
        required_gates: item.required_gates || ["G-EVID"],
        required: item.required !== false
      })
    }
  }
}

const selected = Array.isArray(runIndex.runs) ? runIndex.runs : []
const selectedKey = (row) => `${row.acceptance_id || row.id}|${row.mode}|${row.parameter_case || "default"}`
const byKey = new Map()
for (const row of selected) {
  const key = selectedKey(row)
  if (byKey.has(key)) {
    fail("EVIDENCE_INVALID", { reason: "duplicate required tuple", key })
  }
  byKey.set(key, row)
}

const missing = []
const blocked = []
const skipped = []
const failed = []
const invalid = []
const byGate = {
  "G-BUILD": [],
  "G-PROTOCOL": [],
  "G-SEC": [],
  "G-BROWSER": [],
  "G-DEPLOY": [],
  "G-LIVE": [],
  "G-FI": [],
  "G-EVID": []
}

const indexRoot = path.dirname(path.resolve(runIndexPath))

for (const tuple of requiredTuples) {
  const key = `${tuple.id}|${tuple.mode}|${tuple.parameter_case}`
  const row = byKey.get(key)
  if (!row) {
    missing.push(key)
    continue
  }
  const rel = row.run_json || row.path
  if (!rel) {
    invalid.push({ key, reason: "run_json missing" })
    continue
  }
  const runFile = path.isAbsolute(rel) ? rel : path.resolve(indexRoot, rel)
  if (!fs.existsSync(runFile)) {
    invalid.push({ key, reason: "run.json not found", runFile })
    continue
  }
  let payload
  try {
    payload = readJson(runFile)
  } catch (error) {
    invalid.push({ key, reason: "run.json unreadable" })
    continue
  }
  const bytes = fs.readFileSync(runFile)
  const actualHash = sha256(bytes)
  if (row.sha256 && row.sha256 !== actualHash) {
    invalid.push({ key, reason: "run.json hash mismatch", expected: row.sha256, actual: actualHash })
    continue
  }
  if (!Array.isArray(payload.assertions) || payload.assertions.length === 0) {
    invalid.push({ key, reason: "empty assertions" })
    continue
  }
  if (payload.assertions.some((item) => item.passed !== true) && payload.status === "PASS") {
    invalid.push({ key, reason: "PASS with failed assertion" })
    continue
  }
  if (payload.status === "BLOCKED") blocked.push(key)
  else if (payload.status === "SKIPPED") skipped.push(key)
  else if (payload.status !== "PASS") failed.push(key)
  for (const gate of tuple.required_gates) {
    if (!byGate[gate]) byGate[gate] = []
    byGate[gate].push(payload.status)
  }
}

const gateFail = (statuses) =>
  statuses.some((status) => status !== "PASS") || statuses.length === 0

const gBuild = gateFail(byGate["G-BUILD"]) ? "FAIL" : "PASS"
const gProtocol = gateFail(byGate["G-PROTOCOL"]) ? "FAIL" : "PASS"
const gSec = gateFail(byGate["G-SEC"]) ? "FAIL" : "PASS"
const gBrowser = gateFail(byGate["G-BROWSER"]) ? "FAIL" : "PASS"
const gDeploy = gateFail(byGate["G-DEPLOY"]) ? "FAIL" : "PASS"
const gLive = gateFail(byGate["G-LIVE"]) ? "FAIL" : "PASS"
const gFi = gateFail(byGate["G-FI"]) ? "FAIL" : "PASS"
const gEvid = missing.length || blocked.length || skipped.length || failed.length || invalid.length ? "FAIL" : "PASS"

const gRelease =
  !missing.length &&
  !blocked.length &&
  !skipped.length &&
  !failed.length &&
  !invalid.length &&
  gBuild === "PASS" &&
  gProtocol === "PASS" &&
  gSec === "PASS" &&
  gBrowser === "PASS" &&
  gDeploy === "PASS" &&
  gLive === "PASS" &&
  gFi === "PASS" &&
  gEvid === "PASS"
    ? "PASS"
    : "FAIL"

const report = {
  schema_version: 2,
  gRelease,
  exit_code: gRelease === "PASS" ? 0 : 1,
  source,
  manifest_sha256: sha256(fs.readFileSync(manifestPath)),
  required_tuples: requiredTuples.length,
  selected: selected.length,
  missing,
  blocked,
  skipped,
  failed,
  invalid,
  byGate: {
    "G-BUILD": gBuild,
    "G-PROTOCOL": gProtocol,
    "G-SEC": gSec,
    "G-BROWSER": gBrowser,
    "G-DEPLOY": gDeploy,
    "G-LIVE": gLive,
    "G-FI": gFi,
    "G-EVID": gEvid
  },
  note: "required BLOCKED/SKIPPED/missing/invalid evidence makes G-RELEASE FAIL"
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true })
fs.writeFileSync(outputPath, JSON.stringify(report, null, 2))
console.log(JSON.stringify(report, null, 2))
const blockedMeansFail = gRelease === "FAIL"
process.exit(blockedMeansFail ? 1 : 0)
