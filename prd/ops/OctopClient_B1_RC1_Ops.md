# OctopClient B1-RC1 运维手册

## 范围

本手册覆盖 Page Assist 方案 B 在 Octop Hub 同进程内安装、启停、升级与回滚 `page-assist-octop-client` 的操作。生产路径禁止 `FixtureHostPort` / `fixture_mode=true`。

## 身份与 SHA

证据绑定**实际 checkout SHA**，禁止把基线 SHA 填成已打补丁产物。

- Page Assist 基线：`ff1df1ce4df8b3d12be231fb40857fd3a46fc88c`
- Octop 基线：`e3041c452ffc870f754378bd99d964349580d3f9`
- 采集：`git rev-parse HEAD`（两仓分别记录）+ dirty manifest SHA-256

## 安装

```text
python octop-client/tools/deploy.py install \
  --state-root <ABS> \
  --releases-root <ABS> \
  --manifest <ABS> \
  --manifest-sha256 <sha256> \
  --wheelhouse <ABS> \
  --requirements-lock <ABS> \
  --config <ABS>
```

规则：

- `--releases-root` 为正式参数；`--release-root` 仅为别名。两者同时出现为参数错误。
- 拒绝仅 `--wheel` 的不完整输入。
- 安装使用 hash lock：`--no-index --find-links --require-hashes`。
- 闸门空闲才停服。进程 + 包摘要 + Client API 同时 READY 才算成功。

## 启停

- `enable` / `disable`：热失效配置，不重启宿主，不 cancel 已接纳回合。
- `uninstall`：切到 host-only 新 release，保留业务库与恢复材料。
- `workers=1`。`maintenance.sock` 与 uvicorn 同 loop，不新增 TCP 端口（POSIX）。

## 回滚

失败语义：exit 6 / `RECOVERY_REQUIRED`，不覆盖新消息。

```text
python octop-client/tools/deploy.py rollback --state-root <ABS> --releases-root <ABS>
```

## 登录与托管完成

Dashboard：`/login/client/complete?transaction_id=&client_id=&state=`

必须调用：

`POST /api/auth/client-authorizations/{id}/complete`

body 仅 `{client_id,state}`，使用 `Depends(current_user)`。禁止 body `as_user`。

## 个人 Peer 绑定

`GET/POST/DELETE /api/bridge/connections/{id}/client-binding`

仅 owner + `get_owned`。`shared=True` 拒绝。身份来自已认证 Peer，禁止固定 `peer_user`。

## 验收

```text
node scripts/enterprise/verify.mjs --acceptance ALL --mode fixture --output <ABS>
python octop-client/tools/verify.py --acceptance ALL --mode fixture --output <ABS>
node scripts/enterprise/combine-index.mjs --output <ABS>
node scripts/enterprise/gate.mjs --required contracts/octop-client/v1/required-acceptance.json --run-index <ABS>/run-index-combined.json --release-manifest <ABS> --output <ABS>/G-RELEASE.json
```

单用例 exit：0 PASS / 1 FAIL / 2 BLOCKED / 3 SKIPPED。G-RELEASE 仅 PASS|FAIL。required 的 BLOCKED/SKIPPED/缺失 = FAIL。

## 环境缺项

无 `deployment-input.json` 时 live/deploy AC 标 BLOCKED，字段见 `contracts/octop-client/v1/deployment-input.schema.json`。Windows 无 systemd 时 M4 live 保持 BLOCKED。不把 fixture Alpha Expert 或 mock Peer 标 live PASS。

## 当前工作区证据

- `artifacts/acceptance/run-index-combined.json`
- `artifacts/acceptance/G-RELEASE.json`
- `artifacts/acceptance/closure-summary.json`
- 可重跑：Node `verify.mjs --acceptance ALL --mode fixture`；Python `octop-client/tools/verify.py --acceptance ALL --mode fixture`；`combine-index.mjs`；`gate.mjs`
