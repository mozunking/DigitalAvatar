# 发布计划

## 1. 发布目标

1. 发布计划必须服务于 MVP 主链路落地，而不是引入额外范围。
2. 发布输入物必须与已冻结的产品、架构、测试、部署文档一致。
3. 发布结果必须可回滚、可验证、可复现。
4. 发布通过后，相关文档进入 frozen baseline；原则上不得修改，除非明显错漏、重大矛盾修复，或有证据支持的显著先进性、可落地性、科学性提升。

## 2. 发布阶段

| 阶段 | 目标 | 输入物 | 输出物 | 负责人 | 通过标准 |
|---|---|---|---|---|---|
| MVP 内部可用 | 主链路可由内部团队跑通 | 冻结合同、最小实现、测试结果 | 内部演示版本、问题清单 | Tech Lead / QA / Security | 主链路可执行，P0 测试通过，安全高风险阻断已接入 |
| MVP 对外演示 | 可向外部干系人稳定演示 | Compose 环境、seed 数据、验收记录 | 演示包、演示脚本、版本标记 | PM / Tech Lead / DevOps | Docker 演示环境可重复启动，验收清单通过 |
| Beta 准备 | 为 Beta 扩展做评估和排期 | 复盘记录、遗留问题、指标数据 | Beta backlog、扩展 ADR、风险清单 | Product / Architecture | 遗留问题已分级，扩展项不影响 MVP 基线 |

## 3. 发布输入物清单

### 3.1 文档输入物
- `docs/01-product/requirements.md`
- `docs/01-product/functional-spec.md`
- `docs/01-product/user-journeys.md`
- `docs/02-architecture/api.md`
- `docs/02-architecture/data-model.md`
- `docs/02-architecture/security-architecture.md`
- `docs/02-architecture/frontend-architecture.md`
- `docs/02-architecture/observability.md`
- `docs/03-delivery/testing-plan.md`
- `docs/03-delivery/deployment-plan.md`
- `docs/05-review/acceptance-checklist.md`
- `docs/05-review/quality-gates.md`

### 3.2 产物输入物
- `apps/api/` 最小 API 与 worker 骨架
- `apps/web/` 最小前端页面与路由骨架
- `tests/` 主链路测试骨架与执行结果
- `deploy/docker/ops/compose/` Compose 配置
- `deploy/docker/ops/scripts/` 启停、备份、恢复脚本
- `deploy/docker/ops/health/smoke.http` 或等效 smoke 测试文件
- 演示 seed 数据

## 4. 版本冻结点

| 冻结点 | 必须冻结的内容 | 证据来源 |
|---|---|---|
| F0 文档冻结 | P0 模块、接口、状态机、错误码、Auth 方案、Policy 返回结构 | `interface-freeze-checklist.md` |
| F1 脚手架冻结 | 目录结构、OpenAPI 生成目录、测试目录、Compose 服务清单 | `development-plan.md` `frontend-architecture.md` `deployment-plan.md` |
| F2 发布候选冻结 | 演示环境、测试结果、验收记录、回滚方案 | `acceptance-checklist.md` `quality-gates.md` |

- 未通过 F0，不得进入多代理实现。
- 未通过 F1，不得宣告 scaffold-ready。
- 未通过 F2，不得标记 release candidate。

## 5. 发布门禁

### 5.1 文档门禁
- 关键文档达到 scaffold-ready。
- 冻结项均可定位到字段表、状态图、响应示例或配置表。
- 发布输入物与冻结合同一致。

### 5.2 实现门禁
- 主链路实现存在最小可运行骨架。
- API、状态机、错误码与文档一致。
- 高风险阻断链路已接入。
- `/health` 与最小 smoke 可执行。

### 5.3 测试门禁
- unit / integration / 最小 e2e / security / smoke 已执行。
- 至少 3 类高风险场景阻断测试通过。
- 演示环境可重复启动并完成主链路。

### 5.4 运维门禁
- Compose 服务可启动。
- 日志目录、数据目录、备份恢复脚本齐备。
- 发布版本具备基础监控和健康检查。

## 6. 发布前检查单

1. 核对当前版本对应的 frozen baseline 文档未发生未授权变更。
2. 执行测试计划中的 P0 主链路测试与安全测试。
3. 启动 Compose 演示环境并执行 smoke。
4. 校验 seed 数据存在且仅用于本地/演示环境。
5. 核对 API 返回结构、错误码、trace_id 与合同一致。
6. 核对高风险阻断、审计写入、日志字段完整。
7. 核对备份与恢复脚本可执行。
8. 生成发布说明与已知问题清单。

## 7. 演示发布输入物

| 输入物 | 内容 | 说明 |
|---|---|---|
| 演示环境 | Compose 配置、env、脚本 | 可在单机本地启动；若受外部 Docker 环境阻塞，至少需具备 `docker compose config` 渲染结果、脚本校验与阻塞证据 |
| 演示数据 | demo user / avatar / persona / agent / task samples | 仅本地与演示环境可用 |
| 演示脚本 | 登录、创建 Avatar、生成 Persona、执行 Task、确认 Memory、查看 Audit | 用于稳定复现主链路 |
| 发布说明 | 版本范围、已知限制、回滚方式 | 面向评审者和演示执行者 |

## 8. 回滚条件与回滚规则

### 8.1 必须回滚的情况
- 主链路无法跑通。
- 核心 API 返回结构与合同不一致。
- 高风险输出未被阻断。
- 审计链路断裂或 trace_id 无法串联。
- Compose 环境无法稳定启动。

### 8.2 回滚方式
- 停止 `web`、`api`、`worker`。
- 使用最近一次有效备份恢复 SQLite 数据。
- 恢复上一个可验证版本的 Compose 配置与 env。
- 重新执行 `/health` 与最小 smoke。
- 在发布记录中注明回滚原因与影响范围。

## 9. 发布后动作

1. 记录发布结果与遗留问题。
2. 将问题分为：阻断、P1、P2。
3. 若需修改 frozen baseline，必须先记录变更理由和证据。
4. 输出复盘，更新 `document-review-log.md` 与必要的决策记录。

## 10. 发布约束

- 发布计划只覆盖 MVP 与演示发布，不在本阶段引入 Beta 扩展实现。
- 扩展项如 SSE、多模型、Chroma，只能进入 Beta 评估清单。
- 若无法回答“发布依赖什么输入物、如何检查、失败何时回滚、回滚后如何验证”，则发布计划未达 scaffold-ready。
