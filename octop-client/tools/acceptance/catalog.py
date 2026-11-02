"""Canonical AC/FI catalog for Plan B closure (schema v2)."""

from __future__ import annotations

from typing import Any

DOMAINS = [
    "CONFIG",
    "AUTH",
    "SESSION",
    "UI",
    "CATALOG",
    "CLIENT",
    "HOST",
    "PACKAGE",
    "DEPLOY",
    "UPGRADE",
    "THREAD",
    "TURN",
    "RECOVER",
    "HITL",
    "CONTEXT",
    "FILE",
    "DATA",
    "BRIDGE",
    "COMPAT",
    "SEC",
    "OBS",
    "EVID",
]

NODE_DOMAINS = {"CONFIG", "UI", "CLIENT", "CONTEXT", "DATA", "COMPAT", "EVID"}
NODE_CLOSE = {
    "A-CLOSE-001",
    "A-CLOSE-002",
    "A-CLOSE-003",
    "A-CLOSE-004",
    "A-CLOSE-013",
    "A-CLOSE-015",
    "A-CLOSE-016",
    "A-CLOSE-017",
    "A-CLOSE-022",
    "A-CLOSE-028",
    "A-CLOSE-029",
    "A-CLOSE-037",
    "A-CLOSE-038",
    "A-CLOSE-039",
    "A-CLOSE-040",
    "A-CLOSE-045",
    "A-CLOSE-046",
}

LIVE_INHERITED = {
    "A-AUTH-001",
    "A-HOST-001",
    "A-THREAD-001",
    "A-TURN-001",
    "A-RECOVER-001",
    "A-HITL-001",
    "A-HITL-003",
    "A-FILE-001",
    "A-BRIDGE-001",
    "A-BRIDGE-002",
    "A-BRIDGE-003",
    "A-UPGRADE-002",
    "A-UPGRADE-003",
    "A-COMPAT-001",
    "A-DEPLOY-001",
    "A-DEPLOY-003",
    "A-EVID-003",
}

CLOSE_META: dict[str, dict[str, Any]] = {
    "A-CLOSE-001": {
        "req": ["REQ-CLOSE-001"],
        "modes": ["build"],
        "milestone": "M0",
        "files": ["src/services/octop-api/http.ts", "package.json", "scripts/enterprise/build-all.mjs"],
        "fail": "single target failure must propagate; no releasable zip",
        "verify": "bun run compile && node scripts/enterprise/build-all.mjs",
    },
    "A-CLOSE-002": {
        "req": ["REQ-CLOSE-001"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/components/Octop/ExpertChat.tsx", "src/hooks/octop/state.ts"],
        "fail": "first send before OPEN+subscribe is rejected; input/attachments preserved",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-002 --mode fixture",
    },
    "A-CLOSE-003": {
        "req": ["REQ-CLOSE-001"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/components/Octop/ExpertChat.tsx", "octop-client/src/page_assist_octop_client/api/handlers.py"],
        "fail": "duplicate clicks produce one thread and one receipt",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-003 --mode fixture",
    },
    "A-CLOSE-004": {
        "req": ["REQ-CLOSE-001"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/routes/chrome.tsx", "src/entries-firefox/options/App.tsx"],
        "fail": "Firefox enterprise identity calls remain zero; local history digest unchanged",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-004 --mode fixture",
    },
    "A-CLOSE-005": {
        "req": ["REQ-CLOSE-002"],
        "modes": ["live"],
        "milestone": "M1",
        "files": ["E:/git/octop/src/octop/integrations/page_assist_client/host.py", "E:/git/octop/src/octop/api/app.py"],
        "fail": "production READY with FixtureHostPort is forbidden",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-005 --mode live",
    },
    "A-CLOSE-006": {
        "req": ["REQ-CLOSE-002"],
        "modes": ["fixture", "live"],
        "milestone": "M1",
        "files": ["E:/git/octop/src/octop/api/deps.py", "octop-client/src/page_assist_octop_client/api/asgi.py"],
        "fail": "unready/uninstalled Client API returns 503; JWT exemption is prefix-precise",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-006 --mode fixture",
    },
    "A-CLOSE-007": {
        "req": ["REQ-CLOSE-002"],
        "modes": ["fixture"],
        "milestone": "M1",
        "files": ["octop-client/src/page_assist_octop_client/host/port.py", "octop-client/src/page_assist_octop_client/storage/schema.py"],
        "fail": "commit-before error rolls back thread/meta/receipt to zero delta",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-007 --mode fixture",
    },
    "A-CLOSE-008": {
        "req": ["REQ-CLOSE-002"],
        "modes": ["fixture", "live"],
        "milestone": "M1",
        "files": ["octop-client/src/page_assist_octop_client/integration/register.py"],
        "fail": "drain closes WS; admitted turns are not cancelled",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-008 --mode fixture",
    },
    "A-CLOSE-009": {
        "req": ["REQ-CLOSE-003"],
        "modes": ["live"],
        "milestone": "M1",
        "files": ["E:/git/octop/src/octop/api/routers/auth.py", "src/services/octop-api/index.ts"],
        "fail": "SID is published only after GET /session succeeds",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-009 --mode live",
    },
    "A-CLOSE-010": {
        "req": ["REQ-CLOSE-003"],
        "modes": ["fixture", "live"],
        "milestone": "M1",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py"],
        "fail": "forged subject/state/verifier/replay creates zero SID",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-010 --mode fixture",
    },
    "A-CLOSE-011": {
        "req": ["REQ-CLOSE-003"],
        "modes": ["fixture"],
        "milestone": "M1",
        "files": ["octop-client/src/page_assist_octop_client/storage/db.py"],
        "fail": "half identity is cleared; code cannot be replayed to mint SID",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-011 --mode fixture",
    },
    "A-CLOSE-012": {
        "req": ["REQ-CLOSE-003"],
        "modes": ["fixture", "live"],
        "milestone": "M1",
        "files": ["src/services/octop-api/auth-broker.ts", "src/db/octop/index.ts"],
        "fail": "password/JWT never enter OctopApi logs, Dexie, or URL",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-012 --mode fixture",
    },
    "A-CLOSE-013": {
        "req": ["REQ-CLOSE-004"],
        "modes": ["fixture", "live"],
        "milestone": "M1",
        "files": ["src/services/octop-api/identity-coordinator.ts", "src/services/octop-api/config.ts"],
        "fail": "old token requests to new origin = 0",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-013 --mode fixture",
    },
    "A-CLOSE-014": {
        "req": ["REQ-CLOSE-004"],
        "modes": ["fixture", "live"],
        "milestone": "M1",
        "files": ["octop-client/src/page_assist_octop_client/api/ws.py", "octop-client/src/page_assist_octop_client/integration/register.py"],
        "fail": "post-logout user_turn message/turn delta = 0",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-014 --mode fixture",
    },
    "A-CLOSE-015": {
        "req": ["REQ-CLOSE-004"],
        "modes": ["fixture", "live"],
        "milestone": "M1",
        "files": ["src/services/octop-api/config.ts", "src/entries/background.ts"],
        "fail": "content-script sender cannot call sensitive broker",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-015 --mode fixture",
    },
    "A-CLOSE-016": {
        "req": ["REQ-CLOSE-004"],
        "modes": ["fixture"],
        "milestone": "M1",
        "files": ["src/services/octop-api/identity-coordinator.ts"],
        "fail": "cleanup failure keeps lock; late callback cannot restore identity",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-016 --mode fixture",
    },
    "A-CLOSE-017": {
        "req": ["REQ-CLOSE-005"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/components/Octop/", "src/services/octop-api/index.ts"],
        "fail": "list/recent entry missing means FAIL not implicit empty success",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-017 --mode fixture",
    },
    "A-CLOSE-018": {
        "req": ["REQ-CLOSE-005"],
        "modes": ["fixture"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py", "octop-client/src/page_assist_octop_client/cursors.py"],
        "fail": "stale cursor is CURSOR_STALE; new messages do not duplicate old pages",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-018 --mode fixture",
    },
    "A-CLOSE-019": {
        "req": ["REQ-CLOSE-005"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py"],
        "fail": "wrong owner/expert/channel GET leaves business digest unchanged",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-019 --mode fixture",
    },
    "A-CLOSE-020": {
        "req": ["REQ-CLOSE-005"],
        "modes": ["fixture"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py"],
        "fail": "expired idempotency key is rejected; replay of same hash returns original resource",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-020 --mode fixture",
    },
    "A-CLOSE-021": {
        "req": ["REQ-CLOSE-006"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/ws.py", "src/services/octop-api/websocket.ts"],
        "fail": "ack timeout 10s; ping 20s / pong 40s; no auto cancel on close",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-021 --mode fixture",
    },
    "A-CLOSE-022": {
        "req": ["REQ-CLOSE-006"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/components/Octop/ExpertChat.tsx", "octop-client/src/page_assist_octop_client/host/port.py"],
        "fail": "runtime_revision must not go backwards; reopen is not always IDLE",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-022 --mode fixture",
    },
    "A-CLOSE-023": {
        "req": ["REQ-CLOSE-006"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/services/octop-api/websocket.ts", "octop-client/src/page_assist_octop_client/api/ws.py"],
        "fail": "accepted turn is not resent; ticket is single-use",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-023 --mode fixture",
    },
    "A-CLOSE-024": {
        "req": ["REQ-CLOSE-006"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/ws.py"],
        "fail": "cancel receipt is requested-only; close WS does not cancel",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-024 --mode fixture",
    },
    "A-CLOSE-025": {
        "req": ["REQ-CLOSE-007"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py"],
        "fail": "trailing LF SHA mismatch rejects; original bytes preserved",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-025 --mode fixture",
    },
    "A-CLOSE-026": {
        "req": ["REQ-CLOSE-007"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py", "octop-client/src/page_assist_octop_client/host/fixture.py"],
        "fail": "cross-owner upload reference: accept=0 and B state unchanged",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-026 --mode fixture",
    },
    "A-CLOSE-027": {
        "req": ["REQ-CLOSE-007"],
        "modes": ["fixture"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/storage/db.py"],
        "fail": "orphan after file publish is recoverable; same key does not mint second ready",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-027 --mode fixture",
    },
    "A-CLOSE-028": {
        "req": ["REQ-CLOSE-007"],
        "modes": ["fixture"],
        "milestone": "M2",
        "files": ["src/components/Octop/ExpertChat.tsx"],
        "fail": "first ready kept when second file fails; TTL cleanup failures retry",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-028 --mode fixture",
    },
    "A-CLOSE-029": {
        "req": ["REQ-CLOSE-008"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/components/Octop/ExpertChat.tsx"],
        "fail": "reopen restores same runtime_revision form snapshot",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-029 --mode fixture",
    },
    "A-CLOSE-030": {
        "req": ["REQ-CLOSE-008"],
        "modes": ["fixture"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py"],
        "fail": "empty decisions: pending unconsumed, tools=0",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-030 --mode fixture",
    },
    "A-CLOSE-031": {
        "req": ["REQ-CLOSE-008"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py"],
        "fail": "lost 202 confirmation does not auto-resubmit",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-031 --mode fixture",
    },
    "A-CLOSE-032": {
        "req": ["REQ-CLOSE-008"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["octop-client/src/page_assist_octop_client/api/handlers.py", "src/components/Octop/ExpertChat.tsx"],
        "fail": "remote approval.submit is never forwarded",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-032 --mode fixture",
    },
    "A-CLOSE-033": {
        "req": ["REQ-CLOSE-009"],
        "modes": ["live"],
        "milestone": "M3",
        "files": ["E:/git/octop/src/octop/api/routers/bridge.py", "octop-client/src/page_assist_octop_client/bridge/personal.py"],
        "fail": "fixture Alpha Expert does not satisfy live Peer",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-033 --mode live",
    },
    "A-CLOSE-034": {
        "req": ["REQ-CLOSE-009"],
        "modes": ["fixture", "live"],
        "milestone": "M3",
        "files": ["octop-client/src/page_assist_octop_client/bridge/personal.py"],
        "fail": "fixed peer_user / as_user / auto-bind produce zero private business",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-034 --mode fixture",
    },
    "A-CLOSE-035": {
        "req": ["REQ-CLOSE-009"],
        "modes": ["fixture", "live"],
        "milestone": "M3",
        "files": ["E:/git/octop/src/octop/api/routers/bridge.py"],
        "fail": "shared connection private ops = 0; old resources not inherited",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-035 --mode fixture",
    },
    "A-CLOSE-036": {
        "req": ["REQ-CLOSE-009"],
        "modes": ["fixture", "live"],
        "milestone": "M3",
        "files": ["octop-client/src/page_assist_octop_client/bridge/personal.py"],
        "fail": "unknown turn is not resent after peer disconnect",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-036 --mode fixture",
    },
    "A-CLOSE-037": {
        "req": ["REQ-CLOSE-010"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/hooks/octop/usePageSnapshot.ts"],
        "fail": "preview equals submitted bytes; other tabs unread",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-037 --mode fixture",
    },
    "A-CLOSE-038": {
        "req": ["REQ-CLOSE-010"],
        "modes": ["fixture"],
        "milestone": "M2",
        "files": ["src/components/Octop/ExpertChat.tsx"],
        "fail": "script/command in output is not executed",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-038 --mode fixture",
    },
    "A-CLOSE-039": {
        "req": ["REQ-CLOSE-010"],
        "modes": ["fixture", "live"],
        "milestone": "M2",
        "files": ["src/db/octop/index.ts"],
        "fail": "old Dexie records remain unclaimed",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-039 --mode fixture",
    },
    "A-CLOSE-040": {
        "req": ["REQ-CLOSE-010"],
        "modes": ["fixture"],
        "milestone": "M2",
        "files": ["src/services/octop-api/identity-coordinator.ts", "src/components/Octop/ExpertChat.tsx"],
        "fail": "epoch mismatch drops late drafts; user-visible errors remain",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-040 --mode fixture",
    },
    "A-CLOSE-041": {
        "req": ["REQ-CLOSE-011"],
        "modes": ["live"],
        "milestone": "M4",
        "files": ["octop-client/tools/deploy.py"],
        "fail": "copy-only install cannot return READY",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-041 --mode live",
    },
    "A-CLOSE-042": {
        "req": ["REQ-CLOSE-011"],
        "modes": ["fixture", "live"],
        "milestone": "M4",
        "files": ["octop-client/tools/deploy.py"],
        "fail": "fake wheel / path escape: precheck != 0, stop/switch = 0",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-042 --mode fixture",
    },
    "A-CLOSE-043": {
        "req": ["REQ-CLOSE-011"],
        "modes": ["live"],
        "milestone": "M4",
        "files": ["octop-client/tools/deploy.py", "octop-client/src/page_assist_octop_client/integration/register.py"],
        "fail": "disable does not cancel admitted tasks; PID unchanged",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-043 --mode live",
    },
    "A-CLOSE-044": {
        "req": ["REQ-CLOSE-011"],
        "modes": ["fixture", "live"],
        "milestone": "M4",
        "files": ["octop-client/tools/deploy.py"],
        "fail": "rollback failure exit 6 RECOVERY_REQUIRED; new messages preserved",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-044 --mode fixture",
    },
    "A-CLOSE-045": {
        "req": ["REQ-CLOSE-012"],
        "modes": ["document", "fixture"],
        "milestone": "M0",
        "files": ["scripts/enterprise/verify.mjs", "octop-client/tools/verify.py"],
        "fail": "hardcoded SHA / constant assertions fail the source contract",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-045 --mode document",
    },
    "A-CLOSE-046": {
        "req": ["REQ-CLOSE-012"],
        "modes": ["fixture"],
        "milestone": "M0",
        "files": ["scripts/enterprise/gate.mjs"],
        "fail": "empty evidence / BLOCKED required / bad hash => G-RELEASE FAIL exit 1",
        "verify": "node scripts/enterprise/gate.mjs --required contracts/octop-client/v1/required-acceptance.json --run-index <empty> --release-manifest <m> --output <g>",
    },
    "A-CLOSE-047": {
        "req": ["REQ-CLOSE-012"],
        "modes": ["live"],
        "milestone": "M5",
        "files": ["scripts/enterprise/verify.mjs"],
        "fail": "missing env stays BLOCKED; never fabricated live PASS",
        "verify": "node scripts/enterprise/verify.mjs --acceptance A-CLOSE-047 --mode live",
    },
    "A-CLOSE-048": {
        "req": ["REQ-CLOSE-012"],
        "modes": ["fixture", "live"],
        "milestone": "M5",
        "files": ["octop-client/src/page_assist_octop_client/loggingutil.py"],
        "fail": "log IO failure does not re-execute business",
        "verify": "python octop-client/tools/verify.py --acceptance A-CLOSE-048 --mode fixture",
    },
}

FI_CLOSE_META: dict[str, dict[str, Any]] = {
    "FI-CLOSE-001": {"ac": ["A-CLOSE-001"], "point": "compile/sub-build failure", "post": "total build !=0, no releasable", "modes": ["fixture"]},
    "FI-CLOSE-002": {"ac": ["A-CLOSE-002", "A-CLOSE-003"], "point": "create delay + clicks", "post": "single key/thread", "modes": ["fixture"]},
    "FI-CLOSE-003": {"ac": ["A-CLOSE-007"], "point": "thread/meta/receipt writes", "post": "all deltas 0", "modes": ["fixture"]},
    "FI-CLOSE-004": {"ac": ["A-CLOSE-011"], "point": "auth commit/storage fail", "post": "atomic SID; no code replay", "modes": ["fixture"]},
    "FI-CLOSE-005": {"ac": ["A-CLOSE-013", "A-CLOSE-014", "A-CLOSE-016"], "point": "logout delayed WS", "post": "accept=0", "modes": ["fixture", "live"]},
    "FI-CLOSE-006": {"ac": ["A-CLOSE-021"], "point": "slow handshake/lost ack/no pong", "post": "bounded converge, no auto cancel", "modes": ["fixture"]},
    "FI-CLOSE-007": {"ac": ["A-CLOSE-022"], "point": "seq gap/old revision", "post": "state does not rewind", "modes": ["fixture"]},
    "FI-CLOSE-008": {"ac": ["A-CLOSE-023"], "point": "disconnect after accepted", "post": "turn not resent", "modes": ["fixture", "live"]},
    "FI-CLOSE-009": {"ac": ["A-CLOSE-027"], "point": "publish/SQL/receipt drop", "post": "orphan or unique ready", "modes": ["fixture"]},
    "FI-CLOSE-010": {"ac": ["A-CLOSE-028"], "point": "second file / cleanup fail", "post": "first ready kept", "modes": ["fixture"]},
    "FI-CLOSE-011": {"ac": ["A-CLOSE-031"], "point": "decision SQL / lost 202", "post": "rollback or no re-approve", "modes": ["fixture"]},
    "FI-CLOSE-012": {"ac": ["A-CLOSE-034", "A-CLOSE-035", "A-CLOSE-036"], "point": "peer bind disconnect", "post": "recover or reject old", "modes": ["fixture", "live"]},
    "FI-CLOSE-013": {"ac": ["A-CLOSE-044"], "point": "busy gate / health fail", "post": "stop=0 or restore old", "modes": ["fixture", "live"]},
    "FI-CLOSE-014": {"ac": ["A-CLOSE-044"], "point": "rollback start fail", "post": "exit6 RECOVERY_REQUIRED", "modes": ["fixture", "live"]},
    "FI-CLOSE-015": {"ac": ["A-CLOSE-048"], "point": "log IO fail", "post": "business once, DEGRADED", "modes": ["fixture"]},
    "FI-CLOSE-016": {"ac": ["A-CLOSE-046"], "point": "gate missing/tamper", "post": "Gate FAIL exit1", "modes": ["fixture"]},
}

ENV_FIELDS = [
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
    "live_test_identities",
]


def inherited_ids() -> list[str]:
    return [f"A-{domain}-{n:03d}" for domain in DOMAINS for n in (1, 2, 3)]


def close_ids() -> list[str]:
    return [f"A-CLOSE-{n:03d}" for n in range(1, 49)]


def fi_ids() -> list[str]:
    return [f"FI-{n:02d}" for n in range(1, 17)]


def fi_close_ids() -> list[str]:
    return [f"FI-CLOSE-{n:03d}" for n in range(1, 17)]


def modes_for_inherited(ac_id: str) -> list[str]:
    if ac_id == "A-EVID-001":
        return ["document"]
    if ac_id in {"A-PACKAGE-001", "A-COMPAT-003"}:
        return ["build"]
    modes = ["fixture"]
    if ac_id in LIVE_INHERITED:
        modes.append("live")
    return modes


def owner_for(ac_id: str) -> str:
    if ac_id.startswith("FI"):
        return "python"
    if ac_id.startswith("A-CLOSE-"):
        return "node" if ac_id in NODE_CLOSE else "python"
    domain = ac_id.split("-")[1]
    return "node" if domain in NODE_DOMAINS else "python"


def gates_for(ac_id: str, mode: str) -> list[str]:
    gates = ["G-EVID"]
    if mode == "build":
        gates.append("G-BUILD")
    if mode == "live":
        gates.append("G-LIVE")
    if ac_id.startswith("FI"):
        gates.append("G-FI")
    if ac_id.startswith("A-CLOSE-"):
        n = int(ac_id.split("-")[-1])
        if 5 <= n <= 12 or 17 <= n <= 36 or n == 38:
            gates.append("G-PROTOCOL")
        if n in range(9, 17) or n in range(19, 21) or n in range(25, 29) or n in range(30, 33) or n in range(34, 41) or n == 42:
            gates.append("G-SEC")
        if n in {2, 3, 4, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 22, 23, 24, 28, 29, 31, 32, 37, 38, 39, 40, 47}:
            gates.append("G-BROWSER")
        if n in {41, 42, 43, 44}:
            gates.append("G-DEPLOY")
        return sorted(set(gates))
    domain = ac_id.split("-")[1] if ac_id.startswith("A-") else ""
    protocol = {"AUTH", "SESSION", "CATALOG", "CLIENT", "HOST", "THREAD", "TURN", "RECOVER", "HITL", "FILE", "BRIDGE"}
    sec = {"CONFIG", "AUTH", "SESSION", "THREAD", "HITL", "FILE", "DATA", "BRIDGE", "SEC"}
    browser = {"CONFIG", "UI", "CLIENT", "CONTEXT", "DATA", "COMPAT"}
    deploy = {"DEPLOY", "UPGRADE"}
    if domain in protocol:
        gates.append("G-PROTOCOL")
    if domain in sec:
        gates.append("G-SEC")
    if domain in browser:
        gates.append("G-BROWSER")
    if domain in deploy:
        gates.append("G-DEPLOY")
    return sorted(set(gates))


def tuples() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for ac_id in inherited_ids():
        req = [f"REQ-{ac_id.split('-')[1]}-001"]
        for mode in modes_for_inherited(ac_id):
            items.append(
                {
                    "id": ac_id,
                    "requirement_ids": req,
                    "owner_runner": owner_for(ac_id),
                    "mode": mode,
                    "required": True,
                    "required_gates": gates_for(ac_id, mode),
                    "kind": "acceptance",
                }
            )
    for ac_id, meta in CLOSE_META.items():
        for mode in meta["modes"]:
            items.append(
                {
                    "id": ac_id,
                    "requirement_ids": list(meta["req"]),
                    "owner_runner": owner_for(ac_id),
                    "mode": mode,
                    "required": True,
                    "required_gates": gates_for(ac_id, mode),
                    "kind": "acceptance",
                    "milestone": meta["milestone"],
                }
            )
    for fi_id in fi_ids():
        items.append(
            {
                "id": fi_id,
                "requirement_ids": ["REQ-EVID-001"],
                "owner_runner": "python",
                "mode": "fixture",
                "required": True,
                "required_gates": ["G-FI", "G-EVID"],
                "kind": "failure_injection",
            }
        )
    for fi_id, meta in FI_CLOSE_META.items():
        for mode in meta["modes"]:
            gates = ["G-FI", "G-EVID"]
            if fi_id in {"FI-CLOSE-013", "FI-CLOSE-014"}:
                gates.append("G-DEPLOY")
            if mode == "live":
                gates.append("G-LIVE")
            items.append(
                {
                    "id": fi_id,
                    "requirement_ids": [f"REQ-CLOSE-00{min(12, max(1, int(ac.split('-')[-1]) // 4 + 1))}" for ac in meta["ac"]],
                    "owner_runner": "python",
                    "mode": mode,
                    "required": True,
                    "required_gates": sorted(set(gates)),
                    "kind": "failure_injection",
                    "injection_point": meta["point"],
                    "postcondition": meta["post"],
                }
            )
    return items
