# 数据模型

## 1. 核心表

- `users`
- `avatars`
- `personas`
- `agents`
- `tasks`
- `memories`
- `policies`
- `audit_logs`
- `modules`

## 2. 通用字段

主要业务表统一包含：
- `id`
- `created_at`
- `updated_at`

字段约定：
- `id`：字符串主键
- `created_at` / `updated_at`：UTC 时间戳
- 枚举字段使用字符串字面量，不使用数字枚举
- 默认不做软删除；如需保留删除历史，走审计摘要而非业务表 tombstone

## 3. 核心对象最低字段

### users
| 字段 | 类型 | 必填 | 约束 | 敏感级别 | 加密/保护 | 是否允许回传前端 |
|---|---|---|---|---|---|---|
| `id` | string | 是 | 主键 | low | 无 | 是 |
| `email` | string | 是 | 唯一 | medium | 建议加密存储或脱敏显示 | 是 |
| `password_hash` | string | 是 | 不可回传前端 | high | bcrypt 哈希 | 否 |
| `status` | string | 是 | 账户状态枚举 | low | 无 | 是 |
| `created_at` | datetime | 是 | UTC | low | 无 | 是 |

### avatars
| 字段 | 类型 | 必填 | 约束 | 敏感级别 | 加密/保护 | 是否允许回传前端 |
|---|---|---|---|---|---|---|
| `id` | string | 是 | 主键 | low | 无 | 是 |
| `user_id` | string | 是 | 外键 -> `users.id` | low | 无 | 否 |
| `name` | string | 是 | 同用户下可读性名称 | low | 无 | 是 |
| `goal` | string | 是 | Avatar 目标描述 | medium | 可选 | 是 |
| `visibility` | string | 是 | `private` / `shared` | low | 无 | 是 |
| `status` | string | 是 | Avatar 状态枚举 | low | 无 | 是 |
| `created_at` | datetime | 是 | UTC | low | 无 | 是 |
| `updated_at` | datetime | 是 | UTC | low | 无 | 是 |

### personas
| 字段 | 类型 | 必填 | 约束 | 敏感级别 | 加密/保护 | 是否允许回传前端 |
|---|---|---|---|---|---|---|
| `id` | string | 是 | 主键 | low | 无 | 是 |
| `avatar_id` | string | 是 | 外键 -> `avatars.id` | low | 无 | 否 |
| `summary` | text | 是 | Persona 摘要 | medium | 可选 | 是 |
| `source_count` | int | 是 | 参与生成的样本数量 | low | 无 | 是 |
| `version` | int | 是 | 同 avatar 内递增 | low | 无 | 是 |
| `is_current` | bool | 是 | 同 avatar 仅一个 `true` | low | 无 | 是 |
| `created_at` | datetime | 是 | UTC | low | 无 | 是 |

### agents
| 字段 | 类型 | 必填 | 约束 | 敏感级别 | 加密/保护 | 是否允许回传前端 |
|---|---|---|---|---|---|---|
| `id` | string | 是 | 主键 | low | 无 | 是 |
| `avatar_id` | string | 是 | 外键 -> `avatars.id` | low | 无 | 否 |
| `name` | string | 是 | Agent 名称 | low | 无 | 是 |
| `role` | string | 是 | 角色定义 | low | 无 | 是 |
| `system_prompt` | text | 是 | 初始系统提示 | medium | 可选 | 仅摘要或配置态可见 |
| `status` | string | 是 | Agent 状态枚举 | low | 无 | 是 |
| `created_at` | datetime | 是 | UTC | low | 无 | 是 |
| `updated_at` | datetime | 是 | UTC | low | 无 | 是 |

### tasks
| 字段 | 类型 | 必填 | 约束 | 敏感级别 | 加密/保护 | 是否允许回传前端 |
|---|---|---|---|---|---|---|
| `id` | string | 是 | 主键 | low | 无 | 是 |
| `avatar_id` | string | 是 | 外键 -> `avatars.id` | low | 无 | 否 |
| `agent_id` | string | 是 | 外键 -> `agents.id` | low | 无 | 否 |
| `input` | text | 是 | 原始任务输入 | medium | 可选加密 | 是，限拥有者 |
| `result` | text / json | 否 | 成功时写入 | medium/high | 可选加密+脱敏 | 是，限拥有者 |
| `status` | string | 是 | Task 状态枚举 | low | 无 | 是 |
| `trace_id` | string | 是 | 全链路追踪 | low | 无 | 是 |
| `error_code` | string | 否 | 失败或阻断时写入 | low | 无 | 是 |
| `created_at` | datetime | 是 | UTC | low | 无 | 是 |
| `updated_at` | datetime | 是 | UTC | low | 无 | 是 |

### memories
| 字段 | 类型 | 必填 | 约束 | 敏感级别 | 加密/保护 | 是否允许回传前端 |
|---|---|---|---|---|---|---|
| `id` | string | 是 | 主键 | low | 无 | 是 |
| `avatar_id` | string | 是 | 外键 -> `avatars.id` | low | 无 | 否 |
| `type` | string | 是 | 记忆类型枚举 | low | 无 | 是 |
| `content` | text | 是 | 原始记忆内容 | high | AES-256 应用层加密 | 否，默认仅返回摘要/脱敏内容 |
| `state` | string | 是 | Memory 状态枚举 | low | 无 | 是 |
| `source_task_id` | string | 否 | 外键 -> `tasks.id` | low | 无 | 是 |
| `created_at` | datetime | 是 | UTC | low | 无 | 是 |
| `updated_at` | datetime | 是 | UTC | low | 无 | 是 |

### audit_logs
| 字段 | 类型 | 必填 | 约束 | 敏感级别 | 加密/保护 | 是否允许回传前端 |
|---|---|---|---|---|---|---|
| `id` | string | 是 | 主键 | low | 无 | 是 |
| `trace_id` | string | 是 | 可跨资源串联 | low | 无 | 是 |
| `actor` | string | 是 | 操作主体 | low | 无 | 是 |
| `action` | string | 是 | 操作动作 | low | 无 | 是 |
| `resource_type` | string | 是 | 资源类型 | low | 无 | 是 |
| `resource_id` | string | 是 | 资源标识 | low | 无 | 是 |
| `result` | string | 是 | 成功 / 失败 / 阻断 | low | 无 | 是 |
| `request_summary` | text | 否 | 请求/动作摘要，不记录完整敏感正文 | medium | 脱敏或摘要化 | 是 |
| `policy_hits` | json | 否 | 命中规则列表 | low | 无 | 是 |
| `hash_prev` | string | 否 | 前一条摘要 | low | 无 | 否 |
| `hash_self` | string | 是 | 当前摘要 | low | 无 | 否 |
| `created_at` | datetime | 是 | UTC | low | 无 | 是 |

## 4. 占位表说明

### policies
- 用途：策略规则定义、版本与启停控制。
- MVP 结论：作为脚手架必建表，至少保留规则 ID、阶段、风险等级、启用状态、描述字段。

### modules
- 用途：预留 Beta 扩展注册信息。
- MVP 结论：不是首批业务链路必建表，可作为占位迁移预留；若实现未落地，不得影响主链路。

## 5. 关系约束

- 一个 `user` 可以拥有多个 `avatars`
- 一个 `avatar` 可以拥有多个 `personas`
- 一个 `avatar` 可以拥有多个 `agents`
- 一个 `agent` 可以拥有多个 `tasks`
- 一个 `task` 可以产生零到多条 `memories`
- `audit_logs` 通过 `trace_id` 关联多个业务对象

## 6. 唯一约束与删除策略

### 唯一约束
- `users.email` 全局唯一
- `personas(avatar_id, version)` 唯一
- `personas(avatar_id) where is_current=true` 唯一
- `tasks.trace_id` 不要求全局唯一，但单条任务链路内必须稳定

### 删除策略
| 对象 | 删除方式 | 说明 |
|---|---|---|
| `users` | 业务删除 + 匿名审计保留 | 删除账号时删除业务主数据，保留匿名审计摘要 |
| `avatars` | 级联删除下游业务数据 | 需同步删除 personas / agents / tasks / memories |
| `personas` | 默认不开放单独删除 | MVP 只允许切换当前版本 |
| `agents` | 默认逻辑停用优先 | 不建议直接硬删 |
| `tasks` | 不开放单独删除 | 由账号删除或数据清理策略处理 |
| `memories` | 可按隐私要求删除 | 删除后不允许恢复 |
| `audit_logs` | 不做业务级删除 | 如需清理仅保留匿名化摘要 |

## 7. 状态枚举冻结

### Avatar
- `active`
- `inactive`

### Agent
- `ready`
- `running`
- `disabled`

### Task
- `pending`
- `running`
- `succeeded`
- `failed`
- `blocked`

### Memory
- `captured`
- `pending_confirm`
- `confirmed`
- `rejected`
- `archived`

## 8. Task 状态机

```text
pending -> running -> succeeded
                 ├-> failed
                 └-> blocked
```

- `pending`：任务已创建，等待执行。
- `running`：任务已开始执行。
- `succeeded`：任务成功完成并产出结果。
- `failed`：任务执行失败，记录 `error_code`。
- `blocked`：任务被策略阻断或权限拒绝。

允许迁移：
- `pending -> running`
- `running -> succeeded`
- `running -> failed`
- `running -> blocked`

禁止迁移：
- 终态回退到非终态
- `pending -> succeeded` 直接跳过执行中态

## 9. Memory 状态机

```text
captured -> pending_confirm -> confirmed -> archived
                     └-------> rejected
```

- `captured`：系统刚捕捉到候选记忆。
- `pending_confirm`：等待用户确认是否入长期记忆。
- `confirmed`：用户确认保留。
- `rejected`：用户拒绝写入长期记忆。
- `archived`：历史记忆归档，不再作为默认活跃记忆。

允许迁移：
- `captured -> pending_confirm`
- `pending_confirm -> confirmed`
- `pending_confirm -> rejected`
- `confirmed -> archived`

禁止迁移：
- `rejected -> pending_confirm`
- `archived -> confirmed`

## 10. 索引冻结

1. `avatars(user_id)`
2. `personas(avatar_id, is_current)`
3. `agents(avatar_id, status)`
4. `tasks(agent_id, status)`
5. `tasks(avatar_id, created_at)`
6. `tasks(trace_id)`
7. `memories(avatar_id, state)`
8. `memories(avatar_id, type)`
9. `audit_logs(trace_id)`
10. `audit_logs(resource_type, resource_id)`

## 11. 迁移注意点

- SQLite 为 MVP 默认实现，字段类型与索引设计必须兼容未来 PostgreSQL 迁移。
- 枚举先以字符串字面量落库，避免数据库原生 enum 迁移成本。
- `memories.content` 加密方案必须在迁移脚本中明确密钥来源与轮换策略。
- `modules` 若仅作预留，不应阻塞首批迁移上线。

## 12. 约束说明

- `trace_id` 在任务、策略、审计链路中必须可串联。
- `personas.is_current` 同一 avatar 在任一时刻只能有一个为 `true`。
- `memories.state` 不允许从 `rejected` 回退到 `pending_confirm`。
- `tasks.status` 一旦进入 `succeeded` / `failed` / `blocked`，视为终态。
- `users.email` 必须全局唯一。
- `tasks.trace_id` 在单次任务链路中必须稳定，不允许执行中变更。
- 涉及敏感内容的字段是否加密，由安全架构文档定义并在实现中落地。
- 若某表无法回答“字段类型、必填、唯一性、外键、敏感性、前端暴露范围、删除策略”，则该模型未达 scaffold-ready。