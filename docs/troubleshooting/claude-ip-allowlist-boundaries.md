# 密钥加了 IP 白名单，就能拦住所有调用吗？Claude 覆盖范围与锁死检查

如果你负责 Claude API、Agent 或企业知识库的部署，IP 白名单看起来像一道简单保险：只允许公司网络访问，即使密钥泄露也难被异地滥用。真正的选择却是——限制太少，密钥仍有风险；限制太严，管理员、CI 和夜间任务可能一起被锁在门外。本文帮你在启用前完成范围判断、出口盘点和 403 排错。

> 资料核实日期：2026-11-09（北京时间）。以下是 Anthropic 官方公开能力，不代表 CodingRouter 已支持、透传或验证同等控制。

## 已核实事实

Anthropic 在 2026-11-05 的平台更新中公布 IP allowlist 公测。组织可填写公网 IPv4、IPv6 或 CIDR，最多 1,000 项；不在名单内的受保护请求会被拒绝，例如 Messages API 会返回 403 `permission_error`。保存后的变更最长可能需要 15 分钟生效。

它覆盖 Claude Console，以及 Claude Platform 的 Messages、Message Batches、Token Counting、Models、Files、Skills、部分 Managed Agents 端点和组织 API。但它不是“所有 Claude 流量”的总开关：不控制 Managed Agents 运行时自身的联网，也不适用于 Amazon Bedrock、Claude Platform on AWS、Google Cloud 或 Microsoft Foundry。

## 先判断：白名单解决什么，不解决什么

| 问题 | 白名单能否单独解决 |
| --- | --- |
| 泄露密钥被非授权公网地址使用 | 能降低风险，但只限覆盖端点 |
| 密钥长期有效、离职人员仍持有密钥 | 不能；还需短有效期或 Workload Identity Federation |
| Agent 运行时访问外部网站 | 不能；需单独配置运行时网络策略 |
| 云厂商托管的 Claude 调用 | 不能按此功能推定，需查看对应云平台控制 |
| 管理员会不会把自己锁死 | 会；必须预留恢复路径 |

因此，IP 白名单应被视为“请求来源边界”，而不是密钥轮换、身份治理或运行时防火墙的替代品。

## 启用前的五步检查

1. **盘点真实公网出口。** 列出生产机房、Kubernetes NAT、Serverless、CI、定时任务、VPN、办公室代理和管理员网络。不要填写 `10.0.0.0/8` 这类私网地址；要填写请求离开网络后的公网地址。双栈环境同时检查 IPv4 和 IPv6。
2. **保留紧急入口。** 官方提供允许管理员从任意地址进入白名单设置页的选项，可降低锁死风险；代价是管理员会话一旦被盗，攻击者也可能修改名单。是否开启应形成书面取舍，并保护管理员账号。
3. **分阶段启用。** 先覆盖主业务和一个低风险环境，保存后等待生效，再验证交互请求、批处理和每天或每周才运行一次的任务。
4. **把 403 当配置事件。** 看到 `permission_error` 时，先记录调用方公网出口、IPv6、代理路径和目标端点，不要直接增加无限重试；错误白名单不会因重试自动恢复。
5. **叠加密钥治理。** 为静态密钥设置短有效期和轮换流程；条件允许时改用 Workload Identity Federation。共享代理虽然方便，却会让所有经过它的调用看起来来自同一地址，应额外限制代理访问。

## 预期结果、失败与边界

启用成功后，名单内的受覆盖请求继续工作，名单外请求稳定返回拒绝；审计中能说明“哪个出口、访问哪个端点、为何被允许”。如果只有网页测试成功，而 CI、夜间任务或灾备区没有验证，验收仍不完整。

本文未登录 Claude Console、未调用真实或付费 API，也未验证 CodingRouter 的兼容性、覆盖范围或 SLA。官方能力仍处于公测，平台、端点和限制可能变化；正式上线前应重新核对文档。

## 官方来源

- [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview)
- [IP allowlisting](https://platform.claude.com/docs/en/manage-claude/ip-allowlist)
