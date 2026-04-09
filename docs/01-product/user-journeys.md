# 用户旅程

## 1. 首次使用旅程

```text
Login
  -> Create Avatar / Use Demo Avatar
  -> Import Minimal Sources
  -> Generate Persona
  -> Create Default Agent
  -> Run Suggested Task
  -> Review Candidate Memories
  -> View Growth Report
  -> Finish Onboarding
```

### 关键要求
- 每一步都有明确下一步动作。
- 不要求用户一次导入大量历史资料。
- 失败时提供重试或回退路径。
- 任一步骤都必须能定位到页面、调用接口、成功跳转和失败反馈。

## 2. 首次使用步骤级规格

| 步骤 | 页面 | 表单 / 输入字段 | 触发动作 | 调用接口 | 成功结果 | 失败反馈 | 空态 / 加载态 / 阻断态 |
|---|---|---|---|---|---|---|---|
| 1. 登录 | `LoginView` | `email` `password` | 点击登录 | `POST /api/v1/auth/login` | 建立会话并跳转 Dashboard | 提示凭证错误/限流/账户状态异常 | 初始空表单；提交 loading；若策略阻断显示阻断原因 |
| 2. 创建 Avatar / 使用 Demo | `AvatarCreateView` / `DashboardView` | `name` `goal` `visibility` 或选择 demo | 提交创建 / 选择 demo | `POST /api/v1/avatars` / Demo 初始化接口或本地 demo 数据 | 获得 `avatarId` 并进入 Persona 页面 | 校验失败、未授权、创建失败 | 未有 Avatar 时展示空态 CTA；创建时 loading |
| 3. 导入最小样本 | `PersonaGenerateView` | `samples[]` 或模板选择 | 粘贴文本 / 选择模板 / 点击继续 | 本地暂存或后端样本上传接口（若 MVP 未独立开放，则作为 persona generate 请求体组成部分） | 样本准备完成，进入可生成状态 | 样本为空、长度不足、格式错误 | 空态提示“至少 1 份样本”；解析 loading |
| 4. 生成 Persona | `PersonaGenerateView` | `avatar_id` `samples` | 点击生成 Persona | `POST /api/v1/avatars/{avatarId}/persona/generate` | 生成新 Persona 并展示摘要 | Provider 失败、策略阻断、校验失败 | `source_ready`、`generating`、`blocked`、`failed` 状态可见 |
| 5. 激活 Persona | `PersonaGenerateView` 历史面板 | `personaId` | 点击激活 | `POST /api/v1/personas/{personaId}/activate` | 当前 Persona 切换成功 | 状态冲突、未找到、越权 | 历史为空时展示空态；激活中按钮禁用 |
| 6. 创建默认 Agent | `AgentManagementView` | `avatar_id` `name` `role` | 点击创建默认 Agent | `POST /api/v1/avatars/{avatarId}/agents` | 创建默认 Agent 并回到任务页 | 校验失败、越权、创建失败 | 列表空态提供“一键创建默认 Agent” |
| 7. 运行建议任务 | `TaskExecutionView` | `avatar_id` `agent_id` `input` | 点击执行 | `POST /api/v1/tasks` | 返回 `task_id`，进入轮询查询 | pre-policy 阻断、provider 失败 | `creating`/`pending`/`running`/`blocked`/`failed` 状态可见 |
| 8. 查看任务结果 | `TaskExecutionView` | 无新增字段 | 自动轮询 / 手动刷新 | `GET /api/v1/tasks/{taskId}` | 显示结果、trace_id、候选记忆提示 | 查询失败、任务失败、任务阻断 | 结果为空时显示运行中骨架屏 |
| 9. 处理候选记忆 | `PendingMemoryView` | 可选 `reason` | 点击确认 / 拒绝 | `POST /api/v1/memories/{memoryId}/confirm` 或 `reject` | 记忆状态更新并写审计 | 状态冲突、越权、操作失败 | 无 pending 时显示空态；提交时按钮 loading |
| 10. 查看成长报告 | `DashboardView` / `AvatarDetailView` | `avatarId` | 打开成长报告卡片或详情 | 聚合接口或组合调用 Persona / Memory / Audit / Task 接口 | 看到成长快照、成长洞察、推荐动作与证据入口 | 数据不足、未授权、聚合失败 | `empty` / `building` / `ready` / `demo` 状态清晰可见 |
| 11. 完成引导 | `DashboardView` | 无 | 点击完成 | 可选本地埋点或进度接口 | 显示主控制台入口 | 若数据加载失败仍可手动进入各页 | Onboarding 卡片消失，展示主工作台 |

## 3. Avatar 创建旅程

### 主流程
1. 用户进入 `AvatarCreateView`。
2. 输入 `name`、`goal`、`visibility`。
3. 提交创建请求。
4. 系统创建 Avatar 并返回详情摘要。
5. 页面跳转到 Persona 生成页。

### 页面状态
```text
idle -> editing -> submitting -> created
                             └-> failed
```

### 失败处理
- `VALIDATION_ERROR`：字段级提示。
- `UNAUTHORIZED`：跳转登录页。
- `INTERNAL_ERROR`：展示全局错误并允许重试。

## 4. Persona 生成旅程

### 主流程
1. 用户在 `PersonaGenerateView` 输入样本或选择模板。
2. 页面进入 `source_ready`。
3. 用户点击生成。
4. 后端生成新 Persona 版本。
5. 页面展示摘要、版本号、创建时间。
6. 用户可选择立即激活，或稍后在历史列表中激活。

### 页面状态
```text
idle -> source_ready -> generating -> generated
                              ├-> failed
                              └-> blocked
```

### 失败处理
- `VALIDATION_ERROR`：样本不满足最低要求。
- `POLICY_BLOCKED`：显示阻断原因与 `trace_id`。
- `PROVIDER_UNAVAILABLE`：提示稍后重试。

## 5. Task 执行旅程

### 主流程
1. 用户在 `TaskExecutionView` 选择 Avatar 和 Agent。
2. 输入任务内容。
3. 前端调用 `POST /api/v1/tasks`。
4. 后端执行 `pre_task` policy。
5. 通过后组装 Persona + Memory + Task 上下文。
6. Provider 执行生成。
7. 后端执行 `post_provider_output` policy。
8. 系统持久化结果、候选记忆、审计。
9. 前端轮询 `GET /api/v1/tasks/{taskId}` 直到终态。

### 页面状态
```text
idle -> creating -> pending -> running -> succeeded
                                   ├-> failed
                                   └-> blocked
```

### 失败处理
- `POLICY_BLOCKED`：停留在当前页，展示阻断信息。
- `TASK_EXECUTION_FAILED`：展示错误与重试入口。
- `PROVIDER_UNAVAILABLE`：提示服务暂不可用。

## 6. Memory 确认旅程

### 主流程
1. Task 完成后系统产生候选记忆。
2. `PendingMemoryView` 展示记忆摘要、来源任务、风险标记、trace_id。
3. 用户点击确认或拒绝。
4. 系统更新状态并写审计。
5. 列表刷新至下一条或空态。

### 页面状态
```text
loading -> empty
        └-> has_pending -> confirming -> updated
                       ├-> rejecting -> updated
                       └-> failed
```

### 失败处理
- `MEMORY_STATE_CONFLICT`：提示该记忆已被处理并刷新列表。
- `FORBIDDEN`：提示无权限。
- `INTERNAL_ERROR`：显示重试按钮。

## 7. 审计查看旅程

### 主流程
1. 用户进入 `AuditLogView`。
2. 按 `trace_id`、`resource_type`、时间范围检索。
3. 查看任务、策略命中与关键动作摘要。
4. 从审计项跳转到关联对象详情或任务页。

### 页面状态
```text
idle -> loading -> ready
                ├-> empty
                └-> failed
```

### 失败处理
- 过滤条件非法：表单级提示。
- 未授权：返回登录页。
- 查询失败：保留筛选条件并允许重试。

## 8. 页面级通用规则

- 每个业务页都必须定义空态、loading、error 三种基础视图。
- 所有跨页跳转必须能回溯上一步，不允许把用户带入无返回路径。
- 所有关键写操作必须在成功后展示 `trace_id` 或提供查看审计入口。
- 若用户动作被策略阻断，必须停留在当前上下文并给出可理解原因，不直接吞错。

## 9. 脚手架生成检查点

- 每条旅程必须能直接拆出 `view + api client + store/composable + test case`。
- 每一步必须能回答：页面字段、调用接口、成功跳转、失败反馈、空态/loading/阻断态。
- 若无法按步骤直接生成页面和接口联调骨架，则该旅程未达 scaffold-ready。