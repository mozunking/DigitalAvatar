# 安全架构

## 1. 认证方案

### MVP 冻结
- Access Token：JWT，默认有效期 `15m`
- Refresh Token：长效续期，默认有效期 `7d`
- 密码存储：bcrypt 哈希
- 登录失败次数限制：同账号在滚动 `15m` 窗口内连续失败 `5` 次后临时锁定 `15m`
- 敏感操作需要身份校验与二次确认

### Token 生命周期
| Token | 用途 | 默认有效期 | 存放位置 | 失效条件 | 刷新规则 |
|---|---|---|---|---|---|
| Access Token | 访问受保护 API | 15 分钟 | 前端内存优先；不得落长期明文存储 | 过期、登出、服务端吊销 | 过期前后均可用 refresh token 换新 |
| Refresh Token | 获取新 access token | 7 天 | HttpOnly Cookie 或等效安全容器 | 过期、登出、密码变更、风控吊销 | 每次刷新返回新 token 对，旧 token 立即失效 |

### 认证拦截点
- `POST /api/v1/auth/login`：匿名可访问。
- `POST /api/v1/auth/refresh`：仅接受有效 refresh token。
- 其余 `/api/v1/**`：默认要求有效 access token。
- 导出、删除、敏感配置修改：除 access token 外，要求二次确认。

## 2. 权限原则

1. 默认拒绝
2. 显式授权
3. 最小权限
4. 高风险操作必须门禁
5. 资源归属优先于角色推断

### MVP 权限矩阵
| 资源 / 动作 | 匿名 | 已登录用户 | 资源拥有者 | 备注 |
|---|---|---|---|---|
| 登录 / 刷新 | 允许 | 允许 | 允许 | 登录后仍可刷新 |
| 查看当前用户 | 拒绝 | 允许 | 允许 | `GET /auth/me` |
| 创建 Avatar | 拒绝 | 允许 | 允许 | 归属当前用户 |
| 查看 / 更新自己的 Avatar | 拒绝 | 允许 | 允许 | 只允许访问自己的 Avatar |
| 生成 / 激活 Persona | 拒绝 | 拒绝 | 允许 | 以 Avatar 归属校验 |
| 创建 / 更新 Agent | 拒绝 | 拒绝 | 允许 | 不允许跨 Avatar 迁移 |
| 创建 / 查询 Task | 拒绝 | 拒绝 | 允许 | 只允许使用自己的 Agent |
| 确认 / 拒绝 / 搜索 Memory | 拒绝 | 拒绝 | 允许 | 仅允许访问自己 Avatar 的 Memory |
| 查看 Audit | 拒绝 | 拒绝 | 允许 | MVP 不引入系统管理员视角 |
| 导出 / 删除用户数据 | 拒绝 | 允许 | 允许 | 需二次确认 |

## 3. Policy 执行时机

- `pre_task`
- `pre_provider_call`
- `post_provider_output`
- `pre_memory_write`

### 执行链路要求
1. `pre_task`：在任务创建后、正式执行前检查输入风险与权限上下文。
2. `pre_provider_call`：在发送给模型前检查提示词拼装结果与敏感信息外发风险。
3. `post_provider_output`：在模型输出返回用户前检查冒充、恶意、敏感泄露、高风险建议。
4. `pre_memory_write`：在候选记忆进入长期存储前检查是否包含高敏感内容或违反保留策略。

## 4. Policy 返回结构

```json
{
  "decision": "allow",
  "hits": ["P-001"],
  "risk_level": "low",
  "message": "ok",
  "trace_id": "trace_001"
}
```

### 返回字段冻结
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `decision` | string | 是 | `allow` / `block` |
| `hits` | string[] | 是 | 命中规则 ID 列表，允许空数组 |
| `risk_level` | string | 是 | `low` / `medium` / `high` / `critical` |
| `message` | string | 是 | 面向调用方的简短原因 |
| `trace_id` | string | 是 | 与任务、审计链路一致 |

## 5. LLM 输出安全

### MVP 最小规则枚举
| 规则 ID | 触发阶段 | 风险等级 | 阻断条件 | 最低动作 |
|---|---|---|---|---|
| `P-001` | `post_provider_output` | high | 高风险冒充真实人物或真实身份承诺 | 阻断输出并写审计 |
| `P-002` | `post_provider_output` | high | 明显恶意内容、违法危险指导 | 阻断输出并写审计 |
| `P-003` | `pre_provider_call` / `post_provider_output` | high | 敏感信息外泄或越界总结隐私数据 | 阻断并打敏感标签 |
| `P-004` | `pre_task` | medium | 输入明显越权或访问他人资源 | 阻断任务创建 |
| `P-005` | `pre_memory_write` | medium | 候选记忆含高敏感且不满足入库策略 | 阻断长期写入，仅保留候选摘要 |
| `P-006` | `post_provider_output` | medium | 高风险承诺、误导性专业建议 | 阻断或降级为警告，MVP 默认阻断 |

## 6. 数据安全

### 敏感字段加密矩阵
| 对象 | 字段 | 敏感级别 | 是否必须加密 | 是否允许返回前端 | 备注 |
|---|---|---|---|---|---|
| `users` | `password_hash` | high | 不适用（哈希） | 否 | 仅服务端校验 |
| `users` | `email` | medium | 建议 | 是，必要时脱敏展示 | 登录与用户标识需要 |
| `tasks` | `input` | medium | 可选，取决于部署模式 | 是，限任务拥有者 | 进入审计时只记录摘要 |
| `tasks` | `result` | medium/high | 可选 | 是，限任务拥有者 | 若包含敏感片段需掩码处理 |
| `memories` | `content` | high | 是 | 否，详情接口按策略返回摘要/脱敏内容 | 长期记忆主敏感字段 |
| `audit_logs` | `request_summary` | medium | 否 | 是，摘要级 | 禁止记录完整敏感正文 |
| `policies` 命中记录 | `hits` | low | 否 | 是 | 用于解释阻断 |

### 数据处理要求
- 敏感字段支持 AES-256 应用层加密。
- 数据库文件加密作为部署选项，MVP 不强制，但部署文档必须给出开启方式。
- 高敏感记忆默认不自动入长期库。
- 审计默认记录摘要，不记录完整敏感内容。
- 删除接口应删除业务主数据，同时保留必要的合规级匿名审计摘要。

## 7. 隐私与合规

### MVP 至少提供
- 隐私政策文档
- 用户数据导出接口
- 用户数据删除接口
- 数据保留期限策略
- 敏感数据分类与分级说明

### 数据保留策略
| 数据 | 默认保留策略 | 删除规则 |
|---|---|---|
| 会话 token | 按有效期自动失效 | 登出即吊销 refresh token |
| Task 结果 | 默认保留，供用户追溯 | 用户删除账号时删除 |
| Confirmed Memory | 默认长期保留 | 用户删除账号或单独删除时删除 |
| Rejected Memory | 可短期保留用于冲突判断 | 到期清理 |
| Audit 摘要 | 保留用于追责与诊断 | 删除账号后保留匿名化摘要 |

## 8. 接口鉴权要求

| 接口组 | 是否需要 access token | 是否需要资源归属校验 | 是否需要二次确认 |
|---|---|---|---|
| `/auth/login` | 否 | 否 | 否 |
| `/auth/refresh` | 否（改用 refresh token） | 否 | 否 |
| `/auth/logout` `/auth/me` | 是 | 否 | 否 |
| `/avatars*` | 是 | 是 | 否 |
| `/persona*` `/personas*` | 是 | 是 | 否 |
| `/agents*` | 是 | 是 | 否 |
| `/tasks*` | 是 | 是 | 否 |
| `/memories*` | 是 | 是 | 否 |
| `/audit/logs*` | 是 | 是 | 否 |
| 导出 / 删除接口 | 是 | 是 | 是 |

## 9. 阻断响应与审计要求

### 统一阻断响应
```json
{
  "error": {
    "code": "POLICY_BLOCKED",
    "message": "当前请求触发策略阻断",
    "trace_id": "trace_001",
    "details": {
      "decision": "block",
      "hits": ["P-003"],
      "risk_level": "high"
    }
  }
}
```

### 审计要求
- 所有 `block` 决策必须写入 `audit_logs`。
- 审计记录必须包含：`trace_id`、`actor`、`action`、`resource_type`、`resource_id`、`result=blocked`、`policy_hits`。
- 审计中不得保存完整敏感原文，只保留摘要与规则 ID。

## 10. 模块安全边界

- MVP 不开放任意插件。
- Beta 若开放扩展，必须引入进程隔离、权限声明与资源限制。
- Provider 层只暴露 `chat`、`stream_chat`、`embed`、`health_check`、`model_info` 等受控能力。
- Task 执行链路不得绕过 Policy 与 Audit。

## 11. 脚手架生成约束

- 安全文档必须能直接生成：auth middleware、permission guard、policy service、crypto helper、privacy endpoints、security test skeleton。
- 若无法回答“token 怎么过期、谁能访问哪个接口、哪些字段要加密、被阻断后返回什么”，则安全规格未达 scaffold-ready。