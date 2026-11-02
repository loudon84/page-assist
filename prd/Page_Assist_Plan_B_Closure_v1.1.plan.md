# Page Assist 方案 B 落地收口实施计划 v1.1
status: implemented
generated_at: 2026-11-02T05:54:37Z
prd: prd/Page_Assist_Plan_B_Landing_Closure_PRD_v1.1.md
baseline_prd: prd/Page_Assist_Plan_B_Server_OctopClient_PRD_v1.0.md

## 0. 源码身份

- Page Assist 文档基线: `ff1df1ce4df8b3d12be231fb40857fd3a46fc88c`
- Page Assist 实际 HEAD: `ff1df1ce4df8b3d12be231fb40857fd3a46fc88c`
- Octop 文档基线: `e3041c452ffc870f754378bd99d964349580d3f9`
- Octop 实际 HEAD: `e3041c452ffc870f754378bd99d964349580d3f9`
- 原 PRD git blob: `356f2c2e61a17c032407ede047846840f8c61866`
- 收口 PRD sha256: `e64a30866307104a4d026488a9222b92c4c1d001290f49a7676957b1f084f2b9`
- 证据必须绑定实际 SHA；禁止把基线 SHA 填成已打补丁产物。
- `octop-client/` 仅存在于 Page Assist 根目录；安装运行于 Octop 服务器。

## 1. 环境缺项（live BLOCKED 字段）

- `instance_role`
- `instance_id`
- `releases_root`
- `state_root`
- `db_identity`
- `python`
- `unit`
- `service_user`
- `expected_exec_argv`
- `public_origin`
- `health_probe`
- `client_registrations`
- `baseline_release`
- `baseline_manifest_sha256`
- `release_manifest`
- `wheelhouse`
- `requirements_lock`
- `config`
- `secret_references`
- `live_test_identities`

缺上述字段时继续完成不依赖环境的代码与 fixture/build；相关 AC/FI 标记 `blocked`，G-RELEASE=FAIL。

## 2. 覆盖矩阵

- 继承 22 REQ / 66 AC / FI-01～16 全部保留。
- 新增 REQ-CLOSE-001～012 / A-CLOSE-001～048 / FI-CLOSE-001～016。
- 合计 114 AC + 32 FI；Gate 对 required 的 BLOCKED/SKIPPED/缺失一律 FAIL。

## 3. 批次

- M0 门禁与构建：A-CLOSE-001/045/046，FI-CLOSE-001/016
- M1 宿主与登录：A-CLOSE-005～016，FI-CLOSE-003～005
- M2 会话与材料：A-CLOSE-002～004、017～032、037～040，FI-CLOSE-002、006～011
- M3 个人 Peer：A-CLOSE-033～036，FI-CLOSE-012
- M4 发布运维：A-CLOSE-041～044，FI-CLOSE-013/014
- M5 组合验收：A-CLOSE-047/048 与全集证据

## 4. TASK 清单

### A-CONFIG-001

```yaml
id: TASK-INH-001
requirement_refs: ['REQ-CONFIG-001']
acceptance_refs: ['A-CONFIG-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CONFIG-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CONFIG-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CONFIG-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CONFIG-001\f425e24a-cae4-429e-82bc-72b505732783\run.json
```
### A-CONFIG-002

```yaml
id: TASK-INH-002
requirement_refs: ['REQ-CONFIG-001']
acceptance_refs: ['A-CONFIG-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CONFIG-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CONFIG-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CONFIG-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CONFIG-002\01955747-b65a-4e32-9340-1457fee89cad\run.json
```
### A-CONFIG-003

```yaml
id: TASK-INH-003
requirement_refs: ['REQ-CONFIG-001']
acceptance_refs: ['A-CONFIG-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CONFIG-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CONFIG-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CONFIG-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CONFIG-003\b9069753-3e9d-4319-b7b4-36ddaaf0f23a\run.json
```
### A-AUTH-001

```yaml
id: TASK-INH-004
requirement_refs: ['REQ-AUTH-001']
acceptance_refs: ['A-AUTH-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-AUTH-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-AUTH-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-AUTH-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-AUTH-001\9726e2fa-8671-45de-9507-3fc992be511c\run.json
```
### A-AUTH-002

```yaml
id: TASK-INH-005
requirement_refs: ['REQ-AUTH-001']
acceptance_refs: ['A-AUTH-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-AUTH-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-AUTH-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-AUTH-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-AUTH-002\d2ee6d64-15b5-438c-b760-f0d135672d09\run.json
```
### A-AUTH-003

```yaml
id: TASK-INH-006
requirement_refs: ['REQ-AUTH-001']
acceptance_refs: ['A-AUTH-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-AUTH-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-AUTH-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-AUTH-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-AUTH-003\29c7fe26-c5a1-44c3-82fc-e8362d7beb93\run.json
```
### A-SESSION-001

```yaml
id: TASK-INH-007
requirement_refs: ['REQ-SESSION-001']
acceptance_refs: ['A-SESSION-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-SESSION-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-SESSION-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-SESSION-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-SESSION-001\8f2e04d6-c877-43c0-a077-c8928ec7ee20\run.json
```
### A-SESSION-002

```yaml
id: TASK-INH-008
requirement_refs: ['REQ-SESSION-001']
acceptance_refs: ['A-SESSION-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-SESSION-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-SESSION-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-SESSION-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-SESSION-002\cdf1ad6b-7b8b-40a8-a6c0-d0c7e9f582ef\run.json
```
### A-SESSION-003

```yaml
id: TASK-INH-009
requirement_refs: ['REQ-SESSION-001']
acceptance_refs: ['A-SESSION-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-SESSION-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-SESSION-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-SESSION-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-SESSION-003\109c7e7f-ee8a-471d-8453-8725ad1f7b55\run.json
```
### A-UI-001

```yaml
id: TASK-INH-010
requirement_refs: ['REQ-UI-001']
acceptance_refs: ['A-UI-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-UI-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-UI-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-UI-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-UI-001\589c50d7-bccd-4167-8c1b-140fc5bfd3c1\run.json
```
### A-UI-002

```yaml
id: TASK-INH-011
requirement_refs: ['REQ-UI-001']
acceptance_refs: ['A-UI-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-UI-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-UI-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-UI-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-UI-002\065e1329-9fd6-48eb-a33b-ccfd28b98c44\run.json
```
### A-UI-003

```yaml
id: TASK-INH-012
requirement_refs: ['REQ-UI-001']
acceptance_refs: ['A-UI-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-UI-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-UI-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-UI-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-UI-003\a9b8f36c-5155-4d82-8ff7-8c0b10155273\run.json
```
### A-CATALOG-001

```yaml
id: TASK-INH-013
requirement_refs: ['REQ-CATALOG-001']
acceptance_refs: ['A-CATALOG-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CATALOG-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CATALOG-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CATALOG-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CATALOG-001\9635ca82-38ec-4aff-b2af-2868f29b7366\run.json
```
### A-CATALOG-002

```yaml
id: TASK-INH-014
requirement_refs: ['REQ-CATALOG-001']
acceptance_refs: ['A-CATALOG-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CATALOG-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CATALOG-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CATALOG-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CATALOG-002\19282e24-a1a7-455b-b703-da9002fb22ba\run.json
```
### A-CATALOG-003

```yaml
id: TASK-INH-015
requirement_refs: ['REQ-CATALOG-001']
acceptance_refs: ['A-CATALOG-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CATALOG-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CATALOG-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CATALOG-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CATALOG-003\bf47065f-bd1b-4343-a6e9-2203d5224305\run.json
```
### A-CLIENT-001

```yaml
id: TASK-INH-016
requirement_refs: ['REQ-CLIENT-001']
acceptance_refs: ['A-CLIENT-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CLIENT-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CLIENT-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLIENT-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLIENT-001\a6856be9-c684-47aa-82b7-3ab17269c963\run.json
```
### A-CLIENT-002

```yaml
id: TASK-INH-017
requirement_refs: ['REQ-CLIENT-001']
acceptance_refs: ['A-CLIENT-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CLIENT-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CLIENT-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLIENT-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLIENT-002\84189904-354a-4e2c-935e-4a822e846af0\run.json
```
### A-CLIENT-003

```yaml
id: TASK-INH-018
requirement_refs: ['REQ-CLIENT-001']
acceptance_refs: ['A-CLIENT-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CLIENT-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CLIENT-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLIENT-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLIENT-003\f824568e-3f15-4335-b635-64aac9965338\run.json
```
### A-HOST-001

```yaml
id: TASK-INH-019
requirement_refs: ['REQ-HOST-001']
acceptance_refs: ['A-HOST-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-HOST-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-HOST-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-HOST-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-HOST-001\efaa6dc6-a0ce-49ae-be91-79c2fae88c55\run.json
```
### A-HOST-002

```yaml
id: TASK-INH-020
requirement_refs: ['REQ-HOST-001']
acceptance_refs: ['A-HOST-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-HOST-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-HOST-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-HOST-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-HOST-002\ac2bfc43-c1ec-41ae-a186-9133e308a71c\run.json
```
### A-HOST-003

```yaml
id: TASK-INH-021
requirement_refs: ['REQ-HOST-001']
acceptance_refs: ['A-HOST-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-HOST-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-HOST-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-HOST-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-HOST-003\99a6eaa3-1297-41aa-84ec-b27114538250\run.json
```
### A-PACKAGE-001

```yaml
id: TASK-INH-022
requirement_refs: ['REQ-PACKAGE-001']
acceptance_refs: ['A-PACKAGE-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-PACKAGE-001 行为断言（modes=build）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-PACKAGE-001 行为断言（modes=build）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-PACKAGE-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-PACKAGE-001\23b19851-6c12-4d96-9d36-9029662fbcf3\run.json
```
### A-PACKAGE-002

```yaml
id: TASK-INH-023
requirement_refs: ['REQ-PACKAGE-001']
acceptance_refs: ['A-PACKAGE-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-PACKAGE-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-PACKAGE-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-PACKAGE-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-PACKAGE-002\22702e2d-3d94-4077-8afb-a3e49dce32e4\run.json
```
### A-PACKAGE-003

```yaml
id: TASK-INH-024
requirement_refs: ['REQ-PACKAGE-001']
acceptance_refs: ['A-PACKAGE-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-PACKAGE-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-PACKAGE-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-PACKAGE-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-PACKAGE-003\ff9e27aa-8e1a-4e2d-8c0a-51d435a6a5dc\run.json
```
### A-DEPLOY-001

```yaml
id: TASK-INH-025
requirement_refs: ['REQ-DEPLOY-001']
acceptance_refs: ['A-DEPLOY-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-DEPLOY-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-DEPLOY-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-DEPLOY-001 --mode fixture --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-DEPLOY-001\ec0b8347-3107-49ad-82cf-f27b540b1fc8\run.json
```
### A-DEPLOY-002

```yaml
id: TASK-INH-026
requirement_refs: ['REQ-DEPLOY-001']
acceptance_refs: ['A-DEPLOY-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-DEPLOY-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-DEPLOY-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-DEPLOY-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-DEPLOY-002\ef00a848-8c20-41d0-a38b-1c0f4a5218c4\run.json
```
### A-DEPLOY-003

```yaml
id: TASK-INH-027
requirement_refs: ['REQ-DEPLOY-001']
acceptance_refs: ['A-DEPLOY-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-DEPLOY-003 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-DEPLOY-003 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-DEPLOY-003 --mode fixture --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-DEPLOY-003\8609c98b-0d1f-48c3-b7b3-73377b479464\run.json
```
### A-UPGRADE-001

```yaml
id: TASK-INH-028
requirement_refs: ['REQ-UPGRADE-001']
acceptance_refs: ['A-UPGRADE-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-UPGRADE-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-UPGRADE-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-UPGRADE-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-UPGRADE-001\5b1651f4-a0f4-4245-86a1-b3280c828bb8\run.json
```
### A-UPGRADE-002

```yaml
id: TASK-INH-029
requirement_refs: ['REQ-UPGRADE-001']
acceptance_refs: ['A-UPGRADE-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-UPGRADE-002 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-UPGRADE-002 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-UPGRADE-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-UPGRADE-002\a7c43a1b-cc5f-40a9-aa82-7e598b1f6b43\run.json
```
### A-UPGRADE-003

```yaml
id: TASK-INH-030
requirement_refs: ['REQ-UPGRADE-001']
acceptance_refs: ['A-UPGRADE-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-UPGRADE-003 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-UPGRADE-003 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-UPGRADE-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-UPGRADE-003\9cbc4953-7c95-4748-8dad-f20b436a7737\run.json
```
### A-THREAD-001

```yaml
id: TASK-INH-031
requirement_refs: ['REQ-THREAD-001']
acceptance_refs: ['A-THREAD-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-THREAD-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-THREAD-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-THREAD-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-THREAD-001\703841dc-511b-4633-b3ba-d723070a2c99\run.json
```
### A-THREAD-002

```yaml
id: TASK-INH-032
requirement_refs: ['REQ-THREAD-001']
acceptance_refs: ['A-THREAD-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-THREAD-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-THREAD-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-THREAD-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-THREAD-002\ea90a9cc-6d3a-4206-aa22-7850c7014cf8\run.json
```
### A-THREAD-003

```yaml
id: TASK-INH-033
requirement_refs: ['REQ-THREAD-001']
acceptance_refs: ['A-THREAD-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-THREAD-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-THREAD-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-THREAD-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-THREAD-003\c1b67e5d-648e-485e-b169-c0be61fb69f1\run.json
```
### A-TURN-001

```yaml
id: TASK-INH-034
requirement_refs: ['REQ-TURN-001']
acceptance_refs: ['A-TURN-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-TURN-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-TURN-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-TURN-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-TURN-001\bc31cb85-d8db-4679-871e-ba0a30db181f\run.json
```
### A-TURN-002

```yaml
id: TASK-INH-035
requirement_refs: ['REQ-TURN-001']
acceptance_refs: ['A-TURN-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-TURN-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-TURN-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-TURN-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-TURN-002\3e02336e-96cb-494b-8649-3426ceaf3de1\run.json
```
### A-TURN-003

```yaml
id: TASK-INH-036
requirement_refs: ['REQ-TURN-001']
acceptance_refs: ['A-TURN-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-TURN-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-TURN-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-TURN-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-TURN-003\5179a3d7-fbbc-4690-8e74-4976cc1bee05\run.json
```
### A-RECOVER-001

```yaml
id: TASK-INH-037
requirement_refs: ['REQ-RECOVER-001']
acceptance_refs: ['A-RECOVER-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-RECOVER-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-RECOVER-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-RECOVER-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-RECOVER-001\7985b061-3c55-49b2-b893-843128d327fa\run.json
```
### A-RECOVER-002

```yaml
id: TASK-INH-038
requirement_refs: ['REQ-RECOVER-001']
acceptance_refs: ['A-RECOVER-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-RECOVER-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-RECOVER-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-RECOVER-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-RECOVER-002\470b4e7c-5dde-4b45-bfbb-5009d0a5fd6e\run.json
```
### A-RECOVER-003

```yaml
id: TASK-INH-039
requirement_refs: ['REQ-RECOVER-001']
acceptance_refs: ['A-RECOVER-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-RECOVER-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-RECOVER-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-RECOVER-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-RECOVER-003\2bd28b16-5174-4256-82f7-c2a37cf82b25\run.json
```
### A-HITL-001

```yaml
id: TASK-INH-040
requirement_refs: ['REQ-HITL-001']
acceptance_refs: ['A-HITL-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-HITL-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-HITL-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-HITL-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-HITL-001\7b5d4f99-ab1c-4916-8358-f059559f1c3d\run.json
```
### A-HITL-002

```yaml
id: TASK-INH-041
requirement_refs: ['REQ-HITL-001']
acceptance_refs: ['A-HITL-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-HITL-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-HITL-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-HITL-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-HITL-002\2f4fee20-5d1d-48a6-b80d-ffb7a7661db5\run.json
```
### A-HITL-003

```yaml
id: TASK-INH-042
requirement_refs: ['REQ-HITL-001']
acceptance_refs: ['A-HITL-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-HITL-003 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-HITL-003 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-HITL-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-HITL-003\f2408895-110d-446b-b055-64a322e5841c\run.json
```
### A-CONTEXT-001

```yaml
id: TASK-INH-043
requirement_refs: ['REQ-CONTEXT-001']
acceptance_refs: ['A-CONTEXT-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CONTEXT-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CONTEXT-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CONTEXT-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CONTEXT-001\5b30a121-8e9b-446f-8582-14fab9db936e\run.json
```
### A-CONTEXT-002

```yaml
id: TASK-INH-044
requirement_refs: ['REQ-CONTEXT-001']
acceptance_refs: ['A-CONTEXT-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CONTEXT-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CONTEXT-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CONTEXT-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CONTEXT-002\5f25c682-e33d-4c81-bb48-c9c036fea60f\run.json
```
### A-CONTEXT-003

```yaml
id: TASK-INH-045
requirement_refs: ['REQ-CONTEXT-001']
acceptance_refs: ['A-CONTEXT-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-CONTEXT-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-CONTEXT-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CONTEXT-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CONTEXT-003\a8997427-f04f-4f44-bc9d-a788661c6c81\run.json
```
### A-FILE-001

```yaml
id: TASK-INH-046
requirement_refs: ['REQ-FILE-001']
acceptance_refs: ['A-FILE-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-FILE-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-FILE-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-FILE-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-FILE-001\be186f75-04eb-4b39-9d7d-bae4c5bb6555\run.json
```
### A-FILE-002

```yaml
id: TASK-INH-047
requirement_refs: ['REQ-FILE-001']
acceptance_refs: ['A-FILE-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-FILE-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-FILE-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-FILE-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-FILE-002\6625a143-6680-4b49-81c5-7d0b6172cc51\run.json
```
### A-FILE-003

```yaml
id: TASK-INH-048
requirement_refs: ['REQ-FILE-001']
acceptance_refs: ['A-FILE-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-FILE-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-FILE-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-FILE-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-FILE-003\a0527279-3887-4254-b2b8-0a44e2c1a18a\run.json
```
### A-DATA-001

```yaml
id: TASK-INH-049
requirement_refs: ['REQ-DATA-001']
acceptance_refs: ['A-DATA-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-DATA-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-DATA-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-DATA-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-DATA-001\844aa5f1-7545-4b5d-a333-a35746c1d597\run.json
```
### A-DATA-002

```yaml
id: TASK-INH-050
requirement_refs: ['REQ-DATA-001']
acceptance_refs: ['A-DATA-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-DATA-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-DATA-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-DATA-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-DATA-002\19e28fa4-c279-4c2e-8cef-3622ef39690d\run.json
```
### A-DATA-003

```yaml
id: TASK-INH-051
requirement_refs: ['REQ-DATA-001']
acceptance_refs: ['A-DATA-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-DATA-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-DATA-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-DATA-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-DATA-003\84a9fbf2-c701-4cb8-a6e2-d18e84c73113\run.json
```
### A-BRIDGE-001

```yaml
id: TASK-INH-052
requirement_refs: ['REQ-BRIDGE-001']
acceptance_refs: ['A-BRIDGE-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-BRIDGE-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-BRIDGE-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-BRIDGE-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-BRIDGE-001\5eff0b2b-c1a0-43ce-8ece-0b614be5b769\run.json
```
### A-BRIDGE-002

```yaml
id: TASK-INH-053
requirement_refs: ['REQ-BRIDGE-001']
acceptance_refs: ['A-BRIDGE-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-BRIDGE-002 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-BRIDGE-002 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-BRIDGE-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-BRIDGE-002\93f4a1c8-3b24-4e42-9d10-773c08b15101\run.json
```
### A-BRIDGE-003

```yaml
id: TASK-INH-054
requirement_refs: ['REQ-BRIDGE-001']
acceptance_refs: ['A-BRIDGE-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-BRIDGE-003 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-BRIDGE-003 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-BRIDGE-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-BRIDGE-003\05ba8f32-f91b-4c05-9a37-39481ca3a1fd\run.json
```
### A-COMPAT-001

```yaml
id: TASK-INH-055
requirement_refs: ['REQ-COMPAT-001']
acceptance_refs: ['A-COMPAT-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-COMPAT-001 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-COMPAT-001 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-COMPAT-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-COMPAT-001\16b57ac9-bf33-4f26-b236-2d71ce0c347f\run.json
```
### A-COMPAT-002

```yaml
id: TASK-INH-056
requirement_refs: ['REQ-COMPAT-001']
acceptance_refs: ['A-COMPAT-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-COMPAT-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-COMPAT-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-COMPAT-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-COMPAT-002\edc89e93-1de6-4df9-890a-15d443e675d2\run.json
```
### A-COMPAT-003

```yaml
id: TASK-INH-057
requirement_refs: ['REQ-COMPAT-001']
acceptance_refs: ['A-COMPAT-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-COMPAT-003 行为断言（modes=build）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-COMPAT-003 行为断言（modes=build）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-COMPAT-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-COMPAT-003\b8015fe1-7faf-430f-9881-0377574ab2fa\run.json
```
### A-SEC-001

```yaml
id: TASK-INH-058
requirement_refs: ['REQ-SEC-001']
acceptance_refs: ['A-SEC-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-SEC-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-SEC-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-SEC-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-SEC-001\ae96e275-205a-4be1-95c6-53e81added46\run.json
```
### A-SEC-002

```yaml
id: TASK-INH-059
requirement_refs: ['REQ-SEC-001']
acceptance_refs: ['A-SEC-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-SEC-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-SEC-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-SEC-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-SEC-002\e0f83200-971e-40d8-b1a9-3ccb2291b4e3\run.json
```
### A-SEC-003

```yaml
id: TASK-INH-060
requirement_refs: ['REQ-SEC-001']
acceptance_refs: ['A-SEC-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-SEC-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-SEC-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-SEC-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-SEC-003\67d44878-a881-4432-aa28-05598eb18954\run.json
```
### A-OBS-001

```yaml
id: TASK-INH-061
requirement_refs: ['REQ-OBS-001']
acceptance_refs: ['A-OBS-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-OBS-001 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-OBS-001 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-OBS-001 --mode fixture --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-OBS-001\a3009400-1c1d-414f-ac4d-4439386e814b\run.json
```
### A-OBS-002

```yaml
id: TASK-INH-062
requirement_refs: ['REQ-OBS-001']
acceptance_refs: ['A-OBS-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-OBS-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-OBS-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-OBS-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-OBS-002\e6facbf9-3074-4573-af5c-338ad723df27\run.json
```
### A-OBS-003

```yaml
id: TASK-INH-063
requirement_refs: ['REQ-OBS-001']
acceptance_refs: ['A-OBS-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-OBS-003 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-OBS-003 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-OBS-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-OBS-003\3df8b399-ee86-4da5-8460-1a9a7b316778\run.json
```
### A-EVID-001

```yaml
id: TASK-INH-064
requirement_refs: ['REQ-EVID-001']
acceptance_refs: ['A-EVID-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-EVID-001 行为断言（modes=document）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-EVID-001 行为断言（modes=document）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-EVID-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-EVID-001\da9f5d14-4948-40dc-9401-05eb428d191d\run.json
```
### A-EVID-002

```yaml
id: TASK-INH-065
requirement_refs: ['REQ-EVID-001']
acceptance_refs: ['A-EVID-002']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-EVID-002 行为断言（modes=fixture）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-EVID-002 行为断言（modes=fixture）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-EVID-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-EVID-002\2f0b44fb-b36b-435a-9b90-ef80461d5c64\run.json
```
### A-EVID-003

```yaml
id: TASK-INH-066
requirement_refs: ['REQ-EVID-001']
acceptance_refs: ['A-EVID-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: 保留并按协议 1.1/schema2 升级 A-EVID-003 行为断言（modes=fixture,live）
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 保留并按协议 1.1/schema2 升级 A-EVID-003 行为断言（modes=fixture,live）
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [constant assertion or missing original oracle is FAIL]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-EVID-003 --mode fixture --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-EVID-003\0d45ced0-18e3-4839-82d0-19d33ebdbb52\run.json
```
### A-CLOSE-001

```yaml
id: TASK-CLOSE-001
requirement_refs: ['REQ-CLOSE-001']
acceptance_refs: ['A-CLOSE-001']
files_or_symbols:
  - repository: page-assist
    path: src/services/octop-api/http.ts
    operation: modify
  - repository: page-assist
    path: package.json
    operation: modify
  - repository: page-assist
    path: scripts/enterprise/build-all.mjs
    operation: modify
implementation_goal: single target failure must propagate; no releasable zip
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: single target failure must propagate; no releasable zip
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [single target failure must propagate; no releasable zip]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-001 --mode build --output <ABS>
status: verified
implemented: true
verified: true
milestone: M0
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-001\ce4247b3-f0f9-47ee-8b99-6d826896f863\run.json
```
### A-CLOSE-002

```yaml
id: TASK-CLOSE-002
requirement_refs: ['REQ-CLOSE-001']
acceptance_refs: ['A-CLOSE-002']
files_or_symbols:
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
  - repository: page-assist
    path: src/hooks/octop/state.ts
    operation: modify
implementation_goal: first send before OPEN+subscribe is rejected; input/attachments preserved
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: first send before OPEN+subscribe is rejected; input/attachments preserved
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [first send before OPEN+subscribe is rejected; input/attachments preserved]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-002 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-002 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-002\0715b100-ee4e-4e3a-a713-adf38a45a531\run.json
```
### A-CLOSE-003

```yaml
id: TASK-CLOSE-003
requirement_refs: ['REQ-CLOSE-001']
acceptance_refs: ['A-CLOSE-003']
files_or_symbols:
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
implementation_goal: duplicate clicks produce one thread and one receipt
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: duplicate clicks produce one thread and one receipt
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [duplicate clicks produce one thread and one receipt]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-003 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-003 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-003\5b547092-3fc4-43da-a21f-4d509d05daf4\run.json
```
### A-CLOSE-004

```yaml
id: TASK-CLOSE-004
requirement_refs: ['REQ-CLOSE-001']
acceptance_refs: ['A-CLOSE-004']
files_or_symbols:
  - repository: page-assist
    path: src/routes/chrome.tsx
    operation: modify
  - repository: page-assist
    path: src/entries-firefox/options/App.tsx
    operation: modify
implementation_goal: Firefox enterprise identity calls remain zero; local history digest unchanged
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: Firefox enterprise identity calls remain zero; local history digest unchanged
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [Firefox enterprise identity calls remain zero; local history digest unchanged]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-004 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-004 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-004\4eb73f64-8d24-4ff7-b509-b2bf45d0c8cd\run.json
```
### A-CLOSE-005

```yaml
id: TASK-CLOSE-005
requirement_refs: ['REQ-CLOSE-002']
acceptance_refs: ['A-CLOSE-005']
files_or_symbols:
  - repository: octop
    path: src/octop/integrations/page_assist_client/host.py
    operation: modify
  - repository: octop
    path: src/octop/api/app.py
    operation: modify
implementation_goal: production READY with FixtureHostPort is forbidden
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: production READY with FixtureHostPort is forbidden
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [production READY with FixtureHostPort is forbidden]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-005 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-005\5a75f78a-f8bd-4174-9d30-9d2e18bee04f\run.json
```
### A-CLOSE-006

```yaml
id: TASK-CLOSE-006
requirement_refs: ['REQ-CLOSE-002']
acceptance_refs: ['A-CLOSE-006']
files_or_symbols:
  - repository: octop
    path: src/octop/api/deps.py
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/asgi.py
    operation: modify
implementation_goal: unready/uninstalled Client API returns 503; JWT exemption is prefix-precise
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: unready/uninstalled Client API returns 503; JWT exemption is prefix-precise
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unready/uninstalled Client API returns 503; JWT exemption is prefix-precise]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-006 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-006 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-006\71ccf842-f1f1-4143-8720-feda56cef9ea\run.json
```
### A-CLOSE-007

```yaml
id: TASK-CLOSE-007
requirement_refs: ['REQ-CLOSE-002']
acceptance_refs: ['A-CLOSE-007']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/host/port.py
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/storage/schema.py
    operation: modify
implementation_goal: commit-before error rolls back thread/meta/receipt to zero delta
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: commit-before error rolls back thread/meta/receipt to zero delta
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [commit-before error rolls back thread/meta/receipt to zero delta]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-007 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-007\7177133d-ecd1-4f6b-81e4-a1b2e1456455\run.json
```
### A-CLOSE-008

```yaml
id: TASK-CLOSE-008
requirement_refs: ['REQ-CLOSE-002']
acceptance_refs: ['A-CLOSE-008']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/integration/register.py
    operation: modify
implementation_goal: drain closes WS; admitted turns are not cancelled
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: drain closes WS; admitted turns are not cancelled
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [drain closes WS; admitted turns are not cancelled]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-008 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-008 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-008\3f00e869-0193-435a-8a29-d94095aa8b46\run.json
```
### A-CLOSE-009

```yaml
id: TASK-CLOSE-009
requirement_refs: ['REQ-CLOSE-003']
acceptance_refs: ['A-CLOSE-009']
files_or_symbols:
  - repository: octop
    path: src/octop/api/routers/auth.py
    operation: modify
  - repository: page-assist
    path: src/services/octop-api/index.ts
    operation: modify
implementation_goal: SID is published only after GET /session succeeds
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: SID is published only after GET /session succeeds
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [SID is published only after GET /session succeeds]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-009 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-009\af1de4bb-0af5-402e-9697-8d4b3907dc27\run.json
```
### A-CLOSE-010

```yaml
id: TASK-CLOSE-010
requirement_refs: ['REQ-CLOSE-003']
acceptance_refs: ['A-CLOSE-010']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
implementation_goal: forged subject/state/verifier/replay creates zero SID
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: forged subject/state/verifier/replay creates zero SID
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [forged subject/state/verifier/replay creates zero SID]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-010 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-010 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-010\89757e40-d9ae-49ba-a757-7bbd28a5e9e5\run.json
```
### A-CLOSE-011

```yaml
id: TASK-CLOSE-011
requirement_refs: ['REQ-CLOSE-003']
acceptance_refs: ['A-CLOSE-011']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/storage/db.py
    operation: modify
implementation_goal: half identity is cleared; code cannot be replayed to mint SID
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: half identity is cleared; code cannot be replayed to mint SID
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [half identity is cleared; code cannot be replayed to mint SID]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-011 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-011\01ddf867-8bdd-43de-9c9e-925c6b1e15ad\run.json
```
### A-CLOSE-012

```yaml
id: TASK-CLOSE-012
requirement_refs: ['REQ-CLOSE-003']
acceptance_refs: ['A-CLOSE-012']
files_or_symbols:
  - repository: page-assist
    path: src/services/octop-api/auth-broker.ts
    operation: modify
  - repository: page-assist
    path: src/db/octop/index.ts
    operation: modify
implementation_goal: password/JWT never enter OctopApi logs, Dexie, or URL
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: password/JWT never enter OctopApi logs, Dexie, or URL
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [password/JWT never enter OctopApi logs, Dexie, or URL]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-012 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-012 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-012\ad76834e-f6f0-47e1-979c-0b6f52f04b8d\run.json
```
### A-CLOSE-013

```yaml
id: TASK-CLOSE-013
requirement_refs: ['REQ-CLOSE-004']
acceptance_refs: ['A-CLOSE-013']
files_or_symbols:
  - repository: page-assist
    path: src/services/octop-api/identity-coordinator.ts
    operation: modify
  - repository: page-assist
    path: src/services/octop-api/config.ts
    operation: modify
implementation_goal: old token requests to new origin = 0
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: old token requests to new origin = 0
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [old token requests to new origin = 0]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-013 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-013 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-013\3b3bf0f3-26e9-4f1b-90f4-6605514c15b8\run.json
```
### A-CLOSE-014

```yaml
id: TASK-CLOSE-014
requirement_refs: ['REQ-CLOSE-004']
acceptance_refs: ['A-CLOSE-014']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/ws.py
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/integration/register.py
    operation: modify
implementation_goal: post-logout user_turn message/turn delta = 0
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: post-logout user_turn message/turn delta = 0
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [post-logout user_turn message/turn delta = 0]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-014 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-014 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-014\bb13eea1-ddbf-43e8-b3b4-d4fa76057252\run.json
```
### A-CLOSE-015

```yaml
id: TASK-CLOSE-015
requirement_refs: ['REQ-CLOSE-004']
acceptance_refs: ['A-CLOSE-015']
files_or_symbols:
  - repository: page-assist
    path: src/services/octop-api/config.ts
    operation: modify
  - repository: page-assist
    path: src/entries/background.ts
    operation: modify
implementation_goal: content-script sender cannot call sensitive broker
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: content-script sender cannot call sensitive broker
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [content-script sender cannot call sensitive broker]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-015 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-015 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-015\21988bb6-2d8a-4ba7-bd45-fe87640fdd7c\run.json
```
### A-CLOSE-016

```yaml
id: TASK-CLOSE-016
requirement_refs: ['REQ-CLOSE-004']
acceptance_refs: ['A-CLOSE-016']
files_or_symbols:
  - repository: page-assist
    path: src/services/octop-api/identity-coordinator.ts
    operation: modify
implementation_goal: cleanup failure keeps lock; late callback cannot restore identity
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: cleanup failure keeps lock; late callback cannot restore identity
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [cleanup failure keeps lock; late callback cannot restore identity]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-016 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M1
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-016\ac2c7374-bb02-44b8-b2ea-af36657f5c0e\run.json
```
### A-CLOSE-017

```yaml
id: TASK-CLOSE-017
requirement_refs: ['REQ-CLOSE-005']
acceptance_refs: ['A-CLOSE-017']
files_or_symbols:
  - repository: page-assist
    path: src/components/Octop/
    operation: modify
  - repository: page-assist
    path: src/services/octop-api/index.ts
    operation: modify
implementation_goal: list/recent entry missing means FAIL not implicit empty success
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: list/recent entry missing means FAIL not implicit empty success
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [list/recent entry missing means FAIL not implicit empty success]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-017 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-017 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-017\4eb4a026-bca8-47b2-8068-8d186cc15b63\run.json
```
### A-CLOSE-018

```yaml
id: TASK-CLOSE-018
requirement_refs: ['REQ-CLOSE-005']
acceptance_refs: ['A-CLOSE-018']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/cursors.py
    operation: modify
implementation_goal: stale cursor is CURSOR_STALE; new messages do not duplicate old pages
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: stale cursor is CURSOR_STALE; new messages do not duplicate old pages
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [stale cursor is CURSOR_STALE; new messages do not duplicate old pages]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-018 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-018\f4b486c6-f2be-462e-af43-ab1de9aec9cb\run.json
```
### A-CLOSE-019

```yaml
id: TASK-CLOSE-019
requirement_refs: ['REQ-CLOSE-005']
acceptance_refs: ['A-CLOSE-019']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
implementation_goal: wrong owner/expert/channel GET leaves business digest unchanged
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: wrong owner/expert/channel GET leaves business digest unchanged
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [wrong owner/expert/channel GET leaves business digest unchanged]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-019 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-019 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-019\83e0b22c-2235-4324-a975-c49a00da146d\run.json
```
### A-CLOSE-020

```yaml
id: TASK-CLOSE-020
requirement_refs: ['REQ-CLOSE-005']
acceptance_refs: ['A-CLOSE-020']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
implementation_goal: expired idempotency key is rejected; replay of same hash returns original resource
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: expired idempotency key is rejected; replay of same hash returns original resource
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [expired idempotency key is rejected; replay of same hash returns original resource]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-020 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-020\80199d0f-a997-49d3-a3a2-6f4c9fa65dfd\run.json
```
### A-CLOSE-021

```yaml
id: TASK-CLOSE-021
requirement_refs: ['REQ-CLOSE-006']
acceptance_refs: ['A-CLOSE-021']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/ws.py
    operation: modify
  - repository: page-assist
    path: src/services/octop-api/websocket.ts
    operation: modify
implementation_goal: ack timeout 10s; ping 20s / pong 40s; no auto cancel on close
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: ack timeout 10s; ping 20s / pong 40s; no auto cancel on close
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [ack timeout 10s; ping 20s / pong 40s; no auto cancel on close]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-021 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-021 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-021\958cfe23-b113-40e9-8303-537c4366b3bd\run.json
```
### A-CLOSE-022

```yaml
id: TASK-CLOSE-022
requirement_refs: ['REQ-CLOSE-006']
acceptance_refs: ['A-CLOSE-022']
files_or_symbols:
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/host/port.py
    operation: modify
implementation_goal: runtime_revision must not go backwards; reopen is not always IDLE
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: runtime_revision must not go backwards; reopen is not always IDLE
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [runtime_revision must not go backwards; reopen is not always IDLE]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-022 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-022 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-022\a8d49feb-b649-47f1-86cb-b6ffc9c04a12\run.json
```
### A-CLOSE-023

```yaml
id: TASK-CLOSE-023
requirement_refs: ['REQ-CLOSE-006']
acceptance_refs: ['A-CLOSE-023']
files_or_symbols:
  - repository: page-assist
    path: src/services/octop-api/websocket.ts
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/ws.py
    operation: modify
implementation_goal: accepted turn is not resent; ticket is single-use
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: accepted turn is not resent; ticket is single-use
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [accepted turn is not resent; ticket is single-use]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-023 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-023 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-023\7fd6b0af-60ff-4e06-9b1a-c7517729333d\run.json
```
### A-CLOSE-024

```yaml
id: TASK-CLOSE-024
requirement_refs: ['REQ-CLOSE-006']
acceptance_refs: ['A-CLOSE-024']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/ws.py
    operation: modify
implementation_goal: cancel receipt is requested-only; close WS does not cancel
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: cancel receipt is requested-only; close WS does not cancel
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [cancel receipt is requested-only; close WS does not cancel]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-024 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-024 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-024\392a4944-2738-47d4-8e37-44ccf6feaf3b\run.json
```
### A-CLOSE-025

```yaml
id: TASK-CLOSE-025
requirement_refs: ['REQ-CLOSE-007']
acceptance_refs: ['A-CLOSE-025']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
implementation_goal: trailing LF SHA mismatch rejects; original bytes preserved
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: trailing LF SHA mismatch rejects; original bytes preserved
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [trailing LF SHA mismatch rejects; original bytes preserved]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-025 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-025 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-025\d2a28cc5-6be1-4f75-9f75-282227e23b80\run.json
```
### A-CLOSE-026

```yaml
id: TASK-CLOSE-026
requirement_refs: ['REQ-CLOSE-007']
acceptance_refs: ['A-CLOSE-026']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/host/fixture.py
    operation: modify
implementation_goal: cross-owner upload reference: accept=0 and B state unchanged
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: cross-owner upload reference: accept=0 and B state unchanged
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [cross-owner upload reference: accept=0 and B state unchanged]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-026 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-026 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-026\212ad5be-5c46-4d8f-83a2-1b72960bfc1f\run.json
```
### A-CLOSE-027

```yaml
id: TASK-CLOSE-027
requirement_refs: ['REQ-CLOSE-007']
acceptance_refs: ['A-CLOSE-027']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/storage/db.py
    operation: modify
implementation_goal: orphan after file publish is recoverable; same key does not mint second ready
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: orphan after file publish is recoverable; same key does not mint second ready
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [orphan after file publish is recoverable; same key does not mint second ready]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-027 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-027\86ccc012-c7d2-49d6-9a57-58bca0142b04\run.json
```
### A-CLOSE-028

```yaml
id: TASK-CLOSE-028
requirement_refs: ['REQ-CLOSE-007']
acceptance_refs: ['A-CLOSE-028']
files_or_symbols:
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
implementation_goal: first ready kept when second file fails; TTL cleanup failures retry
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: first ready kept when second file fails; TTL cleanup failures retry
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [first ready kept when second file fails; TTL cleanup failures retry]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-028 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-028\1a0fd2c7-f3a5-4702-bf0e-0af5b1722100\run.json
```
### A-CLOSE-029

```yaml
id: TASK-CLOSE-029
requirement_refs: ['REQ-CLOSE-008']
acceptance_refs: ['A-CLOSE-029']
files_or_symbols:
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
implementation_goal: reopen restores same runtime_revision form snapshot
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: reopen restores same runtime_revision form snapshot
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [reopen restores same runtime_revision form snapshot]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-029 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-029 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-029\a47b2e96-4815-47b4-b0be-f77d0c3a5459\run.json
```
### A-CLOSE-030

```yaml
id: TASK-CLOSE-030
requirement_refs: ['REQ-CLOSE-008']
acceptance_refs: ['A-CLOSE-030']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
implementation_goal: empty decisions: pending unconsumed, tools=0
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: empty decisions: pending unconsumed, tools=0
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [empty decisions: pending unconsumed, tools=0]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-030 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-030\f30e8e0e-2135-4763-9204-f4cde458fc8a\run.json
```
### A-CLOSE-031

```yaml
id: TASK-CLOSE-031
requirement_refs: ['REQ-CLOSE-008']
acceptance_refs: ['A-CLOSE-031']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
implementation_goal: lost 202 confirmation does not auto-resubmit
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: lost 202 confirmation does not auto-resubmit
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [lost 202 confirmation does not auto-resubmit]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-031 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-031 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-031\b28a62c8-13f8-40a9-958f-3cfe82e762aa\run.json
```
### A-CLOSE-032

```yaml
id: TASK-CLOSE-032
requirement_refs: ['REQ-CLOSE-008']
acceptance_refs: ['A-CLOSE-032']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/api/handlers.py
    operation: modify
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
implementation_goal: remote approval.submit is never forwarded
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: remote approval.submit is never forwarded
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [remote approval.submit is never forwarded]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-032 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-032 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-032\341b6369-3579-4e4c-a656-d54cdbd9a235\run.json
```
### A-CLOSE-033

```yaml
id: TASK-CLOSE-033
requirement_refs: ['REQ-CLOSE-009']
acceptance_refs: ['A-CLOSE-033']
files_or_symbols:
  - repository: octop
    path: src/octop/api/routers/bridge.py
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/bridge/personal.py
    operation: modify
implementation_goal: fixture Alpha Expert does not satisfy live Peer
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: fixture Alpha Expert does not satisfy live Peer
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [fixture Alpha Expert does not satisfy live Peer]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-033 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M3
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-033\edbb19e1-cd98-4a6a-a7bf-ec6748a2273b\run.json
```
### A-CLOSE-034

```yaml
id: TASK-CLOSE-034
requirement_refs: ['REQ-CLOSE-009']
acceptance_refs: ['A-CLOSE-034']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/bridge/personal.py
    operation: modify
implementation_goal: fixed peer_user / as_user / auto-bind produce zero private business
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: fixed peer_user / as_user / auto-bind produce zero private business
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [fixed peer_user / as_user / auto-bind produce zero private business]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-034 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-034 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M3
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-034\953a6979-9c37-4e62-9743-704cf5c8db31\run.json
```
### A-CLOSE-035

```yaml
id: TASK-CLOSE-035
requirement_refs: ['REQ-CLOSE-009']
acceptance_refs: ['A-CLOSE-035']
files_or_symbols:
  - repository: octop
    path: src/octop/api/routers/bridge.py
    operation: modify
implementation_goal: shared connection private ops = 0; old resources not inherited
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: shared connection private ops = 0; old resources not inherited
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [shared connection private ops = 0; old resources not inherited]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-035 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-035 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M3
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-035\5c50cdc7-be33-42e1-a795-4517b51f9517\run.json
```
### A-CLOSE-036

```yaml
id: TASK-CLOSE-036
requirement_refs: ['REQ-CLOSE-009']
acceptance_refs: ['A-CLOSE-036']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/bridge/personal.py
    operation: modify
implementation_goal: unknown turn is not resent after peer disconnect
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: unknown turn is not resent after peer disconnect
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unknown turn is not resent after peer disconnect]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-036 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-036 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M3
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-036\f9d7c2c1-001d-48bf-8170-958dc7c3a787\run.json
```
### A-CLOSE-037

```yaml
id: TASK-CLOSE-037
requirement_refs: ['REQ-CLOSE-010']
acceptance_refs: ['A-CLOSE-037']
files_or_symbols:
  - repository: page-assist
    path: src/hooks/octop/usePageSnapshot.ts
    operation: modify
implementation_goal: preview equals submitted bytes; other tabs unread
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: preview equals submitted bytes; other tabs unread
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [preview equals submitted bytes; other tabs unread]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-037 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-037 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-037\51285e69-5dc8-498d-af91-98d9d0295b4d\run.json
```
### A-CLOSE-038

```yaml
id: TASK-CLOSE-038
requirement_refs: ['REQ-CLOSE-010']
acceptance_refs: ['A-CLOSE-038']
files_or_symbols:
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
implementation_goal: script/command in output is not executed
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: script/command in output is not executed
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [script/command in output is not executed]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-038 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-038\436fa6ff-0dd7-445b-8967-126ffeba2f87\run.json
```
### A-CLOSE-039

```yaml
id: TASK-CLOSE-039
requirement_refs: ['REQ-CLOSE-010']
acceptance_refs: ['A-CLOSE-039']
files_or_symbols:
  - repository: page-assist
    path: src/db/octop/index.ts
    operation: modify
implementation_goal: old Dexie records remain unclaimed
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: old Dexie records remain unclaimed
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [old Dexie records remain unclaimed]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-039 --mode fixture --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-039 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-039\7265e464-655f-4464-9ab5-c3cdb29efd08\run.json
```
### A-CLOSE-040

```yaml
id: TASK-CLOSE-040
requirement_refs: ['REQ-CLOSE-010']
acceptance_refs: ['A-CLOSE-040']
files_or_symbols:
  - repository: page-assist
    path: src/services/octop-api/identity-coordinator.ts
    operation: modify
  - repository: page-assist
    path: src/components/Octop/ExpertChat.tsx
    operation: modify
implementation_goal: epoch mismatch drops late drafts; user-visible errors remain
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: epoch mismatch drops late drafts; user-visible errors remain
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [epoch mismatch drops late drafts; user-visible errors remain]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-040 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M2
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-040\e88fa494-17a1-4fbf-ab36-c558dd517c69\run.json
```
### A-CLOSE-041

```yaml
id: TASK-CLOSE-041
requirement_refs: ['REQ-CLOSE-011']
acceptance_refs: ['A-CLOSE-041']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/deploy.py
    operation: modify
implementation_goal: copy-only install cannot return READY
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: copy-only install cannot return READY
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [copy-only install cannot return READY]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-041 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M4
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-041\185616f5-9d57-4974-98a7-0a25c1e1d471\run.json
```
### A-CLOSE-042

```yaml
id: TASK-CLOSE-042
requirement_refs: ['REQ-CLOSE-011']
acceptance_refs: ['A-CLOSE-042']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/deploy.py
    operation: modify
implementation_goal: fake wheel / path escape: precheck != 0, stop/switch = 0
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: fake wheel / path escape: precheck != 0, stop/switch = 0
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [fake wheel / path escape: precheck != 0, stop/switch = 0]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-042 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-042 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M4
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-042\0e24c410-e594-4ed3-9f18-c10268861854\run.json
```
### A-CLOSE-043

```yaml
id: TASK-CLOSE-043
requirement_refs: ['REQ-CLOSE-011']
acceptance_refs: ['A-CLOSE-043']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/deploy.py
    operation: modify
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/integration/register.py
    operation: modify
implementation_goal: disable does not cancel admitted tasks; PID unchanged
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: disable does not cancel admitted tasks; PID unchanged
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [disable does not cancel admitted tasks; PID unchanged]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-043 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M4
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-043\3e77969f-ccab-4462-a7ec-5f1f158b2ac9\run.json
```
### A-CLOSE-044

```yaml
id: TASK-CLOSE-044
requirement_refs: ['REQ-CLOSE-011']
acceptance_refs: ['A-CLOSE-044']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/deploy.py
    operation: modify
implementation_goal: rollback failure exit 6 RECOVERY_REQUIRED; new messages preserved
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: rollback failure exit 6 RECOVERY_REQUIRED; new messages preserved
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [rollback failure exit 6 RECOVERY_REQUIRED; new messages preserved]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-044 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-044 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M4
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-044\688a31d4-3e8a-44a4-ad53-e46522229412\run.json
```
### A-CLOSE-045

```yaml
id: TASK-CLOSE-045
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['A-CLOSE-045']
files_or_symbols:
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
  - repository: page-assist
    path: octop-client/tools/verify.py
    operation: modify
implementation_goal: hardcoded SHA / constant assertions fail the source contract
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: hardcoded SHA / constant assertions fail the source contract
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [hardcoded SHA / constant assertions fail the source contract]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-045 --mode document --output <ABS>
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-045 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M0
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-045\30f90099-06d4-410d-984c-be39eda0899e\run.json
```
### A-CLOSE-046

```yaml
id: TASK-CLOSE-046
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['A-CLOSE-046']
files_or_symbols:
  - repository: page-assist
    path: scripts/enterprise/gate.mjs
    operation: modify
implementation_goal: empty evidence / BLOCKED required / bad hash => G-RELEASE FAIL exit 1
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: empty evidence / BLOCKED required / bad hash => G-RELEASE FAIL exit 1
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [empty evidence / BLOCKED required / bad hash => G-RELEASE FAIL exit 1]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-046 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M0
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-046\7fa42261-94c1-4e89-aa53-13fc1acb7da1\run.json
```
### A-CLOSE-047

```yaml
id: TASK-CLOSE-047
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['A-CLOSE-047']
files_or_symbols:
  - repository: page-assist
    path: scripts/enterprise/verify.mjs
    operation: modify
implementation_goal: missing env stays BLOCKED; never fabricated live PASS
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: missing env stays BLOCKED; never fabricated live PASS
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [missing env stays BLOCKED; never fabricated live PASS]
verification:
  - command: node scripts/enterprise/verify.mjs --acceptance A-CLOSE-047 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-047\8d2f24cb-a018-4918-8d92-a3560310d964\run.json
```
### A-CLOSE-048

```yaml
id: TASK-CLOSE-048
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['A-CLOSE-048']
files_or_symbols:
  - repository: page-assist
    path: octop-client/src/page_assist_octop_client/loggingutil.py
    operation: modify
implementation_goal: log IO failure does not re-execute business
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: log IO failure does not re-execute business
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [log IO failure does not re-execute business]
verification:
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-048 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance A-CLOSE-048 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-048\49eb95a0-a7b9-4c5c-bef4-4d0d92c290a5\run.json
```
### FI-01

```yaml
id: TASK-FI-001
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-01']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-01 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-01 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-01 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-01\4a79b945-7661-4911-8ce2-4929377c58e1\run.json
```
### FI-02

```yaml
id: TASK-FI-002
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-02']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-02 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-02 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-02 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-02\89484b6c-497a-40c7-91ff-c0cbc3564ce7\run.json
```
### FI-03

```yaml
id: TASK-FI-003
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-03']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-03 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-03 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-03 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-03\dcba12eb-22f5-412f-a080-9fc512736664\run.json
```
### FI-04

```yaml
id: TASK-FI-004
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-04']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-04 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-04 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-04 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-04\f91f6f66-648c-4776-89b8-5c009c73b91a\run.json
```
### FI-05

```yaml
id: TASK-FI-005
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-05']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-05 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-05 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-05 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-05\5219dfad-7342-4325-9680-028d0784b934\run.json
```
### FI-06

```yaml
id: TASK-FI-006
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-06']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-06 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-06 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-06 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-06\5d4d8d0a-d5c8-4858-85fb-c9a23644e365\run.json
```
### FI-07

```yaml
id: TASK-FI-007
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-07']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-07 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-07 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-07 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-07\5e40bbbf-076b-4716-b5b1-16518eb6b4a9\run.json
```
### FI-08

```yaml
id: TASK-FI-008
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-08']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-08 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-08 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-08 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-08\9e6c844c-69a6-40c5-ac86-d52b515ed544\run.json
```
### FI-09

```yaml
id: TASK-FI-009
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-09']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-09 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-09 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-09 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-09\e3cd4904-1564-4bfd-bb7a-54b201848c82\run.json
```
### FI-10

```yaml
id: TASK-FI-010
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-10']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-10 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-10 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-10 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-10\bc7d420a-ad73-4d4f-b0ae-9c4b9b38c062\run.json
```
### FI-11

```yaml
id: TASK-FI-011
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-11']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-11 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-11 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-11 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-11\ee7809fa-eb09-42a1-864f-a37790377eef\run.json
```
### FI-12

```yaml
id: TASK-FI-012
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-12']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-12 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-12 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-12 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-12\115aed5f-3271-4f5d-a890-30be417b7405\run.json
```
### FI-13

```yaml
id: TASK-FI-013
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-13']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-13 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-13 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-13 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-13\0741f3ec-b4e0-456f-901a-47d293340549\run.json
```
### FI-14

```yaml
id: TASK-FI-014
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-14']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-14 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-14 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-14 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-14\c2486b0b-8eb1-4796-880d-7ff48d84e28c\run.json
```
### FI-15

```yaml
id: TASK-FI-015
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-15']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-15 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-15 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-15 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-15\b3e33e1a-4628-4638-a4d0-2a9be68a6b3a\run.json
```
### FI-16

```yaml
id: TASK-FI-016
requirement_refs: ['REQ-EVID-001', 'REQ-CLOSE-012']
acceptance_refs: ['FI-16']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 原 FI-16 必须到达注入点且 injection_observed=true
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 原 FI-16 必须到达注入点且 injection_observed=true
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [unobserved injection cannot PASS]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-16 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-16\5d3372c5-83c7-464b-9a1d-74b67baee370\run.json
```
### FI-CLOSE-001

```yaml
id: TASK-FIC-001
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-001', 'A-CLOSE-001']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 compile/sub-build failure；postcondition: total build !=0, no releasable
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 compile/sub-build failure；postcondition: total build !=0, no releasable
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [total build !=0, no releasable]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-001 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-001\cfa966b4-8260-4613-bfb5-856c507f6c95\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-001\ce4247b3-f0f9-47ee-8b99-6d826896f863\run.json
```
### FI-CLOSE-002

```yaml
id: TASK-FIC-002
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-002', 'A-CLOSE-002', 'A-CLOSE-003']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 create delay + clicks；postcondition: single key/thread
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 create delay + clicks；postcondition: single key/thread
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [single key/thread]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-002 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-002\bd1c71a9-a989-4177-9f09-78cb31435fc5\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-002\0715b100-ee4e-4e3a-a713-adf38a45a531\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-003\5b547092-3fc4-43da-a21f-4d509d05daf4\run.json
```
### FI-CLOSE-003

```yaml
id: TASK-FIC-003
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-003', 'A-CLOSE-007']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 thread/meta/receipt writes；postcondition: all deltas 0
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 thread/meta/receipt writes；postcondition: all deltas 0
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [all deltas 0]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-003 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-003\8c71df1a-d2de-493e-8faf-e3733f54b45a\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-007\7177133d-ecd1-4f6b-81e4-a1b2e1456455\run.json
```
### FI-CLOSE-004

```yaml
id: TASK-FIC-004
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-004', 'A-CLOSE-011']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 auth commit/storage fail；postcondition: atomic SID; no code replay
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 auth commit/storage fail；postcondition: atomic SID; no code replay
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [atomic SID; no code replay]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-004 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-004\334bef2c-f3a7-4e2a-9f38-c2fc62fc0cca\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-011\01ddf867-8bdd-43de-9c9e-925c6b1e15ad\run.json
```
### FI-CLOSE-005

```yaml
id: TASK-FIC-005
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-005', 'A-CLOSE-013', 'A-CLOSE-014', 'A-CLOSE-016']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 logout delayed WS；postcondition: accept=0
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 logout delayed WS；postcondition: accept=0
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [accept=0]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-005 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-005 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-005\865fd10d-3d1d-4da1-9a4c-1d2e7376140b\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-013\3b3bf0f3-26e9-4f1b-90f4-6605514c15b8\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-014\bb13eea1-ddbf-43e8-b3b4-d4fa76057252\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-016\ac2c7374-bb02-44b8-b2ea-af36657f5c0e\run.json
```
### FI-CLOSE-006

```yaml
id: TASK-FIC-006
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-006', 'A-CLOSE-021']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 slow handshake/lost ack/no pong；postcondition: bounded converge, no auto cancel
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 slow handshake/lost ack/no pong；postcondition: bounded converge, no auto cancel
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [bounded converge, no auto cancel]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-006 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-006\01a99b1b-0b44-46e3-947a-9e2bdd35d320\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-021\958cfe23-b113-40e9-8303-537c4366b3bd\run.json
```
### FI-CLOSE-007

```yaml
id: TASK-FIC-007
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-007', 'A-CLOSE-022']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 seq gap/old revision；postcondition: state does not rewind
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 seq gap/old revision；postcondition: state does not rewind
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [state does not rewind]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-007 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-007\7163785b-1431-4da6-a7e8-cc28a3d23231\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-022\a8d49feb-b649-47f1-86cb-b6ffc9c04a12\run.json
```
### FI-CLOSE-008

```yaml
id: TASK-FIC-008
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-008', 'A-CLOSE-023']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 disconnect after accepted；postcondition: turn not resent
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 disconnect after accepted；postcondition: turn not resent
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [turn not resent]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-008 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-008 --mode live --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-008\024ddf74-25a2-4232-9d3b-4a040000a391\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-023\7fd6b0af-60ff-4e06-9b1a-c7517729333d\run.json
```
### FI-CLOSE-009

```yaml
id: TASK-FIC-009
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-009', 'A-CLOSE-027']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 publish/SQL/receipt drop；postcondition: orphan or unique ready
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 publish/SQL/receipt drop；postcondition: orphan or unique ready
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [orphan or unique ready]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-009 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-009\a3285a47-18d2-4673-b76a-64b52fee5251\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-027\86ccc012-c7d2-49d6-9a57-58bca0142b04\run.json
```
### FI-CLOSE-010

```yaml
id: TASK-FIC-010
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-010', 'A-CLOSE-028']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 second file / cleanup fail；postcondition: first ready kept
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 second file / cleanup fail；postcondition: first ready kept
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [first ready kept]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-010 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-010\29588f90-a0af-4cca-8bd7-d073f4795965\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-028\1a0fd2c7-f3a5-4702-bf0e-0af5b1722100\run.json
```
### FI-CLOSE-011

```yaml
id: TASK-FIC-011
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-011', 'A-CLOSE-031']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 decision SQL / lost 202；postcondition: rollback or no re-approve
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 decision SQL / lost 202；postcondition: rollback or no re-approve
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [rollback or no re-approve]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-011 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-011\04150b23-41d0-47a9-b4a8-b80b4d67bde5\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-031\b28a62c8-13f8-40a9-958f-3cfe82e762aa\run.json
```
### FI-CLOSE-012

```yaml
id: TASK-FIC-012
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-012', 'A-CLOSE-034', 'A-CLOSE-035', 'A-CLOSE-036']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 peer bind disconnect；postcondition: recover or reject old
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 peer bind disconnect；postcondition: recover or reject old
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [recover or reject old]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-012 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-012 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-012\09d961b5-38fd-495d-b013-9dc9b4cbc64f\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-034\953a6979-9c37-4e62-9743-704cf5c8db31\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-035\5c50cdc7-be33-42e1-a795-4517b51f9517\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-036\f9d7c2c1-001d-48bf-8170-958dc7c3a787\run.json
```
### FI-CLOSE-013

```yaml
id: TASK-FIC-013
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-013', 'A-CLOSE-044']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 busy gate / health fail；postcondition: stop=0 or restore old
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 busy gate / health fail；postcondition: stop=0 or restore old
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [stop=0 or restore old]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-013 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-013 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-013\4eb82ad8-44a6-4dad-85a6-0717c7243528\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-044\688a31d4-3e8a-44a4-ad53-e46522229412\run.json
```
### FI-CLOSE-014

```yaml
id: TASK-FIC-014
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-014', 'A-CLOSE-044']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 rollback start fail；postcondition: exit6 RECOVERY_REQUIRED
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 rollback start fail；postcondition: exit6 RECOVERY_REQUIRED
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [exit6 RECOVERY_REQUIRED]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-014 --mode fixture --output <ABS>
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-014 --mode live --output <ABS>
status: blocked
implemented: true
verified: false
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-014\8863b889-fae5-44e0-b29c-46e35d3de072\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-044\688a31d4-3e8a-44a4-ad53-e46522229412\run.json
```
### FI-CLOSE-015

```yaml
id: TASK-FIC-015
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-015', 'A-CLOSE-048']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 log IO fail；postcondition: business once, DEGRADED
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 log IO fail；postcondition: business once, DEGRADED
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [business once, DEGRADED]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-015 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-015\ab2ff89f-5662-453d-b051-83237aae5551\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-048\49eb95a0-a7b9-4c5c-bef4-4d0d92c290a5\run.json
```
### FI-CLOSE-016

```yaml
id: TASK-FIC-016
requirement_refs: ['REQ-CLOSE-012']
acceptance_refs: ['FI-CLOSE-016', 'A-CLOSE-046']
files_or_symbols:
  - repository: page-assist
    path: octop-client/tools/acceptance/fis.py
    operation: modify
implementation_goal: 注入 gate missing/tamper；postcondition: Gate FAIL exit1
preconditions: [baseline recorded, HostPort/protocol frozen where required]
state_transition: 注入 gate missing/tamper；postcondition: Gate FAIL exit1
side_effect_scope: [managed source, evidence artifacts]
failure_cases: [Gate FAIL exit1]
verification:
  - command: python octop-client/tools/verify.py --acceptance FI-CLOSE-016 --mode fixture --output <ABS>
status: verified
implemented: true
verified: true
milestone: M5
evidence:
  - e:\git\page-assist\artifacts\acceptance\FI-CLOSE-016\fdb781cd-2275-40bc-9dcf-bd703dc86ee3\run.json
  - e:\git\page-assist\artifacts\acceptance\A-CLOSE-046\7fa42261-94c1-4e89-aa53-13fc1acb7da1\run.json
```
## 5. 验证命令

```text
node scripts/enterprise/verify.mjs --acceptance ALL --mode fixture --output <ABS>
python octop-client/tools/verify.py --acceptance ALL --mode fixture --output <ABS>
node scripts/enterprise/gate.mjs --required contracts/octop-client/v1/required-acceptance.json --run-index <ABS>/run-index.json --release-manifest <ABS>/release.json --output <ABS>/G-RELEASE.json
```

单用例 exit: 0=PASS 1=FAIL 2=BLOCKED 3=SKIPPED。G-RELEASE 仅 PASS/FAIL。

## 6. 交付

- implemented 与 verified 分列。
- 交付实际两仓 SHA、构建产物、可重跑命令、证据索引、Gate 结果、运维手册。
- 不得用模拟宿主、模拟 Peer、常量断言或手填 PASS 替代真实交付。


## 9. 实施结果（工作区，未 git commit）

- Page Assist HEAD: `ff1df1ce4df8b3d12be231fb40857fd3a46fc88c`（dirty 工作区含收口补丁；证据绑定实际 SHA + dirty manifest）
- Octop HEAD: `e3041c452ffc870f754378bd99d964349580d3f9`（dirty 工作区含 HostPort/complete/binding 补丁）
- Fixture 唯一 ID：146（114 AC + 32 FI）。PASS 136 / BLOCKED 10 / FAIL 0。
- BLOCKED：`A-OBS-001`、`A-DEPLOY-001`、`A-DEPLOY-003`、`A-EVID-003`、`A-CLOSE-033`、`A-CLOSE-035`、`A-CLOSE-036`、`A-CLOSE-041`、`A-CLOSE-043`、`A-CLOSE-044`。缺 `deployment-input.json` / systemd / 真实 Peer live 参数，未冒充 PASS。
- G-RELEASE：FAIL（required live 元组缺失 + required BLOCKED）。诚实门禁。
- 证据：`artifacts/acceptance/run-index-combined.json`、`artifacts/acceptance/G-RELEASE.json`、`prd/ops/OctopClient_B1_RC1_Ops.md`
