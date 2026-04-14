# Digital Avatar

Digital Avatar 是一个面向个人专业用户与 AI-native 小团队的开源数字分身系统，目标是把用户的风格、知识、偏好和工作方式沉淀为一个可控、可审计、可持续成长的数字分身。

## 当前状态

当前仓库已提交可运行的 MVP 实现，包含前后端脚手架、基础部署文件与自动化测试。当前主链路已覆盖：登录 -> 创建 Avatar -> 生成人设 -> 创建 Agent -> 执行任务 -> 候选记忆确认/拒绝 -> 审计查询。

当前剩余阻塞仅有两类外部环境项：
- live provider 最终验收仍依赖先升级本机 Ollama，并成功拉取 `qwen3.5:latest`
- Docker Compose 真机联调证据仍受本机 Docker daemon 不可连接阻塞；当前已补齐配置、脚本、smoke 与阻塞证据

## 核心价值

- 风格复刻：输出更像用户本人，而不是通用 AI
- 可控执行：在授权范围内辅助完成真实任务
- 长期记忆：沉淀经过确认的长期价值信息
- 审计追踪：关键动作、策略命中、状态变化可回溯
- 分身成长报告：把“系统最近学到了什么、依据是什么、接下来还能怎样更好帮你”持续解释给用户看，形成“越用越懂你”的可验证体验

## MVP 范围

MVP 聚焦一条闭环：

1. 用户登录并创建 Avatar
2. 导入最小资料并生成 Persona
3. 创建默认 Agent
4. 执行首个任务
5. 捕捉候选记忆并由用户确认
6. 写入长期记忆并保留审计链路

## 快速开始

### 后端

```bash
cd apps/api
python3 -m uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd apps/web
npm install
npm run dev
```

### 测试

```bash
cd apps/api
python3 -m pytest

cd apps/web
npm test -- --run
```

### Docker Compose

```bash
cd deploy/docker
docker compose up --build
```

默认会启动 `web`(4173)、`api`(8000)、`worker` 与 `ollama`。为保证本地演示与 CI 稳定，当前 Compose 默认对 `api` / `worker` 使用 `PROVIDER_MODE=mock`；若要切到 live provider，请显式调整环境变量并确保 Ollama 可用。当前默认聊天模型为 `qwen3.5:latest`；若本机 Ollama 版本过旧或本地没有 chat 模型，请先升级 Ollama 并执行 `ollama pull qwen3.5:latest`。

仓库已补齐 `deploy/docker/ops/scripts/dev-up.sh`、`dev-down.sh`、`backup-db.sh`、`restore-db.sh`、`ops/health/smoke.http` 与 `ops/compose/docker-compose.override.yml`；根目录 `.dockerignore` 也已加入，避免把本地运行态文件带入镜像上下文。


- [docs/README.md](docs/README.md) — 文档总入口与阅读顺序
- [docs/01-product/product-design.md](docs/01-product/product-design.md) — 产品与方案总览
- [docs/01-product/functional-spec.md](docs/01-product/functional-spec.md) — 分身成长报告、页面状态与信息结构
- [docs/02-architecture/architecture.md](docs/02-architecture/architecture.md) — 总体技术架构
- [docs/02-architecture/api.md](docs/02-architecture/api.md) — API 合同与错误码
- [docs/03-delivery/development-plan.md](docs/03-delivery/development-plan.md) — 开发计划与里程碑
- [docs/03-delivery/multi-agent-workbreakdown.md](docs/03-delivery/multi-agent-workbreakdown.md) — 多代理并行开发拆解
- [docs/05-review/acceptance-checklist.md](docs/05-review/acceptance-checklist.md) — MVP 验收清单
- [docs/06-improvement/skill.md](docs/06-improvement/skill.md) — 标准化执行方法

## 仓库约定

- 当前仓库已包含真实实现，构建、测试、部署命令应以实际清单文件与脚本为准。
- 方案拆分遵循“产品 / 架构 / 交付 / 执行 / 评审 / 改进”分层，不再依赖单一总文档维护全部信息。
- 旧版总文档与评审文档暂时保留，作为历史输入与追溯依据。

## 相关顶层文件

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [PRIVACY.md](PRIVACY.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [CLAUDE.md](CLAUDE.md)
