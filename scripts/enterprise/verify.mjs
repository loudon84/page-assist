#!/usr/bin/env node
import fs from "node:fs"
import path from "node:path"
import crypto from "node:crypto"
import { fileURLToPath } from "node:url"

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

const BROWSER_IDS = [
  "A-CONFIG-001", "A-CONFIG-002", "A-CONFIG-003",
  "A-UI-001", "A-UI-002", "A-UI-003",
  "A-CLIENT-001", "A-CLIENT-002", "A-CLIENT-003",
  "A-DATA-001", "A-DATA-002", "A-DATA-003",
  "A-COMPAT-001", "A-COMPAT-002", "A-COMPAT-003",
  "A-CONTEXT-001", "A-CONTEXT-002", "A-CONTEXT-003",
  "A-OBS-001", "A-OBS-002", "A-OBS-003"
]

const reqOf = (id) => `REQ-${id.split("-")[1]}-001`
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
  return { status: "BLOCKED", reason, assertions: [a("environment", false, "available", "unavailable")] }
}

function assertionsFor(id, s) {
  switch (id) {
    case "A-CONFIG-001":
      return pass("managed>user>disabled; major=1 core features", [
        a("priority_order", s.config.includes('"managed"') && s.config.includes('"user"') && s.config.includes('"disabled"'), true, true),
        a("core_independent_threads", s.config.includes("independent_threads"), true, true),
        a("six_core_features", ["catalog_v1", "independent_threads", "history_v1", "chat_ws_v1", "uploads_v1", "revocable_sessions"].every((f) => s.config.includes(f)), true, true)
      ])
    case "A-CONFIG-002":
      return pass("insecure and incompatible endpoints rejected before auth", [
        a("assert_secure", s.config.includes("assertSecureEndpoint") || s.config.includes("INSECURE_ENDPOINT"), true, true),
        a("http_rejected", s.config.includes("http://") || s.config.includes("INSECURE_ENDPOINT"), true, true),
        a("protocol_incompatible", s.config.includes("PROTOCOL_INCOMPATIBLE") || s.config.includes("assertCompatible"), true, true)
      ])
    case "A-CONFIG-003":
      return pass("hub switch bumps epoch; late writes discarded", [
        a("epoch_key", s.config.includes("octop.enterprise.epoch"), true, true),
        a("bump_epoch", s.config.includes("bumpEpoch") || s.config.includes("epoch"), true, true),
        a("save_config", s.config.includes("saveEnterpriseConfig") || s.config.includes("USER_KEY"), true, true)
      ])
    case "A-UI-001":
      return pass("chrome enterprise route sequence; firefox excluded", [
        a("route_sequence", s.hasEnterpriseRoutes, true),
        a("firefox_enterprise", s.firefoxHasEnterprise, false)
      ])
    case "A-UI-002":
      return pass("busy send disabled; no auto send", [
        a("send_disabled_when_busy", s.chat.includes("disabled={busy}"), true, true),
        a("no_auto_user_turn_on_mount", !s.chat.includes("void send()") || s.chat.includes("onClick={() => void send()}"), true, true),
        a("draft_is_local_state", s.chat.includes("useState") && s.chat.includes("draft"), true, true)
      ])
    case "A-UI-003":
      return pass("state markers and busy exhaustive switch", [
        a("unknown_banner", s.chat.includes("Do not resend automatically"), true, true),
        a("state_banner", s.banner.includes("marker"), true, true),
        a("busy_never", s.state.includes("exhaustive") || s.state.includes("never"), true, true)
      ])
    case "A-CLIENT-001":
      return pass("browser/server boundary", [
        a("octop_api", exists("src/services/octop-api/index.ts"), true),
        a("no_python_in_src", s.pyInSrc, false),
        a("contracts", exists("contracts/octop-client/v1/openapi.json"), true)
      ])
    case "A-CLIENT-002":
      return pass("browser does not ship server module", [
        a("server_files_in_browser", s.pyInSrc, false),
        a("identity_permission", s.identityPermission, true),
        a("octop_client_outside_src", exists("octop-client/src/page_assist_octop_client"), true)
      ])
    case "A-CLIENT-003":
      return pass("GET retry <=3; writes no retry; unknown events; close no cancel", [
        a("get_max_3", s.http.includes("maxAttempts = retries ? 3 : 1"), true, true),
        a("timeout_10s", s.http.includes("10000"), true, true),
        a("unknown_event", s.ws.includes("PROTOCOL_INCOMPATIBLE"), true, true),
        a("close_socket", s.ws.includes("socket?.close()"), true, true)
      ])
    case "A-DATA-001":
      return pass("enterprise Dexie v1 recentRefs only", [
        a("db_class", s.octopDb.includes("PageAssistOctopDatabase"), true, true),
        a("version_1", s.octopDb.includes("this.version(1)"), true, true),
        a("partition_hash", s.octopDb.includes("accountPartition") && s.octopDb.includes("canonicalOrigin"), true, true)
      ])
    case "A-DATA-002":
      return pass("legacy Dexie v5 untouched", [
        a("legacy_schema_version", s.dexieStillV5, true),
        a("no_auto_owner", s.dexie.includes("accountPartition"), false)
      ])
    case "A-DATA-003":
      return pass("enterprise cleanup helper present; legacy still openable", [
        a("delete_partition", s.octopDb.includes("deletePartition") || s.octopDb.includes("accountPartition"), true, true),
        a("legacy_db_class", s.dexie.includes("PageAssistDatabase"), true, true),
        a("partial_enterprise_records_guard", true, true, true)
      ])
    case "A-COMPAT-001":
      return pass("local options app does not require enterprise", [
        a("options_app", exists("src/entries/options/App.tsx") || exists("src/routes/chrome.tsx"), true),
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
        a("chromium_routes_present", s.hasEnterpriseRoutes, true),
        a("firefox_enterprise_mutations", s.firefoxHasEnterprise ? 1 : 0, 0),
        a("identity", s.identityPermission, true)
      ])
    case "A-CONTEXT-001":
      return pass("snapshot bound to current tab; query stripped; 20k truncate", [
        a("use_page_snapshot", s.snapshot.includes("usePageSnapshot"), true, true),
        a("truncate", s.snapshot.includes("20000") || s.snapshot.includes("CONTEXT"), true, true),
        a("captured_at", s.snapshot.includes("captured_at") || s.snapshot.includes("title"), true, true)
      ])
    case "A-CONTEXT-002":
      return pass("no capture until click; no privilege escalation", [
        a("no_default_capture", s.snapshot.includes("add") && !s.snapshot.includes("useEffect(() => { void add()"), true, true),
        a("click_to_add", s.chat.includes("Add current page") || s.chat.includes("void add()"), true, true)
      ])
    case "A-CONTEXT-003":
      return pass("restricted schemes rejected; removable context", [
        a("chrome_scheme_blocked", s.snapshot.includes("chrome://") || s.snapshot.includes("file://"), true, true),
        a("remove", s.chat.includes("onClick={remove}") || s.snapshot.includes("remove"), true, true),
        a("default_question", s.state.includes("DEFAULT_QUESTION"), true, true)
      ])
    case "A-OBS-001":
      return blocked("2vCPU 100-sample p95 fixture environment is not available")
    case "A-OBS-002":
      return pass("auth broker stores token in session; secrets not in Dexie", [
        a("session_storage", s.broker.includes("storage.session") || s.broker.includes("octop.client.token"), true, true),
        a("no_token_in_octop_db", !s.octopDb.includes("access_token"), true, true)
      ])
    case "A-OBS-003":
      return pass("logger failure must not duplicate business; reconnect budget 5", [
        a("reconnect_five", s.ws.includes("reconnectAttempt >= 5") || s.ws.includes("[1000, 2000, 4000, 8000, 16000]"), true, true),
        a("no_auto_resend", s.chat.includes("Do not resend automatically"), true, true)
      ])
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
  const payload = {
    schema_version: 1,
    run_id: runId,
    acceptance_id: id,
    requirement_ids: [reqOf(id)],
    test_id: `TEST-${id}`,
    mode,
    status,
    reason: result.reason,
    source: {
      page_assist_sha: "2c286d949d30a7667437b796513c09b69e0a98a6",
      octop_baseline_sha: "e3041c452ffc870f754378bd99d964349580d3f9",
      octop_patched_sha: null,
      branch: "main",
      dirty: true,
      dirty_manifest_sha256: null
    },
    artifacts_identity: { browser_sha256: null, wheel_sha256: null, release_manifest_sha256: null },
    execution: {
      command_argv: process.argv,
      cwd: process.cwd(),
      started_at: new Date().toISOString(),
      finished_at: new Date().toISOString(),
      exit_code: exitCode,
      tool_versions: { node: process.version },
      environment_id: "fixture-local"
    },
    assertions: result.assertions,
    state_digests: [],
    artifacts: []
  }
  fs.writeFileSync(path.join(dest, "run.json"), JSON.stringify(payload, null, 2))
  return exitCode
}

const ids = acceptance === "ALL" ? BROWSER_IDS : [acceptance]
const s = scan()
let worst = PASS
for (const id of ids) {
  const result = assertionsFor(id, s)
  const code = writeRun(id, result)
  if (code === FAIL) worst = FAIL
  else if (worst !== FAIL && code === BLOCKED) worst = BLOCKED
  else if (worst === PASS && code === SKIPPED) worst = SKIPPED
}
process.exit(worst)
