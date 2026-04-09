# 功能规格

## 1. 模块规格表

| 模块 | 页面 / 入口 | 输入 | 输出 | 主状态 | 失败分支 | 权限要求 | 审计要求 | 最低脚手架文件 |
|---|---|---|---|---|---|---|---|---|
| Auth 登录 | 登录页、受保护路由重定向 | `email` `password` | `access_token` `refresh_token` `user` `trace_id` | `idle -> submitting -> authenticated / failed` | 凭证错误、账户锁定、限流 | 匿名可访问登录接口；登录后才能访问受保护接口 | 登录成功/失败都写审计 | `api/v1/auth.py` `services/auth_service.py` `schemas/auth.py` `views/auth/LoginView.vue` `stores/auth.ts` |
| Auth 刷新 | 启动恢复、401 自动续期 | `refresh_token` | 新 `access_token` `refresh_token` | `refreshing -> refreshed / expired` | refresh 失效、被撤销 | 持有 refresh token | refresh 成功/失败写审计 | `services/auth_refresh.py` `api/auth.ts` `composables/useAuthRefresh.ts` |
| Avatar 创建 | Dashboard CTA、Avatar 创建页 | `name` `goal` `visibility` | Avatar 摘要对象 | `idle -> submitting -> created / failed` | 校验失败、未授权 | 登录用户 | avatar created 写审计 | `api/v1/avatars.py` `services/avatar_service.py` `views/avatar/AvatarCreateView.vue` |
| Avatar 列表 / 详情 / 更新 | Avatar 列表页、详情页 | `page` `page_size` 或 `avatarId`；更新时 `name` `goal` `visibility` | 分页列表或详情对象 | `loading -> ready / empty / failed`；更新 `editing -> saved / failed` | 未找到、未授权、校验失败 | 登录用户，只能访问自己的 Avatar | avatar updated 写审计 | `views/avatar/AvatarListView.vue` `views/avatar/AvatarDetailView.vue` `stores/avatar.ts` |
| Persona 生成 | Persona 生成页 | `avatar_id` + 样本输入 / 模板选择 | 新 Persona 版本摘要 | `idle -> source_ready -> generating -> generated / failed` | 样本不足、策略阻断、Provider 不可用 | 登录用户且拥有 Avatar | persona generated 写审计 | `api/v1/personas.py` `services/persona_service.py` `views/persona/PersonaGenerateView.vue` |
| Persona 激活 / 历史 | Persona 生成页、Persona 历史抽屉 | `personaId` | 当前 Persona 切换结果 | `loading -> ready -> activating -> activated / failed` | 未找到、状态冲突 | 登录用户且拥有 Avatar | persona switched 写审计 | `components/persona/PersonaHistoryDrawer.vue` `api/personas.ts` |
| Agent 管理 | Agent 管理页 | 创建时 `avatar_id` `name` `role`；更新时 `status` `role` | Agent 摘要 / 详情 | `loading -> ready -> saving / failed` | 未找到、越权、校验失败 | 登录用户且拥有 Avatar | agent created/updated/enabled/disabled 写审计 | `api/v1/agents.py` `services/agent_service.py` `views/agent/AgentManagementView.vue` |
| Task 创建 / 查询 | Task 执行页、Dashboard 快捷入口 | `avatar_id` `agent_id` `input` `trace_id?` | `task_id` `status` `trace_id` `result` `error` | `idle -> creating -> pending -> running -> succeeded / failed / blocked` | policy 阻断、provider 失败、未授权 | 登录用户且可使用目标 Agent | task created/started/completed/failed/blocked 写审计 | `api/v1/tasks.py` `services/task_service.py` `workers/task_worker.py` `views/task/TaskExecutionView.vue` |
| Memory pending / confirm / reject | Pending Memory 页 | `avatarId`；决策时 `memoryId` `reason?` | pending 列表、确认/拒绝结果 | `loading -> empty / has_pending -> confirming/rejecting -> updated / failed` | 状态冲突、越权、未找到 | 登录用户且拥有 Avatar | memory confirmed/rejected 写审计 | `api/v1/memories.py` `services/memory_service.py` `views/memory/PendingMemoryView.vue` |
| Memory 搜索 / 详情 | Memory 搜索页、详情抽屉 | `query` `type?` `page` `page_size` `memoryId` | 搜索列表、记忆详情 | `idle -> loading -> ready / empty / failed` | 未找到、未授权 | 登录用户且拥有 Avatar | memory viewed 可选摘要审计 | `views/memory/MemorySearchView.vue` `components/memory/MemoryDetailDrawer.vue` |
| Growth Report | Dashboard、Avatar 详情页 | `avatarId`、可选时间范围 / 视图筛选 | 成长快照、最近新增确认记忆、成长洞察、推荐动作、证据入口 | `loading -> empty / building / ready / demo / failed` | 数据不足、审计缺失、未授权 | 登录用户且拥有 Avatar；Demo 模式需明确标识 | 报告查看可选摘要审计；所有洞察需可回溯到 memory / task / trace_id | `views/dashboard/GrowthReportCard.vue` `views/avatar/AvatarGrowthReportView.vue` `api/growth-report.ts` `tests/unit/growth-report.spec.ts` |

## 2. 页面清单与职责

### 登录 / 认证页
- 目的：建立会话并处理过期恢复。
- 页面元素：邮箱、密码、登录按钮、错误提示、加载态。
- 必须调用：`POST /api/v1/auth/login`。
- 成功后跳转：Dashboard。
- 失败反馈：表单级错误、全局提示、重试按钮。

### Dashboard
- 目的：展示当前 Avatar 概览、推荐下一步、最近 Task / Pending Memory。
- 页面元素：快速创建 Avatar、继续 Persona、建议任务、待确认记忆卡片。
- 必须调用：`GET /api/v1/avatars`、`GET /api/v1/avatars/{avatarId}/tasks`、`GET /api/v1/avatars/{avatarId}/memories/pending`。

### Avatar 列表页
- 目的：浏览、进入详情、新建。
- 页面元素：列表表格、搜索/分页、新建按钮、空态。

### Avatar 创建页
- 目的：完成 Avatar 初始化。
- 页面元素：`name` `goal` `visibility` 表单、提交按钮、返回按钮。

### Persona 生成页
- 目的：导入最小样本、生成 Persona、查看历史版本、激活版本。
- 页面元素：样本输入区、模板入口、历史列表、生成结果面板。

### Agent 管理页
- 目的：查看默认 Agent、调整角色与状态。
- 页面元素：Agent 列表、状态开关、角色表单、权限提示。

### Task 执行页
- 目的：输入任务、查看运行状态与结果。
- 页面元素：Avatar 选择、Agent 选择、任务输入框、trace_id 展示、状态条、结果区、错误区。

### Pending Memory 确认页
- 目的：逐条处理候选记忆。
- 页面元素：记忆卡片、来源任务、风险标记、确认/拒绝按钮、reason 输入。

### Memory 搜索 / 详情页
- 目的：检索已确认记忆并查看详情。
- 页面元素：搜索框、过滤器、分页、详情抽屉。

### Growth Report / 分身成长报告
- 目的：向用户解释分身最近学到了什么、为什么这样判断、因此下一步建议做什么。
- 页面元素：成长快照、已确认记忆摘要、成长洞察、推荐动作、证据入口、Demo 标识。
- 数据来源约束：只能把 `confirmed` memory 作为“系统已学会”的依据；`pending_confirm` 与 `rejected` 不得进入成长洞察。
- 基础状态：
  - `empty`：暂无足够 confirmed memory；
  - `building`：已有任务和候选记忆，但成长结论仍不足；
  - `ready`：可展示成长快照、洞察与推荐动作；
  - `demo`：基于 Demo Avatar 的示例报告；
  - `failed`：聚合失败或缺少必要数据。
- 失败/限制要求：
  - 不得夸大系统已掌握的内容；
  - 审计缺失时不得宣称“完全可追溯”；
  - provider 当前不可用不应抹掉历史成长报告。

### Settings 页
- 目的：配置 Provider、查看隐私说明、执行导出/删除。
- 页面元素：配置表单、导出按钮、删除确认对话框、安全提示。

### 404 / 错误页
- 目的：承接未知路由与严重错误。
- 页面元素：错误说明、返回首页按钮、重试按钮。

## 3. 状态机约束

### 登录会话状态机
```text
idle -> submitting -> authenticated
                 └-> failed
authenticated -> refreshing -> authenticated
                           └-> expired
```

### Avatar 创建状态机
```text
idle -> editing -> submitting -> created
                             └-> failed
```

### Persona 生成状态机
```text
idle -> source_ready -> generating -> generated
                              ├-> failed
                              └-> blocked
```

### Task 执行状态机
```text
idle -> creating -> pending -> running -> succeeded
                                   ├-> failed
                                   └-> blocked
```

### Pending Memory 处理状态机
```text
loading -> empty
        └-> has_pending -> confirming -> updated
                       ├-> rejecting -> updated
                       └-> failed
```

## 4. 失败分支统一要求

- 所有失败必须有明确错误码，不允许仅返回自然语言。
- 页面必须区分：表单校验失败、权限失败、策略阻断、Provider 异常、系统异常。
- 对于可重试动作，必须提供重试入口；对不可重试动作，必须给出下一步建议。
- 策略阻断必须展示可理解的阻断原因与 `trace_id`。

## 5. 权限与审计规则

- Auth 登录页是唯一匿名业务入口；其余业务页默认需要登录。
- 所有写操作默认需要写审计：创建、更新、确认、拒绝、删除、阻断。
- 读取型接口若涉及敏感对象详情，可只记录摘要审计，不记录敏感内容全文。
- Settings 中导出、删除、敏感配置修改必须要求二次确认。

## 6. 脚手架生成约束

- 每个模块至少要能生成：route/controller、service、schema/model、前端页面、API client、store/composable、测试骨架。
- 若某模块无法回答“页面入口、接口入口、状态机、失败分支、权限要求、审计要求”，则该模块规格未达 scaffold-ready。
- 未在此文档声明的页面交互，不视为 MVP 稳定依赖。