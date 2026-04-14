# 部署计划

## 1. MVP 部署形态

- 单机 Docker Compose
- Web + API + Worker + SQLite + Ollama（可外置）
- 默认本地优先部署，不引入 MVP 不必要的外部依赖

## 2. Compose 服务清单

| 服务 | 作用 | 默认端口 | 关键挂载 | 健康检查 |
|---|---|---|---|---|
| `web` | 前端静态站点 / SPA | `4173` | 无 | HTTP `GET /` |
| `api` | REST API | `8000` | `./data` `./logs` | HTTP `GET /health` |
| `worker` | Task 异步执行 | 无外部暴露 | `./data` `./logs` | 依赖任务执行回写与容器存活 |
| `ollama` | 本地模型服务，可选外置 | `11434` | Docker volume `ollama_data` | HTTP `GET /api/tags` |

## 3. 最低目录结构

```text
deploy/docker/
├── docker-compose.yml
├── .env.example
└── ops/
    ├── compose/
    │   └── docker-compose.override.yml
    ├── scripts/
    │   ├── dev-up.sh
    │   ├── dev-down.sh
    │   ├── backup-db.sh
    │   └── restore-db.sh
    └── health/
        └── smoke.http
```

当前仓库已提供以上真实文件落点于 `deploy/docker/` 下；若需切换 live provider，可在默认 Compose 之外叠加 `deploy/docker/ops/compose/docker-compose.override.yml`。

## 4. 环境变量清单

| 变量 | 必填 | 默认值建议 | 说明 |
|---|---|---|---|
| `APP_ENV` | 是 | `production` | 运行环境 |
| `API_PORT` | 否 | `8000` | API 对外端口 |
| `WEB_PORT` | 否 | `4173` | Web 对外端口 |
| `DATABASE_URL` | 是 | `sqlite:///./data/app.db` | SQLite 路径 |
| `JWT_SECRET` | 是 | 无 | JWT 签名密钥 |
| `JWT_ACCESS_TTL_MINUTES` | 是 | `15` | Access token 有效期 |
| `JWT_REFRESH_TTL_DAYS` | 是 | `7` | Refresh token 有效期 |
| `OLLAMA_BASE_URL` | 否 | `http://ollama:11434` | Provider 地址 |
| `OLLAMA_MODEL` | 否 | `qwen3.5:latest` | Ollama 模型名 |
| `PROVIDER_MODE` | 是 | `mock` | Provider 模式；演示环境默认 mock |
| `LOG_LEVEL` | 是 | `INFO` | 日志级别 |
| `DATA_DIR` | 否 | `./data` | 业务数据目录挂载根 |
| `LOG_DIR` | 否 | `./logs` | 日志目录挂载根 |
| `MEMORY_ENCRYPTION_KEY` | 否 | 无 | 记忆加密密钥，启用加密时必填 |

## 5. 部署要求

- 环境变量模板
- 一键启动脚本
- 数据目录挂载
- 日志目录挂载
- 备份与恢复说明
- 健康检查
- 基础监控
- 日志滚动策略
- SQLite 备份策略
- 数据迁移说明
- Docker 构建上下文排除规则（`.dockerignore`）

## 6. 健康检查

### API
- `GET /health` 返回 `status=ok`
- 检查 DB、Provider、Worker 三项子状态

### Web
- 首页返回 200
- 静态资源可访问

### Worker
- 心跳日志持续输出
- 能处理最小任务并正确写回状态

### Ollama
- Provider health endpoint 返回可用状态

## 7. 初始化数据

- demo 用户 1 个
- demo avatar 1 个
- current persona 1 个
- default agent 1 个
- onboarding 所需推荐任务样例

初始化方式：
1. API 启动时按显式命令执行 seed；
2. 不允许隐式修改生产数据；
3. demo 数据仅用于本地 / 演示环境。

## 8. 备份与恢复

### 备份
- SQLite：复制数据库文件前先停止写入或走安全快照命令。
- 日志：按日期归档压缩。
- 备份命令：`deploy/docker/ops/scripts/backup-db.sh`

### 恢复
- 恢复前停止 `api` 与 `worker`
- 使用 `deploy/docker/ops/scripts/restore-db.sh <backup-file>`
- 恢复后执行 `GET /health` 与最小 smoke 测试

## 9. 数据迁移说明

- MVP 使用 Alembic 或等效迁移工具。
- 首次启动前应执行 schema migration。
- 每次变更数据模型后必须同步更新迁移脚本与文档。

## 10. 部署原则

- 默认支持本地优先部署。
- 不引入 MVP 不必要的外部依赖。
- 观测与备份能力必须与部署文档一起落地。
- 安全默认值优先于便捷默认值。

## 11. 脚手架生成要求

- 本文档必须能直接生成：`docker-compose.yml`、`.env.example`、启动/停止脚本、备份/恢复脚本、health smoke 文件。
- 当前仓库对应实现位置：`deploy/docker/docker-compose.yml`、`deploy/docker/.env.example`、`deploy/docker/ops/scripts/*`、`deploy/docker/ops/health/smoke.http`、`deploy/docker/ops/compose/docker-compose.override.yml`、仓库根 `.dockerignore`。
- 若无法回答“有哪些服务、端口多少、挂载哪里、环境变量是什么、怎么备份恢复”，则部署规格未达 scaffold-ready。
