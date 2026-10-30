# Release 页写“无需行动”，安全公告却是 CVSS 10.0：LiteLLM Enterprise 怎么升级？

Treat the security advisory—not the release summary—as the upgrade authority for affected Enterprise proxies.

资料核实：2026-10-30（北京时间）。本文只解读 LiteLLM 官方公开公告，未运行漏洞利用、未调用付费 API，也不代表 CodingRouter 使用或支持 LiteLLM。

如果你在运行带 Enterprise 许可证的 LiteLLM Proxy，不能只看普通 release 摘要决定是否升级。本文帮助你确认适用范围、选择修复版本，并在暂时不能升级时先缩小暴露面。

## 两个官方页面为什么看起来冲突

LiteLLM v1.106.5 的 release 页面列出日志与 GCS logger 变更，并对这些变更标注“无需行动”。但 2026-10-27 发布的安全公告 GHSA-w4c7-34wj-hqm8 将另一问题评为 **Critical / CVSS 10.0**，并把 1.106.5 列为 1.106 分支的修复版本。

这不是说 release 页面错误，而是两个页面回答的问题不同：普通 release 摘要描述所列功能变更；安全公告才是判断该漏洞影响范围和修复版本的依据。不能把一句“无需行动”扩大成“所有部署都无需安全升级”。

## 先确认你是不是受影响对象

官方公告限定了三个关键条件：

1. Proxy 运行时启用了 **Enterprise 许可证**；
2. 使用的版本低于对应维护分支的修复版本；
3. 攻击者能向任一 LLM 路由发送请求。这里不是只有管理后台才有风险。

公告说明，构造后的未认证请求可能让 Proxy 读取本地文件，并把内容发送到攻击者指定的 URL。若读取 `/proc/self/environ`，可能暴露 `LITELLM_MASTER_KEY` 和供应商 API Key；某些配置下还可能进一步造成以 root 执行任意 Python 代码。

无 Enterprise 许可证的开源部署不受这条公告影响，因为相关代码路径不会加载。这里的“Enterprise”指运行时许可证状态，不是团队规模。

## 按当前分支选择最低修复版本

| 当前维护分支 | 升级到至少 |
| --- | --- |
| 1.103 | 1.103.10 |
| 1.104 | 1.104.8 |
| 1.105 | 1.105.6 |
| 1.106 | 1.106.5 |

不要只改镜像标签后就宣布完成。记录升级前版本、目标版本、镜像 digest、配置差异和回滚点；在隔离环境验证鉴权、常用模型路由、日志与出站规则，再逐步切流。

如果从早于 1.106.3 的版本跨越升级，还要单独检查 Cosign 公钥轮换：新镜像使用 commit `e82a3c6` 中的公钥，固定旧公钥的 CI 或准入策略会验签失败。这是供应链验证问题，与本次 Enterprise 漏洞是否命中要分开判断。

## 不能马上升级时，先做三层收缩

官方给出的临时缓解包括：

- 在 WAF、Ingress 或反向代理拒绝或移除包含 `standard_callback_dynamic_params`、`gcs_path_service_account`、`callbacks`、`success_callback`、`failure_callback` 的 POST 请求体；
- 将 Proxy 出站网络限制到已配置的模型供应商端点，阻断向攻击者端点外传文件；
- 尽量不要把 Proxy 直接暴露在公网，可使用 VPN、mTLS、带认证的入口或 IP 白名单。

这些是临时防线，不是永久替代升级。公告还建议从 Secret Manager 加载主密钥、设置独立的 `LITELLM_SALT_KEY`，并持续使用出站白名单。

## 已经暴露过，升级并不等于旧密钥自动失效

如果受影响实例曾直接对外提供路由，或日志中出现可疑字段与异常出站请求，建议按可能泄露处理：先保全脱敏日志与时间线，再升级并轮换 LiteLLM 主密钥和相关供应商 API Key。密钥轮换是基于公告所述泄露后果的运营建议，不是本文对入侵事实的判断。

不要把环境变量、完整请求体、密钥或客户数据贴到公开 Issue。公开排错只保留版本、脱敏路径、时间和已执行的缓解措施。

## 发布边界

本文没有复现漏洞、没有扫描任何实例，也没有验证 CodingRouter 或读者环境是否使用 Enterprise 许可证。CVSS、受影响条件和修复版本均来自 LiteLLM 官方安全公告；未来若公告更新，应以官方页面为准。

## 官方来源

- [LiteLLM 安全公告 GHSA-w4c7-34wj-hqm8](https://github.com/BerriAI/litellm/security/advisories/GHSA-w4c7-34wj-hqm8)：影响范围、CVSS、修复版本与临时缓解。
- [LiteLLM v1.106.5 release](https://github.com/BerriAI/litellm/releases/tag/v1.106.5)：版本存在、发布时间及普通 release 摘要。

后续可把升级记录整理为脱敏检查模板。需要讨论网关部署时，可通过仓库主页公开渠道说明版本、网络边界和调用规模，勿公开密钥。
