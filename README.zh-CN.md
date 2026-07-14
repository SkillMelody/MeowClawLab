# MeowClawLab

> English version: [README.en.md](./README.en.md)

MeowClawLab 是一个面向 OpenClaw 的实验仓库，用来沉淀实用技能、工作流和运维型 playbook。

当前重点是“可靠优先”的自动化：技能要让普通用户容易使用，同时在真实系统中足够保守，能保护 Gateway 可用性、配置安全、插件、频道、agent 路由和最终交付质量。

## 技能列表

| 技能 | 用途 | 状态 |
| --- | --- | --- |
| [`openclaw-verified-upgrade`](./Skills/openclaw-verified-upgrade/) | 带验证链路的 OpenClaw 安全升级技能：选择目标版本、检查版本风险、创建可验证备份、安全升级，并验证运行中的 Gateway 与关键用户链路。 | 已发布 |
| [`article-html-to-ppt`](./Skills/article-html-to-ppt/) | 将文章、Markdown、HTML、公众号草稿或审稿通过的长文转成正式、品牌一致的演示稿，并支持 HTML 预览、PPTX / 飞书幻灯片导出路径与交付验证。 | 已发布 |

## 今日重点样例：复杂图 PPT 升级

`article-html-to-ppt` 近期重点升级了复杂图解能力：不再只生成僵硬的直线和模板色块，而是支持更接近正式咨询稿的原生 PPT 图形。

本次用 McKinsey / QuantumBlack 的 *The State of AI in 2025* 公开报告做压力测试，生成了一套 14 页图解 deck：

- **0 张栅格贴图作为正文页**：核心文本、卡片、表格、节点、箭头和关系图均为 PPT 原生对象。
- **302 段可编辑文本**：便于后续在 PowerPoint、Keynote 或 Feishu Slides 中继续修改。
- **复杂关系图增强**：补齐曲线箭头、虚线、折线、肘线、双箭头等图元，用于飞轮、反馈回路、分层架构和因果链。
- **配色契约升级**：五套风格的默认色从荧光蓝/紫/金/橙和死白背景，升级为低饱和、有色温、克制的配色体系。

![State of AI 2025 14-page PPT sample](./Assets/article-html-to-ppt/stateofai-2025-final-contact-sheet.png)

![Palette upgrade overview](./Assets/article-html-to-ppt/palette-upgrade-overview.png)

![Native editable architecture diagram](./Assets/article-html-to-ppt/native-architecture-diagram.png)

## 设计原则

- **用户入口要简单。** 普通用户只需要表达目标，不应该被迫理解底层命令、平台权限和交付格式细节。
- **内部流程要严格。** 执行前必须做能力检查、风险评估、必要备份、受控执行和结果验证。
- **最新不等于最好。** 对升级类任务，除非用户明确要求 latest，或 latest 修复了当前相关问题，否则优先推荐相对稳定版本。
- **创建成功不等于最终完成。** 对文档、幻灯片、视频、应用等交付物，要区分 `Created`、`Rendered`、`Read back` 和 `Final`。
- **来源边界要清楚。** 外部文章、图片、截图、复原图和引用内容必须保留使用边界，不能把参考材料包装成自有事实。
- **授权边界要清楚。** 安装、更新、覆盖、强制升级、重启、回滚、上传、发布等状态变更都需要明确授权。

## 仓库结构

```text
MeowClawLab/
├── README.md
├── README.en.md
├── README.zh-CN.md
├── LICENSE
└── Skills/
    ├── article-html-to-ppt/
    │   ├── README.md
    │   ├── SKILL.md
    │   ├── skill-card.md
    │   ├── references/
    │   └── templates/
    └── openclaw-verified-upgrade/
        ├── README.md
        ├── README.zh-CN.md
        ├── SKILL.md
        └── test-prompts.json
```

## 如何使用技能

把需要的技能目录复制或安装到 OpenClaw 的 skills 路径中，然后让 agent 在匹配任务时使用该技能。

例如，`openclaw-verified-upgrade` 适合这些请求：

```text
帮我安全升级 OpenClaw。
把 OpenClaw 升级到稳定版本，并确认 Gateway 还能正常工作。
把 OpenClaw 升级到 2026.x.x，升级前备份，失败时要有回滚计划。
```

`article-html-to-ppt` 适合这些请求：

```text
把这篇公众号文章转成飞书幻灯片。
把这份 Markdown 草稿做成正式品牌版 PPT。
先生成演示分镜和 HTML 预览，再导出到幻灯片。
```

## 安全提示

这些技能可能涉及运行中的 OpenClaw Gateway、外部平台、文档上传、幻灯片生成或公开发布。升级、重启、回滚、配置修复、daemon 修改、skill 更新、飞书上传、GitHub 发布等都属于状态变更操作，应在明确授权和验证后执行。
