# 接口冻结检查清单

## 1. 并行开发前必须冻结

- [x] 领域对象定义
- [x] 状态枚举与状态机
- [x] API 路径与 DTO
- [x] 错误码
- [x] 审计字段结构
- [x] Policy 返回结构
- [x] Auth 方案
- [x] 向量存储选型
- [x] 前端类型生成方式
- [x] 测试目录与最低用例骨架
- [x] 亮点功能的信息结构与边界（如 Avatar Growth Report）
- [x] Compose 服务清单与环境变量

## 2. 冻结通过标准

| 冻结项 | 通过标准 | 冻结证据 |
|---|---|---|
| 领域对象定义 | 每个核心对象已有字段、关系、职责边界，且与需求文档一致 | `data-model.md` 字段表与关系说明 |
| 状态枚举与状态机 | 所有状态值唯一且流转方向明确，无“待定”状态 | `data-model.md` 状态枚举与状态机图 |
| API 路径与 DTO | 已列出路径、方法、关键请求/响应字段、成功/失败语义 | `api.md` 资源级字段表与示例 |
| 错误码 | 每个关键失败场景都能映射到统一错误码 | `api.md` 错误码冻结与触发条件表 |
| 审计字段结构 | 已定义 trace_id、actor、resource、action、result、created_at | `data-model.md` `audit_logs` 表；`observability.md` 日志字段 |
| Policy 返回结构 | 已定义 allow / block 语义、原因、命中规则与 trace_id | `security-architecture.md` Policy 响应结构 |
| Auth 方案 | 已定义登录、刷新、登出、鉴权、权限拒绝语义 | `security-architecture.md` token 生命周期与鉴权矩阵 |
| 向量存储选型 | MVP 选型、升级路径、索引方式已明确 | ADR 与 `decision-log.md` |
| 前端类型生成方式 | OpenAPI 生成方式、输出目录、更新触发规则已明确 | `frontend-architecture.md` 类型生成规则 |
| 测试目录与最低用例骨架 | 已明确 unit / integration / e2e / security 目录、夹具与最低断言入口 | `testing-plan.md` 测试矩阵与建议文件路径 |
| 目录结构与模块边界 | 已明确后端、前端、测试、部署的目录与边界责任 | `development-plan.md` `frontend-architecture.md` |
| 亮点功能的信息结构与边界 | 已定义目标用户价值、页面入口、状态语义、数据来源、证据链与非目标约束 | `product-design.md` `functional-spec.md` `acceptance-checklist.md` |

## 3. 冻结责任

| 冻结项 | 主责任角色 |
|---|---|
| 领域对象定义 / 状态枚举与状态机 | 后端内核代理 |
| API 路径与 DTO / 错误码 | API 代理 |
| 审计字段结构 / Policy 返回结构 | Policy / Audit 代理 |
| Auth 方案 | Auth / Security 代理 |
| 向量存储选型 | 后端内核代理 |
| 前端类型生成方式 | 前端代理 |
| 目录结构与模块边界 | 主控代理 |
| 测试目录与最低用例骨架 | 测试代理 |
| Compose 服务清单与环境变量 | 部署与运维代理 |

## 4. 交叉校验要求

- `API 路径与 DTO` 必须与 `docs/02-architecture/api.md` 一致。
- `领域对象定义`、`状态枚举与状态机` 必须与 `docs/02-architecture/data-model.md` 一致。
- `Policy 返回结构`、`Auth 方案` 必须与 `docs/02-architecture/security-architecture.md` 一致。
- `前端类型生成方式` 与 `docs/02-architecture/frontend-architecture.md` 一致。
- `测试目录与最低用例骨架` 与 `docs/03-delivery/testing-plan.md` 一致。
- `Compose 服务清单与环境变量` 与 `docs/03-delivery/deployment-plan.md` 一致。
- `通过标准` 与 `docs/05-review/acceptance-checklist.md`、`docs/05-review/quality-gates.md` 不得冲突。
- 任一冻结项如无法落到具体字段、状态图、示例响应、配置表或建议文件路径，视为未冻结。

## 5. 冻结失败判定

出现以下任一情况，视为冻结失败：
- 文档中仍存在“实现时再定”“后续补充”等影响主链路实现的条目。
- 接口只有路径，没有请求/响应字段或错误码。
- 模型只有名称，没有字段、关系、敏感级别或删除策略。
- 页面只有名称，没有字段、调用接口、状态与跳转关系。
- 测试或部署文档无法回答最低接入点。

## 6. 使用规则

- 未冻结项不得启动跨团队并行实现。
- 冻结项变更必须同步更新决策日志、ADR、相关方案与验收文档。
- 若任一冻结项变更，受影响代理必须重新确认输入与交付物。
- 评审中若出现“实现时再定”，视为未冻结。
- 定版后原则上不得修改；仅允许明显错漏、重大矛盾修复，或有证据支持的显著先进性、可落地性、科学性提升。
