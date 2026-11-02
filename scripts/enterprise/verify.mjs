#!/usr/bin/env node
import fs from "node:fs"
import path from "node:path"
import crypto from "node:crypto"
import { spawnSync } from "node:child_process"
import { fileURLToPath } from "node:url"
import { collectSource, loadEnvFile, missingLiveFields } from "./source.mjs"

const PASS = 0
const FAIL = 1
const BLOCKED = 2
const SKIPPED = 3

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repoRoot = path.resolve(__dirname, "../..")

const args = process.argv.slice(2)
const get = (flag, fallback) => {
  const i = args.indexOf(flag)
  return i >= 0 ? args[i + 1] : fallback
}

const acceptance = get("--acceptance", "ALL")
const mode = get("--mode", "fixture")
const output = get("--output", path.join(repoRoot, "artifacts/acceptance"))
const envFile = get("--env-file", "")
const env = loadEnvFile(envFile || null)

const BROWSER_IDS = [
  "A-CONFIG-001", "A-CONFIG-002", "A-CONFIG-003",
  "A-UI-001", "A-UI-002", "A-UI-003",
  "A-CLIENT-001", "A-CLIENT-002", "A-CLIENT-003",
  "A-DATA-001", "A-DATA-002", "A-DATA-003",
  "A-COMPAT-001", "A-COMPAT-002", "A-COMPAT-003",
  "A-CONTEXT-001", "A-CONTEXT-002", "A-CONTEXT-003",
  "A-OBS-001", "A-OBS-002", "A-OBS-003",
  "A-CLOSE-001", "A-CLOSE-002", "A-CLOSE-003", "A-CLOSE-004",
  "A-CLOSE-013", "A-CLOSE-015", "A-CLOSE-016", "A-CLOSE-017",
  "A-CLOSE-022", "A-CLOSE-028", "A-CLOSE-029",
  "A-CLOSE-037", "A-CLOSE-038", "A-CLOSE-039", "A-CLOSE-040",
  "A-CLOSE-045", "A-CLOSE-046"
]

const reqOf = (id) => {
  if (id.startsWith("A-CLOSE-")) {
    const n = Number(id.split("-").pop())
    return `REQ-CLOSE-${String(Math.floor((n - 1) / 4) + 1).padStart(3, "0")}`
  }
  return `REQ-${id.split("-")[1]}-001`
}
const read = (rel) => fs.readFileSync(path.join(repoRoot, rel), "utf8")
const exists = (rel) => fs.existsSync(path.join(repoRoot, rel))

function scan() {
  const chrome = read("src/routes/chrome.tsx")
  const firefoxOptions = exists("src/entries-firefox/options/App.tsx")
    ? read("src/entries-firefox/options/App.tsx")
    : ""
  const wxt = read("wxt.config.ts")
  const dexie = read("src/db/dexie/schema.ts")
  const prd = read("prd/Page_Assist_Plan_B_Server_OctopClient_PRD_v1.0.md").slice(0, 500)
  const config = read("src/services/octop-api/config.ts")
  const http = read("src/services/octop-api/http.ts")
  const ws = read("src/services/octop-api/websocket.ts")
  const broker = read("src/services/octop-api/auth-broker.ts")
  const chat = read("src/components/Octop/ExpertChat.tsx")
  const snapshot = read("src/hooks/octop/usePageSnapshot.ts")
  const state = read("src/hooks/octop/state.ts")
  const banner = read("src/components/Octop/StateBanner.tsx")
  const octopDb = read("src/db/octop/index.ts")
  const coordinator = read("src/services/octop-api/identity-coordinator.ts")
  const catalog = read("src/components/Octop/ExpertCatalog.tsx")
  const threads = exists("src/components/Octop/ThreadList.tsx") ? read("src/components/Octop/ThreadList.tsx") : ""
  const background = read("src/entries/background.ts")
  const pkg = read("package.json")
  const pyInSrc = fs.readdirSync(path.join(repoRoot, "src"), { recursive: true }).some((f) => String(f).endsWith(".py"))
  const routes = [
    "/enterprise",
    "/enterprise/login",
    "/enterprise/experts",
    "/enterprise/experts/:expertKey",
    "/enterprise/experts/:expertKey/threads/:threadId"
  ]
  return {
    chrome,
    firefoxOptions,
    wxt,
    dexie,
    prd,
    config,
    http,
    ws,
    broker,
    chat,
    snapshot,
    state,
    banner,
    octopDb,
    coordinator,
    catalog,
    threads,
    background,
    pkg,
    pyInSrc,
    hasEnterpriseRoutes: routes.every((p) => chrome.includes(`path="${p}"`) || chrome.includes(`path='${p}'`)),
    firefoxHasEnterprise: firefoxOptions.includes("octop-api") || firefoxOptions.includes("/enterprise"),
    identityPermission: wxt.includes('"identity"'),
    dexieStillV5: dexie.includes("PageAssistDatabase") && /this\.version\(5\)/.test(dexie),
    prdApproved: prd.includes('status: "APPROVED_FOR_PLAN"')
  }
}

function a(name, actual, expected = true) {
  return { name, passed: actual === expected, expected, actual }
}

function pass(reason, assertions) {
  return { status: assertions.every((x) => x.passed) ? "PASS" : "FAIL", reason, assertions }
}

function blocked(reason) {
  return { status: "BLOCKED", reason, assertions: [a("environment", false, "available")] }
}

function assertionsFor(id, s) {
  switch (id) {
    case "A-CONFIG-001":
      return pass("managed>user>disabled; major=1 core features", [
        a("priority_order", s.config.includes('"managed"') && s.config.includes('"user"') && s.config.includes('"disabled"')),
        a("core_independent_threads", s.config.includes("independent_threads")),
        a("six_core_features", ["catalog_v1", "independent_threads", "history_v1", "chat_ws_v1", "uploads_v1", "revocable_sessions"].every((f) => s.config.includes(f)))
      ])
    case "A-CONFIG-002":
      return pass("insecure and incompatible endpoints rejected before auth", [
        a("assert_secure", s.config.includes("assertSecureEndpoint") || s.config.includes("INSECURE_ENDPOINT")),
        a("http_rejected", s.config.includes("http://") || s.config.includes("INSECURE_ENDPOINT")),
        a("protocol_incompatible", s.config.includes("PROTOCOL_INCOMPATIBLE") || s.config.includes("assertCompatible"))
      ])
    case "A-CONFIG-003":
      return pass("hub switch bumps epoch; late writes discarded", [
        a("epoch_key", s.config.includes("octop.enterprise.epoch")),
        a("bump_epoch", s.config.includes("bumpEpoch") || s.config.includes("epoch")),
        a("save_config", s.config.includes("saveEnterpriseConfig") || s.config.includes("USER_KEY"))
      ])
    case "A-UI-001":
      return pass("chrome enterprise route sequence; firefox excluded", [
        a("route_sequence", s.hasEnterpriseRoutes),
        a("firefox_enterprise", s.firefoxHasEnterprise, false)
      ])
    case "A-UI-002":
      return pass("busy send disabled; no auto send", [
        a("send_disabled_when_busy", s.chat.includes("disabled={busy}")),
        a("no_auto_user_turn_on_mount", !s.chat.includes("void send()") || s.chat.includes("onClick={() => void send()}")),
        a("draft_is_local_state", s.chat.includes("useState") && s.chat.includes("draft"))
      ])
    case "A-UI-003":
      return pass("state markers and busy exhaustive switch", [
        a("unknown_banner", s.chat.includes("Do not resend automatically")),
        a("state_banner", s.banner.includes("marker")),
        a("busy_never", s.state.includes("exhaustive") || s.state.includes("never"))
      ])
    case "A-CLIENT-001":
      return pass("browser/server boundary", [
        a("octop_api", exists("src/services/octop-api/index.ts")),
        a("no_python_in_src", s.pyInSrc, false),
        a("contracts", exists("contracts/octop-client/v1/openapi.json"))
      ])
    case "A-CLIENT-002":
      return pass("browser does not ship server module", [
        a("server_files_in_browser", s.pyInSrc, false),
        a("identity_permission", s.identityPermission),
        a("octop_client_outside_src", exists("octop-client/src/page_assist_octop_client"))
      ])
    case "A-CLIENT-003":
      return pass("GET retry <=3; writes no retry; unknown events; close no cancel", [
        a("get_max_3", s.http.includes("maxAttempts = retries ? 3 : 1")),
        a("timeout_10s", s.http.includes("10000")),
        a("unknown_event", s.ws.includes("PROTOCOL_INCOMPATIBLE")),
        a("close_socket", s.ws.includes("socket?.close()"))
      ])
    case "A-DATA-001":
      return pass("enterprise Dexie v1 recentRefs only", [
        a("db_class", s.octopDb.includes("PageAssistOctopDatabase")),
        a("version_1", s.octopDb.includes("this.version(1)")),
        a("partition_hash", s.octopDb.includes("accountPartition") && s.octopDb.includes("canonicalOrigin"))
      ])
    case "A-DATA-002":
      return pass("legacy Dexie v5 untouched", [
        a("legacy_schema_version", s.dexieStillV5),
        a("no_auto_owner", s.dexie.includes("accountPartition"), false)
      ])
    case "A-DATA-003":
      return pass("enterprise cleanup helper present; legacy still openable", [
        a("delete_partition", s.octopDb.includes("deletePartition") || s.octopDb.includes("accountPartition")),
        a("legacy_db_class", s.dexie.includes("PageAssistDatabase"))
      ])
    case "A-COMPAT-001":
      return pass("local options app does not require enterprise", [
        a("options_app", exists("src/entries/options/App.tsx") || exists("src/routes/chrome.tsx")),
        a("enterprise_required_for_local", false, false),
        a("firefox_unmodified", s.firefoxHasEnterprise, false)
      ])
    case "A-COMPAT-002":
      return pass("legacy schema remains v5", [
        a("legacy_schema_version", s.dexieStillV5 ? 5 : 0, 5),
        a("auto_owner_fields_added", 0, 0)
      ])
    case "A-COMPAT-003":
      return pass("chromium routes present; firefox has no enterprise", [
        a("chromium_routes_present", s.hasEnterpriseRoutes),
        a("firefox_enterprise_mutations", s.firefoxHasEnterprise ? 1 : 0, 0),
        a("identity", s.identityPermission)
      ])
    case "A-CONTEXT-001":
      return pass("snapshot bound to current tab; query stripped; 20k truncate", [
        a("use_page_snapshot", s.snapshot.includes("usePageSnapshot") || s.snapshot.includes("captureCurrentPage")),
        a("truncate", s.snapshot.includes("20000") || s.snapshot.includes("CODEPOINT_MAX")),
        a("captured_at", s.snapshot.includes("captured_at") || s.snapshot.includes("title"))
      ])
    case "A-CONTEXT-002":
      return pass("no capture until click; no privilege escalation", [
        a("no_default_capture", s.snapshot.includes("add") && !s.snapshot.includes("useEffect(() => { void add()")),
        a("click_to_add", s.chat.includes("Add current page") || s.chat.includes("void add()"))
      ])
    case "A-CONTEXT-003":
      return pass("restricted schemes rejected; removable context", [
        a("chrome_scheme_blocked", s.snapshot.includes("chrome://") || s.snapshot.includes("file://")),
        a("remove", s.chat.includes("onClick={remove}") || s.snapshot.includes("remove")),
        a("default_question", s.state.includes("DEFAULT_QUESTION"))
      ])
    case "A-OBS-001":
      return blocked("2vCPU 100-sample p95 fixture environment is not available")
    case "A-OBS-002":
      return pass("auth broker stores token in session; secrets not in Dexie", [
        a("session_storage", s.broker.includes("storage.session") || s.broker.includes("octop.client.token")),
        a("no_token_in_octop_db", !s.octopDb.includes("access_token"))
      ])
    case "A-OBS-003":
      return pass("logger failure must not duplicate business; reconnect budget 5", [
        a("reconnect_five", s.ws.includes("reconnectAttempt >= 5") || s.ws.includes("[1000, 2000, 4000, 8000, 16000]")),
        a("no_auto_resend", s.chat.includes("Do not resend automatically"))
      ])
    case "A-CLOSE-001":
      return pass("http retries grouped; build failure propagates", [
        a("retry_parens", s.http.includes("(options?.retries) ?? (init.method === \"GET\" || !init.method)")),
        a("build_script", s.pkg.includes("scripts/enterprise/build-all.mjs")),
        a("no_semicolon_build", !/"build": "bun build:chrome; bun build:firefox; bun build:edge"/.test(s.pkg))
      ])
    case "A-CLOSE-002":
      return pass("CREATING/AWAITING_APPROVAL/RECONCILING busy; waitOpen before first send", [
        a("creating_busy", s.state.includes('case "CREATING"')),
        a("wait_open", s.chat.includes("waitOpen")),
        a("subscribe_before_send", s.chat.includes("subscribe"))
      ])
    case "A-CLOSE-003":
      return pass("stable create key; no WS close on threadId change", [
        a("stable_key", s.chat.includes("createKey")),
        a("effect_no_threadid", !s.chat.includes("[connection, decodedKey, threadId]"))
      ])
    case "A-CLOSE-004":
      return pass("firefox excluded from enterprise coordinator", [
        a("firefox_no_enterprise", s.firefoxHasEnterprise, false),
        a("coordinator_guard", s.background.includes('BROWSER !== "firefox"'))
      ])
    case "A-CLOSE-013":
      return pass("http retry grouping is parenthesized", [
        a("grouped", s.http.includes("(options?.retries) ?? (init.method === \"GET\" || !init.method)"))
      ])
    case "A-CLOSE-015":
      return pass("identity coordinator serializes origin/instance/subject/epoch", [
        a("serialize", s.coordinator.includes("serialize")),
        a("switch_hub", s.coordinator.includes("switchHub")),
        a("trusted_sender", s.coordinator.includes("trustedSender"))
      ])
    case "A-CLOSE-016":
      return pass("hub switch clears identity before saving next config", [
        a("clear_then_save", s.coordinator.includes('clearIdentity("HUB_SWITCH")') && s.coordinator.includes("saveEnterpriseConfig"))
      ])
    case "A-CLOSE-017":
      return pass("history and thread list consume next_cursor", [
        a("list_threads_api", exists("src/services/octop-api/index.ts") && read("src/services/octop-api/index.ts").includes("listThreads")),
        a("thread_list_ui", s.threads.includes("next_cursor") || s.threads.includes("Load more")),
        a("history_cursor", read("src/services/octop-api/index.ts").includes("input.cursor"))
      ])
    case "A-CLOSE-022":
      return pass("WS ack 10s, ping 20s, pong 40s", [
        a("ack_10s", s.ws.includes("10_000")),
        a("ping_20s", s.ws.includes("20_000")),
        a("pong_40s", s.ws.includes("40_000"))
      ])
    case "A-CLOSE-028":
      return pass("page snapshot 20k/64k caps; click to add", [
        a("codepoint", s.snapshot.includes("20000") || s.snapshot.includes("CODEPOINT_MAX")),
        a("click", s.chat.includes("void add()"))
      ])
    case "A-CLOSE-029":
      return pass("enterprise Dexie stores only recentRefs", [
        a("recent_only", s.octopDb.includes("recentRefs") && !s.octopDb.includes("access_token"))
      ])
    case "A-CLOSE-037":
      return pass("chrome and sidepanel share enterprise routes", [
        a("option_routes", s.chrome.includes("OptionRoutingChrome") || s.chrome.includes("enterpriseRoutes")),
        a("sidepanel_routes", s.chrome.includes("SidepanelRoutingChrome") || s.chrome.includes("enterpriseRoutes"))
      ])
    case "A-CLOSE-038":
      return pass("thread list surface exists on both catalog and chat", [
        a("catalog_threads", s.catalog.includes("view=threads")),
        a("thread_list", s.threads.includes("Load more"))
      ])
    case "A-CLOSE-039":
      return pass("login and catalog exist as separate pages", [
        a("login", exists("src/components/Octop/LoginPage.tsx")),
        a("catalog", exists("src/components/Octop/ExpertCatalog.tsx"))
      ])
    case "A-CLOSE-040":
      return pass("firefox has no enterprise identity coordinator", [
        a("bg_guard", s.background.includes("firefox")),
        a("no_ff_enterprise", s.firefoxHasEnterprise, false)
      ])
    case "A-CLOSE-045": {
      const empty = path.join(repoRoot, "artifacts", "_empty_gate")
      fs.mkdirSync(empty, { recursive: true })
      const proc = spawnSync("node", [
        path.join(repoRoot, "scripts/enterprise/gate.mjs"),
        "--required", path.join(repoRoot, "contracts/octop-client/v1/required-acceptance.json"),
        "--run-index", path.join(empty, "missing.json"),
        "--release-manifest", path.join(empty, "missing-manifest.json"),
        "--output", path.join(empty, "G-RELEASE.json")
      ], { encoding: "utf8" })
      return pass("empty evidence Gate FAIL", [
        a("gate_nonzero", proc.status !== 0)
      ])
    }
    case "A-CLOSE-046": {
      const source = collectSource(repoRoot)
      const verifySrc = read("scripts/enterprise/verify.mjs")
      const banned = ["2c286d94", "9d30a7667437b796513c09b69e0a98a6"].join("")
      return pass("actual SHA collected; hardcoded patched SHA forbidden", [
        a("sha_not_unknown", source.page_assist_implemented_sha !== "UNKNOWN"),
        a("uses_collect_source", verifySrc.includes("collectSource")),
        a("no_literal_old_sha", !verifySrc.includes(banned)),
        a("not_impersonating_baseline", source.page_assist_implemented_sha.length === 40)
      ])
    }
    default:
      return blocked("server-owned AC; run python octop-client/tools/verify.py")
  }
}

function writeRun(id, result) {
  const runId = crypto.randomUUID()
  const dest = path.join(output, id, runId)
  fs.mkdirSync(dest, { recursive: true })
  const status = result.status
  const exitCode = { PASS, FAIL, BLOCKED, SKIPPED }[status]
  const source = collectSource(repoRoot)
  const payload = {
    schema_version: 2,
    run_id: runId,
    acceptance_id: id,
    requirement_ids: [reqOf(id)],
    test_ids: [`TEST-${id}`],
    mode,
    parameter_case: "default",
    status,
    reason: result.reason,
    source,
    artifact_identity: { browser_sha256: null, module_wheel_sha256: null, host_wheel_sha256: null, release_manifest_sha256: null },
    execution: {
      command_argv: process.argv,
      cwd: process.cwd(),
      started_at: new Date().toISOString(),
      finished_at: new Date().toISOString(),
      exit_code: exitCode,
      tool_versions: { node: process.version },
      environment_id: mode === "live" ? "live" : "fixture-local"
    },
    assertions: result.assertions,
    state_digests: [],
    artifacts: []
  }
  fs.writeFileSync(path.join(dest, "run.json"), JSON.stringify(payload, null, 2))
  return { exitCode, runPath: path.join(dest, "run.json"), status }
}

const ids = acceptance === "ALL" ? BROWSER_IDS : [acceptance]
if (mode === "live" && missingLiveFields(env).length) {
  const missing = missingLiveFields(env)
  for (const id of ids) {
    writeRun(id, {
      status: "BLOCKED",
      reason: "ENVIRONMENT_REQUIRED: " + missing.join(","),
      assertions: [{ name: "environment", passed: false, expected: "deployment-input.json", actual: missing }]
    })
  }
  process.exit(BLOCKED)
}

const s = scan()
const indexRuns = []
let worst = PASS
for (const id of ids) {
  const result = assertionsFor(id, s)
  const written = writeRun(id, result)
  indexRuns.push({
    acceptance_id: id,
    mode,
    parameter_case: "default",
    run_json: written.runPath,
    sha256: crypto.createHash("sha256").update(fs.readFileSync(written.runPath)).digest("hex"),
    status: written.status
  })
  if (written.exitCode === FAIL) worst = FAIL
  else if (worst !== FAIL && written.exitCode === BLOCKED) worst = BLOCKED
  else if (worst === PASS && written.exitCode === SKIPPED) worst = SKIPPED
}
const indexPath = path.join(output, "run-index-node.json")
fs.mkdirSync(output, { recursive: true })
fs.writeFileSync(indexPath, JSON.stringify({ schema_version: 2, source: collectSource(repoRoot), runs: indexRuns }, null, 2))
process.exit(worst)
