# Digital Avatar 正式方案（V14）

> 文档状态：正式升版 / 基于 MiniMax 多智能体评审意见修订  
> 修订依据：`docs/minimax多智能体评审意见.md`、`docs/frontend-architecture-review.md`  
> 适用阶段：MVP 立项冻结、仓库初始化、并行开发、Beta 演进基线  
> 文档目标：提供一份可直接交给开发智能体或开发团队执行的、边界清晰、可检查、可落地的完整方案

---

## 1. 修订摘要

本版相较 V13，重点补齐了评审中识别出的 P0 / P1 问题：

### 1.1 本次升版新增冻结项
1. **认证授权方案冻结**：MVP 采用 JWT + Refresh Token + bcrypt 密码哈希
2. **向量存储方案冻结**：MVP 采用 `sqlite-vec`，Beta 预留迁移 `Chroma`
3. **冷启动方案补充**：增加 Demo Avatar、预置 Persona 模板、引导式首启流程
4. **LLM 输出安全补充**：增加输出安全过滤、风险分级与阻断策略
5. **隐私与合规补充**：增加用户导出、删除、保留期限与隐私文档要求
6. **前端架构补充**：冻结 Pinia、Vue Router 4、Axios、OpenAPI 类型生成
7. **页面体系补充**：增加登录页、分身列表页、Agent 管理页、错误页、设置页
8. **数据库与索引补充**：增加高频查询索引与状态字段约束
9. **日志与可观测性补充**：增加结构化日志、trace_id、健康检查与基础指标
10. **MVP 成功标准补充**：增加可量化验收指标

### 1.2 本版核心结论
> Digital Avatar 的 MVP 必须从“概念完整”升级为“执行可落地”。
> 因此首版应以 **安全可控、冷启动可体验、契约可冻结、执行可审计** 为第一优先级，而不是继续扩展抽象层与插件能力。

---

## 2. 项目定位

### 2.1 项目定义
Digital Avatar 是一个面向个人专业用户和 AI-native 小团队的开源数字分身系统。

系统围绕以下四个核心能力构建：

1. **风格复刻**：输出更像用户本人，而不是通用 AI
2. **可控执行**：在授权范围内辅助完成真实任务
3. **长期记忆**：沉淀经过确认的长期价值信息
4. **审计追踪**：关键操作、策略命中、状态变化可回溯

### 2.2 产品边界
它不是：
- 通用聊天产品
- 高自治 Agent 平台
- 首版即开放插件市场的平台
- 企业级 IAM / 多租户系统

它是：
- 用户可控的数字分身系统
- 本地优先的任务辅助系统
- 记忆与风格持续演化的个人智能资产载体

---

## 3. 用户与价值主张（UVP）

### 3.1 目标用户分层

#### A. 核心用户：个人专业用户
1. 开发者
2. 产品经理
3. 内容创作者
4. 研究者 / 分析师
5. 重度 AI 用户

#### B. 次级用户：AI-native 小团队
1. 创业团队
2. 工作室 / 顾问团队
3. 教学与研究小组

#### C. 当前不优先用户
1. 大型企业组织级部署
2. 高合规生产场景
3. 多租户复杂权限治理场景
4. 大规模面向 C 端聊天用户

### 3.2 核心用户问题
1. 每次都要重新教 AI 自己的风格与偏好
2. 历史上下文无法稳定继承
3. AI 能输出内容，但执行边界不清晰
4. 缺少长期记忆沉淀与纠错机制
5. 缺少可信的审计链路
6. 首次使用门槛高，不容易快速感知价值

### 3.3 核心价值主张
> Digital Avatar 帮助用户把自己的风格、知识、偏好和工作方式沉淀为一个可控、可审计、可持续成长的数字分身，用于持续辅助真实任务执行，而不是每次从零开始重新训练一个临时 AI。

### 3.4 价值量化指标（新增）
MVP 必须定义基础效果指标：

1. **首次可用时间**：从注册到完成首个任务 ≤ 15 分钟
2. **冷启动完成率**：新用户完成 Avatar→Persona→Task 闭环 ≥ 60%
3. **记忆确认率**：候选记忆中被确认比例 ≥ 30%
4. **风格匹配感知**：用户主观评分 ≥ 7/10
5. **任务完成率**：成功完成任务比例 ≥ 80%
6. **安全阻断准确率**：高风险规则命中后应阻断的场景 ≥ 95%

---

## 4. 产品设计原则

1. **先验证闭环，再扩展生态**
2. **先冷启动可体验，再追求复杂记忆体系**
3. **先安全可控，再增强自治能力**
4. **先本地优先，再云端扩展**
5. **先单链路跑通，再做多代理协同**
6. **先契约冻结，再并行开发**
7. **默认可审计，默认最小权限**
8. **用户可纠正、可撤回、可删除、可导出**
9. **复杂度必须为真实价值服务**
10. **设计必须服务实现，不保留无落地收益的抽象**

---

## 5. 版本策略与范围冻结

### 5.1 MVP 核心命题
> 用户能够导入自己的资料，生成初始数字分身，并让其在受控条件下执行一个任务，同时自动捕捉候选记忆，经用户确认后写入长期记忆库。

### 5.2 MVP 必须完成
1. 用户认证登录
2. Avatar 创建与管理
3. 资料 / 样本导入
4. Persona 生成与版本切换
5. 单 Agent 创建与管理
6. 单任务执行
7. 候选记忆自动捕捉
8. 记忆确认 / 拒绝 / 查看
9. 基础 Policy 检查
10. 审计日志记录与查看
11. Demo 数据与新手引导
12. Web 控制台
13. Docker 一键部署

### 5.3 MVP 明确不做
1. 真正插件运行时
2. 通用事件总线平台
3. 多组织复杂权限体系
4. 多设备同步
5. 插件市场
6. 高级多代理自治编排
7. 桌面端正式交付
8. 企业级多租户能力

### 5.4 Beta 方向
1. 多模型 Provider
2. Chroma 向量存储迁移选项
3. 多 Agent 模板
4. Memory 检索增强与重排
5. 模块/扩展最小机制
6. 导出/备份能力增强
7. SDK / API 生态
8. 可选桌面端

---

## 6. 冷启动与用户增长设计（新增）

评审指出冷启动门槛高，这是首版必须修复的问题。

### 6.1 MVP 冷启动方案
1. **Demo Avatar**：内置一个可立即体验的示例分身
2. **预置 Persona 模板**：开发者 / 产品经理 / 创作者 / 分析师
3. **引导式首启流程**：登录后分步骤完成
   - 创建 Avatar
   - 导入资料
   - 生成 Persona
   - 创建 Agent
   - 执行首个任务
4. **样本导入最小化**：首版支持文本粘贴 + 示例导入，不要求大量资料
5. **首个任务推荐模板**：如“请用我的风格总结这段内容”
6. **Avatar 成长报告**：展示已学习偏好、已确认记忆数、任务执行数

### 6.2 首次使用流程

```text
Login
  -> Create Avatar / Use Demo Avatar
  -> Import Minimal Sources
  -> Generate Persona
  -> Create Default Agent
  -> Run Suggested Task
  -> Review Candidate Memories
  -> Finish Guided Onboarding
```

---

## 7. 核心对象模型

### 7.1 User
系统使用者。

### 7.2 Avatar
用户数字分身的顶层容器。

### 7.3 Persona
当前生效的稳定画像摘要，包括风格、偏好、约束与角色理解。

### 7.4 Agent
面向具体任务的执行角色实例，不是独立人格主体。

### 7.5 Task
具有输入、上下文、执行状态、结果和追踪信息的任务单元。

### 7.6 Memory
可检索、可确认、可归档的离散长期信息条目。

### 7.7 Policy
用于边界约束、风险校验和阻断决策的规则定义。

### 7.8 AuditLog
追踪关键动作、策略命中与结果的审计记录。

### 7.9 Module
扩展能力声明载体。MVP 不做真正动态运行时。

---

## 8. 关键边界冻结

### 8.1 Avatar 与 Persona
- 一个 Avatar 可拥有多版 Persona 历史
- 同一时刻只允许一个当前 Persona 生效

### 8.2 Avatar 与 Agent
- 一个 Avatar 可拥有多个 Agent
- 所有 Agent 共享 Avatar 级 Memory 池
- MVP 不做 Agent 私有长期记忆

### 8.3 Persona 与 Memory
- **Persona**：稳定画像、风格、偏好、边界摘要
- **Memory**：离散记忆项，支持检索、确认、归档与删除

### 8.4 MVP 记忆类型冻结
- `profile`
- `episodic`
- `knowledge`

### 8.5 模块边界冻结
- MVP 仅保留模块声明模型，不启用真实动态加载
- 所有扩展点先以内建注册方式存在

---

## 9. 总体架构

### 9.1 分层架构

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

### 9.2 架构原则
1. Controller 不承载核心业务逻辑
2. 主链路优先走同步服务调用
3. 异步只用于非关键路径或后续扩展
4. 扩展能力不污染核心链路
5. 模块边界按领域划分而非按页面划分
6. 依赖关系遵循依赖反转，避免循环依赖

### 9.3 扩展点定义（新增）
MVP 明确以下未来扩展点，但只冻结接口，不全面实现插件化：

1. Provider Adapter
2. Memory Extractor
3. Policy Evaluator
4. Audit Sink
5. Task Executor

---

## 10. 技术选型冻结

### 10.1 后端
- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PyJWT / jose
- bcrypt / passlib

### 10.2 前端
- Vue 3 + Composition API
- Vite
- TypeScript strict
- Pinia
- Vue Router 4
- Axios
- Element Plus（按需导入）
- OpenAPI 类型生成

### 10.3 存储
- SQLite（MVP）
- `sqlite-vec`（MVP 向量存储）
- Chroma（Beta 可迁移）

### 10.4 测试
- Pytest
- Vitest
- Playwright

### 10.5 交付与运维
- Docker / Docker Compose
- GitHub Actions
- JSON 结构化日志
- Prometheus 指标（MVP 最小集）

### 10.6 关键技术决策（ADR 方向）
必须记录以下 ADR：
1. 为什么 MVP 选 sqlite-vec
2. 为什么 MVP 不做插件运行时
3. 为什么 Task 采用异步建模
4. 为什么前端采用 Pinia + OpenAPI 类型生成

---

## 11. 模块化设计

### 11.1 User/Auth 模块（新增）
负责：
- 登录认证
- Token 生成与刷新
- 密码哈希
- 用户会话管理

### 11.2 Avatar 模块
负责：
- Avatar 创建、列表、查询、更新

### 11.3 Persona 模块
负责：
- 样本输入
- Persona 生成
- Persona 版本管理
- 当前 Persona 获取与切换

### 11.4 Agent 模块
负责：
- Agent 创建、查询、启用/停用
- 角色定义
- 权限绑定

### 11.5 Task 模块
负责：
- Task 创建
- 执行编排
- 状态流转
- 结果持久化

### 11.6 Memory 模块
负责：
- 候选记忆捕捉
- 记忆确认 / 拒绝 / 归档 / 搜索

### 11.7 Policy 模块
负责：
- 输入校验
- 输出校验
- 风险识别
- 决策返回

### 11.8 Audit 模块
负责：
- 审计追加记录
- Trace 串联
- 查询与回溯

### 11.9 Provider 模块
负责：
- chat / stream_chat / embed / health_check / model_info

---

## 12. 核心流程设计

### 12.1 初始化分身流程

```text
Create Avatar
  -> Import Sources
  -> Generate Persona
  -> Save Persona Version
  -> Avatar Ready
```

### 12.2 任务执行主链路

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

### 12.3 记忆确认流程

```text
Task Completed
  -> Memory Candidates Captured
  -> Pending List Visible
  -> User Confirm / Reject
  -> Persist State Change
  -> Append Audit Log
```

### 12.4 登录认证流程（新增）

```text
Register / Login
  -> Verify Credential
  -> Issue Access Token
  -> Issue Refresh Token
  -> Load User Workspace
```

---

## 13. 上下文组装规范

### 13.1 固定拼装顺序
1. Base system instructions
2. Avatar Persona summary
3. Agent role prompt
4. Selected memories
5. Current task input
6. Policy constraints / runtime limits

### 13.2 设计原则
- Persona 是稳定底座
- Memory 是检索增强
- Agent role 是任务视角
- Task input 是当前目标
- Policy 是不可绕过边界

---

## 14. 安全与合规设计

安全是本次评审最主要短板，本版将其升级为 MVP 冻结要求。

### 14.1 认证授权机制（新增）
MVP 冻结方案：

1. Access Token：JWT，短期有效
2. Refresh Token：长效，用于续期
3. 密码存储：bcrypt 哈希
4. 登录失败次数限制
5. 敏感操作需要用户身份校验

### 14.2 权限原则
1. 默认拒绝
2. 显式授权
3. 最小权限
4. 高风险操作必须门禁

### 14.3 Policy 执行时机
- `pre_task`
- `pre_provider_call`
- `post_provider_output`
- `pre_memory_write`

### 14.4 Policy 统一返回结构

```json
{
  "decision": "allow",
  "hits": ["P-001"],
  "risk_level": "low",
  "message": "ok"
}
```

### 14.5 LLM 输出安全过滤（新增）
首版必须覆盖：
1. 高风险冒充阻断
2. 明显恶意内容阻断
3. 敏感信息外泄检测
4. 高风险承诺或误导性建议拦截

### 14.6 数据安全（新增）
1. 敏感字段支持 AES-256 应用层加密
2. 数据库文件加密能力作为部署选项（如 SQLCipher）
3. 高敏感记忆默认不自动入长期库
4. 审计默认记录摘要，不记录完整敏感内容

### 14.7 隐私与合规（新增）
MVP 至少提供：
1. 隐私政策文档
2. 用户数据导出接口
3. 用户数据删除接口
4. 数据保留期限策略
5. 敏感数据分类与分级说明

### 14.8 插件/模块安全
- MVP 不开放任意插件
- Beta 若开放扩展，需进程隔离、权限声明、资源限制

---

## 15. 审计规范

### 15.1 必须审计的动作
1. user login / logout
2. avatar created / updated
3. persona generated / switched
4. agent created / updated / enabled / disabled
5. task created / started / completed / failed / blocked
6. policy warned / blocked
7. memory confirmed / rejected / archived / deleted
8. module enabled / disabled

### 15.2 审计最小字段
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

### 15.3 日志与审计约束（新增）
- 使用 JSON 结构化日志
- 每条任务链路必须传递 trace_id
- 错误日志与审计日志分离，但通过 trace_id 关联

---

## 16. 数据模型与索引设计

### 16.1 核心表
- `users`
- `avatars`
- `personas`
- `agents`
- `tasks`
- `memories`
- `policies`
- `audit_logs`
- `modules`

### 16.2 通用字段约束
主要业务表统一包含：
- `id`
- `created_at`
- `updated_at`

### 16.3 状态枚举冻结

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

### 16.4 索引设计（新增）
MVP 至少建立以下索引：

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

---

## 17. API 规范

### 17.1 API 设计原则
1. REST-first
2. 统一前缀 `/api/v1`
3. DTO 明确
4. 错误码统一
5. 查询同步，执行异步

### 17.2 统一错误响应结构（新增）

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

### 17.3 错误码冻结
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

### 17.4 MVP API 集

#### Auth
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

#### Avatar
- `POST /api/v1/avatars`
- `GET /api/v1/avatars`
- `GET /api/v1/avatars/{avatarId}`
- `PATCH /api/v1/avatars/{avatarId}`

#### Persona
- `POST /api/v1/avatars/{avatarId}/persona/generate`
- `GET /api/v1/avatars/{avatarId}/persona/latest`
- `GET /api/v1/avatars/{avatarId}/personas`
- `POST /api/v1/personas/{personaId}/activate`

#### Agent
- `POST /api/v1/avatars/{avatarId}/agents`
- `GET /api/v1/agents/{agentId}`
- `GET /api/v1/avatars/{avatarId}/agents`
- `PATCH /api/v1/agents/{agentId}`

#### Task
- `POST /api/v1/tasks`
- `GET /api/v1/tasks/{taskId}`
- `GET /api/v1/avatars/{avatarId}/tasks`

#### Memory
- `GET /api/v1/avatars/{avatarId}/memories/pending`
- `GET /api/v1/avatars/{avatarId}/memories/search`
- `GET /api/v1/memories/{memoryId}`
- `POST /api/v1/memories/{memoryId}/confirm`
- `POST /api/v1/memories/{memoryId}/reject`

#### Audit
- `GET /api/v1/audit/logs`
- `GET /api/v1/audit/logs/{logId}`

### 17.5 Task 异步语义冻结
`POST /api/v1/tasks` 只返回任务壳：

```json
{
  "task_id": "task_001",
  "status": "pending",
  "trace_id": "trace_001"
}
```

MVP 默认采用轮询，SSE 作为 P1 增强项。

---

## 18. 前端架构与页面体系

### 18.1 前端技术方案冻结
- Pinia 作为状态管理
- Vue Router 4 作为路由
- Axios 作为 HTTP 客户端
- `openapi-typescript` 生成 API 类型
- Element Plus 使用按需导入

### 18.2 推荐目录结构

```text
apps/web/src/
├── api/
├── types/
├── stores/
├── composables/
├── components/
├── views/
├── router/
└── utils/
```

### 18.3 MVP 页面范围（升版）
1. 登录 / 认证页
2. 首页 / Dashboard
3. Avatar 列表页
4. Avatar 创建页
5. Persona 生成页
6. Agent 管理页
7. Task 执行页
8. Pending Memory 确认页
9. Memory 搜索 / 详情页
10. Audit 日志页
11. Settings 页
12. 404 / 错误页

### 18.4 页面状态机最低要求

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

### 18.5 前端交互规范（新增）
1. 定义全局加载态
2. 定义全局错误提示
3. 定义空状态模板
4. 请求支持取消机制
5. 对敏感确认操作增加二次确认

---

## 19. 性能与可观测性

### 19.1 MVP 性能约束
1. 首屏核心页面加载尽可能 < 2.5s
2. Task 状态查询接口 P95 < 500ms（不含 LLM 执行）
3. Memory pending 列表查询 P95 < 300ms
4. Audit 列表查询支持分页

### 19.2 LLM 调用优化（新增）
1. Provider 调用设置超时
2. 指数退避重试
3. 并发限制
4. 幂等 trace_id 透传
5. 对重复请求预留缓存机制

### 19.3 可观测性最低要求
1. `/health` 健康检查端点
2. `/metrics` 基础指标端点
3. 结构化日志
4. trace_id 全链路透传

---

## 20. 测试策略

### 20.1 测试目标
确保：
- 主链路稳定
- 安全边界有效
- 回归可快速发现
- 核心指标可验证

### 20.2 单元测试重点
- Persona 生成逻辑
- Memory 状态机
- Policy 决策
- Task 状态流转
- Auth Token 校验逻辑

### 20.3 集成测试重点
1. 登录认证
2. Avatar 创建
3. Persona 生成
4. Agent 创建
5. Task 执行
6. 候选记忆生成
7. 用户确认记忆
8. 审计查询

### 20.4 E2E 测试重点
1. 首次引导闭环
2. 单任务执行闭环
3. 待确认记忆处理闭环
4. 登录到 Dashboard 的基本流转

### 20.5 安全测试重点
1. 未授权请求阻断
2. 越权操作阻断
3. 非法状态流转阻断
4. 高风险输出阻断
5. 敏感记忆不自动入库
6. 用户导出 / 删除接口正确执行

---

## 21. 部署与运维方案

### 21.1 MVP 部署形态
- 单机 Docker Compose 部署
- Web + API + SQLite + Ollama（可外置）

### 21.2 部署要求
1. 环境变量模板
2. 一键启动脚本
3. 数据目录挂载
4. 日志目录挂载
5. 备份与恢复说明

### 21.3 运维补充（新增）
1. 健康检查
2. 基础监控
3. 日志滚动策略
4. SQLite 备份策略
5. 数据迁移说明

---

## 22. GitHub 开源项目规范

### 22.1 仓库级文件
必须具备：
- `README.md`
- `CLAUDE.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `PRIVACY.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/roadmap.md`

### 22.2 GitHub 模板
- Bug report template
- Feature request template
- Pull request template
- Security report guidance

### 22.3 CI 最低要求
- lint
- type check
- unit tests
- integration tests
- build check
- security scan

---

## 23. 多代理并行开发规范

### 23.1 并行开发前必须冻结
1. 领域模型
2. 状态枚举
3. API 合同
4. 错误码
5. 目录结构
6. DTO 边界
7. 审计结构
8. Policy 返回结构
9. Auth 方案
10. 向量存储方案

### 23.2 推荐角色拆分

#### 主控代理
负责：方案冻结、目录骨架、集成裁决、验收合并

#### 产品 / 文档代理
负责：需求、流程、指标、文档对齐

#### 后端内核代理
负责：Provider、Task orchestration、Service layer

#### Auth / Security 代理
负责：登录认证、权限检查、安全策略、隐私接口

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

#### 部署与运维代理
负责：Docker、健康检查、日志、监控、备份说明

### 23.3 并行开发原则
1. 按领域切，不按页面切
2. 先冻结契约，再并行开发
3. 主链路优先于扩展链路
4. 测试尽早介入，不在最后补
5. 每个代理只负责一个清晰边界
6. 所有交付必须附带验收标准

---

## 24. 推荐目录结构

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
│  ├─ auth/
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
│  ├─ security.md
│  ├─ privacy.md
│  └─ adr/
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

## 25. MVP 成功标准

只有同时满足以下条件，MVP 才算完成：

1. 用户可登录并创建 Avatar
2. 用户可在 15 分钟内跑通首次体验闭环
3. Persona 可生成并持久化
4. Agent 可创建并执行任务
5. Task 有完整 trace_id 与状态流转
6. 候选记忆可被确认 / 拒绝
7. 高风险策略能阻断典型危险输出
8. 审计日志可查询与关联
9. Docker 可一键启动演示环境
10. 核心测试通过，主要安全用例覆盖

---

## 26. 一句话总结

> Digital Avatar V14 应被视为一个以用户为中心、以冷启动可体验为入口、以可控执行为核心、以长期记忆沉淀为增益、以安全审计与隐私合规为底座的数字分身系统；其 MVP 必须在架构、认证、前端、存储、审计和多代理协作上完成必要冻结，确保后续开发可以一比一落地执行。
