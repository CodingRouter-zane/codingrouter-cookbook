# 零留存不等于零账单：Claude EFS 选型前要算清哪些成本？

面向评估企业内部知识库、Agent 的技术与采购负责人：如果要求厂商不留存请求，能否直接启用 EFS，再沿用原架构和预算？本文给出功能筛选、成本清单与切流门槛。场景是编辑假设，不是真实客户反馈。

事件日期：2026-11-23；资料核实：2026-11-27（北京时间）。这是对本周公告的落地分析，不是今日新消息。*A practical decision guide, not a deployment report.*

## 已核实：不由厂商保存，不等于不存在副本

Anthropic 发布了 Enterprise Frontier Safeguards（EFS）beta：合资格组织的提示与响应不由 Anthropic 留存，密封安全数据写入组织自有云存储桶。它包含加密的提示、响应和模型推理；桶属于你，并不表示你的团队能直接读取这些密封内容。企业团队承担 Safety Cases 审查。[1][2]

先查资格再谈架构：当前 Claude Platform 设置指南明确为组织内部使用；不能直接推定适用于面向外部客户的 SaaS。EFS 不另收费、也不改变模型 API 定价，但云存储、读写、密钥操作及适用网络传输仍有费用。[2][3]

## 工程取舍：存储控制权可能改变功能组合

下表的动作建议是 CodingRouter 的分析，不是厂商承诺。

| 当前需求 | 官方边界 | 选型动作 |
| --- | --- | --- |
| 内部 Messages API 工作流 | EFS 按 workspace 生效，不按模型分别开关 | 需要不同安排的流量先拆 workspace |
| 依赖 Batch API | FAQ 明确 EFS 不支持 Batch | 先评估逐请求改造及成本，别假定原方案不变 |
| 依赖 Claude Managed Agents 托管服务 | EFS workspace 不支持其会话运行 | 先判断替代方案是否可接受，不直接切生产 |

Files、代码执行容器等功能自身保存的数据也不能靠 EFS 一项配置兜底。历史数据不会因新配置自动迁走。[4]

## 可执行方案：先做一张完整成本表

建议预算分三栏：原有模型调用费、云资源账单、内部运维与审查投入。后两栏不是新的 token 单价，也不能混算成厂商涨价。

可复用字段：月份、workspace、功能、费用归属、计量项、用量、计费依据、负责人。云资源按实际账单填；未知项写“待确认”，不要用模型 token 数推算加密对象大小。

例如内部报告 Agent 同时用了实时请求和批处理，先分别列出流量与依赖，再比较保持现状、拆分 workspace、改为逐请求三种方案。只有功能可用、数据安排满足要求，才比较总成本；不承诺某方案一定更省。

## 验证结果与上线边界

本次仅完成官方资料交叉核验，没有创建桶、访问账户或运行 API；上述成本表是建议模板，不是实测账单。

实施团队应先用无敏感数据验证配置。当前指南要求观察所选桶出现首个新对象后再等 10 分钟；若桶已有其他 workspace 写入，新对象本身不能证明本次切换成功，应按指南向 Anthropic 确认。[3] 未确认前不要切入敏感流量。

预期产物是一张“功能—存储—费用—证据—负责人”清单。任何资格、功能或切流证据未确认，就暂停迁移，而不是用“已勾选零留存”代替验收。Beta 条款和行为可能变化；本文不构成合规认证，也不代表 CodingRouter 已支持 EFS。后续按官方变更修订边界。

## 官方来源

1. [11月23日发布记录](https://platform.claude.com/docs/en/release-notes/overview)
2. [EFS 概述](https://platform.claude.com/docs/en/manage-claude/enterprise-frontier-safeguards/overview)
3. [Claude Platform 设置与验证指南](https://platform.claude.com/docs/en/manage-claude/enterprise-frontier-safeguards/setup-console)
4. [EFS FAQ：覆盖范围及功能限制](https://platform.claude.com/docs/en/manage-claude/enterprise-frontier-safeguards/faq)
