# 写了 `toolChoice: 'none'`，工具还可能被执行？别把模型参数当成安全边界

*When “no tools” is a safety boundary, verify execution—not just the request field.*

如果你的 Agent 能发消息、改数据、下单或运行代码，`toolChoice: 'none'` 往往被当成“这一轮绝不执行工具”。读完本文，你可以判断项目是否落在 Vercel AI SDK 5.0.281 的修复范围内，并建立一组不调用真实 API 的回归检查。

## 已核实事实：问题不只在模型端

Vercel 于北京时间 2026-10-24 发布 AI SDK 5.0.281。官方说明称，在 5.0 分支的特定路径中，`toolChoice: 'none'` 可能仍让已注册工具保持可执行。

修复包含两层：

1. 将 `none` 转发给 Hugging Face Responses API；
2. 即使模型仍返回工具调用，也在 `generateText`、`streamText` 的本地执行前拒绝。

非流式路径会产生 `ToolChoiceViolationError`。流式路径会阻止工具输入、调用和结果片段进入客户端执行层，并跳过工具调用修复流程。官方 PR 报告相关 Node、Edge、Hugging Face 测试以及类型检查通过。

这是一项回移到 `release-v5.0` 的修复，不能据此断言所有 AI SDK 版本、所有 Provider 或 CodingRouter 接入都出现过同一问题。

## 先判断是否需要行动

| 当前情况 | 建议 |
| --- | --- |
| 使用 AI SDK 5.0，版本早于 5.0.281，并在禁用工具时仍注册工具 | 优先升级，并补执行层回归测试 |
| 已使用 5.0.281 或更高的 5.0 补丁 | 核对 lockfile 与线上产物确实包含修复，再运行 mock 测试 |
| 使用 6.x、7.x 或其他 SDK | 回到对应版本文档核实；不要直接套用 5.0.281 的受影响结论 |
| 自己消费流式事件并触发浏览器或服务端工具 | 检查事件到执行回调之间是否还有一层默认拒绝 |

版本清单应记录实际安装版本与锁文件，不用“latest”代替部署证据。

## 用 mock 验证，而不是拿生产工具试错

构造一个模拟 Provider：请求声明 `none`，响应却故意返回工具调用。测试至少确认：

- 服务端工具回调执行次数为 0；
- 流中没有可触发客户端工具的调用片段；
- 违规调用进入明确错误分支；
- repair 或自动重试不会把被禁止的调用重新变成可执行调用；
- 普通文本仍可通过；
- 已产生的用量可以记录，但业务结果应标记为失败或受控降级。

这些检查不需要 API 密钥，也不应连接真实供应商。测试的目标不是证明模型“永不犯错”，而是证明模型出错时应用仍不会执行越权动作。

## 执行层还要保留哪些门

`toolChoice` 是请求约束，不是完整的授权系统。涉及付款、删除、发消息、写数据库等副作用时，还应保留：

- 允许执行的工具白名单；
- 参数类型、范围与资源归属校验；
- 调用者权限检查；
- 幂等键与重复执行保护；
- 高风险动作的人为确认或二次授权。

更稳妥的原则是：模型负责提出动作，应用负责决定动作是否有权执行。

## 验证状态与限制

本文依据 Vercel 官方发布说明、文档与合并 PR 核实，未调用付费 API，也未对 CodingRouter 接口做线上测试。配套离线样例正在 [Issue #9](https://github.com/CodingRouter-zane/codingrouter-cookbook/issues/9) 跟踪；当前草稿 PR 未满足全部验收条件，因此不作为本文的本地验证证据。

官方来源：

- [Vercel AI SDK 5.0.281 release](https://github.com/vercel/ai/releases/tag/ai%405.0.281)
- [修复 PR #23846](https://github.com/vercel/ai/pull/23846)
- [AI SDK 工具调用文档](https://github.com/vercel/ai/blob/main/content/docs/03-ai-sdk-core/15-tools-and-tool-calling.mdx)

资料核实：2026-10-26（北京时间）。

后续项目改进：配套 mock 示例只有在技术 PR 与免费离线验证均满足 Issue #9 后才会进入 main。
