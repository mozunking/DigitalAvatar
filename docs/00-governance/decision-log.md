# 决策日志

> 本文件记录当前已冻结或要求进入 ADR 的关键决策索引。

| ID | 决策 | 当前结论 | 关联文档 |
|---|---|---|---|
| D-001 | MVP 向量存储选型 | 使用 `sqlite-vec`，Beta 预留迁移 Chroma | `02-architecture/adr/ADR-001-sqlite-vec.md` |
| D-002 | 插件/模块边界 | MVP 不开放真实动态插件运行时 | `02-architecture/adr/ADR-002-no-plugin-runtime-in-mvp.md` |
| D-003 | Task 执行语义 | 创建请求返回任务壳，执行按异步语义建模 | `02-architecture/adr/ADR-003-async-task-model.md` |
| D-004 | 前端冻结方案 | Pinia + Vue Router 4 + Axios + OpenAPI 类型生成 | `02-architecture/adr/ADR-004-pinia-openapi.md` |
| D-005 | 认证方案 | JWT + Refresh Token + bcrypt | `02-architecture/security-architecture.md` |
| D-006 | 记忆写入原则 | 候选记忆默认不直接写入长期库，必须用户确认 | `02-architecture/security-architecture.md` |
| D-007 | 并行开发前提 | 先冻结领域模型、状态枚举、API、错误码、审计结构 | `03-delivery/interface-freeze-checklist.md` |
| D-008 | 文档定版策略 | 关键分层文档通过 scaffold-ready 与 frozen baseline 门禁后，默认进入冻结基线 | `05-review/quality-gates.md` `00-governance/document-map.md` |
| D-009 | frozen baseline 变更例外 | 仅允许明显错漏、重大矛盾修复，或有证据支持的显著先进性、可落地性、科学性提升 | `CONTRIBUTING.md` `06-improvement/skill.md` |

## 使用规则

- 新增冻结项时，先补 ADR 或专题说明，再更新本索引。
- 若某决策被推翻，必须写明替代决策、迁移影响与受影响文档，不能只删除旧记录。
- 若变更影响 frozen baseline，必须同步更新：
  - `docs/03-delivery/interface-freeze-checklist.md`
  - `docs/05-review/quality-gates.md`
  - 受影响的产品 / 架构 / 交付 / 评审文档
