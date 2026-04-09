# 文档总览

本仓库当前已包含可运行 MVP 实现与配套治理文档，用于把 `Digital Avatar 正式方案 V14.md` 拆解为可长期维护、可并行执行、可审查验收的 GitHub 风格文档体系，并持续对齐真实代码与测试交付。

## 阅读顺序

### 1. 先看全局
- [README.md](../README.md) — 仓库入口与项目定位
- [00-governance/document-map.md](00-governance/document-map.md) — 全量文档地图
- [00-governance/decision-log.md](00-governance/decision-log.md) — 关键冻结决策索引

### 2. 再看产品
- [01-product/product-design.md](01-product/product-design.md) — 产品总设计、UVP 与分身成长报告定位
- [01-product/requirements.md](01-product/requirements.md) — 范围、优先级、验收口径
- [01-product/user-journeys.md](01-product/user-journeys.md) — 核心用户旅程与成长报告进入路径
- [01-product/functional-spec.md](01-product/functional-spec.md) — 模块功能规格、成长报告状态与信息结构
- [01-product/non-functional-requirements.md](01-product/non-functional-requirements.md) — 安全、性能、可观测性、合规要求

### 3. 然后看架构
- [02-architecture/architecture.md](02-architecture/architecture.md) — 总体架构与边界
- [02-architecture/domain-model.md](02-architecture/domain-model.md) — 领域对象与关系
- [02-architecture/api.md](02-architecture/api.md) — API 合同与错误码
- [02-architecture/data-model.md](02-architecture/data-model.md) — 数据模型、状态机、索引
- [02-architecture/security-architecture.md](02-architecture/security-architecture.md) — 认证授权、策略与隐私边界
- [02-architecture/frontend-architecture.md](02-architecture/frontend-architecture.md) — 前端冻结方案
- [02-architecture/observability.md](02-architecture/observability.md) — 日志、trace、健康检查与指标
- [02-architecture/adr/](02-architecture/adr/) — 关键架构决策记录

### 4. 再进入交付执行
- [03-delivery/development-plan.md](03-delivery/development-plan.md) — 里程碑与阶段目标
- [03-delivery/multi-agent-workbreakdown.md](03-delivery/multi-agent-workbreakdown.md) — 多代理职责拆解
- [03-delivery/interface-freeze-checklist.md](03-delivery/interface-freeze-checklist.md) — 并行开发前冻结项
- [03-delivery/testing-plan.md](03-delivery/testing-plan.md) — 测试分层与覆盖矩阵
- [03-delivery/deployment-plan.md](03-delivery/deployment-plan.md) — 部署方案与运行要求
- [03-delivery/release-plan.md](03-delivery/release-plan.md) — 发布节奏与版本门禁

### 5. 最后用于管理与复盘
- [04-execution/progress.md](04-execution/progress.md) — 当前总进展
- [04-execution/iteration-log.md](04-execution/iteration-log.md) — 分轮次执行记录
- [04-execution/open-issues.md](04-execution/open-issues.md) — 遗留问题与阻塞
- [05-review/review-framework.md](05-review/review-framework.md) — 评审框架
- [05-review/acceptance-checklist.md](05-review/acceptance-checklist.md) — MVP 验收清单
- [05-review/quality-gates.md](05-review/quality-gates.md) — 质量门禁
- [05-review/security-checklist.md](05-review/security-checklist.md) — 安全专项检查表
- [05-review/document-review-log.md](05-review/document-review-log.md) — 文档评审记录
- [06-improvement/improvement-plan.md](06-improvement/improvement-plan.md) — 整改计划
- [06-improvement/retrospective.md](06-improvement/retrospective.md) — 阶段复盘
- [06-improvement/skill.md](06-improvement/skill.md) — 标准化执行方法

## 使用原则

- 设计、架构、交付、执行、评审、改进分层维护，不再把全部信息堆在单一总文档中。
- 历史方案与评审文档保留为输入，不作为当前执行口径。
- 冻结项变更必须同步更新相关 ADR、决策日志、接口冻结清单与验收文档。
