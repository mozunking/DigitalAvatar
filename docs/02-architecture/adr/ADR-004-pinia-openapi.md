# ADR-004: 前端采用 Pinia + OpenAPI 类型生成

## 状态
Accepted

## 决策
前端状态管理采用 Pinia，接口类型采用 OpenAPI 自动生成。

## 原因
- Pinia 是 Vue 3 官方推荐方案，TypeScript 支持更好
- 自动生成类型可减少前后端契约漂移
- 有利于多代理并行开发时保持接口一致性

## 影响
- 前端实现必须围绕 API 合同和类型生成链路组织
- 任何 API 变更都应同步更新 OpenAPI 与前端类型产物
