# 多代理并行开发拆解

## 1. 并行开发前提

并行开发只能在关键契约冻结后开始，禁止边开发边改核心接口。

进入并行开发前，必须冻结：
- 领域对象定义
- 状态枚举与状态机
- API 路径、DTO、错误码
- Auth 方案与权限边界
- Policy 返回结构与审计字段
- 前端类型生成方式与目录骨架
- Compose 服务清单与健康检查

## 2. 角色拆分

### 主控代理
- 输入：总方案、冻结项、评审意见、开发计划
- 输出：目录骨架、波次裁决、冲突处理结论、集成顺序
- 验收：关键边界无冲突，交付顺序稳定

### 产品 / 文档代理
- 输入：产品设计、用户旅程、评审意见
- 输出：需求、旅程、功能规格、验收文档
- 验收：需求可映射到页面、接口、状态机与脚手架文件

### 后端内核代理
- 输入：领域模型、API 合同、数据模型、开发计划
- 输出：Task orchestration、Service layer、Provider 接口、Worker 骨架
- 验收：主链路服务边界清晰，可支撑最小执行链路

### Auth / Security 代理
- 输入：安全架构、隐私要求、错误码、接口鉴权要求
- 输出：认证授权、权限拦截、Policy 规则、敏感字段处理骨架
- 验收：未授权、越权、高风险场景被阻断

### Persona / Memory 代理
- 输入：用户旅程、领域模型、Memory 状态机、相关 API
- 输出：Persona 生成、Memory capture、确认/拒绝链路骨架
- 验收：候选记忆与确认链路正确

### Policy / Audit 代理
- 输入：安全架构、审计规范、trace_id 约束、Policy 规则
- 输出：规则引擎、审计追加、trace helper、过滤查询骨架
- 验收：关键链路可审计、trace 可串联

### API 代理
- 输入：接口清单、错误码、DTO 边界、鉴权要求
- 输出：REST routes、OpenAPI、契约校验、响应结构骨架
- 验收：接口与文档一致，OpenAPI 可生成前端类型

### 前端代理
- 输入：前端架构、页面规格、OpenAPI 类型、用户旅程
- 输出：页面、路由、store、API client、通用状态组件骨架
- 验收：主页面可联调并覆盖空态/loading/error/blocked

### 测试代理
- 输入：测试计划、验收清单、安全检查表、冻结合同
- 输出：unit / integration / e2e / security / smoke 用例骨架
- 验收：关键风险具备自动化覆盖

### 部署与运维代理
- 输入：部署方案、观测要求、发布门禁
- 输出：Compose、脚本、健康检查、日志与备份恢复骨架
- 验收：演示环境可启动，基本观测可用

## 3. 每个代理首批输出物

| 角色 | 首批必须创建的文件 / 目录 |
|---|---|
| 主控代理 | `apps/` `tests/` `ops/` 目录骨架定义，集成顺序文档 |
| 产品 / 文档代理 | `docs/01-product/requirements.md` `functional-spec.md` `user-journeys.md` |
| 后端内核代理 | `apps/api/app/models/` `apps/api/app/schemas/` `apps/api/app/services/` `apps/api/app/workers/` |
| Auth / Security 代理 | `apps/api/app/api/v1/auth.py` `apps/api/app/core/security.py` `apps/api/app/core/permissions.py` `apps/api/app/services/policy_service.py` |
| Persona / Memory 代理 | `apps/api/app/api/v1/personas.py` `apps/api/app/api/v1/memories.py` `apps/api/app/services/persona_service.py` `apps/api/app/services/memory_service.py` |
| Policy / Audit 代理 | `apps/api/app/services/policy_service.py` `apps/api/app/services/audit_service.py` `apps/api/app/core/trace.py` |
| API 代理 | `apps/api/app/api/v1/` 路由文件、`openapi.json` 或等效导出规则 |
| 前端代理 | `apps/web/src/router/` `views/` `stores/` `api/` `types/generated/` |
| 测试代理 | `tests/unit/` `tests/integration/` `tests/e2e/` `tests/security/` `tests/smoke/` `tests/fixtures/` |
| 部署与运维代理 | `ops/compose/` `ops/scripts/` `ops/health/` |

## 4. 依赖关系

- Auth / Security、API、前端代理依赖已冻结的 Auth 方案与错误码。
- Persona / Memory 代理依赖领域模型、Memory 状态机与相关 API 已冻结。
- Policy / Audit 代理依赖安全架构、审计字段结构与 trace_id 规范。
- 前端代理依赖 API 代理输出稳定的 OpenAPI 合同。
- 测试代理依赖主链路接口、状态机、验收清单稳定。
- 部署与运维代理依赖应用拓扑、健康检查与日志要求稳定。
- 任一上游冻结项变化，受影响代理必须重新确认输入后才能继续。

## 5. 波次分配建议

### Wave 0：冻结与骨架校准
- 主控代理
- 产品 / 文档代理
- API 代理
- 后端内核代理
- 安全代理
- 前端代理

### Wave 1：业务骨架生成
- 后端内核代理
- Auth / Security 代理
- Persona / Memory 代理
- Policy / Audit 代理
- API 代理
- 前端代理

### Wave 2：测试与部署接入
- 测试代理
- 部署与运维代理
- 主控代理

### Wave 3：交叉评审与定版
- 主控代理
- 产品 / 文档代理
- QA / Security / Review 角色

## 6. 交付物清单

| 角色 | 最低交付物 | 交付标准 |
|---|---|---|
| 主控代理 | 集成裁决记录、冲突处理结论、阶段完成定义 | 可指导多代理合并 |
| 产品 / 文档代理 | 需求文档、用户旅程、功能规格、验收口径 | 能映射脚手架输入 |
| 后端内核代理 | 服务边界说明、主链路骨架、Provider 接口 | 主链路可串联 |
| Auth / Security 代理 | 认证授权实现、安全策略、隐私接口说明 | 鉴权与阻断清晰 |
| Persona / Memory 代理 | Persona 生成链路、Memory 状态机实现与接口 | 确认链路正确 |
| Policy / Audit 代理 | 规则实现、审计写入链路、trace 关联验证 | 审计可追踪 |
| API 代理 | OpenAPI、DTO、错误码与实现一致性 | 前端可生成类型 |
| 前端代理 | 页面状态机、页面实现、联调记录 | 主页面闭环可操作 |
| 测试代理 | 测试用例、覆盖矩阵、关键缺陷记录 | 风险场景有覆盖 |
| 部署与运维代理 | Compose 配置、运行说明、健康检查、备份恢复说明 | 演示环境可启动 |

## 7. 协作规则

1. 按领域切分，不按页面碎片切分。
2. 每个代理只负责一个清晰边界，不越界改他人冻结合同。
3. 所有交付必须附带输入、输出、依赖、验收标准。
4. 主控代理负责裁决冲突，不允许私自扩展冻结范围。
5. 接口、模型、错误码、状态机变更必须先回写文档，再改实现。
6. 未明确归属的工作不得直接开始。

## 8. 并行开发完成定义

- 每个代理都能明确回答：自己依赖什么、要创建哪些文件、产出什么、如何验收。
- 任一 P0 模块都能映射到至少一个负责代理和一组最低交付物。
- 若某代理无法回答“首批创建哪些文件、依赖哪些冻结项、完成后由谁验收”，则并行拆解未达 scaffold-ready。
