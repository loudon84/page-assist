import { execSync } from "node:child_process"
import crypto from "node:crypto"
import fs from "node:fs"
import path from "node:path"

export const PA_BASELINE = "ff1df1ce4df8b3d12be231fb40857fd3a46fc88c"
export const OC_BASELINE = "e3041c452ffc870f754378bd99d964349580d3f9"

const git = (repo, args) => {
  try {
    return execSync(`git ${args}`, { cwd: repo, encoding: "utf8" }).trim()
  } catch {
    return ""
  }
}

export function collectSource(repoRoot, octopRoot = process.env.OCTOP_REPO || "E:\\\\git\\\\octop") {
  const paSha = git(repoRoot, "rev-parse HEAD") || "UNKNOWN"
  const branch = git(repoRoot, "rev-parse --abbrev-ref HEAD") || "UNKNOWN"
  const porcelain = git(repoRoot, "status --porcelain")
  const dirty = Boolean(porcelain)
  const dirtyHash = dirty ? crypto.createHash("sha256").update(porcelain).digest("hex") : null
  const ocExists = fs.existsSync(octopRoot)
  const ocSha = ocExists ? git(octopRoot, "rev-parse HEAD") || null : null
  return {
    page_assist_baseline: PA_BASELINE,
    page_assist_implemented_sha: paSha,
    octop_baseline: OC_BASELINE,
    octop_patched_sha: ocSha,
    branch,
    dirty,
    dirty_manifest_sha256: dirtyHash,
    page_assist_sha: paSha,
    octop_baseline_sha: OC_BASELINE
  }
}

export const LIVE_FIELDS = [
  "instance_role",
  "instance_id",
  "releases_root",
  "state_root",
  "db_identity",
  "python",
  "unit",
  "service_user",
  "expected_exec_argv",
  "public_origin",
  "health_probe",
  "client_registrations",
  "baseline_release",
  "baseline_manifest_sha256",
  "release_manifest",
  "wheelhouse",
  "requirements_lock",
  "config",
  "secret_references",
  "live_test_identities"
]

export function missingLiveFields(env) {
  if (!env) return [...LIVE_FIELDS]
  return LIVE_FIELDS.filter((field) => {
    const value = env[field]
    return value === undefined || value === null || value === "" || (Array.isArray(value) && value.length === 0)
  })
}

export function loadEnvFile(envPath) {
  if (!envPath) return null
  return JSON.parse(fs.readFileSync(path.resolve(envPath), "utf8"))
}
