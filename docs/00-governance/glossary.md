# 术语表

| 术语 | 定义 |
|---|---|
| Avatar | 用户数字分身的顶层容器，承载 Persona、Agent、Memory 等关联对象。 |
| Persona | 对用户风格、偏好、边界与角色特征的稳定摘要。 |
| Agent | 面向具体任务的执行角色实例，使用 Avatar 与 Persona 能力但不是独立人格主体。 |
| Task | 一次可追踪的执行单元，具有输入、状态、结果与 trace_id。 |
| Memory | 可检索、可确认、可归档的离散长期信息条目。 |
| Policy | 对输入、执行、输出、记忆写入等阶段进行校验和阻断的规则。 |
| AuditLog | 对关键行为、策略命中、结果状态进行追踪的审计记录。 |
| Module | 扩展能力声明载体；MVP 不开放任意动态运行时。 |
| Provider | 模型与嵌入能力的适配层，提供 chat、stream_chat、embed 等能力。 |
| trace_id | 串联任务链路、日志与审计记录的全链路追踪标识。 |
| Candidate Memory | 由任务执行产生、尚未被用户确认写入长期库的候选记忆。 |
| Cold Start | 新用户从首次进入到完成首个可感知价值闭环的阶段。 |
| Contract Freeze | 并行开发前对领域模型、状态枚举、API、错误码等关键契约进行冻结。 |
| ADR | Architecture Decision Record，记录关键技术决策及其理由。 |
