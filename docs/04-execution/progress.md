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
- [x] 完整测试套件已实施并通过（后端 integration `13 passed`，web test/build passed），外部栈依赖用例按环境自动 skip
- [x] CI / E2E workflow 已加固：web 校验 OpenAPI 类型同步，HTTP E2E 覆盖真实主链路
- [x] Policy 安全规则已扩展并通过专项测试（敏感凭证导出、Bearer Token、私钥、云访问密钥）
- [x] Provider 选模逻辑已修复：live 模式不再误选 embedding-only Ollama tag，默认模型切换为 `qwen3.5:latest`
- [x] Provider 运行态可观测性已补强：`/health` 暴露 provider mode/status/model/version/chat_model_available/message，`/metrics` 同步暴露 provider 诊断字段，smoke/integration 断言保持一致
- [x] Provider 退化态诊断已补强：仅 embedding 模型或连接失败时返回可读 message，便于定位 live 环境问题
- [x] Audit 多租户隔离与隐私数据闭环已补强：审计列表/详情仅返回当前用户拥有资源，隐私导出覆盖 persona/agent/task/memory/audit，隐私删除同步清理关联审计记录
- [x] Avatar Growth Report 前端体验已落地：Dashboard / Avatar 详情页展示成长快照、已确认洞察、下一步推荐动作与证据口径，且只基于 confirmed memory 输出“已学会”结论
- [x] Avatar Growth Report 失败态与前端直测已补齐：工作区聚合失败时显式进入 failed 状态，不再在数据缺失时继续输出成长结论
- [x] Demo / Onboarding 首次体验已落地：Dashboard 新增分步引导、Demo Avatar 快速入口、按 user + avatar 持久化完成态，并要求跑通 Persona→Agent→Task→Memory 审核后才可结束引导
- [x] Docker 交付骨架真实产物已补齐：新增 `.dockerignore`、启动/停止脚本、备份/恢复脚本、live override 模板与 smoke 文件，部署文档已有实际文件落点
- [x] 前端路由守卫验收证据已补齐：新增 `tests/unit/web.spec.ts` 覆盖匿名访问受保护页面跳转登录、已登录访问 `/login` 跳转 Dashboard 与正常放行规则
- [x] 认证生命周期已做实：refresh token rotation、服务端 logout token 吊销、`/auth/me` 吊销校验、login/refresh/logout 审计闭环与前端后端联动测试均已通过

## 当前阶段

MVP 功能基本完备，核心闭环 + 主要辅助功能已全部落地。

- 整体交付完成度：98%
- 剩余未闭环项：仅剩 live provider 真机验收与 Docker Compose 真机联调，两项均受仓库外部运行环境阻塞

### 模块进度

| 模块 | 进度 | 说明 |
|---|---:|---|
| 根目录协作与治理文档 | 100% | 已完成并与当前仓库状态对齐 |
| 产品/架构/交付/评审文档体系 | 100% | 已补齐 Growth Report 亮点能力、Demo / Onboarding 首次体验与验收约束 |
| 后端主链路与审计/记忆能力 | 100% | 登录→Avatar→Persona→Agent→Task→Memory→Audit 已验证，隐私闭环与 auth refresh/logout/token revocation 也已补齐并通过 focused tests |
| 前端主链路与类型同步 | 100% | Web `check:types` / test / build 已全部通过，OpenAPI 生成产物已与当前后端合同重新同步；Dashboard / Avatar 详情已补齐 Avatar Growth Report 真实视图，并新增 Demo / Onboarding 分步引导、登出联动、avatar-scoped Persona/Agent 路由联动与路由守卫验收测试 |
| 仓库卫生与 GitHub 发布准备 | 98% | `.gitignore`、`.dockerignore`、命令可移植性与敏感数据排除已修复；已补 `.workbuddy/` / 根级 `node_modules/` 忽略与 README 发布口径收敛，待完成 `gh auth login`、配置 remote 并完成 push 验证 |
| Provider 可观测性与降级诊断 | 100% | 后端健康/指标/设置页诊断字段与 focused tests 已全部补齐 |
| Live Provider 最终验收 | 60% | 2026-04-11 再次确认当前环境无 Ollama 服务监听 `localhost:11434`，live 证据仍完全受外部环境阻塞 |
| Docker Compose 实机联调 | 72% | Compose 配置、`.dockerignore`、ops 脚本、smoke 文件与阻塞证据已齐备；2026-04-11 实机 `docker compose up --build -d` 因 Docker daemon 不可连接而失败 |

- 2026-04-12 已补齐前端路由入口联动：`App.vue` / `SidebarContent.vue` / `DashboardView.vue` / `AvatarDetailView.vue` / `GrowthReportCard.vue` 现统一优先跳转 avatar-scoped Persona / Agent 路由，并把 pending memory 入口统一收口到 `/memories/pending`
- 2026-04-12 前端路由守卫单测已扩展：`tests/unit/web.spec.ts` 新增覆盖 `/avatars/:avatarId/persona`、`/avatars/:avatarId/agents`、`/memories/pending` 的匿名拦截与登录放行语义
- 2026-04-12 前端完整测试再次通过：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run test -- --run` 结果 `11 passed`
- 2026-04-12 前端生产构建再次通过：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run build` 成功产出最新 bundle，仍仅保留 Vite chunk size warning
- 2026-04-12 仓库根后端 integration 再次通过：`python3 -m pytest /Users/hfy/Downloads/DigitalAvatar/tests/integration/test_api.py -v` 结果 `13 passed, 1 warning`，确认错误码映射修正未破坏主链路合同
- 后端完整测试已通过：`40 passed, 3 skipped, 1 warning`，其中 `test_compose_stack.py` 3 项因 Docker daemon 不可用自动 skip
- 2026-04-11 使用本地 API 包路径完成后端 integration 复核：`PYTHONPATH=/Users/hfy/Downloads/DigitalAvatar/apps/api python3 -m pytest /Users/hfy/Downloads/DigitalAvatar/tests/integration/test_api.py -v` 结果 `13 passed, 1 warning`
- 2026-04-11 为测试入口补齐本地 API 包优先级保护：新增 `tests/conftest.py` 先把 `apps/api` 插入 `sys.path`，避免从仓库根执行 `python3 -m pytest tests/integration/test_api.py -v` 时误命中本机已安装旧版 `app` 包；补后该命令已在仓库根重新通过（`13 passed, 1 warning`）
- 2026-04-11 冻结并验证 memory 合同：`/avatars/{id}/memories/search` 与 `/memories` 返回 `excerpt` 摘要分页，`/avatars/{id}/memories/pending` 与 `/avatars/{id}/memories/{memoryId}` 返回完整 `content`；同时修复 `apps/api/app/api/v1/avatar_memories.py` 中 `pending` 被动态 `{memory_id}` 路由吞掉的顺序问题
- 2026-04-11 前端完整测试再次通过：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run test -- --run` 结果 `11 passed`
- 2026-04-11 前端生产构建再次通过：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run build` 成功产出最新 bundle，仅保留 Vite chunk size warning，不阻断交付
- 2026-04-11 OpenAPI 类型同步校验再次触发真实合同差异：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run check:types` 失败原因为已生成产物与仓库旧版 schema 仍有 diff，差异集中在 logout header、avatar `PATCH`、agent detail path、memory page schema、avatar memory detail 与 task 时间字段
- 2026-04-11 OpenAPI 产物已重新生成：`apps/web/openapi/schema.json` 与 `apps/web/src/types/generated/openapi.ts` 已同步到当前后端合同（memory page schema / avatar memory detail / agent path / avatar patch / logout header）
- 2026-04-11 前端类型同步校验脚本已收口：`apps/web/package.json` 中 `check:types` 改为基于临时快照重生成并用 `cmp` 校验 `schema.json` / `openapi.ts` 是否漂移，避免再被仓库其他 diff 干扰；`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run check:types` 已重新通过
- 后端 focused tests 已通过：`19 passed`（provider unit + integration + app smoke），覆盖 provider `base_url` / version / message / chat model availability 诊断字段
- 前端 provider readiness focused tests 已通过：`3 passed`
- 后端 focused auth tests 已通过：`3 passed`，覆盖 refresh token rotation、logout access/refresh token 吊销、auth 审计写入
- 前端 focused auth/onboarding/workspace tests 已通过：`8 passed`（`auth.spec.ts`、`workspace.spec.ts`、`onboarding.spec.ts`）
- 前端路由守卫单测已通过：`tests/unit/web.spec.ts` 共 `3 passed`
- 前端生产构建已通过：`npm --prefix apps/web run build`
- 新增隐私/审计专项集成测试已通过：`10 passed, 1 warning`，覆盖审计日志按当前用户隔离、隐私导出包含 persona/agent/task/memory/audit、隐私删除同步清理关联审计记录
- 已新增 `.gitignore`，排除 `.venv/`、`data/*.db`、`apps/web/node_modules/`、`apps/web/dist/`、`apps/api/build/`、Claude 本地状态等，避免上传 GitHub 时带入个人或运行时文件
- 2026-04-10 继续补强仓库发布卫生：新增根级 `node_modules/` 与 `.workbuddy/` 忽略规则，避免本地工具状态继续污染发布面
- 新增 `.dockerignore`，排除 `.git`、`.claude`、`.venv`、`node_modules`、构建产物与本地数据库，降低 Compose 构建上下文污染与敏感数据入镜像风险
- README 中本机绝对路径已移除，改为可移植命令
- 前端新增 Avatar Growth Report 验证通过：`npm --prefix apps/web run test -- --run` 与 `npm --prefix apps/web run build` 通过，Dashboard / Avatar 详情页均已接入成长报告组件
- 前端新增 Growth Report 失败态验证：`workspace.spec.ts` 覆盖 confirmed memory 成功聚合与 workspace load 失败降级，保证数据缺失时不继续输出成长结论
- 前端新增 Demo / Onboarding 验证通过：`onboarding.spec.ts` 校验 storage key、Demo 常量与完成条件，`DashboardView` 已接入 Demo Avatar 快速入口与按 user + avatar 持久化的新手引导完成态
- Docker 交付脚本已校验：`dev-up.sh` / `dev-down.sh` / `backup-db.sh` / `restore-db.sh` 通过 `bash -n`，Compose 默认配置与 live override 均可被 `docker compose config` 成功渲染
- 2026-04-11 Docker 实机拉起再次验证失败：`docker compose -f /Users/hfy/Downloads/DigitalAvatar/deploy/docker/docker-compose.yml up --build -d` 返回 `Cannot connect to the Docker daemon at unix:///Users/hfy/.orbstack/run/docker.sock`，当前仅能据实保留配置渲染、脚本校验与 smoke skip 证据
- 2026-04-11 仓库根执行 smoke 入口再次通过：`python3 -m pytest /Users/hfy/Downloads/DigitalAvatar/tests/smoke/test_app_smoke.py -v` 结果 `1 passed, 1 warning`，说明新增 `tests/conftest.py` 后测试入口与本地 API 源码解析保持一致
- 2026-04-11 仓库根后端 integration 再次稳定通过：`python3 -m pytest /Users/hfy/Downloads/DigitalAvatar/tests/integration/test_api.py -v` 结果 `13 passed, 1 warning`，确认不再依赖显式 `PYTHONPATH` 也能命中仓库内最新 API 源码
- 2026-04-11 前端验证矩阵再次通过：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run test -- --run` 结果 `11 passed`，`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run build` 成功产出最新 bundle，仍仅保留 Vite chunk size warning
- 2026-04-11 OpenAPI 类型同步校验再次通过：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run check:types` 可稳定重生成并校验 `openapi/schema.json` 与 `src/types/generated/openapi.ts` 无漂移
- 2026-04-11 Compose 配置再次渲染成功：`docker compose -f /Users/hfy/Downloads/DigitalAvatar/deploy/docker/docker-compose.yml config` 已输出完整 `api/web/worker/ollama` 服务矩阵，说明交付脚手架仍保持可渲染状态
- 2026-04-11 Docker 实机终验再次复核失败：`docker compose -f /Users/hfy/Downloads/DigitalAvatar/deploy/docker/docker-compose.yml up --build -d` 仍返回 `Cannot connect to the Docker daemon at unix:///Users/hfy/.orbstack/run/docker.sock`，说明阻塞仍完全来自本机 Docker daemon 不可用
- Compose smoke 已具备可执行用例：`tests/smoke/test_compose_stack.py` 当前因本机未运行 Docker daemon 自动 skip；除 `/health` 与首页壳外，已新增对前端构建产物中 onboarding 关键标识的断言；应用内 smoke `test_app_smoke.py` 通过（`1 passed`）
- 2026-04-10 再次复核 live provider 阻塞：`ollama --version` 为 `0.1.28`，`/api/version` 返回 `0.1.28`，`/api/tags` 仅有 embedding 模型 `bge-m3:latest`，执行 `ollama pull qwen3.5:latest` 明确返回 manifest 412（需升级 Ollama）
- 2026-04-11 live provider 就绪性再次复核失败：`curl -fsS http://localhost:11434/api/tags` 无法连接，说明当前会话不存在可达 Ollama 服务，live provider 最终验收继续受外部环境阻塞
- 2026-04-11 外部阻塞终验再次复核：`curl -fsS http://localhost:11434/api/tags` 继续返回连接失败，`docker compose up --build -d` 继续被 Docker daemon 不可连接阻塞，确认项目剩余问题仍全部位于仓库外部运行环境
- 2026-04-12 部署交付外部环境证据已再次刷新：`docker compose -f /Users/hfy/Downloads/DigitalAvatar/deploy/docker/docker-compose.yml config` 仍可成功渲染完整 `api/web/worker/ollama` 服务矩阵，`deploy/docker/ops/scripts/*.sh` 语法校验通过；但 `curl -fsS http://localhost:11434/api/tags` 继续连接失败，`docker compose ... up --build -d` 继续报 `Cannot connect to the Docker daemon at unix:///Users/hfy/.orbstack/run/docker.sock`，说明剩余阻塞仍全部位于仓库外运行环境
- 2026-04-12 avatar-scoped Persona 路由闭环已补齐：`PersonaView.vue` / `AgentView.vue` 现统一优先解析 `route.params.avatarId`，`workspace.ts` 的 `activatePersona` 已支持显式 avatar 上下文并在激活后重载对应工作区，focused web tests 与 `npm run build` 已重新通过
- 2026-04-12 前端完整测试再次通过：`npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run test -- --run` 结果 `11 passed`
- 2026-04-12 后端源码 compile check 通过：`cd /Users/hfy/Downloads/DigitalAvatar/apps/api && python3 -m compileall app` 完成，无编译错误
- 当前剩余主阻塞为外部环境：本机 Ollama `0.1.28` 仅有 `bge-m3:latest`，尚无可聊天 Qwen3.5 模型；仓库默认模型引用已统一收敛到 `qwen3.5:latest`；Docker daemon 当前不可连接 `unix:///Users/hfy/.orbstack/run/docker.sock`，待外部运行环境恢复后即可继续补 Docker 实机联调证据

## 主要风险

- Provider live 模式最终验收仍依赖本机 Ollama 升级并成功拉取 Qwen3 / Qwen3.5；2026-04-10 实测 `ollama pull qwen3.5:latest` 仍被 412 拒绝
- Docker Compose 最终启动证据仍受外部 Docker daemon 阻塞；待运行环境恢复后，基于现有 Compose/ops 产物补实机验证
