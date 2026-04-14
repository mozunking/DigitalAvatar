# 遗留问题

| 问题 | 影响 | 优先级 | 当前状态 |
|---|---|---|---|
| Live provider 最终验收仍依赖本地/容器内 Ollama 可用且版本足够新 | 当前代码、focused backend tests 与 2026-04-12 integration / web 验证均已通过；2026-04-12 再次执行 `curl -fsS http://localhost:11434/api/tags` 仍直接连接失败，叠加此前本机 Ollama `0.1.28` 无法拉取 Qwen3 / Qwen3.5（2026-04-10 实测 `ollama pull qwen3.5:latest` 返回 manifest 412），live 最终证据继续受外部环境阻塞 | P0 | 已知 |
| Docker Compose 联调与一键演示验证受本机 Docker daemon 阻塞 | 当前交付已具备 Compose 配置渲染、ops 脚本校验、smoke 用例与阻塞证据；2026-04-12 再次执行 `docker compose -f /Users/hfy/Downloads/DigitalAvatar/deploy/docker/docker-compose.yml up --build -d` 仍明确返回 `Cannot connect to the Docker daemon at unix:///Users/hfy/.orbstack/run/docker.sock`，因此仍缺实机启动证据 | P0 | 已知 |
| 文档与实现已基本对齐，但演示环境最终可启动证据仍待外部运行环境恢复后补齐 | 当前部署/发布/验收文档已更新到 `deploy/docker/*` 真实路径、脚本与阻塞证据口径；`apps/web/openapi/schema.json` 与 `src/types/generated/openapi.ts` 也已在 2026-04-12 重新同步并通过 `npm --prefix /Users/hfy/Downloads/DigitalAvatar/apps/web run check:types`；在 Docker daemon 与 Ollama 恢复前，不应把“可渲染/可校验”误写成“已实机启动” | P1 | 跟踪中 |
