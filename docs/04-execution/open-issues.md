# 遗留问题

| 问题 | 影响 | 优先级 | 当前状态 |
|---|---|---|---|
| Live provider 最终验收仍依赖本地/容器内 Ollama 可用且版本足够新 | 当前本机 Ollama `0.1.28` 无法拉取 Qwen3 / Qwen3.5（manifest 412）；代码侧已补齐 provider 选模、`/health`/`/metrics` 诊断字段、version 与可读 message 暴露，focused backend tests 已通过（17 passed），但 live 最终证据仍待升级 Ollama 后补齐 | P0 | 已知 |
| Docker Compose 联调与一键演示验证已延期 | 当前交付聚焦非 Docker 主链路；Compose 配置与 smoke 已就绪，但实机联调证据后补 | P1 | Deferred |
