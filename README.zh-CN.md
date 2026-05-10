# MeowClawLab

MeowClawLab 是一个面向 OpenClaw 的实验仓库，用来沉淀实用技能、工作流和运维型 playbook。

当前重点是“可靠优先”的自动化：技能要让普通用户容易使用，同时在真实系统中足够保守，能保护 Gateway 可用性、配置安全、插件、频道和 agent 路由。

## 技能列表

| 技能 | 用途 | 状态 |
| --- | --- | --- |
| [`openclaw-verified-upgrade`](./Skills/openclaw-verified-upgrade/) | 一个带验证链路的 OpenClaw 安全升级技能：选择目标版本、检查版本风险、创建可验证备份、安全升级，并验证运行中的 Gateway 与关键用户链路。 | 初始版本 |

## 设计原则

- **用户入口要简单。** 普通用户只需要选择：推荐稳定版、最新版，或指定版本。
- **内部流程要严格。** 执行命令前必须做命令发现、版本风险评估、备份、受控升级和升级后验证。
- **最新不等于最好。** 除非用户明确要求 latest，或 latest 修复了当前相关问题，否则优先推荐相对稳定版本。
- **CLI 版本不代表 Gateway 已升级。** 必须区分已安装的 CLI/package 版本和正在运行的 Gateway 版本。
- **进程健康不代表业务可用。** 还要验证配置、Gateway 健康、关键插件/频道、agent 路由和用户关键工作流。
- **授权边界要清楚。** 安装、更新、覆盖、强制升级、重启、回滚、修配置等状态变更都需要明确授权。

## 仓库结构

```text
MeowClawLab/
├── README.md
├── README.zh-CN.md
├── LICENSE
└── Skills/
    └── openclaw-verified-upgrade/
        ├── README.md
        ├── README.zh-CN.md
        └── SKILL.md
```

## 如何使用技能

把需要的技能目录复制或安装到 OpenClaw 的 skills 路径中，然后让 agent 在匹配任务时使用该技能。

例如，`openclaw-verified-upgrade` 适合这些请求：

```text
帮我安全升级 OpenClaw。
把 OpenClaw 升级到稳定版本，并确认 Gateway 还能正常工作。
把 OpenClaw 升级到 2026.x.x，升级前备份，失败时要有回滚计划。
```

## 安全提示

这些技能可能涉及运行中的 OpenClaw Gateway。升级、重启、回滚、配置修复、daemon 修改、skill 更新等都属于状态变更操作，应在明确授权和验证后执行。
