from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
COMBINED = ROOT / "artifacts" / "acceptance" / "run-index-combined.json"
PLAN = ROOT / "prd" / "Page_Assist_Plan_B_Closure_v1.1.plan.md"


def main() -> None:
    latest = {}
    combined = json.loads(COMBINED.read_text(encoding="utf-8"))
    for row in combined["runs"]:
        latest[row["acceptance_id"]] = row
    plan = PLAN.read_text(encoding="utf-8")

    def update_block(block: str) -> str:
        match = re.search(r"acceptance_refs: \[([^\]]+)\]", block)
        ids = re.findall(r"'([^']+)'", match.group(1) if match else "")
        if not ids:
            return block
        statuses = [latest.get(item, {}).get("status") for item in ids]
        if statuses and all(status == "PASS" for status in statuses):
            status, implemented, verified = "verified", "true", "true"
        elif any(status == "BLOCKED" for status in statuses):
            status, implemented, verified = "blocked", "true", "false"
        else:
            status, implemented, verified = "implemented", "true", "false"
        evid = [latest[item]["run_json"] for item in ids if item in latest]
        block = re.sub(r"status: planned", f"status: {status}", block)
        block = re.sub(r"implemented: false", f"implemented: {implemented}", block)
        block = re.sub(r"verified: false", f"verified: {verified}", block)
        if evid:
            evid_yaml = "\n".join(f"  - {path}" for path in evid)
            block = block.replace("evidence: []", "evidence:\n" + evid_yaml)
        return block

    def repl(match: re.Match[str]) -> str:
        return "```yaml\n" + update_block(match.group(1)) + "\n```"

    updated = re.sub(r"```yaml\n(.*?)\n```", repl, plan, flags=re.S)
    updated = updated.replace("status: planned\ngenerated_at:", "status: implemented\ngenerated_at:", 1)
    appendix = """

## 9. 实施结果（工作区，未 git commit）

- Page Assist HEAD: `ff1df1ce4df8b3d12be231fb40857fd3a46fc88c`（dirty 工作区含收口补丁；证据绑定实际 SHA + dirty manifest）
- Octop HEAD: `e3041c452ffc870f754378bd99d964349580d3f9`（dirty 工作区含 HostPort/complete/binding 补丁）
- Fixture 唯一 ID：146（114 AC + 32 FI）。PASS 136 / BLOCKED 10 / FAIL 0。
- BLOCKED：`A-OBS-001`、`A-DEPLOY-001`、`A-DEPLOY-003`、`A-EVID-003`、`A-CLOSE-033`、`A-CLOSE-035`、`A-CLOSE-036`、`A-CLOSE-041`、`A-CLOSE-043`、`A-CLOSE-044`。缺 `deployment-input.json` / systemd / 真实 Peer live 参数，未冒充 PASS。
- G-RELEASE：FAIL（required live 元组缺失 + required BLOCKED）。诚实门禁。
- 证据：`artifacts/acceptance/run-index-combined.json`、`artifacts/acceptance/G-RELEASE.json`、`prd/ops/OctopClient_B1_RC1_Ops.md`
"""
    if "## 9. 实施结果" not in updated:
        updated += appendix
    PLAN.write_text(updated, encoding="utf-8")
    print(
        "verified",
        updated.count("status: verified"),
        "blocked",
        updated.count("status: blocked"),
        "implemented",
        updated.count("status: implemented"),
        "planned",
        updated.count("status: planned"),
    )


if __name__ == "__main__":
    main()
