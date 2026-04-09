# 测试计划

## 1. 测试分层

### 单元测试
- Persona 生成逻辑
- Memory 状态机
- Policy 决策
- Task 状态流转
- Auth Token 校验

### 集成测试
- 登录认证
- Avatar 创建
- Persona 生成
- Agent 创建
- Task 执行
- 候选记忆生成
- 用户确认记忆
- 审计查询

### E2E 测试
- 首次引导闭环
- 单任务执行闭环
- 待确认记忆处理闭环
- 登录到 Dashboard 基本流转

### 安全测试
- 未授权请求阻断
- 越权操作阻断
- 非法状态流转阻断
- 高风险输出阻断
- 敏感记忆不自动入库
- 导出 / 删除接口正确执行

## 2. P0 测试矩阵

| 模块 | unit | integration | e2e | security | 重点断言 | 建议文件 |
|---|---|---|---|---|---|---|
| Auth | token 解析、密码校验、登录失败计数 | login / refresh / logout / me | 登录到 Dashboard | 未登录访问受保护接口被拒绝、限流生效 | token 生命周期、401/刷新逻辑正确 | `tests/unit/test_auth_service.py` `tests/integration/test_auth_api.py` `tests/e2e/test_login_flow.spec.ts` `tests/security/test_auth_guards.py` |
| Avatar | avatar 校验与更新逻辑 | create/list/detail/update | 创建 Avatar 后进入 Persona | 越权访问他人 Avatar 被拒绝 | 返回字段与合同一致 | `tests/unit/test_avatar_service.py` `tests/integration/test_avatar_api.py` |
| Persona | 版本递增、is_current 切换 | generate/latest/list/activate | 导入样本并生成 Persona | 样本非法、阻断规则生效 | 新版本生成，不覆盖历史 | `tests/unit/test_persona_service.py` `tests/integration/test_persona_api.py` |
| Agent | 状态变更逻辑 | create/list/detail/update | 创建默认 Agent | 越权或非法状态更新被拒绝 | 禁止跨 Avatar 迁移 | `tests/unit/test_agent_service.py` `tests/integration/test_agent_api.py` |
| Task | 状态机、trace_id 稳定性 | create/detail/list | 执行任务直到终态 | pre_task / post_output 阻断生效 | `pending -> running -> terminal` | `tests/unit/test_task_state_machine.py` `tests/integration/test_task_api.py` `tests/e2e/test_task_flow.spec.ts` `tests/security/test_task_policy_blocks.py` |
| Memory | 状态迁移、冲突判断 | pending/detail/confirm/reject/search | 处理候选记忆 | 非 `pending_confirm` 决策被拒绝 | 返回 `MEMORY_STATE_CONFLICT` | `tests/unit/test_memory_state_machine.py` `tests/integration/test_memory_api.py` |
| Policy | 规则匹配与风险等级 | 任务/记忆链路集成 | 任务被阻断闭环 | 至少 3 类高风险阻断 | 审计必须记录 hit 和 trace_id | `tests/unit/test_policy_service.py` `tests/security/test_policy_blocks.py` |
| Audit | hash 串联与过滤逻辑 | audit list/detail/filter | 从任务页跳转审计 | 未授权查看被拒绝 | trace_id 可串联关键动作 | `tests/unit/test_audit_service.py` `tests/integration/test_audit_api.py` |
| Deployment | 配置装载逻辑 | 健康检查 / Compose smoke | 一键启动演示环境 | 默认暴露面受限 | `/health` 正常、关键服务可连通 | `tests/smoke/test_compose_stack.py` |

## 3. 夹具 / 种子数据

### 后端夹具
- `user_factory`
- `avatar_factory`
- `persona_factory`
- `agent_factory`
- `task_factory`
- `memory_factory`
- `audit_log_factory`

### 集成测试种子
- demo 用户 1 个
- demo avatar 1 个
- current persona 1 个
- default agent 1 个
- pending memory 2 条
- blocked task 1 条

### 前端 E2E 种子
- 最小样本输入文本
- 默认 Agent 名称
- 推荐任务文案

## 4. 断言重点

- 所有关键写操作返回 `trace_id`。
- 所有错误路径返回统一错误结构。
- 列表接口默认分页。
- Task 与 Memory 状态机不允许未定义分支。
- 高风险阻断后必须可在审计中检索到对应记录。
- Memory 搜索默认不返回完整敏感 `content`。

## 5. 覆盖策略

- 每个 P0 能力至少具备一条集成或 E2E 用例。
- 每个关键状态机至少具备正向 + 异常路径测试。
- 每个高风险安全边界至少具备一条阻断用例。
- 每类页面至少覆盖空态、loading、error 三种基础视图。

## 6. 测试目录骨架

```text
tests/
├── unit/
├── integration/
├── e2e/
├── security/
├── smoke/
└── fixtures/
```

## 7. 执行顺序

1. 先写状态机与服务层单元测试。
2. 再补接口集成测试，校验合同一致性。
3. 再补主链路 E2E，用于验证首次体验闭环。
4. 同步补安全专项与 Compose smoke。

## 8. 通过标准

- 主链路 unit / integration / 最小 e2e 可执行。
- 至少 3 类高风险阻断有安全专项测试。
- Compose smoke 能覆盖健康检查与最小可用路径。
- 若某 P0 模块没有建议测试文件、夹具、重点断言，则测试规格未达 scaffold-ready。