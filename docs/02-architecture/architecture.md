# 总体架构

## 1. 分层结构

```text
┌────────────────────────────────────────────┐
│ Application Layer                          │
│ Web Console / REST API / CLI / Docker      │
├────────────────────────────────────────────┤
│ Domain Layer                               │
│ User / Avatar / Persona / Agent / Task     │
│ Memory / Policy / Audit                    │
├────────────────────────────────────────────┤
│ Service Layer                              │
│ Use Cases / Orchestration / Validation     │
├────────────────────────────────────────────┤
│ Infrastructure Layer                       │
│ DB / Provider / Vector Store / File Store  │
├────────────────────────────────────────────┤
│ Extension Layer (Beta-oriented)            │
│ Events / Modules / Integrations            │
└────────────────────────────────────────────┘
```

## 2. 架构原则

1. Controller 不承载核心业务逻辑。
2. 主链路优先同步服务调用。
3. 异步用于长耗时执行与非关键路径。
4. 扩展能力不污染 MVP 主链路。
5. 模块边界按领域划分，而不是按页面划分。
6. 依赖关系遵循依赖反转，避免循环依赖。

## 3. 核心扩展点

- Provider Adapter
- Memory Extractor
- Policy Evaluator
- Audit Sink
- Task Executor

> MVP 只冻结接口与职责，不开放通用插件运行时。

## 4. 主链路

```text
Create Task
  -> Pre-Policy Check
  -> Assemble Context
  -> Invoke Provider
  -> Post-Policy Check
  -> Persist Result
  -> Capture Candidate Memories
  -> Append Audit Log
  -> Return Task Status
```

## 4.1 Growth Report 数据拼装约束

```text
Current Persona
  + Confirmed Memories
  + Recent Tasks
  + Audit Evidence
  -> Growth Snapshot
  -> Growth Insights
  -> Recommended Next Actions
```

- Growth Report 只消费解释所需的稳定数据，不反向驱动 Persona 自动改写。
- Growth Insight 必须能回溯到 memory、task 或 trace_id。
- Policy 继续作为边界层，防止不应沉淀的信息被包装成成长结论。

## 5. 分身成长报告（Avatar Growth Report）

- 该能力属于现有领域对象之上的解释层能力，不是新的基础设施层或开放运行时。
- 复用数据来源：当前 Persona、已确认 Memory、近期 Task 结果、Audit 证据、Policy 边界。
- 只允许使用 `confirmed` memory 进入“系统已学会/已掌握”的结论；`pending_confirm` 与 `rejected` 不能进入成长结论。
- Growth Report 用于展示“最近学到了什么、依据是什么、接下来建议做什么”，不允许静默改写 Persona 或绕过人工确认把候选记忆提升为长期事实。
- 若 Demo Avatar 展示成长报告，必须明确标记为示例/seeded data。

## 6. 模块边界

- Auth：登录、Token、密码哈希、身份校验
- Avatar：分身创建与管理
- Persona：样本输入、生成、版本切换
- Agent：角色、权限、启停
- Task：执行编排、状态流转、结果持久化
- Memory：候选记忆、确认、搜索、归档
- Policy：规则评估与阻断决策
- Audit：审计追加、trace 关联、回溯查询
- Provider：模型与嵌入能力适配
