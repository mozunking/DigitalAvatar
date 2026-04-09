# 需求总表

## 1. 范围定义

### P0：MVP 必须完成
1. 用户登录、刷新、登出、会话识别
2. Avatar 创建、列表、详情、更新
3. 最小样本导入与 Persona 生成
4. Persona 历史与当前激活版本
5. 单 Agent 创建、查询、启停
6. Task 创建、状态查询、结果查看
7. 候选记忆捕捉、确认、拒绝、搜索、详情
8. 基础策略检查与高风险阻断
9. 审计日志记录与查询
10. Demo 数据与新手引导
11. Docker Compose 部署

### P1：MVP 质量增强
1. Task 状态 SSE
2. Avatar 成长报告
3. 更完善的空态 / 错误态 / 加载态
4. 更细的安全与性能指标看板

#### Avatar 成长报告冻结口径
- 只允许使用 `confirmed` memory 进入“系统已学会/已掌握”的结论。
- 需要明确区分 Persona、候选记忆、已确认长期记忆、审计证据。
- 报告的目标是解释分身如何持续成长，并给出狭义、可执行的下一步建议。
- Demo Avatar 如展示成长报告，必须标记为示例数据，不得冒充真实用户成长结果。

### P2：Beta 方向
1. 多模型 Provider
2. 更强的记忆检索与重排
3. 最小模块化扩展能力
4. SDK / API 生态

## 2. 角色视角需求

### 用户视角
- 我需要快速完成首次配置，尽快感知系统价值。
- 我需要知道系统记住了什么、为什么记住、如何删除。
- 我需要在关键风险场景下被阻断，而不是事后追责。
- 我需要看到分身最近学到了什么，以及这些结论是否真的来自我已确认的长期信息。

### 产品视角
- 必须跑通单条价值闭环，避免范围膨胀。
- 必须可量化评估冷启动、完成率、安全阻断效果。
- 必须把“越用越懂你”的长期价值做成用户可感知、可解释、可审计的产品表面，而不是只停留在底层能力。

### 开发视角
- 领域模型、状态枚举、API、错误码必须先冻结。
- 文档应按边界拆分，便于多人并行实现。
- 每个 P0 模块都必须能映射到页面、接口、状态机和最低脚手架文件。

### 测试视角
- 每个 P0 能力都必须有验收口径与测试入口。
- 安全与状态机测试不得遗漏。

## 3. P0 模块交付映射

| P0 模块 | 用户结果 | 对应页面 | 对应接口 | 对应状态机 | 最低脚手架文件 |
|---|---|---|---|---|---|
| Auth | 用户可登录并访问受保护资源 | `LoginView`、`SettingsView` | `/auth/login` `/auth/refresh` `/auth/logout` `/auth/me` | 登录会话状态机 | `apps/api/app/api/v1/auth.py` `apps/api/app/services/auth_service.py` `apps/api/app/schemas/auth.py` `apps/web/src/views/auth/LoginView.vue` `apps/web/src/stores/auth.ts` `tests/integration/test_auth_api.py` |
| Avatar | 用户可创建和管理 Avatar | `AvatarListView` `AvatarCreateView` `AvatarDetailView` | `/avatars` `/avatars/{avatarId}` | Avatar 创建/更新状态机 | `apps/api/app/api/v1/avatars.py` `apps/api/app/services/avatar_service.py` `apps/api/app/models/avatar.py` `apps/web/src/views/avatar/*.vue` `tests/integration/test_avatar_api.py` |
| Persona | 用户可生成并切换 Persona | `PersonaGenerateView` `PersonaHistoryPanel` | `/avatars/{avatarId}/persona/generate` `/avatars/{avatarId}/persona/latest` `/avatars/{avatarId}/personas` `/personas/{personaId}/activate` | Persona 生成与激活状态机 | `apps/api/app/api/v1/personas.py` `apps/api/app/services/persona_service.py` `apps/web/src/views/persona/*.vue` `tests/integration/test_persona_api.py` |
| Agent | 用户可创建默认 Agent 并启停 | `AgentManagementView` | `/avatars/{avatarId}/agents` `/agents/{agentId}` | Agent 启停状态机 | `apps/api/app/api/v1/agents.py` `apps/api/app/services/agent_service.py` `apps/web/src/views/agent/*.vue` `tests/integration/test_agent_api.py` |
| Task | 用户可发起任务并查看结果 | `TaskExecutionView` `TaskHistoryPanel` | `/tasks` `/tasks/{taskId}` `/avatars/{avatarId}/tasks` | Task 状态机 | `apps/api/app/api/v1/tasks.py` `apps/api/app/services/task_service.py` `apps/api/app/workers/task_worker.py` `apps/web/src/views/task/*.vue` `tests/integration/test_task_api.py` |
| Memory | 用户可确认/拒绝候选记忆并搜索 | `PendingMemoryView` `MemorySearchView` `MemoryDetailDrawer` | `/avatars/{avatarId}/memories/pending` `/avatars/{avatarId}/memories/search` `/memories/{memoryId}` `/memories/{memoryId}/confirm` `/memories/{memoryId}/reject` | Memory 状态机 | `apps/api/app/api/v1/memories.py` `apps/api/app/services/memory_service.py` `apps/web/src/views/memory/*.vue` `tests/integration/test_memory_api.py` |
| Policy | 高风险场景被阻断 | 无独立业务页，作为任务/记忆链路反馈组件出现 | 内嵌于任务、记忆、Provider 调用链路 | Policy 决策状态机 | `apps/api/app/services/policy_service.py` `apps/api/app/domain/policies/*.py` `tests/security/test_policy_blocks.py` |
| Audit | 用户可按 trace_id 检索关键动作 | `AuditLogView` | `/audit/logs` `/audit/logs/{logId}` | 审计查询状态机 | `apps/api/app/api/v1/audit.py` `apps/api/app/services/audit_service.py` `apps/web/src/views/audit/*.vue` `tests/integration/test_audit_api.py` |
| Demo / Onboarding | 新用户可在 15 分钟内跑通闭环 | `DashboardView` `OnboardingGuide` | 组合调用 Auth、Avatar、Persona、Task、Memory | 首次使用旅程状态机 | `apps/web/src/views/dashboard/DashboardView.vue` `apps/web/src/components/onboarding/*` `tests/e2e/test_onboarding_flow.spec.ts` |
| Deployment | 团队可一键启动演示环境 | 无业务页 | 无业务 API，依赖系统服务健康检查 | 部署健康状态机 | `docker-compose.yml` `.env.example` `ops/compose/*` `ops/scripts/dev-up.sh` `tests/smoke/test_compose_stack.py` |

## 4. 模块边界与最低结果

### Auth
- 边界：会话创建、刷新、撤销、当前用户识别。
- 最低结果：未登录访问受保护接口返回 `UNAUTHORIZED`；刷新后可继续访问。

### Avatar
- 边界：Avatar 元数据管理，不负责 Persona 生成与任务执行。
- 最低结果：可创建、列表、详情、更新，返回字段与 API 合同一致。

### Persona
- 边界：样本输入结果汇总、Persona 版本生成与当前版本激活。
- 最低结果：生成新版本，不覆盖历史版本；同一 Avatar 仅一个当前激活版本。

### Agent
- 边界：Agent 元数据、角色、状态、权限范围。
- 最低结果：可创建默认 Agent，且可启停。

### Task
- 边界：任务受理、编排、状态流转、结果回写。
- 最低结果：创建请求返回任务壳；状态可从 `pending -> running -> succeeded/failed/blocked` 流转。

### Memory
- 边界：候选记忆捕捉、确认、拒绝、搜索、归档。
- 最低结果：候选记忆不自动进入长期记忆；只允许在 `pending_confirm` 执行确认/拒绝。

### Policy
- 边界：任务前、Provider 调用前后、记忆写入前的安全决策。
- 最低结果：至少覆盖冒充、恶意输出、敏感信息泄露三类高风险阻断。

### Audit
- 边界：关键动作、策略命中、结果状态的追加记录与查询。
- 最低结果：可通过 `trace_id` 串联任务、策略命中、结果与人工确认动作。

## 5. 验收口径

| 需求 | 最低验收标准 |
|---|---|
| 登录认证 | 能成功登录、刷新、登出，未授权访问被阻断 |
| Avatar 管理 | 能创建、查询、更新，列表展示正确 |
| Persona 生成 | 样本导入后可生成并激活新 Persona |
| Agent 管理 | 能创建默认 Agent 并控制启停 |
| Task 执行 | 创建任务返回任务壳，后续可查状态与结果 |
| Memory 确认 | 候选记忆可确认/拒绝，状态流转正确 |
| Policy 阻断 | 高风险输入/输出被阻断并留下审计 |
| Audit 追踪 | 任务链路可通过 trace_id 串联 |
| 部署 | Docker Compose 能启动演示环境 |

## 6. 非目标与范围约束

- 不把 MVP 扩展成通用聊天产品。
- 不在首版引入真实插件运行时。
- 不把企业级多租户、复杂 IAM、桌面端正式交付塞入 MVP。
- 不接受没有明确用户价值与验收标准的能力进入 P0。
- P0 不引入需要额外基础设施编排的重量级分布式组件。

## 7. 变更规则

- 若新增 P0 需求，必须同步评估对安全、测试、部署、验收和并行拆解的影响。
- 不接受未经文档同步更新的重大契约变更。
- 若某 P0 模块无法映射到页面、接口、状态机、最低脚手架文件，视为需求尚未冻结。
- 需求进入 frozen baseline 后，原则上不得修改；仅允许用于修复明显错漏、重大矛盾，或基于证据的显著先进性、可落地性、科学性提升。