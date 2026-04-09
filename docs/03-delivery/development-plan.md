# 开发计划

## 1. 实施目标与定版目标

### 实施目标
1. 在已提交的 MVP 实现基础上，把主链路、测试、部署与验收证据做实，而不是只停留在脚手架阶段。
2. 多代理或多模块并行时，仍以冻结合同和真实实现状态为边界推进，不重复设计已落地部分。
3. 主链路实现顺序、输入输出、交付物、回归点可直接执行并可通过自动化验证。

### 定版目标
1. 关键文档完成交叉一致性检查。
2. 通过 scaffold-ready 门禁与 frozen baseline 门禁。
3. 定版后原则上不再修改，除非明显错漏、重大矛盾修复，或有证据支持的显著先进性、可落地性、科学性提升。

## 2. 执行波次（Wave）

| Wave | 目标 | 输入 | 输出文档 / 产物 | 负责角色 | 依赖 | 完成定义 | 质量门禁 | 不允许变更的冻结项 |
|---|---|---|---|---|---|---|---|---|
| Wave 0 | 校准已实现 MVP 与冻结合同 | 现有代码、产品/架构/评审文档 | 差异清单、任务异步语义、Provider 模式、验收口径统一 | 主控、产品、API、后端、安全、前端 | 无 | 每个 P0 模块都有“已实现 / 待修正 / 待验证”判断 | 主链路和关键合同差异可定位 | 领域对象、状态枚举、错误码、Auth 方案、Policy 返回结构 |
| Wave 1 | 收口主链路实现 | Wave 0 差异清单 | 后端、前端、测试、Docker 的真实修复与对齐 | 主控、后端、API、前端、测试 | Wave 0 | 登录到审计查询主链路真实可跑通 | 主链路回归通过 | API 路径与 DTO、前端类型生成方式、模块边界 |
| Wave 2 | 加固测试、CI 与部署门禁 | Wave 1 已收口实现 | 单测、集成、e2e、smoke、CI workflow、Compose 验证 | 安全、测试、部署、运维 | Wave 1 | 自动化验证可作为发布门禁 | 测试与部署覆盖全部 P0 | 审计字段结构、日志字段模板、Compose 服务清单 |
| Wave 3 | 统一文档与交付证据 | 全部关键代码与 workflow | README / CLAUDE / API / 验收 / 遗留问题等文档回写 | 主控、评审、治理 | Wave 2 | 文档与当前实现、命令、门禁保持一致 | 关键文档无过期表述 | frozen baseline 文档范围与变更条件 |
| Wave 4 | 冻结亮点功能设计包 | Wave 3 定版文档与现有 MVP 能力 | Avatar Growth Report 的产品合同、信息结构、实施拆解与验收口径 | 主控、产品、架构、前端、后端、评审 | Wave 3 | Growth Report 文档可直接指导后续实现 | 术语统一、数据来源可信、边界不超 scope | Persona/Memory 区分、confirmed memory 口径、审计可追溯性 |

## 3. 首批脚手架生成顺序

1. 先生成目录和配置骨架
   - `apps/api/`
   - `apps/web/`
   - `tests/`
   - `ops/`
   - `docker-compose.yml`
   - `.env.example`
2. 再生成后端骨架
   - `api/v1/*.py`
   - `services/*.py`
   - `schemas/*.py`
   - `models/*.py`
   - `workers/*.py`
3. 再生成前端骨架
   - `router/index.ts`
   - `views/**`
   - `stores/**`
   - `api/**`
   - `components/**`
   - `types/generated/**`
4. 最后生成测试与部署骨架
   - `tests/unit/**`
   - `tests/integration/**`
   - `tests/e2e/**`
   - `tests/security/**`
   - `ops/compose/**`
   - `ops/scripts/dev-up.sh`

## 4. 波次级执行细化

### Wave 0：文档冻结与校准
- 输入：现有分层文档、历史评审输入。
- 动作：补齐产品规格、接口字段、模型字段、安全规则、前端映射、观测字段。
- 输出：可生成脚手架的稳定合同。
- 回归点：任一冻结项变化，必须回看 requirements / api / data-model / security / acceptance 是否一致。

### Wave 1：业务骨架生成准备
- 输入：已冻结合同。
- 动作：把模块映射成具体文件/目录骨架与代理首批交付物。
- 输出：后端、前端、测试、部署的骨架目标路径。
- 回归点：若页面或接口无法对应文件路径，回退到功能规格或前端架构补齐。

### Wave 2：安全 / 测试 / 部署可执行化
- 输入：骨架目标路径与冻结合同。
- 动作：明确测试用例文件、夹具、Compose 服务、端口、env、健康检查、发布检查单。
- 输出：测试与部署脚手架可直接生成。
- 回归点：若测试无法覆盖全部 P0，或部署无法回答服务拓扑，则回退补文档。

### Wave 3：定版与治理固化
- 输入：全部 scaffold-ready 文档。
- 动作：执行交叉评审、记录结论、标记 frozen baseline、收紧贡献规则。
- 输出：默认不可随意修改的文档基线。
- 回归点：若仍存在“实现时再定”条目，则不得进入定版。

### Wave 4：Avatar Growth Report 设计冻结
- 输入：现有 MVP 主链路、已冻结的产品/架构/验收文档。
- 动作：冻结 Growth Report 的产品定位、信息结构、状态语义、数据来源约束、推荐动作边界、Demo 标识与验收口径。
- 输出：可直接指导后续前端、后端、测试实施拆分的设计包。
- 回归点：若出现未确认记忆被纳入成长结论、Persona/Memory 边界混淆、或文档暗示超出 MVP 的开放能力，则回退修订。

## 5. 角色进入条件

| 角色 | 开始前必须满足 |
|---|---|
| 后端内核 | 领域模型、Task 状态、错误码、Provider 边界已冻结 |
| Auth / Security | Auth 方案、权限边界、隐私要求、阻断响应已冻结 |
| Persona / Memory | Persona 生成规则、Memory 状态机、相关 API 已冻结 |
| Policy / Audit | Policy 返回结构、trace_id 规则、审计字段已冻结 |
| API | DTO、错误码、统一错误结构、资源级字段表已冻结 |
| 前端 | OpenAPI 合同稳定、路由表稳定、页面映射稳定 |
| 测试 | 验收清单、关键状态机、典型风险场景、测试矩阵已明确 |
| 部署与运维 | Compose 目标、环境变量、健康检查与日志要求已明确 |

## 6. 代理首批输出物

| 角色 | 首批输出物 |
|---|---|
| 主控代理 | 根目录结构、集成顺序、冲突裁决规则 |
| 产品 / 文档代理 | `requirements.md` `functional-spec.md` `user-journeys.md` |
| 后端内核代理 | `models/` `schemas/` `services/` `workers/` 骨架 |
| Auth / Security 代理 | `auth middleware` `permission guard` `policy service` 骨架 |
| Persona / Memory 代理 | persona / memory 相关 service 与 API 骨架 |
| Policy / Audit 代理 | policy rules、audit append、trace helper 骨架 |
| API 代理 | `api/v1/*.py` 与 OpenAPI 初稿 |
| 前端代理 | router、views、stores、api client、generated types 目录骨架 |
| 测试代理 | unit / integration / e2e / security 测试目录与样例文件 |
| 部署与运维代理 | `docker-compose.yml` `.env.example` `ops/compose/` `scripts/dev-up.sh` |

## 7. 完成定义（Definition of Done）

### Wave 0 完成定义
- 每个 P0 模块都能回答：页面、接口、状态机、最低脚手架文件。
- 每个接口都能回答：请求字段、响应字段、错误码、鉴权、审计要求。
- 每个模型都能回答：字段类型、唯一性、外键、敏感性、暴露范围、删除策略。

### Wave 1 完成定义
- 后端、前端、测试、部署目录路径全部明确。
- 多代理首批创建文件清单稳定。
- OpenAPI 生成产物目录与触发规则稳定。

### Wave 2 完成定义
- 全部 P0 模块有测试矩阵和用例骨架建议。
- Compose 服务列表、端口、挂载、env、健康检查、备份恢复命令明确。
- 发布前检查单与回滚条件明确。

### Wave 3 完成定义
- 关键文档已被标记为 frozen baseline。
- 文档评审记录完整。
- 贡献规则与决策日志已固化“原则上不改”的策略。

## 8. 阶段退出标准

### Wave 0 退出标准
- `docs/03-delivery/interface-freeze-checklist.md` 全部打勾。
- 决策日志与 ADR 可追溯到所有冻结项。
- 多代理职责、依赖、最低交付物已明确。

### Wave 1 退出标准
- 页面、接口、模型、目录之间一一映射。
- 前端与后端骨架路径无冲突。
- 测试与部署可找到对应接入点。

### Wave 2 退出标准
- 测试计划覆盖全部 P0。
- Docker Compose 规格可直接生成最小演示环境。
- 健康检查、日志、审计、指标要求齐备。

### Wave 3 退出标准
- scaffold-ready 文档门禁通过。
- frozen baseline 门禁通过。
- 文档中不再存在“实现时再定”。

## 9. 回归检查点

- `requirements.md` 变更：回归 `functional-spec.md`、`user-journeys.md`、`acceptance-checklist.md`。
- `api.md` 变更：回归 `frontend-architecture.md`、`testing-plan.md`、`interface-freeze-checklist.md`。
- `data-model.md` 变更：回归 `security-architecture.md`、`testing-plan.md`、`observability.md`。
- `security-architecture.md` 变更：回归 `api.md`、`acceptance-checklist.md`、`quality-gates.md`。
- `deployment-plan.md` 变更：回归 `release-plan.md`、`quality-gates.md`。

## 10. 执行原则

- 主链路优先于扩展链路。
- 文档冻结优先于并行开发。
- 测试与安全从第一波次介入。
- 每个波次都要输出可检查结果。
- 不允许跳过冻结项直接并行开工。
- 若文档不能直接回答脚手架生成问题，继续补文档而不是带着歧义开工。