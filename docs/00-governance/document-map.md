# 文档地图

## 1. 文档域

| 域 | 路径 | 作用 | 主要维护角色 | 文档类型 |
|---|---|---|---|---|
| 治理 | `docs/00-governance/` | 导航、术语、决策索引、冻结范围 | 主控代理 / 架构负责人 | baseline / index |
| 产品 | `docs/01-product/` | 价值、范围、需求、旅程、功能 | 产品负责人 | baseline |
| 架构 | `docs/02-architecture/` | 技术边界、模型、接口、安全、前端、可观测性 | 架构/后端/前端/安全负责人 | baseline |
| 交付 | `docs/03-delivery/` | 开发计划、并行拆解、测试、部署、发布 | Tech Lead / PM / QA / DevOps | baseline |
| 执行 | `docs/04-execution/` | 进展、轮次记录、遗留问题 | 主控代理 / PM | execution-state |
| 评审 | `docs/05-review/` | 检查框架、验收、门禁、评审记录 | Review Lead / QA / Security | baseline / review |
| 改进 | `docs/06-improvement/` | 整改、复盘、标准化沉淀 | 主控代理 / 质量负责人 | baseline / improvement |

## 2. frozen baseline 范围

以下文档属于当前默认冻结基线：
- `docs/01-product/requirements.md`
- `docs/01-product/functional-spec.md`
- `docs/01-product/user-journeys.md`
- `docs/02-architecture/api.md`
- `docs/02-architecture/data-model.md`
- `docs/02-architecture/security-architecture.md`
- `docs/02-architecture/frontend-architecture.md`
- `docs/02-architecture/observability.md`
- `docs/03-delivery/development-plan.md`
- `docs/03-delivery/multi-agent-workbreakdown.md`
- `docs/03-delivery/interface-freeze-checklist.md`
- `docs/03-delivery/testing-plan.md`
- `docs/03-delivery/deployment-plan.md`
- `docs/03-delivery/release-plan.md`
- `docs/05-review/acceptance-checklist.md`
- `docs/05-review/quality-gates.md`
- `docs/05-review/review-framework.md`
- `docs/05-review/document-review-log.md`
- `docs/00-governance/document-map.md`
- `docs/00-governance/decision-log.md`
- `docs/06-improvement/skill.md`
- `CONTRIBUTING.md`

## 3. execution-state 文档范围

以下文档用于记录执行状态，不属于稳定设计合同：
- `docs/04-execution/*`
- 临时进展、遗留问题、轮次记录

这些文档允许随执行进展持续更新，不适用“原则上不改”的冻结规则。

## 4. 当前主源与历史输入

### 当前执行基线
- `docs/` 分层文档体系 — 当前正式执行基线。

### 历史输入
- `Digital Avatar 正式方案 V14.md` — 当前分层文档的主要来源之一。
- `Digital Avatar 正式方案 V13.md` — 历史正式版本。
- `总体设计方案.md` — 初始总体提案。
- `docs/minimax多智能体评审意见.md` — 多专家评审输入。
- `docs/frontend-architecture-review.md` — 前端专项评审输入。

历史输入用于追溯背景，不直接作为当前实施合同。

## 5. 维护规则

1. 先改对应领域文档，再改索引型文档。
2. frozen baseline 文档原则上不得修改；仅允许明显错漏、重大矛盾修复，或有证据支持的显著先进性、可落地性、科学性提升。
3. 冻结项变更必须同步更新：
   - `docs/00-governance/decision-log.md`
   - `docs/03-delivery/interface-freeze-checklist.md`
   - 相关 ADR
   - 受影响的验收、评审、测试、部署文档
4. 历史评审输入不直接复制进现行规范，改为在目标文档中沉淀结论。
5. 执行类文档记录当前状态，方案类文档记录稳定规则，不混写。

## 6. 使用约束

- 若某文档无法回答其职责域内的脚手架生成问题，则不应列入 frozen baseline。
- 若用户或开发智能体需要依赖当前设计开工，应优先读取 frozen baseline 文档，而不是历史输入。
