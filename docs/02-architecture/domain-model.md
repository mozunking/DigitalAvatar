# 领域模型

## 1. 核心对象

### User
- 系统使用者
- 拥有登录凭据与工作空间

### Avatar
- 数字分身顶层容器
- 关联 Persona、Agent、Memory、Task

### Persona
- 风格、偏好、边界、角色理解的稳定摘要
- 支持多版本，任一时刻仅一个版本生效

### Agent
- 面向具体任务的执行角色实例
- 共享 Avatar 级长期记忆池

### Task
- 一次执行单元
- 具有输入、状态、结果、trace_id

### Memory
- 离散长期信息条目
- 支持确认、拒绝、归档、搜索

### Policy
- 边界校验与风险决策规则

### AuditLog
- 对关键行为和状态变化的审计追踪

### Module
- 扩展能力声明载体
- MVP 仅保留声明，不启用真实动态加载

## 2. 关键关系

- User 1:N Avatar
- Avatar 1:N Persona
- Avatar 1:N Agent
- Avatar 1:N Memory
- Avatar 1:N Task
- Agent 1:N Task
- Task 1:N Candidate Memory
- Task / Memory / Policy 命中都可产生 AuditLog

## 3. 边界冻结

- Persona 是稳定画像；Memory 是离散可检索条目。
- MVP 不做 Agent 私有长期记忆。
- 模块仅作为未来扩展占位，不进入主链路。
