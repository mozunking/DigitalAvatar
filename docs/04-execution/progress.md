# 总进展

## 当前状态

- [x] 根目录 GitHub 风格文档已建立
- [x] docs 目录骨架已建立
- [x] 后端 API 骨架已提交（FastAPI + SQLAlchemy + JWT）
- [x] 前端骨架已提交（Vue 3 + Vite + Element Plus + Pinia）
- [x] 用户注册 API 已实现
- [x] Provider 模式显式化（mock / live / degraded），取消静默假绿 fallback
- [x] 隐私导出/删除接口已实现
- [x] 主链路已验证（登录→注册→创建Avatar→Agent→执行Task→记忆捕获→审计日志）
- [x] 中英文切换功能（vue-i18n + Element Plus 国际化）
- [x] API 路径修正为规范格式（/avatars/{id}/persona/generate, /avatars/{id}/agents）
- [x] Memory 搜索接口（/avatars/{id}/memories/search + pending）
- [x] Audit 接口增加过滤参数（trace_id, resource_type, start_at, end_at + 分页）
- [x] 统一错误码结构（ErrorResponse 在所有异常中使用）
- [x] 审计日志自动写入（Avatar 创建、Task 执行、策略/状态流转）
- [x] 前端 Memory 搜索页面 + 详情抽屉
- [x] 前端 Persona 激活/历史版本功能
- [x] 前端 Audit 页面过滤器 + 分页
- [x] 前端全局错误处理（401 自动续期 + 403/429/5xx 提示）
- [x] 前端 Token 自动刷新
- [x] Task 异步状态流转与轮询语义已实现
- [x] 完整测试套件已实施并通过（28 passed, web test/build passed），外部栈依赖用例按环境自动 skip
- [x] CI / E2E workflow 已加固：web 校验 OpenAPI 类型同步，HTTP E2E 覆盖真实主链路
- [x] Policy 安全规则已扩展并通过专项测试（敏感凭证导出、Bearer Token、私钥、云访问密钥）
- [x] Provider 选模逻辑已修复：live 模式不再误选 embedding-only Ollama tag，默认模型切换为 `qwen3.5:7b-instruct-q4_0`
- [x] Provider 运行态可观测性已补强：`/health` 暴露 provider mode/status/model/version/chat_model_available/message，`/metrics` 同步暴露 provider 诊断字段，smoke/integration 断言保持一致
- [x] Provider 退化态诊断已补强：仅 embedding 模型或连接失败时返回可读 message，便于定位 live 环境问题
- [ ] Provider live 模式验收仍需本机 Ollama 升级并补最终证据

## 当前阶段

MVP 功能基本完备，核心闭环 + 主要辅助功能已全部落地。

### 模块进度

| 模块 | 进度 | 说明 |
|---|---:|---|
| 根目录协作与治理文档 | 100% | 已完成并与当前仓库状态对齐 |
| 产品/架构/交付/评审文档体系 | 100% | 已补齐 Growth Report 亮点能力与验收约束 |
| 后端主链路与审计/记忆能力 | 100% | 登录→Avatar→Persona→Agent→Task→Memory→Audit 已验证 |
| 前端主链路与类型同步 | 100% | Web 测试与 build 已通过，OpenAPI 同步已加固 |
| 仓库卫生与 GitHub 发布准备 | 90% | `.gitignore` 与命令可移植性已修复，待完成最终 commit/push 验证 |
| Provider 可观测性与降级诊断 | 95% | 代码与测试已补齐，live 最终环境证据待补 |
| Live Provider 最终验收 | 60% | 受本机 Ollama 0.1.28 + 无 chat 模型阻塞 |
| Docker Compose 实机联调 | 35% | 配置和文档已在位，按范围延后实机验证 |

### 最新验证

- 后端 focused tests 已通过：`17 passed`（provider unit + integration + smoke）
- 已新增 `.gitignore`，排除 `.venv/`、`data/*.db`、`apps/web/node_modules/`、`apps/web/dist/`、`apps/api/build/`、Claude 本地状态等，避免上传 GitHub 时带入个人或运行时文件
- README 中本机绝对路径已移除，改为可移植命令
- 当前剩余主阻塞为外部环境：本机 Ollama `0.1.28` 仅有 `bge-m3:latest`，尚无可聊天 Qwen3.5 模型

## 主要风险

- Provider live 模式最终验收仍依赖本机 Ollama 升级并成功拉取 Qwen3 / Qwen3.5
- Docker Compose 部署尚未实际验证
