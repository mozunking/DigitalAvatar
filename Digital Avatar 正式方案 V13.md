# Digital Avatar 正式方案（V13）

> 文档状态：正式方案 / 多视角评审优化版  
> 适用阶段：MVP 立项、仓库初始化、并行开发冻结、Beta 演进基线  
> 文档目标：为产品、架构、开发、测试、安全与开源协作提供统一执行规范

---

## 1. 项目定义

### 1.1 项目名称
**Digital Avatar**

### 1.2 项目定位
Digital Avatar 是一个面向个人专业用户的开源数字分身系统。

它不是单纯的聊天机器人，也不是仅做工具编排的 Agent Shell，而是一个围绕**风格复刻、可控执行、长期记忆、边界约束、审计追踪**构建的个人智能系统。

### 1.3 核心目标
让用户拥有一个：

- 更像自己而不是像通用 AI 的数字分身
- 能在明确授权边界内执行任务的助手
- 会持续沉淀长期价值信息的知识代理
- 可审计、可纠正、可删除、可迁移的本地优先系统

---

## 2. 用户与价值主张（UVP）

### 2.1 目标用户

#### 一级目标用户
1. 开发者
2. 产品经理
3. 内容创作者
4. 独立研究者
5. 重度 AI 用户

#### 二级目标用户
1. 小型创业团队
2. AI-native 工作室
3. 顾问型团队
4. 教学与研究小组

#### 当前非优先用户
1. 大型企业组织级协作
2. 高合规生产级行业场景
3. 多组织复杂权限治理场景
4. 通用社交聊天应用用户

### 2.2 核心用户问题
目标用户当前面临的问题包括：

1. 每次都要重新教 AI 自己的风格和偏好
2. 对话上下文无法长期稳定继承
3. AI 能说很多，但执行边界不清楚
4. 缺乏长期记忆沉淀和纠正机制
5. 缺乏可审计、可解释、可回溯的执行链路

### 2.3 核心价值主张
> Digital Avatar 帮助用户把自己的风格、知识、偏好和工作方式沉淀为一个可控、可审计、可持续成长的数字分身，用于持续辅助真实任务执行，而不是每次从零开始重新训练一个临时 AI。

### 2.4 价值拆解

#### 1）表达复刻
系统输出应尽可能体现用户的表达风格、结构偏好与边界约束。

#### 2）任务辅助
系统应支持完成有明确输入、目标和结果的任务，而不是停留在泛对话层。

#### 3）长期记忆
系统能将用户真正有价值的信息提炼为长期资产，而不是机械记录全部历史对话。

#### 4）边界可控
系统必须在高风险行为、越权调用、敏感操作等场景下提供明确门禁。

#### 5）本地优先
系统优先支持本地部署、本地模型与本地数据存储，保障数据主权。

---

## 3. 产品设计原则

1. **先验证闭环，再扩展生态**
2. **先定义身份与边界，再叠加能力**
3. **先可控，再强大**
4. **先本地优先，再云端扩展**
5. **先单链路跑通，再做多代理协同**
6. **先模块清晰，再做插件化**
7. **默认可审计，默认最小权限**
8. **用户可纠正、可撤回、可删除**
9. **避免黑箱式自治**
10. **复杂度必须为真实价值服务**

---

## 4. 版本策略与范围收敛

### 4.1 MVP 核心命题
MVP 只验证一个闭环：

> 用户能够导入自己的资料，生成初始数字分身，并让其在受控条件下执行一个任务，同时自动捕捉候选记忆，经用户确认后写入长期记忆库。

### 4.2 MVP 必须完成
1. Avatar 创建
2. 用户资料 / 对话样本导入
3. Persona 生成
4. 单 Agent 创建
5. 单任务执行
6. 候选记忆自动捕捉
7. 记忆确认 / 拒绝
8. 基础 Policy 检查
9. 审计日志记录
10. Web 控制台
11. Docker 一键部署

### 4.3 MVP 明确不做
1. 真正插件运行时
2. 通用事件总线平台
3. 多组织复杂权限体系
4. 多设备同步
5. 插件市场
6. 高级多代理自治编排
7. 桌面端正式交付
8. 高风险自动执行能力

### 4.4 Beta 扩展方向
1. 多模型 Provider 抽象
2. 多 Agent 模板
3. 记忆检索增强
4. 模块/扩展最小机制
5. 导出/备份能力
6. 更完整的策略规则
7. 开放 API / SDK
8. 可选桌面端实验版

---

## 5. 核心对象模型

### 5.1 User
系统使用者。

### 5.2 Avatar
用户数字分身的顶层容器。

### 5.3 Persona
数字分身当前生效的稳定画像摘要，包括风格、偏好、约束与角色理解。

### 5.4 Agent
面向具体任务的执行角色实例，不是独立人格主体。

### 5.5 Task
具有输入、上下文、执行状态、结果和追踪信息的任务单元。

### 5.6 Memory
可检索、可确认、可归档的离散长期信息条目。

### 5.7 Policy
用于边界约束、风险校验和阻断决策的规则定义。

### 5.8 AuditLog
用于追踪关键动作、状态变化、策略命中与结果的审计记录。

### 5.9 Module
扩展能力的声明载体，MVP 只保留模型与元数据，不做真正动态运行时。

---

## 6. 关键边界冻结

### 6.1 Avatar 与 Persona
- 一个 Avatar 可拥有多版 Persona 历史
- 同一时刻只允许一个当前生效 Persona

### 6.2 Avatar 与 Agent
- 一个 Avatar 可拥有多个 Agent
- 所有 Agent 共享同一个 Avatar 级 Memory 池
- MVP 不做 Agent 私有长期记忆

### 6.3 Persona 与 Memory
- **Persona**：稳定画像、风格、偏好、边界摘要
- **Memory**：离散记忆项，支持检索、确认、归档与删除

### 6.4 MVP 记忆类型冻结
MVP 只保留以下 3 类：

- `profile`
- `episodic`
- `knowledge`

`procedural` 延后到 Beta。

---

## 7. 总体架构

### 7.1 分层架构

```text
┌────────────────────────────────────────────┐
│ Application Layer                          │
│ Web Console / REST API / CLI / Docker      │
├────────────────────────────────────────────┤
│ Domain Layer                               │
│ Avatar / Persona / Agent / Task / Memory   │
│ Policy / Audit                             │
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

### 7.2 架构原则
1. Controller 不承载核心业务逻辑
2. 主链路优先走同步服务调用
3. 扩展能力通过独立边界承载，不污染核心链路
4. 模块边界按领域划分，而非按页面划分
5. 数据模型优先稳定，前端交互可持续迭代

---

## 8. 模块化设计

### 8.1 Avatar 模块
负责：
- Avatar 创建与查询
- Avatar 元数据管理

### 8.2 Persona 模块
负责：
- 资料 / 样本输入
- Persona 生成
- Persona 版本管理
- 当前 Persona 获取

### 8.3 Agent 模块
负责：
- Agent 创建
- 角色定义
- 权限绑定
- Agent 状态管理

### 8.4 Task 模块
负责：
- Task 创建
- 执行编排
- 状态流转
- 结果持久化

### 8.5 Memory 模块
负责：
- 候选记忆捕捉
- 记忆确认 / 拒绝
- 检索与归档

### 8.6 Policy 模块
负责：
- 输入校验
- 输出校验
- 风险识别
- 决策返回

### 8.7 Audit 模块
负责：
- 审计追加记录
- Trace 串联
- 查询与回溯

### 8.8 Provider 模块
负责：
- 模型调用适配
- embedding 能力
- health check
- 模型元信息

---

## 9. 核心流程设计

### 9.1 初始化分身流程

```text
Create Avatar
  -> Import Sources
  -> Generate Persona
  -> Save Persona Version
  -> Avatar Ready
```

### 9.2 任务执行主链路

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

### 9.3 记忆确认流程

```text
Task Completed
  -> Memory Candidates Captured
  -> Pending List Visible
  -> User Confirm / Reject
  -> Persist State Change
  -> Append Audit Log
```

---

## 10. 上下文组装规范

### 10.1 固定拼装顺序
1. Base system instructions
2. Avatar Persona summary
3. Agent role prompt
4. Selected memories
5. Current task input
6. Policy constraints / runtime limits

### 10.2 设计原则
- Persona 是稳定底座
- Memory 是检索增强
- Agent role 是任务视角
- Task input 是当前目标
- Policy 是不可绕过边界

---

## 11. 安全与边界控制

### 11.1 安全原则
1. 默认拒绝
2. 显式授权
3. 最小权限
4. 高风险操作必须门禁
5. 审计默认开启
6. 敏感信息默认不自动写入长期记忆
7. 用户数据可导出、可删除、可纠正

### 11.2 Policy 执行时机
MVP 冻结以下策略执行时机：

- `pre_task`
- `pre_provider_call`
- `post_provider_output`
- `pre_memory_write`

### 11.3 Policy 统一返回结构

```json
{
  "decision": "allow",
  "hits": ["P-001"],
  "risk_level": "low",
  "message": "ok"
}
```

### 11.4 决策枚举
- `allow`
- `warn`
- `block`

### 11.5 敏感度分级
- `low`
- `medium`
- `high`

规则：
- `high` 敏感度内容默认不得自动进入长期记忆
- 审计记录默认优先保存摘要而非完整原文

---

## 12. 审计规范

### 12.1 必须审计的动作
1. Avatar created
2. Persona generated
3. Agent created / updated
4. Task created / started / completed / failed / blocked
5. Policy warned / blocked
6. Memory confirmed / rejected / archived / deleted
7. Module enabled / disabled

### 12.2 审计记录最小字段
- actor
- action
- resource_type
- resource_id
- result
- trace_id
- created_at
- request_summary
- policy_hits
- hash_prev
- hash_self

### 12.3 审计原则
- 默认开启
- 查询类接口默认只记摘要
- 不使用“绝对不可篡改”表述
- 使用哈希链与校验机制支持追溯与篡改检测

---

## 13. 数据模型建议

### 13.1 核心表
- `users`
- `avatars`
- `personas`
- `agents`
- `tasks`
- `memories`
- `policies`
- `audit_logs`
- `modules`

### 13.2 通用字段约束
主要业务表建议统一包含：
- `id`
- `created_at`
- `updated_at`

### 13.3 状态枚举冻结

#### Avatar
- `active`
- `inactive`

#### Agent
- `ready`
- `running`
- `disabled`

#### Task
- `pending`
- `running`
- `succeeded`
- `failed`
- `blocked`

#### Memory
- `captured`
- `pending_confirm`
- `confirmed`
- `rejected`
- `archived`

---

## 14. API 规范

### 14.1 API 设计原则
1. REST-first
2. 统一前缀 `/api/v1`
3. DTO 明确
4. 错误码统一
5. 查询同步，执行异步

### 14.2 MVP 最低 API 集

#### Avatar
- `POST /api/v1/avatars`
- `GET /api/v1/avatars/{avatarId}`

#### Persona
- `POST /api/v1/avatars/{avatarId}/persona/generate`
- `GET /api/v1/avatars/{avatarId}/persona/latest`

#### Agent
- `POST /api/v1/avatars/{avatarId}/agents`
- `GET /api/v1/agents/{agentId}`

#### Task
- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{taskId}`

#### Memory
- `GET /api/v1/avatars/{avatarId}/memories/pending`
- `POST /api/v1/memories/{memoryId}/confirm`
- `POST /api/v1/memories/{memoryId}/reject`

#### Audit
- `GET /api/v1/audit/logs`
- `GET /api/v1/audit/logs/{logId}`

### 14.3 Task 异步语义冻结
`POST /api/v1/tasks` 只返回任务壳与追踪信息：

```json
{
  "task_id": "task_001",
  "status": "pending",
  "trace_id": "trace_001"
}
```

前端通过轮询 `GET /api/v1/tasks/{taskId}` 获取状态。

### 14.4 错误码建议
至少冻结以下错误码：
- `VALIDATION_ERROR`
- `NOT_FOUND`
- `POLICY_BLOCKED`
- `PROVIDER_UNAVAILABLE`
- `TASK_EXECUTION_FAILED`
- `MEMORY_STATE_CONFLICT`

---

## 15. 前端产品体验设计

### 15.1 MVP 页面范围
1. Workspace / 首页
2. Persona 生成页
3. Task 执行页
4. Pending Memory 确认页
5. Audit 日志页

### 15.2 页面状态机

#### Persona 页面
- `idle`
- `source_ready`
- `generating`
- `generated`
- `failed`

#### Task 页面
- `idle`
- `creating`
- `running`
- `succeeded`
- `failed`
- `blocked`

#### Pending Memory 页面
- `loading`
- `empty`
- `has_pending`
- `confirming`
- `rejecting`
- `error`

### 15.3 交互原则
1. 首页只回答三件事：我的分身是谁、它知道什么、我能让它做什么
2. 风险状态必须可见
3. 记忆写入必须可确认
4. 错误提示必须清晰但不过度技术化

---

## 16. 技术栈建议

### 16.1 MVP 推荐栈

#### 后端
- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy

#### 前端
- Vue 3
- Vite
- TypeScript
- Element Plus

#### 存储
- SQLite
- 向量存储：Chroma / FAISS / sqlite-vec（三选一）

#### 模型运行时
- Ollama

#### 测试
- Pytest
- Vitest
- Playwright

#### 交付
- Docker
- GitHub Actions

---

## 17. 测试策略

### 17.1 测试目标
确保：
- 主链路稳定
- 安全边界有效
- 回归可快速发现

### 17.2 单元测试重点
- Persona 生成逻辑
- Memory 状态机
- Policy 决策
- Task 状态流转

### 17.3 集成测试重点
覆盖主链路：
1. Avatar 创建
2. Persona 生成
3. Agent 创建
4. Task 执行
5. 候选记忆生成
6. 用户确认记忆
7. 审计查询

### 17.4 E2E 测试重点
1. 初始化闭环
2. 单任务执行闭环
3. 待确认记忆处理闭环

### 17.5 安全测试重点
1. 越权操作阻断
2. 非法状态流转阻断
3. 高风险输出阻断
4. 敏感记忆未自动入库
5. Provider 不可用时失败处理
6. 审计记录存在性校验

---

## 18. GitHub 开源项目规范

### 18.1 仓库级文件
建议首版即具备：
- `README.md`
- `CLAUDE.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/roadmap.md`

### 18.2 GitHub 模板
建议提供：
- Bug report template
- Feature request template
- Pull request template

### 18.3 CI 最低要求
至少覆盖：
- lint
- unit tests
- integration tests
- build check

---

## 19. 多代理并行开发规范

### 19.1 并行开发前必须冻结
1. 领域模型
2. 状态枚举
3. API 合同
4. 错误码
5. 目录结构
6. DTO 边界
7. 审计结构
8. Policy 返回结构

### 19.2 推荐角色拆分

#### 主控代理
负责：方案冻结、目录骨架、集成裁决、验收合并

#### 后端内核代理
负责：Provider、Task orchestration、Service layer

#### Persona / Memory 代理
负责：Persona generation、Memory capture、Memory state machine

#### Policy / Audit 代理
负责：Policy engine、Audit append、Risk metadata

#### API 代理
负责：DTO、REST routes、OpenAPI

#### 前端代理
负责：页面状态机、页面实现、API 联调

#### 测试代理
负责：unit / integration / e2e / regression suite

#### 文档与治理代理
负责：README、docs、模板、SECURITY、CONTRIBUTING

### 19.3 并行开发原则
1. 按领域切，不按页面切
2. 先冻结契约，再并行开发
3. 主链路优先于扩展链路
4. 测试尽早介入，不在最后补
5. 每个代理只负责一个清晰边界

---

## 20. 推荐目录结构

```text
digital-avatar/
├─ apps/
│  ├─ api/
│  └─ web/
├─ packages/
│  ├─ domain/
│  ├─ services/
│  ├─ provider/
│  ├─ memory/
│  ├─ policy/
│  ├─ audit/
│  └─ shared/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ e2e/
│  └─ fixtures/
├─ docs/
│  ├─ architecture.md
│  ├─ api.md
│  ├─ product.md
│  ├─ roadmap.md
│  └─ security.md
├─ deploy/
│  └─ docker/
├─ .github/
│  ├─ workflows/
│  ├─ ISSUE_TEMPLATE/
│  └─ PULL_REQUEST_TEMPLATE.md
├─ CLAUDE.md
├─ README.md
└─ LICENSE
```

---

## 21. MVP 冻结结论

在正式开工前，以下结论必须冻结：

1. MVP 不做真正插件运行时
2. MVP 不做通用事件总线平台
3. 一个 Avatar 只有一个当前 Persona
4. 同 Avatar 的 Agent 共享 Memory 池
5. MVP 记忆类型缩减为三类
6. Task 一律异步建模
7. Policy 返回结构统一
8. 审计最小集合明确
9. 上下文组装顺序固定
10. 前后端状态枚举冻结

---

## 22. 一句话总结

> Digital Avatar 应被设计为一个以用户为中心、以可控执行为核心、以长期记忆沉淀为增益、以安全审计为底座的数字分身系统；其 MVP 必须剃刀化聚焦单条主链路，采用模块化与流程化架构，并通过冻结契约支持多代理并行开发，逐步演进为强大而可信的开源智能体平台。
