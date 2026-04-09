# ADR-001: MVP 使用 sqlite-vec

## 状态
Accepted

## 决策
MVP 向量存储采用 `sqlite-vec`。

## 原因
- 与 SQLite 本地优先策略一致
- 依赖少，便于仓库初始化与单机部署
- 足以支撑 MVP 数据量与并行开发验证

## 影响
- MVP 先优化可落地性，不追求高规模检索能力
- Beta 若数据规模增长，预留迁移 Chroma 的路径
