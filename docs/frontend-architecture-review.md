# Digital Avatar 前端架构与设计评审报告

> **评审版本**: V12
> **评审日期**: 2026-04-08
> **评审视角**: 前端架构师 / 资深前端专家
> **文档状态**: 正式评审报告

---

## 1. 前端技术栈评审

### 1.1 技术选型总评

| 技术选型 | 评分 | 评价 |
|---------|------|------|
| Vue 3 | ⭐⭐⭐⭐⭐ | 成熟稳定，Composition API 契合现代前端开发模式 |
| Vite | ⭐⭐⭐⭐⭐ | 构建速度快，开发体验优秀，与 Vue 3 生态深度集成 |
| TypeScript (strict) | ⭐⭐⭐⭐⭐ | 类型安全是大型项目的基石，strict 模式是正确选择 |
| Element Plus | ⭐⭐⭐⭐ | 企业级组件库，但建议补充轻量级替代方案评估 |

### 1.2 技术栈优势分析

**✅ 优点：**

1. **Vue 3 + Composition API**
   - 契合设计方案中"页面状态与领域对象解耦"的要求
   - Composition API 的 `setup()` 语法天然支持组件逻辑复用
   - 与 TypeScript 的集成日趋成熟（Vue 3.4+ 改进显著）

2. **Vite**
   - 开发服务器启动时间从秒级降至毫秒级
   - 内置 TypeScript 支持，无需额外配置
   - 热模块替换（HMR）体验优秀，提升开发效率

3. **TypeScript strict 模式**
   - 设计方案中的选择非常正确，建议启用以下规则：
     - `strictNullChecks`: 防止 null/undefined 访问错误
     - `noImplicitAny`: 强制显式类型声明
     - `strictPropertyInitialization`: 属性必须初始化
     - `noUnusedLocals` / `noUnusedParameters`: 消除死代码

4. **Element Plus**
   - 企业级组件库，表单项、对话框、数据表格完备
   - 社区活跃，文档完善
   - 与 Vue 3 深度集成

### 1.3 可改进点与风险

**⚠️ 可改进点：**

1. **Element Plus 的体积问题**
   - Element Plus 默认包体积约 300KB+，影响首屏加载
   - **建议**：配置 Vite 的按需导入（unplugin-vue-components）
   - **备选方案**：考虑 Naive UI（更轻量，类型支持更好）或 UnoCSS + Headless UI 组合

2. **Pinia 状态管理未明确**
   - 设计方案未提及状态管理方案
   - **建议**：明确使用 Pinia（Vue 3 官方推荐），而非 Vuex
   - Pinia 体积更小，TypeScript 支持更好

3. **路由方案未明确**
   - 设计方案未指定 Vue Router 版本或路由管理策略
   - **建议**：使用 Vue Router 4.x，并制定路由懒加载规范

4. **HTTP Client 未明确**
   - 设计方案未指定 Axios / Fetch / ky 等 HTTP 客户端
   - **建议**：统一使用 Axios（拦截器、错误处理更完善）或 ky（更现代）

### 1.4 技术选型建议汇总

| 类别 | 当前方案 | 建议方案 | 理由 |
|------|----------|----------|------|
| 状态管理 | 未明确 | **Pinia** | Vue 3 官方推荐，TS 支持好 |
| 路由 | 未明确 | **Vue Router 4.x** + 懒加载 | 标准方案，与构建工具集成 |
| HTTP 客户端 | 未明确 | **Axios** 或 **ky** | 拦截器、类型支持 |
| UI 组件库 | Element Plus | Element Plus + 按需导入 | 企业级可用，按需导入优化体积 |

---

## 2. 页面设计评审

### 2.1 页面范围评估

设计方案定义了 7 个 MVP 页面：

| 序号 | 页面名称 | 优先级 | 完整性 | 建议 |
|------|----------|--------|--------|------|
| 1 | 首页 / 工作台 | ⭐⭐⭐⭐⭐ | 需补充 | 建议增加快捷操作入口、任务状态概览 |
| 2 | 分身创建页 | ⭐⭐⭐⭐⭐ | 完整 | - |
| 3 | Persona 生成页 | ⭐⭐⭐⭐⭐ | 完整 | - |
| 4 | 任务执行页 | ⭐⭐⭐⭐⭐ | 需补充 | 建议增加任务历史、执行日志展示 |
| 5 | 候选记忆确认页 | ⭐⭐⭐⭐⭐ | 需补充 | 建议增加批量操作、记忆详情查看 |
| 6 | 审计查看页 | ⭐⭐⭐⭐ | 需补充 | 建议增加筛选、导出能力 |
| 7 | 设置页 | ⭐⭐⭐ | 需补充 | 建议明确设置项范围 |

### 2.2 缺失页面建议

**🔴 建议新增页面：**

1. **登录/认证页** (优先级：⭐⭐⭐⭐⭐)
   - 当前方案未涉及用户认证
   - 即使 MVP 简化认证，也需要登录入口
   - 建议：先做简化版（简单密码或 token 模式）

2. **分身管理列表页** (优先级：⭐⭐⭐⭐⭐)
   - 支撑多分身管理
   - 分身切换、编辑、删除操作

3. **子代理管理页** (优先级：⭐⭐⭐⭐)
   - Agent 创建、编辑、启用/停用
   - 权限配置界面

4. **记忆详情页** (优先级：⭐⭐⭐⭐)
   - 单条记忆的完整查看
   - 关联的任务、来源追溯

5. **404 / 错误页** (优先级：⭐⭐⭐)
   - 提升用户体验
   - 错误恢复引导

### 2.3 页面优先级建议

```
P0 - 必须完成（MVP 核心闭环）
├── 首页 / 工作台
├── 分身创建页
├── Persona 生成页
├── 任务执行页
└── 候选记忆确认页

P1 - 应该完成（体验完整性）
├── 登录页
├── 分身管理列表页
├── 子代理管理页
├── 审计查看页
└── 记忆详情页

P2 - 建议完成（体验优化）
├── 设置页
├── 404 / 错误页
└── 国际化支持（预留）
```

### 2.4 页面间跳转流程建议

```
用户登录
    ↓
首页/工作台 ←→ 分身列表
    ↓
创建分身 → Persona生成 → 创建子代理 → 任务执行 → 记忆确认
    ↓
审计查看 ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
    ↓
设置页
```

---

## 3. 前端架构评审

### 3.1 整体架构评估

设计方案的前端规范：
> 1. TypeScript strict 模式
> 2. API 类型自动生成或集中维护
> 3. 页面状态与领域对象解耦
> 4. 组件按页面域拆分

**✅ 优点：**
- 规范清晰，与后端 API 契约对齐
- "页面状态与领域对象解耦"是正确方向
- "组件按页面域拆分"避免组件库膨胀

### 3.2 推荐前端架构方案

#### 3.2.1 分层架构设计

```
src/
├── api/                    # API 层：HTTP 请求封装、接口调用
│   ├── client.ts          # Axios 实例配置
│   ├── avatar.ts          # Avatar API
│   ├── agent.ts           # Agent API
│   ├── task.ts            # Task API
│   ├── memory.ts          # Memory API
│   ├── policy.ts          # Policy API
│   ├── audit.ts           # Audit API
│   └── module.ts          # Module API
│
├── types/                  # 类型定义层：统一类型管理
│   ├── api.d.ts          # API 请求/响应类型
│   ├── domain.d.ts       # 领域对象类型
│   └── index.d.ts        # 全局类型声明
│
├── stores/                 # 状态管理层
│   ├── avatar.ts         # Avatar 状态
│   ├── agent.ts          # Agent 状态
│   ├── task.ts           # Task 状态
│   ├── memory.ts         # Memory 状态
│   └── ui.ts             # UI 状态（模态框、侧边栏等）
│
├── composables/            # 组合式函数层
│   ├── useAvatar.ts      # Avatar 相关逻辑
│   ├── useTask.ts        # Task 相关逻辑
│   ├── useLoading.ts     # 加载状态管理
│   └── useError.ts       # 错误处理
│
├── components/             # 组件层
│   ├── common/           # 通用组件
│   │   ├── AppHeader.vue
│   │   ├── AppSidebar.vue
│   │   ├── DataTable.vue
│   │   └── ConfirmDialog.vue
│   │
│   └── domain/           # 领域组件
│       ├── avatar/
│       ├── task/
│       └── memory/
│
├── views/                  # 页面层
│   ├── HomeView.vue
│   ├── avatar/
│   ├── task/
│   ├── memory/
│   ├── audit/
│   └── settings/
│
├── router/                 # 路由层
│   ├── index.ts
│   └── guards.ts          # 路由守卫
│
├── utils/                  # 工具层
│   ├── format.ts
│   ├── validation.ts
│   └── storage.ts
│
└── App.vue
```

#### 3.2.2 API 类型管理建议

**方案一：手动维护（适合 MVP）**

```typescript
// types/api/avatar.ts
export interface CreateAvatarRequest {
  name: string;
  description?: string;
}

export interface CreateAvatarResponse {
  id: string;
  name: string;
  status: 'active' | 'inactive';
}

export interface AvatarDetailResponse {
  id: string;
  user_id: string;
  name: string;
  description: string;
  status: string;
  profile_version: number;
  created_at: string;
  updated_at: string;
}
```

**方案二：OpenAPI 自动生成（推荐，团队协作更好）**

使用 `openapi-typescript` 从后端 OpenAPI 文档自动生成类型：

```bash
npm install -D openapi-typescript
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api-generated.ts
```

#### 3.2.3 状态管理方案（Pinia）

```typescript
// stores/avatar.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { AvatarDetailResponse } from '@/types/api';

export const useAvatarStore = defineStore('avatar', () => {
  // State
  const currentAvatar = ref<AvatarDetailResponse | null>(null);
  const avatars = ref<AvatarDetailResponse[]>([]);
  const isLoading = ref(false);

  // Actions
  async function fetchAvatar(avatarId: string) {
    isLoading.value = true;
    try {
      const response = await avatarApi.getAvatar(avatarId);
      currentAvatar.value = response.data;
      return response.data;
    } finally {
      isLoading.value = false;
    }
  }

  async function createAvatar(data: CreateAvatarRequest) {
    isLoading.value = true;
    try {
      const response = await avatarApi.createAvatar(data);
      avatars.value.push(response.data);
      return response.data;
    } finally {
      isLoading.value = false;
    }
  }

  return { currentAvatar, avatars, isLoading, fetchAvatar, createAvatar };
});
```

### 3.3 可改进点

**⚠️ 架构层面改进建议：**

1. **API 类型管理未明确机制**
   - 建议：明确使用 OpenAPI 自动生成，避免手写类型与后端不一致

2. **错误处理机制未定义**
   - 建议：统一封装 HTTP 错误处理，建立全局错误拦截器

3. **请求取消机制未提及**
   - 场景：用户快速切换 Tab 时，前一个请求仍会执行
   - 建议：使用 Axios 的 AbortController 或请求队列

4. **数据持久化策略未定义**
   - 场景：刷新页面后状态丢失
   - 建议：使用 localStorage / sessionStorage 持久化关键状态

---

## 4. 用户体验评审

### 4.1 核心用户流程分析

#### 4.1.1 分身创建 → Persona 生成 → 任务执行 → 记忆确认

**✅ 优点：**
- 流程清晰，符合设计方案中的"核心闭环"
- 步骤之间有明确的依赖关系

**⚠️ 改进建议：**

1. **步骤引导优化**
   - 建议增加进度指示器（Stepper）
   - 每步完成后显示完成状态

2. **任务执行页的实时反馈**
   - 建议增加 SSE/WebSocket 实时接收任务状态
   - 当前轮询方案对用户不友好

3. **记忆确认页的批量操作**
   - 候选记忆可能有多条
   - 建议支持批量确认/拒绝
   - 建议支持快捷键操作

### 4.2 加载与错误状态设计

| 场景 | 当前状态 | 建议改进 |
|------|----------|----------|
| API 请求中 | 未定义 | 骨架屏 + 加载指示器 |
| 网络错误 | 未定义 | 友好错误提示 + 重试按钮 |
| 任务执行中 | 未定义 | 进度条 + 实时状态 |
| 表单验证失败 | 未定义 | 行内错误提示 |
| 空状态 | 未定义 | 空状态插画 + 引导操作 |

### 4.3 响应式设计建议

- **目标设备**：桌面端为主（控制台场景）
- **建议断点**：
  - Desktop: ≥ 1280px
  - Tablet: 768px - 1279px
  - Mobile: < 768px（MVP 可简化）

### 4.4 可访问性（a11y）建议

| 维度 | 建议 |
|------|------|
| 键盘导航 | 所有交互元素支持 Tab 聚焦 |
| ARIA 标签 | 按钮、表单元素添加 aria-label |
| 颜色对比度 | 符合 WCAG AA 标准（4.5:1） |
| 焦点管理 | 模态框打开/关闭时焦点管理 |
| 屏幕阅读器 | 动态内容更新使用 aria-live |

---

## 5. 代码质量评审

### 5.1 TypeScript strict 模式评估

**✅ 优点：**
- 强制类型安全，减少运行时错误
- 提升代码可维护性
- IDE 支持更好

**📋 建议启用的 strict 规则：**

```json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "strictPropertyInitialization": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### 5.2 代码组织规范

**✅ 当前规范合理：**
- "API 类型自动生成或集中维护" → 建议使用 OpenAPI 生成
- "页面状态与领域对象解耦" → 符合分层架构原则
- "组件按页面域拆分" → 避免组件膨胀

**📋 补充建议：**

1. **命名规范**
   - 组件文件：PascalCase（如 `AvatarCard.vue`）
   - 工具函数：camelCase（如 `formatDate.ts`）
   - 常量：UPPER_SNAKE_CASE
   - 类型/接口：PascalCase，以 `I` 开头或语义化命名

2. **目录规范**
   - `composables/` 用于业务逻辑复用
   - `utils/` 用于纯函数工具
   - 禁止在 `utils/` 中调用 API 或操作状态

3. **注释规范**
   - 公共函数必须 JSDoc 注释
   - 复杂逻辑添加行内注释
   - 重要决策记录注释原因

### 5.3 代码复用机制

| 复用方式 | 适用场景 | 建议 |
|----------|----------|------|
| Composables | 业务逻辑复用 | 优先使用 |
| Mixins | Vue 2 迁移场景 | MVP 不推荐 |
| 高阶组件 | 逻辑增强 | 谨慎使用 |
| Slots | UI 定制 | 优先使用 |

### 5.4 代码质量检查工具

| 工具 | 用途 | 配置建议 |
|------|------|----------|
| ESLint | 代码风格检查 | extends: ['plugin:vue/vue3-recommended', '@vue/ts/recommended'] |
| Prettier | 代码格式化 | 与 ESLint 集成，统一格式化 |
| TypeScript | 类型检查 | strict 模式 |
| husky + lint-staged | Git Hooks | 提交前检查 |
| Vitest | 单元测试 | 组件测试、Composable 测试 |

---

## 6. 性能与安全评审

### 6.1 前端性能考虑

#### 6.1.1 首屏加载优化

| 优化项 | 方案 | 优先级 |
|--------|------|--------|
| 代码分割 | Vite 路由懒加载 | P0 |
| 组件懒加载 | `defineAsyncComponent` | P0 |
| UI 库按需导入 | unplugin-vue-components | P0 |
| 图片优化 | WebP 格式、懒加载 | P1 |
| Gzip 压缩 | Vite build.targets | P1 |
| 预加载关键资源 | `<link rel="preload">` | P2 |

#### 6.1.2 运行时性能

| 优化项 | 方案 | 优先级 |
|--------|------|--------|
| 虚拟滚动 | 长列表使用 vue-virtual-scroller | P1 |
| 防抖/节流 | 用户输入、搜索框 | P1 |
| Memoization | 复杂计算使用 computed | P1 |
| 长任务拆分 | Web Worker 或 requestIdleCallback | P2 |

#### 6.1.3 性能指标建议

| 指标 | 目标值 | 说明 |
|------|--------|------|
| FCP | < 1.8s | First Contentful Paint |
| LCP | < 2.5s | Largest Contentful Paint |
| FID | < 100ms | First Input Delay |
| CLS | < 0.1 | Cumulative Layout Shift |
| 首屏 JS Bundle | < 200KB (gzip) | 初始加载 JS 大小 |

### 6.2 安全性考虑

#### 6.2.1 XSS 防护

| 风险点 | 防护方案 | 实现方式 |
|--------|----------|----------|
| 用户输入 | Vue 默认自动转义 | 确保使用模板插值而非 v-html |
| 富文本渲染 | DOMPurify 净化 | 对必要内容使用 |
| 第三方脚本 | CSP (Content Security Policy) | HTTP 响应头配置 |

**✅ 方案优势：** Vue 3 默认启用 HTML 转义，天然防护 XSS。

#### 6.2.2 CSRF 防护

| 风险点 | 防护方案 | 实现方式 |
|--------|----------|----------|
| API 请求 | CSRF Token | Axios 拦截器自动添加 |
| SameSite Cookie | SameSite=Lax/Strict | 后端设置 |

**⚠️ 建议：**
- Axios 请求拦截器自动添加 CSRF Token
- 敏感操作（如删除、确认）增加二次确认

#### 6.2.3 敏感数据处理

| 数据类型 | 处理方式 | 说明 |
|----------|----------|------|
| 用户凭证 | HttpOnly Cookie | 禁止 JavaScript 访问 |
| API Token | 内存存储 | 不持久化到 localStorage |
| 敏感配置 | 环境变量 | VITE_ 前缀暴露给前端 |
| 日志脱敏 | 前端脱敏 | 审计日志中敏感字段掩码 |

#### 6.2.4 安全工具链

| 工具 | 用途 | 集成方式 |
|------|------|----------|
| Snyk | 依赖安全扫描 | CI 集成 |
| npm audit | 依赖漏洞检查 | pre-commit hook |
| CSP | 内容安全策略 | Nginx / 后端配置 |

---

## 7. 开发效率评审

### 7.1 开发工具链

| 工具类别 | 推荐工具 | 说明 |
|----------|----------|------|
| 包管理 | pnpm | 速度快，节省磁盘 |
| IDE | VS Code / WebStorm | TypeScript 支持好 |
| 调试 | Vue DevTools | 状态调试 |
| API 测试 | Postman / Insomnia | 前后端联调 |
| CI/CD | GitHub Actions | 与 GitHub 集成 |

### 7.2 开发体验优化

**✅ 已有优势：**
- Vite 的 HMR 体验优秀
- TypeScript + Vue 3.4+ 的类型推断改进显著

**📋 补充建议：**

1. **Mock Server**
   - 使用 MSW (Mock Service Worker) 或 json-server
   - 与后端并行开发

2. **开发服务器配置**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     server: {
       port: 3000,
       proxy: {
         '/api': {
           target: 'http://localhost:8000',
           changeOrigin: true
         }
       }
     }
   })
   ```

3. **环境变量管理**
   ```
   .env                # 默认
   .env.local          # 本地覆盖（不提交）
   .env.development    # 开发环境
   .env.production     # 生产环境
   ```

### 7.3 组件复用性评估

| 组件类型 | 复用性 | 建议 |
|----------|--------|------|
| 通用组件（Button, Input） | 高 | Element Plus 已提供 |
| 业务组件（AvatarCard, TaskItem） | 中 | 抽取为独立组件 |
| 页面组件 | 低 | 按业务定制 |

### 7.4 UI 组件库选型对比

| 组件库 | 体积 | TypeScript | 适用场景 | 评分 |
|--------|------|------------|----------|------|
| Element Plus | ~350KB | 完整 | 企业中后台 | ⭐⭐⭐⭐ |
| Naive UI | ~200KB | 完整 | 企业中后台 | ⭐⭐⭐⭐⭐ |
| Ant Design Vue | ~400KB | 完整 | 企业级复杂应用 | ⭐⭐⭐⭐ |
| Headless UI | ~50KB | 完整 | 定制化项目 | ⭐⭐⭐ |
| UnoCSS + 自建 | 按需 | 完整 | 轻量项目 | ⭐⭐⭐ |

**结论：** Element Plus 的选择合理，但建议配置按需导入。

---

## 8. 风险评估与缓解措施

### 8.1 高风险项

| 风险项 | 风险等级 | 影响 | 缓解措施 |
|--------|----------|------|----------|
| 前端状态与后端类型不一致 | 高 | 运行时错误 | 使用 OpenAPI 自动生成类型 |
| API 响应慢导致用户体验差 | 高 | 用户流失 | 添加骨架屏、错误重试 |
| 页面状态丢失（刷新） | 中 | 用户体验 | 实现状态持久化 |
| Element Plus 按需导入配置错误 | 中 | 包体积过大 | 查阅官方按需导入配置 |

### 8.2 中风险项

| 风险项 | 风险等级 | 影响 | 缓解措施 |
|--------|----------|------|----------|
| 多人协作时代码风格不一致 | 中 | 代码可读性 | ESLint + Prettier 强制规范 |
| 组件库版本升级 Breaking Change | 低 | 升级成本 | 锁定版本，定期升级 |
| 移动端体验不佳 | 低 | 特殊用户 | MVP 聚焦桌面端 |

---

## 9. 总结与优先级建议

### 9.1 总体评价

| 维度 | 评分 | 说明 |
|------|------|------|
| 技术栈选择 | ⭐⭐⭐⭐⭐ | Vue 3 + Vite + TS 是成熟可靠的选择 |
| 页面设计 | ⭐⭐⭐⭐ | 基本覆盖 MVP 需求，需补充部分页面 |
| 架构规范 | ⭐⭐⭐⭐ | 分层合理，需补充状态管理方案 |
| 用户体验 | ⭐⭐⭐ | 核心流程清晰，需细化交互设计 |
| 代码质量 | ⭐⭐⭐⭐ | TypeScript strict 模式保障质量 |
| 性能安全 | ⭐⭐⭐ | 需补充安全防护配置 |
| 开发效率 | ⭐⭐⭐⭐ | 工具链完善，开发体验好 |

### 9.2 改进优先级排序

| 优先级 | 改进项 | 工作量 | 价值 |
|--------|--------|--------|------|
| P0 | 明确状态管理方案（Pinia） | 低 | 高 |
| P0 | 补充登录/认证页 | 中 | 高 |
| P0 | 补充分身管理列表页 | 中 | 高 |
| P0 | 配置 UI 库按需导入 | 低 | 高 |
| P1 | 任务执行页 SSE 实时状态 | 高 | 中 |
| P1 | API 类型自动生成机制 | 中 | 高 |
| P1 | 全局错误处理与加载态 | 中 | 高 |
| P1 | 安全防护（CSRF、XSS） | 低 | 中 |
| P2 | 响应式设计优化 | 中 | 中 |
| P2 | 可访问性改进 | 中 | 低 |
| P2 | 性能监控集成 | 中 | 中 |

### 9.3 最终建议

1. **立即行动**
   - 明确使用 Pinia 作为状态管理
   - 使用 pnpm 作为包管理器
   - 配置 Element Plus 按需导入
   - 建立 API 类型生成机制

2. **48小时内完成**
   - 补充缺失页面（登录、分身列表）
   - 实现核心流程的 UI
   - 配置全局错误处理

3. **Beta 版本考虑**
   - 响应式设计完善
   - 移动端适配
   - 国际化支持
   - 性能监控与优化

---

## 附录：前端技术规范速查表

### A. TypeScript 配置

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "strictNullChecks": true,
    "strictPropertyInitialization": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### B. Vite 配置

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [ElementPlusResolver()]
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

### C. 目录结构建议

```
web/
├── public/
├── src/
│   ├── api/
│   ├── assets/
│   ├── components/
│   ├── composables/
│   ├── router/
│   ├── stores/
│   ├── types/
│   ├── utils/
│   ├── views/
│   ├── App.vue
│   └── main.ts
├── tests/
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
└── .env
```

---

**评审结论：**

设计方案的前端技术栈选择合理、整体架构方向正确，但需要补充以下关键内容：
1. 明确状态管理方案（Pinia）
2. 补充缺失页面定义
3. 建立 API 类型生成机制
4. 细化交互设计与错误处理规范

建议在正式开发前，将本评审报告的 P0 改进项纳入设计方案的细化版本中。
