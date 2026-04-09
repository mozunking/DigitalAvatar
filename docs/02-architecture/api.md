# API 合同

## 1. 设计原则

1. REST-first
2. 统一前缀 `/api/v1`
3. DTO 边界明确
4. 错误码统一
5. 查询同步，执行按异步语义建模

## 2. 统一错误结构

```json
{
  "error": {
    "code": "POLICY_BLOCKED",
    "message": "当前请求触发策略阻断",
    "trace_id": "trace_001",
    "details": {}
  }
}
```

## 3. 错误码冻结

- `VALIDATION_ERROR`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `NOT_FOUND`
- `POLICY_BLOCKED`
- `PROVIDER_UNAVAILABLE`
- `TASK_EXECUTION_FAILED`
- `MEMORY_STATE_CONFLICT`
- `RATE_LIMITED`
- `INTERNAL_ERROR`

### 错误码触发条件
| 错误码 | 典型触发接口 | 触发条件 |
|---|---|---|
| `VALIDATION_ERROR` | login / avatars / tasks / memories decision | 请求字段缺失、格式非法、分页参数越界 |
| `UNAUTHORIZED` | 所有受保护接口 | 无 access token、token 过期或无效 |
| `FORBIDDEN` | avatar/persona/agent/task/memory/audit 相关接口 | 访问不属于当前用户的资源 |
| `NOT_FOUND` | 详情或更新类接口 | 资源不存在 |
| `POLICY_BLOCKED` | task create / persona generate / memory confirm flow | 触发策略阻断 |
| `PROVIDER_UNAVAILABLE` | persona generate / task run | 模型服务不可用或超时 |
| `TASK_EXECUTION_FAILED` | task detail | 任务执行失败 |
| `MEMORY_STATE_CONFLICT` | memory confirm / reject | 非 `pending_confirm` 状态重复决策 |
| `RATE_LIMITED` | login | 超过登录失败频率或接口限流 |
| `INTERNAL_ERROR` | 全局 | 未分类系统异常 |

## 4. MVP API 集

### Auth
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

### Avatar
- `POST /api/v1/avatars`
- `GET /api/v1/avatars`
- `GET /api/v1/avatars/{avatarId}`
- `PATCH /api/v1/avatars/{avatarId}`

### Persona
- `POST /api/v1/avatars/{avatarId}/persona/generate`
- `GET /api/v1/avatars/{avatarId}/persona/latest`
- `GET /api/v1/avatars/{avatarId}/personas`
- `POST /api/v1/personas/{personaId}/activate`

### Agent
- `POST /api/v1/avatars/{avatarId}/agents`
- `GET /api/v1/agents/{agentId}`
- `GET /api/v1/avatars/{avatarId}/agents`
- `PATCH /api/v1/agents/{agentId}`

### Task
- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{taskId}`
- `GET /api/v1/tasks`

### Memory
- `GET /api/v1/avatars/{avatarId}/memories/pending`
- `GET /api/v1/avatars/{avatarId}/memories/search`
- `GET /api/v1/memories`
- `GET /api/v1/memories/{memoryId}`
- `POST /api/v1/memories/{memoryId}/confirm`
- `POST /api/v1/memories/{memoryId}/reject`
- `POST /api/v1/memories/{memoryId}/archive`

### Audit
- `GET /api/v1/audit`
- `GET /api/v1/audit/{auditId}`

### Privacy
- `GET /api/v1/privacy/export`
- `DELETE /api/v1/privacy/delete`

## 5. 关键 DTO 最低要求

### LoginRequest
- `email`
- `password`

### LoginResponse
- `access_token`
- `refresh_token`
- `user`
- `trace_id`

### CreateAvatarRequest
- `name`
- `goal`
- `visibility`

### CreateTaskRequest
- `avatar_id`
- `agent_id`
- `input`
- `trace_id`（客户端可选，服务端必须兜底生成）

### TaskResponse
- `task_id`
- `status`
- `trace_id`
- `result`（未完成时可为空）
- `error`（失败或阻断时返回）

### MemoryDecisionRequest
- `reason`（可选）

### PolicyCheckResult
- `decision`（`allow` / `block`）
- `rule_id`
- `message`
- `trace_id`

## 6. 分页与列表约定

所有列表接口默认分页，最小返回结构：

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

默认约定：
- `page` 默认 `1`
- `page_size` 默认 `20`
- `page_size` 最大 `100`
- 审计日志、任务历史、Persona 历史必须分页

## 7. 资源级字段规格

### `POST /api/v1/auth/login`
| 位置 | 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| body | `email` | 是 | 无 | 登录邮箱 |
| body | `password` | 是 | 无 | 明文密码，仅请求体使用 |

响应字段：`access_token` `refresh_token` `user.id` `user.email` `trace_id`

### `GET /api/v1/avatars`
查询参数：
| 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `page` | 否 | `1` | 页码 |
| `page_size` | 否 | `20` | 每页数量，最大 `100` |

返回：Avatar 摘要分页列表；摘要字段至少包含 `id` `name` `goal` `visibility` `status` `created_at`。

### `POST /api/v1/avatars`
| 位置 | 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| body | `name` | 是 | 无 | Avatar 名称 |
| body | `goal` | 是 | 无 | Avatar 目标 |
| body | `visibility` | 是 | 无 | `private` / `shared` |

### `POST /api/v1/avatars/{avatarId}/persona/generate`
| 位置 | 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| path | `avatarId` | 是 | 无 | Avatar 标识 |
| body | `samples` | 是 | 无 | 最小样本文本数组或等效结构 |
| body | `template_id` | 否 | 无 | 选择模板时传入 |

返回：新 Persona 摘要；至少包含 `id` `avatar_id` `summary` `source_count` `version` `is_current` `created_at`。

### `POST /api/v1/tasks`
| 位置 | 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| body | `avatar_id` | 是 | 无 | 任务归属 Avatar |
| body | `agent_id` | 是 | 无 | 执行 Agent |
| body | `input` | 是 | 无 | 用户任务输入 |
| body | `trace_id` | 否 | 服务端生成 | 客户端透传链路 ID |

返回：任务壳；至少包含 `task_id` `status` `trace_id`。创建成功后初始状态为 `pending`，客户端需继续轮询 `GET /api/v1/tasks/{taskId}` 观察 `running`、`succeeded`、`failed` 或 `blocked` 终态。

### `GET /api/v1/tasks/{taskId}`
返回：任务详情；至少包含 `task_id` `status` `trace_id` `result` `error`。
- `result`：运行中时允许为 `null`
- `error`：仅 `failed` / `blocked` 时有值

### `GET /api/v1/avatars/{avatarId}/memories/search`
查询参数：
| 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `query` | 否 | 空 | 搜索关键词 |
| `type` | 否 | 空 | 记忆类型过滤 |
| `page` | 否 | `1` | 页码 |
| `page_size` | 否 | `20` | 每页大小 |

返回：记忆摘要分页列表；不得默认返回完整敏感 `content`。

### `GET /api/v1/audit`
查询参数：
| 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `trace_id` | 否 | 空 | 链路过滤 |
| `resource_type` | 否 | 空 | 资源类型过滤 |
| `start_at` | 否 | 空 | 起始时间 |
| `end_at` | 否 | 空 | 结束时间 |
| `page` | 否 | `1` | 页码 |
| `page_size` | 否 | `20` | 每页大小 |

实现当前返回按时间倒序分页的审计日志，并可通过 `trace_id` 串联 `task_created`、`task_started`、`task_completed` / `task_blocked` / `task_failed`。

## 8. 关键接口示例

### `POST /api/v1/auth/login`

请求：

```json
{
  "email": "user@example.com",
  "password": "******"
}
```

成功响应：

```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "id": "user_001",
    "email": "user@example.com"
  },
  "trace_id": "trace_001"
}
```

### `POST /api/v1/avatars`

请求：

```json
{
  "name": "My Avatar",
  "goal": "写作与研究协作",
  "visibility": "private"
}
```

成功响应：

```json
{
  "id": "avatar_001",
  "name": "My Avatar",
  "goal": "写作与研究协作",
  "visibility": "private",
  "status": "active",
  "created_at": "2026-04-08T10:00:00Z"
}
```

### `POST /api/v1/tasks`

请求：

```json
{
  "avatar_id": "avatar_001",
  "agent_id": "agent_001",
  "input": "帮我总结今天的会议纪要",
  "trace_id": "trace_001"
}
```

成功响应：

```json
{
  "task_id": "task_001",
  "status": "pending",
  "trace_id": "trace_001"
}
```

### `GET /api/v1/tasks/{taskId}`

成功响应：

```json
{
  "task_id": "task_001",
  "status": "running",
  "trace_id": "trace_001",
  "result": null,
  "error": null
}
```

### `GET /api/v1/memories`
查询参数：
| 字段 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `avatar_id` | 否 | 空 | Avatar 过滤 |
| `state` | 否 | 空 | 记忆状态过滤 |
| `page` | 否 | `1` | 页码 |
| `page_size` | 否 | `20` | 每页大小 |

返回：记忆分页列表；实现当前返回 `content`、`source_type`、`task_id` 等字段供确认页展示。

### `GET /api/v1/memories/{memoryId}`
返回：Memory 详情。

### `POST /api/v1/memories/{memoryId}/confirm`

请求：

```json
{
  "reason": "符合长期偏好"
}
```

成功响应：

```json
{
  "id": "memory_001",
  "state": "confirmed",
  "trace_id": "trace_001"
}
```

## 9. Task 异步语义

`POST /api/v1/tasks` 只返回任务壳，不同步等待模型完成。

状态查询由 `GET /api/v1/tasks/{taskId}` 或任务列表接口承担。

MVP 默认使用轮询，SSE 作为 P1 增强项。

## 10. 端点语义约束

- `POST /api/v1/avatars/{avatarId}/persona/generate` 必须生成新版本 Persona，不覆盖历史版本。
- `POST /api/v1/personas/{personaId}/activate` 只能激活单个 Persona，并取消同 avatar 其他版本的当前激活态。
- `PATCH /api/v1/agents/{agentId}` 仅允许更新角色、状态、权限相关字段，不允许跨 avatar 迁移。
- `POST /api/v1/memories/{memoryId}/confirm` 与 `reject` 只允许对 `pending_confirm` 状态执行。
- `GET /api/v1/audit/logs` 必须支持 `trace_id`、`resource_type`、时间范围过滤。
- 详情接口允许返回更多字段；列表接口默认只返回摘要字段。
- `password_hash`、完整 memory `content`、敏感审计原文不得作为前端稳定依赖字段。

## 11. 合同约束

- 所有错误响应必须返回统一错误结构。
- 所有关键写操作必须生成或透传 `trace_id`。
- 列表接口默认分页，避免一次返回完整审计或任务历史。
- OpenAPI 文档必须作为前端类型生成的唯一来源。
- 未在合同中声明的字段，不视为前后端稳定依赖。
- 若接口文档未写明请求字段、响应字段、错误码、鉴权要求、审计要求，则该接口未达 scaffold-ready。