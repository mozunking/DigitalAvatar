# 迭代日志

## Iteration 1
- 基于 V14 与评审意见搭建 GitHub 风格文档体系。
- 完成治理、产品、架构、交付、执行、评审、改进目录骨架。
- 补齐 README、CONTRIBUTING、SECURITY、PRIVACY、CODE_OF_CONDUCT、LICENSE。

## Iteration 2
- 完成可运行 MVP 主链路与分层测试基线。
- 补齐 CI / E2E、OpenAPI 类型同步、provider 观测字段与退化态诊断。
- 修复默认聊天模型到 `qwen3.5:7b-instruct-q4_0`，并同步 README / 设置页提示。
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
