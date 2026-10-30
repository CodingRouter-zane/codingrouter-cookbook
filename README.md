# CodingRouter Cookbook

Practical guides for evaluating and integrating AI model APIs.

面向开发者与 AI 团队的模型 API 接入、成本分析和应用实践资料库。由 CodingRouter 整理，帮助你把模型能力转化为可检查、可维护的应用。

## 从这里开始

| 教程 | 解决的问题 |
| --- | --- |
| [API 接入前的验收清单](docs/api-acceptance.md) | 接口能返回内容，是否足够上线？ |
| [重试、停止与回退](docs/troubleshooting/retry-budget.md) | API 失败后，怎样避免越重试越慢？ |
| [工具禁用的执行边界](docs/troubleshooting/tool-choice-none.md) | 写了 `toolChoice: 'none'`，怎样确认工具真的不会执行？ |
| [每个有效任务究竟花了多少钱](docs/effective-task-cost.md) | 如何比较不同接口的实际成本？ |
| [用 CSV 离线复算有效任务成本](examples/effective-task-cost/README.md) | 如何把失败、返工和零合格结果计入单位成本？ |
| [给 Agent 的搜索和抓取设费用边界](docs/updates/2026-10-23-deepseek-search-fetch-cost.md) | 固定订阅如何处理按次增长的联网工具费？ |
| [LiteLLM Enterprise 安全升级检查](docs/updates/2026-10-30-litellm-enterprise-master-key-security.md) | Release 页写“无需行动”，为什么安全公告仍要求判断版本？ |
| [理解用户自带额度的应用模式](docs/user-funded-apps.md) | 如何区分授权、额度与应用接入？ |

## 阅读说明

各篇正文标明资料核实日期与适用范围。首批三篇核实于 2026-10-15；常青教程中的历史案例不作为当天新发布消息。文章明确区分官方能力、分析建议和示意数据；没有进行付费 API 调用或线上性能实测。第三方产品能力不代表 CodingRouter 已支持同一功能。

后续更新关注模型/API 变化、接入教程和实际应用案例。已有内容会随官方接口变化修订，修改记录通过 Git 提交保留。

## 如何提出问题

欢迎提交文档纠错、兼容性问题和教程建议。描述问题时，请提供所需模型、应用场景、接入工具与预计调用量。报错示例请先脱敏，勿公开 API 密钥或客户数据。

商务需求可通过本仓库所有者 GitHub 个人主页中自行公开的联系方式沟通。本仓库不作模型官方授权、服务可用性、性能或收益承诺。

## 来源与使用

各文章列出官方参考来源。本文档以自己的结构和应用分析编写，不包含第三方项目源代码；第三方代码与素材的使用应遵循各自许可证。本仓库许可证尚未选定，不代表自动授予第三方素材许可。
