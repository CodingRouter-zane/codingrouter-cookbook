# 固定版本也会到期：Claude Sonnet 4.5 11月30日退休前怎么迁移？

**English summary:** Inventory every Sonnet 4.5 route, replay tool workflows against Sonnet 5.5, and cut over only after errors, quality, cost, and rollback are measurable.

面向仍固定使用 Claude Sonnet 4.5 的 AI SaaS、Agent、知识库和 computer use 团队：模型名不变能减少意外升级，却不能阻止型号退役。读完本文，你可以找全旧调用，识别会报 400 的迁移差异，并用同一批任务决定是否放量。

资料核实：2026-11-20（北京时间）。以下事实来自 Anthropic 官方文档，不代表 CodingRouter 已支持相同模型、参数或平台行为；本文没有进行付费 API、线上兼容或性能测试。

## 已核实事实：日期版和别名都受影响

Anthropic 将 `claude-sonnet-4-5-20250929` 标为 deprecated，并计划于 **2026-11-30** 在 Claude API 退役，推荐替代为 `claude-sonnet-5-5`。不带日期的 `claude-sonnet-4-5` 别名也包含在这次退役中；模型退役后，请求会失败。

这不是所有平台共享的一张日历。官方说明该日期适用于 Anthropic 运营的平台；Amazon Bedrock、Google 管理的 Claude Models 等合作伙伴平台可采用不同时间。采购或迁移记录必须同时写“模型 ID + 实际平台”，不能只写“Claude 4.5”。

## 真正的冲突：版本可控，不等于迁移成本为零

Sonnet 5.5 迁移指南列出的变化会直接影响工具型应用：

| 旧用法 | 迁移风险 | 应验证的替代 |
| --- | --- | --- |
| `tool_choice` 为 `any` 或指定 `tool` | 返回 400 | `auto` 配合 strict tools，并用提示词说明何时调用 |
| thinking budget、`thinking.disabled`、采样参数 | 部分设置返回 400 或语义变化 | 改用 effort，重新测 Token、质量和输出长度 |
| assistant prefill、旧 `output_format`、旧 beta header | 请求结构不再兼容 | 移除 prefill，迁移到 `output_config.format`，逐项删除旧 header |
| 旧 computer use 工具版本 | Claude API 可能返回 400 | 按平台改用受支持的 toolset |
| 修改历史后重放 thinking block | 可能丢上下文或报错 | 保持会话 append-only，并保留可回滚的新会话路径 |

因此，“把模型名替换掉，接口返回 200”不是迁移完成。工具是否被正确调用、结构化结果是否合格、thinking 是否仍能续接，都要单独验收。

## 第一步：先找全旧模型从哪里被选中

官方建议从 Claude Console 的 Usage 页面导出 CSV，按 API Key 和模型审计实际用量。再搜索代码、配置中心、环境变量、网关路由、fallback chain、子 Agent 定义和定时任务中的：

- `claude-sonnet-4-5-20250929` 与 `claude-sonnet-4-5`；
- 依赖“sonnet”别名的 Claude Code 或脚本；
- forced tool choice、thinking budget、assistant prefill；
- computer use 工具类型和 beta header。

给每条路径记录负责人、平台、调用量、是否有工具、回退模型和最晚切换时间。找不到负责人或无法回放的路径应列为阻塞项，而不是直接全量替换。

## 第二步：用同一批任务做回放

准备脱敏或合成的固定任务集，至少覆盖纯文本、结构化输出、一次工具调用、多轮工具、拒绝/错误和长上下文。两边使用相同输入与验收标准，记录：

| 指标 | 通过条件 |
| --- | --- |
| 请求成功率 | 没有新增 400、鉴权或平台路由错误 |
| 工具正确率 | 工具、参数、调用顺序满足业务规则 |
| 合格任务率 | 最终结果通过同一人工或自动验收 |
| 端到端时间 | 包含排队、工具执行、重试和回退 |
| 每个合格任务成本 | 实际总费用 ÷ 合格任务数 |

不要用单次演示判断“更聪明”或“更便宜”。若输出更长、工具次数更多或合格率下降，即使每 Token 单价看起来合适，真实任务成本仍可能上升。

## 第三步：灰度、回滚，再停止旧路由

先让少量内部或低风险流量进入 Sonnet 5.5，错误按“请求构造、平台路由、模型输出、工具执行”分层统计。只有在回放集和灰度流量都满足门槛后才扩大比例。

回滚不能只把模型名改回去：如果请求已改成新 effort、toolset 或输出结构，旧模型未必接受。保留成对的“模型 + 请求模板 + 工具版本”配置，并在 11 月 30 日前设置早于官方截止日的内部切换点。若依赖合作伙伴平台，应以该平台的公开退役日为准重新排期。

## 结果与边界

完成上述检查后，团队应该能回答：还有哪些旧调用、哪些差异会报 400、哪些任务质量发生变化、什么指标允许放量，以及如何在一键回滚时恢复完整请求合同。

本文不证明 CodingRouter 已上线 Sonnet 5.5，也不承诺兼容性、价格、性能、模型保真、SLA 或第三方平台日期。产品支持范围应以 CodingRouter 后续可公开确认的信息为准。

## 官方来源

- [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- [Model deprecations](https://platform.claude.com/docs/en/about-claude/model-deprecations)
- [Claude Sonnet 5.5 migration guide](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide)

如需讨论迁移评估，可通过仓库所有者主页公开渠道提供脱敏的模型 ID、平台、工具类型和验收标准，勿公开密钥或客户数据。
