# 可观测性

## 1. 最低要求

- `/health` 健康检查端点
- `/metrics` 基础指标端点
- JSON 结构化日志
- `trace_id` 全链路透传
- 错误日志与审计日志分离，但通过 `trace_id` 关联

## 2. 日志字段模板

### 应用日志最小字段
| 字段 | 必填 | 说明 |
|---|---|---|
| `timestamp` | 是 | UTC 时间戳 |
| `level` | 是 | `debug` / `info` / `warn` / `error` |
| `service` | 是 | `api` / `worker` / `web` |
| `trace_id` | 是 | 全链路追踪 ID |
| `actor` | 否 | 当前用户或系统主体 |
| `event` | 是 | 事件名，如 `task_created` |
| `resource_type` | 否 | 资源类型 |
| `resource_id` | 否 | 资源 ID |
| `message` | 是 | 简短说明 |
| `error_code` | 否 | 错误码 |
| `latency_ms` | 否 | 耗时 |

### 示例
```json
{
  "timestamp": "2026-04-08T10:00:00Z",
  "level": "info",
  "service": "api",
  "trace_id": "trace_001",
  "actor": "user_001",
  "event": "task_created",
  "resource_type": "task",
  "resource_id": "task_001",
  "message": "task accepted"
}
```

## 3. trace 透传入口

- HTTP 入站：从请求头读取 `X-Trace-Id`，不存在则服务端生成。
- API -> Service -> Worker：必须保留原始 `trace_id`，不得中途重写。
- Worker -> Provider：通过 provider metadata 透传 `trace_id`。
- API -> Web：所有关键响应与错误响应必须返回 `trace_id`。
- 审计日志：以相同 `trace_id` 记录关键业务动作与策略命中。

## 4. 必须审计的动作

1. user login / logout
2. avatar created / updated
3. persona generated / switched
4. agent created / updated / enabled / disabled
5. task created / started / completed / failed / blocked
6. policy warned / blocked
7. memory confirmed / rejected / archived / deleted
8. privacy export / delete requested / completed

## 5. 审计最小字段

- `actor`
- `action`
- `resource_type`
- `resource_id`
- `result`
- `trace_id`
- `created_at`
- `request_summary`
- `policy_hits`
- `hash_prev`
- `hash_self`

## 6. 指标建议

### API 指标
- `http_requests_total{route,method,status}`
- `http_request_duration_ms{route,method}`
- `auth_login_failures_total`
- `policy_block_total{rule_id}`

### 任务与记忆指标
- `task_created_total`
- `task_terminal_total{status}`
- `task_running_duration_ms`
- `memory_pending_total`
- `memory_decision_total{decision}`

### Provider 指标
- `provider_requests_total{provider,model,status}`
- `provider_latency_ms{provider,model}`
- `provider_timeout_total{provider,model}`

## 7. 性能与运行指标

- 首屏核心页面加载尽可能 < 2.5s
- Task 状态查询 P95 < 500ms（不含模型执行）
- Memory pending 查询 P95 < 300ms
- Audit 列表必须分页
- 登录接口 P95 < 300ms

## 8. 健康检查响应结构

### `/health`
```json
{
  "status": "ok",
  "service": "Digital Avatar API",
  "time": "2026-04-08T10:00:00+00:00",
  "checks": {
    "db": "ok",
    "provider": "mock"
  },
  "provider": {
    "mode": "mock",
    "status": "mock",
    "model": "qwen3.5:7b-instruct-q4_0",
    "version": "mock",
    "chat_model_available": true
  }
}
```

### `/metrics`
- 采用 Prometheus 文本格式或兼容格式输出。
- 至少暴露 API 请求、任务状态、策略阻断、Provider 调用四类指标。
- 当前 MVP 兼容输出中至少包含 provider mode/status/model/version，以及 `provider_chat_model_available` 诊断字段。

## 9. Provider 调用约束

- 超时控制
- 指数退避重试
- 并发限制
- 幂等 `trace_id` 透传
- 为重复请求预留缓存机制
- Provider 日志只记录模型、耗时、状态，不记录完整 prompt 正文

## 10. 审计 / 日志联动规则

- 应用日志用于运行诊断，审计日志用于安全追责；两者不得混写。
- 任何 `POLICY_BLOCKED`、`UNAUTHORIZED`、`FORBIDDEN` 都必须既有错误日志也有审计摘要。
- 排查主链路问题时，必须能用单个 `trace_id` 串起 API 日志、任务记录、策略命中、审计摘要。

## 11. 脚手架生成要求

- 本文档必须能直接生成：logging middleware、trace context helper、metrics endpoint、health check handler、audit/log correlation tests。
- 若无法回答“日志长什么样、trace_id 从哪里来、健康检查返回什么、指标怎么命名”，则可观测性规格未达 scaffold-ready。