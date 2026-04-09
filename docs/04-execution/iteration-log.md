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
