# openclaw-verified-upgrade

一个可靠性优先的 OpenClaw 安全升级技能。

这个技能把升级视为一笔有证据的事务，而不是“跑一个 update 命令”。内置守卫只记录状态和授权边界，不会自行调用 OpenClaw、服务管理器或其他程序。

## 命名说明

- ClawHub slug / 安装标识：`upgrade-openclaw-safely`
- 本地 OpenClaw Skill key：`openclaw-verified-upgrade`
- 展示名：`OpenClaw Verified Upgrade`

公开 slug 不同，是因为 ClawHub 的 `openclaw-*` 命名空间受保护。这个映射是有意保留的，不会生成第二个本地 Skill。

## 什么时候使用

当你需要：

- 安全升级 OpenClaw。
- 在最新版、指定版本、推荐稳定版之间做选择。
- 升级前检查 release notes / changelog。
- 避免破坏正在运行的 Gateway、频道、插件、模型或 agent 路由。
- 从 OpenClaw 半升级、升级失败、Gateway 不健康等状态中恢复。

## 核心理念

**OpenClaw 升级是否完成，不看升级命令是否成功，而看运行中的 Gateway 是否真的健康可用。**

技能会明确区分：

- CLI / package 版本
- 正在运行的 Gateway / runtime 版本
- 服务管理器路径，例如 LaunchAgent / systemd / 手动进程
- 配置是否有效
- 插件、频道、agent 是否可用
- 用户关键工作流是否仍然可用

这很重要，因为 CLI 可能已经升级，但原来的 Gateway 进程仍然在运行旧版本。

## 事务流程

用户只需要选择升级方式：

```text
1. 推荐稳定版（默认）
2. 最新版
3. 指定版本
```

后续由 agent 按有上限的事务执行：

1. 识别当前环境。
2. 发现当前 OpenClaw 可用命令，并确认命令语义。
3. 选择或校验目标版本。
4. 阅读 release notes，评估升级风险。
5. 建立用户关键链路检查清单。
6. 检查升级前健康状态。
7. 创建并读回校验本地备份。
8. 在真正变更前请求最终确认。
9. 只允许一次核心升级尝试。
10. 即使命令非零退出，也先记录实际安装版本。
11. 失败先分类并从持久化状态恢复，不盲目重跑 update。
12. 最多武装一个单独授权的服务动作。
13. 收集多次 readiness 观测并计算稳定性。
14. 给出带证据的结果，或安全停止并提供恢复计划。

## 关键护栏

- 最新不等于最好。
- OpenClaw 命令和参数会随版本变化。
- 执行命令前必须先做命令发现。
- 命令存在不代表语义没有变化。
- 升级前必须检查 release notes 和 migration 风险。
- 变更前必须创建并读回校验备份。
- 一次授权不等于授权所有恢复动作。
- 单个事务最多开始一次核心升级。
- 单个事务最多武装一个服务生命周期动作。
- 目标版本已存在时进入升级后恢复，绝不再次完整更新。
- 重试必须基于失败分类，并且有次数上限。
- 除非提前授权，否则回滚前必须再次确认。
- 成功必须基于证据，而不是 exit code 0。
- 破坏性清理、覆盖配置、修改 daemon、重装、降级、`sudo`、stop+start 都需要单独明确授权。

## 备份要求

变更前，agent 应创建带时间戳的本地备份清单，至少包含：

- OpenClaw 配置文件。
- 当前 CLI 版本和路径。
- Gateway / service 状态。
- service command path，以及可用时的运行中进程路径。
- 配置校验结果。
- 安装方式 / 包管理器元数据。
- 关键链路的升级前基线。
- 目标版本和版本风险评估摘要。

如果备份创建失败，或无法读回校验，必须停止升级。

## 升级后验证要求

升级后，agent 必须验证：

- CLI / package 版本等于目标版本。
- 正在运行的 Gateway / runtime 版本等于目标版本，或提供等价运行时证据。
- 运行中进程路径和升级后的安装路径一致。
- Gateway 状态和连接探测健康。
- 配置校验或 doctor 等价检查通过。
- 日志中没有新的 fatal startup error。
- 关键插件、频道、agent、路由仍然可用。
- 在安全且支持的情况下，完成最小端到端检查。
- 至少三次采样覆盖 120 秒，PID、二进制路径和 inode 保持一致。
- service、port、RPC、application、channel 全通过，且没有新增 fatal、外部 SIGTERM 或 `source=update` 增量。

## 失败处理

如果升级失败，技能要求 agent：

- 立即停止继续变更。
- 对失败进行分类。
- 在任何重试前重新读取当前状态。
- 只重试安全、有限、可恢复的步骤。
- 保留日志和证据。
- 对回滚、覆盖配置、修改 daemon、重装、清缓存、sudo、降级等动作重新请求授权，除非用户已提前明确授权。

## 文件

- [`SKILL.md`](./SKILL.md) — 实际 OpenClaw skill 文档。
- [`README.md`](./README.md) — 英文说明。
- [`README.zh-CN.md`](./README.zh-CN.md) — 中文说明。
- [`scripts/upgrade-transaction.mjs`](./scripts/upgrade-transaction.mjs) — scanner-safe 事务状态守卫。
- [`references/transaction-contract.md`](./references/transaction-contract.md) — 状态、尝试次数和完成条件。
- [`references/recovery-contract.md`](./references/recovery-contract.md) — 失败分类和恢复边界。
- [`examples/test-prompts.json`](./examples/test-prompts.json) — 当前压力测试提示词。
- [`test-prompts.json`](./test-prompts.json) — 兼容保留的旧版提示词。

## 发布提示

这个技能适合复用和发布到 GitHub。不要在文档中包含本地密钥、用户专属凭据，或把某个版本的命令写成所有 OpenClaw 版本都通用。
