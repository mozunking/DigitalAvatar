# 迭代日志

## Iteration 1
- 基于 V14 与评审意见搭建 GitHub 风格文档体系。
- 完成治理、产品、架构、交付、执行、评审、改进目录骨架。
- 补齐 README、CONTRIBUTING、SECURITY、PRIVACY、CODE_OF_CONDUCT、LICENSE。

## Iteration 2
- 完成可运行 MVP 主链路与分层测试基线。
- 补齐 CI / E2E、OpenAPI 类型同步、provider 观测字段与退化态诊断。
- 修复默认聊天模型到 `qwen3.5:latest`，并同步 README / 设置页提示。
- 增加仓库 `.gitignore`，排除本地虚拟环境、数据库、构建产物、node_modules、Claude 本地状态等个人/运行时文件，降低上传 GitHub 泄露风险。
- 清理 README 中本机绝对路径命令，改为仓库可移植命令。

## Iteration 3
- 补强审计与隐私闭环：审计列表/详情仅返回当前用户拥有资源，隐私导出覆盖 persona / agent / task / memory / audit，隐私删除同步清理关联审计记录。
- 新增后端集成测试验证多租户隔离与隐私数据清理闭环，避免跨用户审计泄露与残留数据。

## Iteration 4
- 新增 Avatar Growth Report 前端能力：`Dashboard` 与 `Avatar Detail` 页面均接入成长报告卡片，展示成长快照、已确认洞察、推荐动作与可信说明。
- 扩展前端工作区状态：补充 `confirmedMemories` 拉取与确认后即时回填，避免把 pending memory 误当作“已学会”。
- 完成 Growth Report 中英文本地化，明确 empty / building / ready / demo 状态与“仅 confirmed memory 才进入成长结论”的口径。
- 执行前端验证：`npm --prefix apps/web run test -- --run` 与 `npm --prefix apps/web run build` 通过。

## Iteration 5
- 补齐 Growth Report 失败态：工作区聚合失败时显式进入 `failed` 状态，停止输出未经验证的成长结论。
- 扩展前端 store 降级逻辑：工作区 / pending / confirmed memory 拉取失败时清空对应数据并记录 `workspace_load_failed`，避免沿用陈旧状态。
- 新增 `workspace.spec.ts`，覆盖 confirmed memory 成功聚合与失败降级场景，补上 Growth Report 直接测试证据。

## Iteration 6
- 落地 Dashboard 新手引导：新增 `OnboardingGuide.vue` 与 `onboarding.ts`，把 Demo Avatar、Persona、Agent、Task、Memory 审核串成可见的首次体验步骤。
- Dashboard 接入本地 onboarding 完成态：按 user + avatar 维度持久化完成状态，只有跑通主闭环后才允许结束引导并回到日常工作台。
- 新增 `onboarding.spec.ts`，校验 Demo 常量、storage key 与完成条件；执行 `npm --prefix apps/web run test -- --run` 与 `npm --prefix apps/web run build` 通过。

## Iteration 10
- 补齐认证生命周期真实交付：后端 `/api/v1/auth/refresh` 改为 refresh token rotation，`/api/v1/auth/logout` 正式执行 access/refresh token 吊销，`/auth/me` 对已吊销 access token 返回 `UNAUTHORIZED`，并为 login / refresh / logout 统一写入审计。
- 前端登出链路改为后端感知：`authApi.logout()`、`auth.logout()`、App 头部退出与设置页注销后退出均接入服务端注销，同时保留本地 session 清理兜底。
- 新增并通过 focused 验证：后端认证集成测试 `3 passed`（refresh rotation、logout revocation、auth audit），前端 auth store focused tests `3 passed`。
- 补齐前端验收证据：抽离路由守卫纯函数 `resolveRouteRedirect`，新增 `tests/unit/web.spec.ts` 验证登录页/受保护路由跳转规则；同时复跑 `auth.spec.ts`、`workspace.spec.ts`、`onboarding.spec.ts` 共 `8 passed`，并确认 `npm --prefix apps/web run build` 通过。



## Iteration 14
- 继续收口交付文档与真实产物路径：`deployment-plan.md`、`release-plan.md`、`acceptance-checklist.md`、`interface-freeze-checklist.md`、`open-issues.md` 已统一到 `deploy/docker/*` 实际路径，并明确区分“实机启动成功”与“配置可渲染/可校验但受外部环境阻塞”。
- 再次刷新部署外部环境证据：`docker compose config` 成功渲染，`deploy/docker/ops/scripts/*.sh` 语法校验通过；`curl -fsS http://localhost:11434/api/tags` 仍连接失败，`docker compose up --build -d` 仍被 Docker daemon 不可连接阻塞。

## Iteration 16
- 回填接口冻结检查清单：基于 `docs/02-architecture/data-model.md` 已冻结的领域对象、状态枚举与状态机，以及 `docs/00-governance/decision-log.md` 中已记录的向量存储选型决策，将 `interface-freeze-checklist.md` 中对应历史未勾选项补齐为已冻结。
- 明确 GitHub 发布最后前置条件：当前机器已安装 `gh`，但 `gh auth status` 显示未登录，因此仓库公开发布仅剩交互式 `gh auth login`、配置 remote 与 push 验证三步。

