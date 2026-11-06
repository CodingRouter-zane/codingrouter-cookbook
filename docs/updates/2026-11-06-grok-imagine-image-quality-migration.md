# 接口没报错，画质却切到 low：Grok Imagine 旧 slug 迁移检查

如果图像应用仍在请求 `grok-imagine-image-quality` 或 `grok-imagine-image-pro`，一次 HTTP 200 已不能证明后端仍是原来的模型与质量档。本文帮助你确认实际服务档位和费用，并把“兼容但不透明”的旧别名迁移为可控配置。

## 已核实事实

xAI 已于 2026 年 11 月 2 日退役上述两个旧 slug。旧请求不会立即报错，而会被 `grok-imagine-image-2.0` 以 `quality: "low"` 服务；请求与响应结构不变，图像生成和编辑接口都受影响。旧版 `grok-imagine-image` 1.0 不在这次退役范围内。

这降低了中断风险，也带来一个工程取舍：调用成功不等于模型语义没有变化。这里的 `low` 是官方服务档位，不应直接推断为业务样图一定变差；是否可接受，仍要用自己的提示词、参考图和验收标准回归。

## 先看费用差异

以下是 xAI 官方美元单价，每张输出图计费：

| 分辨率 | 旧 quality slug | 2.0 low | 2.0 medium |
| --- | ---: | ---: | ---: |
| 1K | $0.05 | $0.04 | $0.06 |
| 1.5K | $0.06 | $0.05 | $0.07 |
| 2K | $0.07 | $0.06 | $0.08 |

编辑任务还会按每张输入图收取 $0.01。2.0 的 `auto` 当前在生成时选择 low、编辑时选择 medium，并按实际服务档计费；若你需要可重复的成本与效果，不要把默认值当作固定合同。

## 五步迁移检查

1. 搜索配置、数据库和队列消息中的两个旧 slug，区分生成与编辑调用。
2. 同时记录请求的模型、`quality`、分辨率、接口类型和响应中的 `usage.cost_in_usd_ticks`；使用 xAI SDK 时，也记录响应报告的模型。
3. 显式改用 `grok-imagine-image-2.0`，按业务要求填写 `low` 或 `medium`，不要只依赖 `auto`。
4. 用固定的代表性提示词和参考图分别回归生成、编辑，比较合格率、返工率、延迟和每个合格结果成本。
5. 把模型与质量档做成可回滚配置。旧 slug 已经重定向，不能作为“回到旧模型”的回滚开关。

建议先以合格结果成本而不是单张价格决策：如果 low 的单价更低，但返工后成本或交付时间上升，就不应仅凭账面降价切换；如果 medium 没有带来可测的合格率提升，则也没有必要为更高档位长期付费。回归记录应保留样本、参数、服务档与结论，避免以后把提示词变化误判为模型变化。

预期结果是每个生产请求都能回答三个问题：请求了哪个 slug、实际按哪个档位服务、最终按什么价格计费。若响应缺少可审计字段或第三方平台改变了字段映射，应先标记为未知并暂停自动迁移，而不是从 HTTP 状态码猜测。

## 验证边界

资料于 2026-11-06（北京时间）核实。本文依据官方迁移指南、发布说明和定价页整理，未进行付费调用或视觉质量基准测试，也不证明 CodingRouter 已支持相同 slug、档位或价格；经第三方平台调用时，应以该平台公开文档和实际账单字段为准。

## 官方来源

- [xAI：Imagine Image Quality 退役迁移指南](https://docs.x.ai/developers/migration/imagine-image-quality-nov-2)
- [xAI：Release Notes](https://docs.x.ai/developers/release-notes)
- [xAI：Grok Imagine Image 2.0](https://docs.x.ai/developers/models/grok-imagine-image-2.0)
- [xAI：API Pricing](https://docs.x.ai/developers/pricing)
