# 前端架构

## 1. 技术冻结

- Vue 3 + Composition API
- Vite
- TypeScript strict
- Pinia
- Vue Router 4
- Axios
- Element Plus（按需导入）
- `openapi-typescript` 自动生成 API 类型

## 2. 目录骨架

```text
apps/web/
├── src/
│   ├── api/
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── avatars.ts
│   │   ├── personas.ts
│   │   ├── agents.ts
│   │   ├── tasks.ts
│   │   ├── memories.ts
│   │   ├── audit.ts
│   │   └── privacy.ts
│   ├── types/
│   │   ├── generated/
│   │   └── ui/
│   ├── stores/
│   │   ├── auth.ts
│   │   ├── avatar.ts
│   │   ├── task.ts
│   │   └── memory.ts
│   ├── composables/
│   │   ├── useAuth.ts
│   │   ├── usePagination.ts
│   │   ├── useTaskPolling.ts
│   │   └── useConfirmAction.ts
│   ├── components/
│   │   ├── common/
│   │   ├── auth/
│   │   ├── avatar/
│   │   ├── persona/
│   │   ├── agent/
│   │   ├── task/
│   │   ├── memory/
│   │   └── audit/
│   ├── views/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── avatar/
│   │   ├── persona/
│   │   ├── agent/
│   │   ├── task/
│   │   ├── memory/
│   │   ├── audit/
│   │   ├── settings/
│   │   └── system/
│   ├── router/
│   │   └── index.ts
│   ├── plugins/
│   ├── styles/
│   └── utils/
├── public/
└── openapi/
```

## 3. OpenAPI 类型生成

- OpenAPI 文档是前端类型唯一来源。
- 生成命令的目标产物目录冻结为：`apps/web/src/types/generated/`。
- API 封装层只引用生成类型，不手写重复 DTO。
- 生成触发规则：
  1. API 合同冻结后首次生成。
  2. 接口字段或错误结构变更后重新生成。
  3. 合并前必须确认生成产物与合同一致。

## 4. 路由表

| 路由 | 页面组件 | 鉴权 | 主要数据来源 | 说明 |
|---|---|---|---|---|
| `/login` | `views/auth/LoginView.vue` | 匿名 | `POST /auth/login` | 登录入口 |
| `/` | `views/dashboard/DashboardView.vue` | 需要 | avatars + tasks + pending memories | 首页 / 工作台 |
| `/avatars` | `views/avatar/AvatarListView.vue` | 需要 | `GET /avatars` | Avatar 列表 |
| `/avatars/new` | `views/avatar/AvatarCreateView.vue` | 需要 | `POST /avatars` | 创建 Avatar |
| `/avatars/:avatarId` | `views/avatar/AvatarDetailView.vue` | 需要 | `GET /avatars/{avatarId}` + `PATCH /avatars/{avatarId}` | Avatar 详情与更新 |
| `/avatars/:avatarId/persona` | `views/persona/PersonaGenerateView.vue` | 需要 | persona generate + latest + list | Persona 生成与历史 |
| `/avatars/:avatarId/agents` | `views/agent/AgentManagementView.vue` | 需要 | agents list/create/update | Agent 管理 |
| `/tasks` | `views/task/TaskExecutionView.vue` | 需要 | task create + task detail | Task 执行 |
| `/memories/pending` | `views/memory/PendingMemoryView.vue` | 需要 | pending memories + confirm/reject | 候选记忆处理 |
| `/memories/search` | `views/memory/MemorySearchView.vue` | 需要 | memory search + detail | 记忆搜索 |
| `/audit` | `views/audit/AuditLogView.vue` | 需要 | audit list + detail | 审计日志 |
| `/settings` | `views/settings/SettingsView.vue` | 需要 | auth me + provider/privacy actions | 设置 |
| `/:pathMatch(.*)*` | `views/system/NotFoundView.vue` | 按路由守卫 | 无 | 404 |

## 5. 页面到 store / composable / api 映射

| 页面 | store | composable | api 模块 | 必备子组件 |
|---|---|---|---|---|
| LoginView | `auth.ts` | `useAuth` | `api/auth.ts` | `LoginForm` `AuthErrorAlert` |
| DashboardView | `avatar.ts` `task.ts` `memory.ts` | `usePagination` | `api/avatars.ts` `api/tasks.ts` `api/memories.ts` | `OnboardingGuide` `RecentTaskCard` `PendingMemoryCard` |
| AvatarListView | `avatar.ts` | `usePagination` | `api/avatars.ts` | `AvatarTable` `EmptyState` |
| AvatarCreateView | `avatar.ts` | `useConfirmAction` | `api/avatars.ts` | `AvatarForm` |
| AvatarDetailView | `avatar.ts` | `useConfirmAction` | `api/avatars.ts` | `AvatarDetailCard` `AvatarEditForm` |
| PersonaGenerateView | 可局部状态 + `avatar.ts` | `useConfirmAction` | `api/personas.ts` | `SampleInputPanel` `PersonaResultCard` `PersonaHistoryDrawer` |
| AgentManagementView | 可局部状态 | `useConfirmAction` | `api/agents.ts` | `AgentList` `AgentRoleForm` |
| TaskExecutionView | `task.ts` | `useTaskPolling` | `api/tasks.ts` | `TaskForm` `TaskStatusPanel` `TaskResultPanel` |
| PendingMemoryView | `memory.ts` | `useConfirmAction` | `api/memories.ts` | `PendingMemoryList` `DecisionDialog` |
| MemorySearchView | `memory.ts` | `usePagination` | `api/memories.ts` | `MemorySearchForm` `MemoryDetailDrawer` |
| AuditLogView | 可局部状态 | `usePagination` | `api/audit.ts` | `AuditFilterBar` `AuditTable` `AuditDetailDrawer` |
| SettingsView | `auth.ts` | `useConfirmAction` | `api/auth.ts` `api/privacy.ts` | `ProviderConfigForm` `PrivacyActionPanel` |

## 6. 全局状态项

### `auth` store
- `currentUser`
- `accessTokenState`
- `isAuthenticated`
- `loginLoading`
- `refreshLoading`

### `avatar` store
- `avatarList`
- `currentAvatar`
- `avatarPagination`
- `avatarLoading`

### `task` store
- `activeTask`
- `taskHistory`
- `taskPollingState`
- `taskError`

### `memory` store
- `pendingMemories`
- `memorySearchResult`
- `memoryDetail`
- `decisionLoading`

## 7. 页面状态机最低要求

### Persona 页面
- `idle`
- `source_ready`
- `generating`
- `generated`
- `failed`
- `blocked`

### Task 页面
- `idle`
- `creating`
- `pending`
- `running`
- `succeeded`
- `failed`
- `blocked`

### Pending Memory 页面
- `loading`
- `empty`
- `has_pending`
- `confirming`
- `rejecting`
- `error`

### Audit 页面
- `idle`
- `loading`
- `ready`
- `empty`
- `error`

## 8. 通用交互骨架

### 全局组件
- `AppLoadingOverlay`
- `AppErrorAlert`
- `AppEmptyState`
- `TraceIdBadge`
- `ConfirmActionDialog`
- `PolicyBlockedBanner`

### 统一规则
- 定义全局加载态。
- 定义全局错误提示。
- 定义空状态模板。
- 请求支持取消机制。
- 敏感确认操作增加二次确认。
- 被策略阻断时优先展示 `PolicyBlockedBanner`，同时暴露 `trace_id`。

## 9. API Client 约束

- `api/client.ts` 统一封装 Axios 实例、鉴权头、错误拦截、trace_id 透传。
- 401 时只允许单点刷新，避免并发重复刷新。
- 取消场景统一使用 `AbortController`。
- 所有列表查询统一走分页参数结构。

## 10. 脚手架生成要求

- 每个页面都必须能直接生成：route、view、api module、store/composable、子组件、Vitest 页面测试、Playwright 流程测试。
- 若无法回答“该页面用哪个 store、哪个 api 模块、有哪些状态、有哪些组件”，则前端规格未达 scaffold-ready。