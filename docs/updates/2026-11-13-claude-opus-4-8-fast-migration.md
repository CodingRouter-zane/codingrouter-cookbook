# 快模式不是永久档位：Claude Opus 4.8 fast 11月30日下线，如何控制迁移成本

**English summary:** Separate output speed from first-token latency, then compare migration options by cost per accepted task.

面向正在用 Claude Opus 4.8 fast 的 AI SaaS、Agent 和长文本应用团队：11 月 30 日前，你既要避免请求突然报错，也要判断迁移后“更便宜的单价”能否真的降低业务成本。读完本文，你可以完成一次不依赖厂商宣传数字的迁移评估。

资料核实：2026-11-13（北京时间）。以下是 Anthropic 官方能力与价格解读，不代表 CodingRouter 已支持这些模型、参数或价格；本文没有执行付费 API 或线上性能测试。

## 先分清：下线的是快模式，不是模型

Anthropic 在 2026-10-30 公告：Claude Opus 4.8 的 fast mode 将于 2026-11-30 移除。此后向 `claude-opus-4-8` 发送 `speed: "fast"` 会报错；要继续使用 fast，官方迁移方向是 Claude Opus 5.5。Opus 4.8 模型本身仍列为可用，标准档请求不是这次公告所说的下线对象。

官方对 fast 的描述是最高可提高 2.5 倍输出 tokens/second（OTPS），并明确收益集中在输出阶段，不是 time to first token（TTFT）。短回复或多次工具调用的任务，网络、首 Token、工具执行与排队可能占据大部分时间，不能把 OTPS 直接当成端到端提速。

## 价格下降，不等于每个有效任务一定更便宜

当前 Claude API 公布价格如下，单位均为美元/百万 Token：

| 方案 | 输入 | 输出 |
| --- | ---: | ---: |
| Opus 4.8 标准 | 5 | 25 |
| Opus 4.8 fast | 10 | 50 |
| Opus 5.5 标准 | 4 | 20 |
| Opus 5.5 fast | 8 | 40 |

从挂牌单价看，Opus 5.5 fast 比 Opus 4.8 fast 低 20%；但模型迁移也可能改变输出长度、工具调用次数、返工率和合格率。Prompt caching、数据驻留等价格修饰还可能叠加。采购判断应回到：

`每个有效任务成本 = 同一批任务的实际总费用 ÷ 合格任务数`

不要只比较每 Token，也不要用厂商“最高 2.5 倍”推算自己的利润。

## 用五个指标决定要不要 fast

| 指标 | 回答的问题 |
| --- | --- |
| TTFT | 用户多久看到第一个 Token？ |
| OTPS | 长输出生成阶段是否更快？ |
| 端到端时间 | 工具、重试和网络计入后，任务实际多久完成？ |
| 合格率 | 迁移后结果是否仍满足同一验收标准？ |
| 有效任务成本 | 为一份合格结果实际付了多少钱？ |

用同一组脱敏或合成任务，对 Opus 5.5 标准档和 fast 档分别测试；固定提示词、effort、输出上限、工具配置与验收标准。记录实际模型、请求速度档、响应中的 `usage.speed`、Token、错误、重试和最终是否合格。fast 有独立限流，遇到 429/529 时，等待、失败或回到标准档必须是预先批准的策略，不能静默换档后仍按原配置记账。

## 11月30日前的迁移清单

1. 搜索代码和配置中的 `claude-opus-4-8`、`speed: "fast"`、相关 beta header、别名与网关回退。
2. 先跑 Opus 5.5 标准/fast 对照，确认格式、工具、质量和成本边界，再决定默认档位。
3. 为不支持 fast、独立限流和容量不足设置明确状态；回退到标准档时保留审计字段。
4. 在生产切换前保留小流量灰度与回滚开关，并在 11 月 30 日前完成。

## 边界与后续

不同云平台的 fast 可用方式可能不同，例如 Microsoft Foundry 使用独立的 fast 模型部署；不能把 Claude API 的参数直接复制到所有平台。本文未验证 CodingRouter 的模型清单、兼容性、性能、限流或报价。后续如获得可公开的产品确认，可再补 CodingRouter 专属迁移说明。

官方来源：
- [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- [Fast mode](https://platform.claude.com/docs/en/build-with-claude/fast-mode)
- [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

如需讨论迁移评估，可通过仓库所有者主页公开渠道说明模型、任务长度、并发和验收标准，勿公开密钥或客户数据。
