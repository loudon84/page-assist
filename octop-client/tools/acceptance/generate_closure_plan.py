#!/usr/bin/env python3
"""Generate plan.md and required-acceptance.json from the catalog."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from catalog import (  # noqa: E402
    CLOSE_META,
    ENV_FIELDS,
    FI_CLOSE_META,
    close_ids,
    fi_close_ids,
    fi_ids,
    inherited_ids,
    modes_for_inherited,
    owner_for,
    tuples,
)

PA_BASELINE = "ff1df1ce4df8b3d12be231fb40857fd3a46fc88c"
OC_BASELINE = "e3041c452ffc870f754378bd99d964349580d3f9"
PRD_BLOB = "356f2c2e61a17c032407ede047846840f8c61866"
PRD_ID = "PRD-PA-OCTOP-B-CLOSURE-001"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def git_sha(repo: Path) -> str:
    head = repo / ".git" / "HEAD"
    if not head.exists():
        return "UNKNOWN"
    ref = head.read_text(encoding="utf-8").strip()
    if ref.startswith("ref:"):
        target = repo / ".git" / ref.split(" ", 1)[1].strip()
        return target.read_text(encoding="utf-8").strip()
    return ref


def yaml_task(
    task_id: str,
    reqs: list[str],
    acs: list[str],
    files: list[str],
    goal: str,
    fail: str,
    commands: list[str],
    milestone: str,
    status: str = "planned",
) -> str:
    lines = [
        "```yaml",
        f"id: {task_id}",
        f"requirement_refs: {reqs}",
        f"acceptance_refs: {acs}",
        "files_or_symbols:",
    ]
    for path in files:
        repo = "octop" if path.replace("\\", "/").startswith("E:/git/octop") or "/octop/" in path and "octop-client" not in path and path.startswith("E:") else "page-assist"
        if path.startswith("E:/git/octop") or path.startswith("E:\\git\\octop"):
            repo = "octop"
            rel = path.replace("E:/git/octop/", "").replace("E:\\git\\octop\\", "")
        else:
            repo = "page-assist"
            rel = path
        lines.append("  - repository: " + repo)
        lines.append(f"    path: {rel}")
        lines.append("    operation: modify")
    lines.extend(
        [
            f"implementation_goal: {goal}",
            "preconditions: [baseline recorded, HostPort/protocol frozen where required]",
            f"state_transition: {goal}",
            "side_effect_scope: [managed source, evidence artifacts]",
            f"failure_cases: [{fail}]",
            "verification:",
        ]
    )
    for command in commands:
        lines.append(f"  - command: {command}")
    lines.extend(
        [
            f"status: {status}",
            "implemented: false",
            "verified: false",
            f"milestone: {milestone}",
            "evidence: []",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def build_required_json(prd_sha: str) -> dict:
    acceptances = []
    injections = []
    for item in tuples():
        entry = {
            "id": item["id"],
            "requirement_ids": item["requirement_ids"],
            "owner_runner": item["owner_runner"],
            "required_modes": [item["mode"]],
            "parameter_cases": ["default"],
            "required": True,
            "oracle_types": ["behavior"],
            "required_artifact_kinds": ["run.json"],
            "required_gates": item["required_gates"],
        }
        if item["kind"] == "failure_injection":
            entry["injection_point"] = item.get("injection_point", "legacy")
            entry["expected_postcondition"] = item.get("postcondition", "injection_observed")
            injections.append(entry)
        else:
            # merge modes for same id
            existing = next((a for a in acceptances if a["id"] == item["id"]), None)
            if existing:
                if item["mode"] not in existing["required_modes"]:
                    existing["required_modes"].append(item["mode"])
                existing["required_gates"] = sorted(set(existing["required_gates"] + item["required_gates"]))
            else:
                acceptances.append(entry)
    return {
        "schema_version": 2,
        "prd_id": PRD_ID,
        "prd_sha256": prd_sha,
        "baseline_prd_blob": PRD_BLOB,
        "page_assist_baseline_sha": PA_BASELINE,
        "octop_baseline_sha": OC_BASELINE,
        "acceptances": acceptances,
        "failure_injections": injections,
        "additionalProperties": False,
    }


def build_plan(prd_sha: str, pa_head: str, oc_head: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts: list[str] = []
    parts.append("# Page Assist 方案 B 落地收口实施计划 v1.1\n")
    parts.append("status: planned\n")
    parts.append(f"generated_at: {now}\n")
    parts.append("prd: prd/Page_Assist_Plan_B_Landing_Closure_PRD_v1.1.md\n")
    parts.append("baseline_prd: prd/Page_Assist_Plan_B_Server_OctopClient_PRD_v1.0.md\n")
    parts.append("\n## 0. 源码身份\n\n")
    parts.append(f"- Page Assist 文档基线: `{PA_BASELINE}`\n")
    parts.append(f"- Page Assist 实际 HEAD: `{pa_head}`\n")
    parts.append(f"- Octop 文档基线: `{OC_BASELINE}`\n")
    parts.append(f"- Octop 实际 HEAD: `{oc_head}`\n")
    parts.append(f"- 原 PRD git blob: `{PRD_BLOB}`\n")
    parts.append(f"- 收口 PRD sha256: `{prd_sha}`\n")
    parts.append("- 证据必须绑定实际 SHA；禁止把基线 SHA 填成已打补丁产物。\n")
    parts.append("- `octop-client/` 仅存在于 Page Assist 根目录；安装运行于 Octop 服务器。\n")
    if pa_head != PA_BASELINE:
        parts.append("- **警告**：Page Assist HEAD 与文档基线不一致，计划与证据绑定实际 HEAD。\n")
    if oc_head != OC_BASELINE:
        parts.append("- **警告**：Octop HEAD 与文档基线不一致，计划与证据绑定实际 HEAD。\n")
    parts.append("\n## 1. 环境缺项（live BLOCKED 字段）\n\n")
    for field in ENV_FIELDS:
        parts.append(f"- `{field}`\n")
    parts.append("\n缺上述字段时继续完成不依赖环境的代码与 fixture/build；相关 AC/FI 标记 `blocked`，G-RELEASE=FAIL。\n")
    parts.append("\n## 2. 覆盖矩阵\n\n")
    parts.append("- 继承 22 REQ / 66 AC / FI-01～16 全部保留。\n")
    parts.append("- 新增 REQ-CLOSE-001～012 / A-CLOSE-001～048 / FI-CLOSE-001～016。\n")
    parts.append("- 合计 114 AC + 32 FI；Gate 对 required 的 BLOCKED/SKIPPED/缺失一律 FAIL。\n")
    parts.append("\n## 3. 批次\n\n")
    parts.append("- M0 门禁与构建：A-CLOSE-001/045/046，FI-CLOSE-001/016\n")
    parts.append("- M1 宿主与登录：A-CLOSE-005～016，FI-CLOSE-003～005\n")
    parts.append("- M2 会话与材料：A-CLOSE-002～004、017～032、037～040，FI-CLOSE-002、006～011\n")
    parts.append("- M3 个人 Peer：A-CLOSE-033～036，FI-CLOSE-012\n")
    parts.append("- M4 发布运维：A-CLOSE-041～044，FI-CLOSE-013/014\n")
    parts.append("- M5 组合验收：A-CLOSE-047/048 与全集证据\n")
    parts.append("\n## 4. TASK 清单\n\n")

    n = 1
    for ac_id in inherited_ids():
        modes = ",".join(modes_for_inherited(ac_id))
        domain = ac_id.split("-")[1]
        runner = "node" if owner_for(ac_id) == "node" else "python"
        cmd = (
            f"node scripts/enterprise/verify.mjs --acceptance {ac_id} --mode fixture --output <ABS>"
            if runner == "node"
            else f"python octop-client/tools/verify.py --acceptance {ac_id} --mode fixture --output <ABS>"
        )
        parts.append(f"### {ac_id}\n\n")
        parts.append(
            yaml_task(
                f"TASK-INH-{n:03d}",
                [f"REQ-{domain}-001"],
                [ac_id],
                ["octop-client/tools/verify.py", "scripts/enterprise/verify.mjs"],
                f"保留并按协议 1.1/schema2 升级 {ac_id} 行为断言（modes={modes}）",
                "constant assertion or missing original oracle is FAIL",
                [cmd],
                "M5",
            )
        )
        n += 1

    n = 1
    for ac_id in close_ids():
        meta = CLOSE_META[ac_id]
        cmds = [
            f"{'node scripts/enterprise/verify.mjs' if owner_for(ac_id)=='node' else 'python octop-client/tools/verify.py'} --acceptance {ac_id} --mode {mode} --output <ABS>"
            for mode in meta["modes"]
        ]
        parts.append(f"### {ac_id}\n\n")
        parts.append(
            yaml_task(
                f"TASK-CLOSE-{n:03d}",
                list(meta["req"]),
                [ac_id],
                list(meta["files"]),
                meta["fail"],
                meta["fail"],
                cmds,
                meta["milestone"],
            )
        )
        n += 1

    n = 1
    for fi_id in fi_ids():
        parts.append(f"### {fi_id}\n\n")
        parts.append(
            yaml_task(
                f"TASK-FI-{n:03d}",
                ["REQ-EVID-001", "REQ-CLOSE-012"],
                [fi_id],
                ["octop-client/tools/acceptance/fis.py"],
                f"原 {fi_id} 必须到达注入点且 injection_observed=true",
                "unobserved injection cannot PASS",
                [f"python octop-client/tools/verify.py --acceptance {fi_id} --mode fixture --output <ABS>"],
                "M5",
            )
        )
        n += 1

    n = 1
    for fi_id in fi_close_ids():
        meta = FI_CLOSE_META[fi_id]
        cmds = [
            f"python octop-client/tools/verify.py --acceptance {fi_id} --mode {mode} --output <ABS>"
            for mode in meta["modes"]
        ]
        parts.append(f"### {fi_id}\n\n")
        parts.append(
            yaml_task(
                f"TASK-FIC-{n:03d}",
                ["REQ-CLOSE-012"],
                [fi_id, *meta["ac"]],
                ["octop-client/tools/acceptance/fis.py"],
                f"注入 {meta['point']}；postcondition: {meta['post']}",
                meta["post"],
                cmds,
                "M5",
            )
        )
        n += 1

    parts.append("## 5. 验证命令\n\n")
    parts.append("```text\n")
    parts.append("node scripts/enterprise/verify.mjs --acceptance ALL --mode fixture --output <ABS>\n")
    parts.append("python octop-client/tools/verify.py --acceptance ALL --mode fixture --output <ABS>\n")
    parts.append("node scripts/enterprise/gate.mjs --required contracts/octop-client/v1/required-acceptance.json --run-index <ABS>/run-index.json --release-manifest <ABS>/release.json --output <ABS>/G-RELEASE.json\n")
    parts.append("```\n")
    parts.append("\n单用例 exit: 0=PASS 1=FAIL 2=BLOCKED 3=SKIPPED。G-RELEASE 仅 PASS/FAIL。\n")
    parts.append("\n## 6. 交付\n\n")
    parts.append("- implemented 与 verified 分列。\n")
    parts.append("- 交付实际两仓 SHA、构建产物、可重跑命令、证据索引、Gate 结果、运维手册。\n")
    parts.append("- 不得用模拟宿主、模拟 Peer、常量断言或手填 PASS 替代真实交付。\n")
    return "".join(parts)


def main() -> int:
    prd_path = ROOT / "prd" / "Page_Assist_Plan_B_Landing_Closure_PRD_v1.1.md"
    prd_sha = sha256_file(prd_path) if prd_path.exists() else "MISSING"
    pa_head = git_sha(ROOT)
    oc_head = git_sha(Path("E:/git/octop"))
    required = build_required_json(prd_sha)
    dest_json = ROOT / "contracts" / "octop-client" / "v1" / "required-acceptance.json"
    dest_json.parent.mkdir(parents=True, exist_ok=True)
    dest_json.write_text(json.dumps(required, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    plan = build_plan(prd_sha, pa_head, oc_head)
    dest_plan = ROOT / "prd" / "Page_Assist_Plan_B_Closure_v1.1.plan.md"
    dest_plan.write_text(plan, encoding="utf-8")
    print(json.dumps({"plan": str(dest_plan), "required": str(dest_json), "prd_sha256": prd_sha, "tuples": len(tuples())}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
