# MeowClaw Lab

[English](README.en.md)

面向 Agent 的实用工作流与可复用技能。当前收录 **PPT Smith** 和 **OpenClaw Verified Upgrade**：前者把材料整理成可继续编辑的演示文稿，后者以备份、事务跟踪和运行证据完成 OpenClaw 升级。

> **PPT Smith 的最新源码、安装、作品和后续更新，请前往 [PPT-Smith 独立仓库 →](https://github.com/SkillMelody/PPT-Smith)。**
> 想持续关注 PPT Smith，请在独立仓库 **Star / Watch**。本仓库保留的 PPT 技能为 **3.0.2 历史版本**，不代表当前主线。

## PPT Smith 作品集

以下展示来自独立仓库已公开的真实作品与渲染图。当前公开主线为 **5.3.0**；各作品保留其原始版本与验证范围。

### 小米集团 2025Q2 及上半年经营复盘 · 36 页

从经营摘要、指标拆解到行动排期与管理层决策，展示完整的商务汇报结构。点击总览，前往完整作品集。

[![36页经营复盘模板路线成稿真实渲染总览](https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.3-xiaomi-2025-q2-h1-template-36page-overview.jpg)](https://github.com/SkillMelody/PPT-Smith#作品展示)

<table>
  <tr>
    <td width="33%" valign="top"><a href="https://github.com/SkillMelody/PPT-Smith#作品展示"><img src="https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.2-xiaomi-q2-h1-22page-overview.png" alt="22页经营复盘装饰商务汇报总览" width="100%"></a><br><strong>22 页装饰商务汇报</strong><br>内容构图变化与整册一致性</td>
    <td width="33%" valign="top"><a href="https://github.com/SkillMelody/PPT-Smith#作品展示"><img src="https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.1-template-native-4page-2col-overview.png" alt="4页原生模板组件复用对照" width="100%"></a><br><strong>4 页原生模板复用</strong><br>保留模板语言与原生对象</td>
    <td width="33%" valign="top"><a href="https://github.com/SkillMelody/PPT-Smith#作品展示"><img src="https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.1-no-image-policy-page-01.png" alt="6页无生图政策解读作品中的封面" width="100%"></a><br><strong>6 页无生图政策解读</strong><br>原生对象设计与实际预览</td>
  </tr>
</table>

[查看完整作品、代表页与可下载样例 →](https://github.com/SkillMelody/PPT-Smith#作品展示)

<details>
<summary>作品来源与验证边界</summary>

36 页作品是用户提供的模板路线成稿，已完成文件核对和 LibreOffice 36/36 页真实渲染；这不是本轮重新执行 5.3.0 完整生成过程的证明。稿件包含原生形状、表格与图片，没有原生数据图表，不能宣称图形表达均可编辑图表数据。未重新审计财务事实，也未完成 PowerPoint/WPS 编辑、保存、重开验收。

其余作品分别来自更早的商务实测、模板组件复用和政策解读案例，不统一改标为 5.3.0。图片固定引用独立仓库公开提交，原始资料、用户原稿及完整运行日志不随本仓库上传。详细证据和每个案例的限制见独立仓库。

</details>

## PPT Smith：从材料到可编辑演示文稿

适合文章、研究报告、PRD、经营数据、已批准设计图，以及公司或客户的原生 PPTX 模板。由模型理解内容和设计页面，固定工具生成、编辑并核验文件。

| 需求 | 制作方式 |
| --- | --- |
| 从资料原创设计演示 | **create**：组织叙事、设计原生页面，真实渲染与审核 |
| 重建已批准的完整设计 | **recreate**：对照冻结的设计目标进行原生重建 |
| 保留原生 PPTX 模板 | **template**：选择、复制并编辑源页，保留模板资产与页面关系 |

**5.3.0 的主要变化：**

- **原页模板编辑**：从真实源页克隆布局、母版与主题，再更新文字、支持的图表/表格、备注及页序。
- **局部修订可接续**：稳定页 ID、冻结模板和 revision 检查，让修订有明确的当前版本。
- **验证对应当前候选**：分别检查模板保留底线、真实渲染和独立逐页审核；缺失或过期证据不等于正式交付。
- **兼容既有任务**：继续保留 create / recreate / template 三个入口与已有组件流程；生图是可选能力。

工具支持的对象、操作系统和办公软件验收范围以独立仓库说明为准。原生对象或成功渲染，不单独代表目标软件中的全部编辑能力。

[获取最新 Skill、使用示例和安装自检 →](https://github.com/SkillMelody/PPT-Smith)
[Lab 内 3.0.2 历史版本说明](Skills/article-html-to-ppt/README.md)

## OpenClaw Verified Upgrade · 2.0.0

[`openclaw-verified-upgrade`](Skills/openclaw-verified-upgrade/README.zh-CN.md) 用于评估版本、执行已授权升级，以及在失败后保留证据、定位恢复边界。验收覆盖实际运行的 Gateway、插件、配置和关键工作流。

**此次更新：**

- **官方持久事务**：优先采用官方升级器，跟进原 runId；区分核心包替换与同版本插件维护。
- **完整恢复覆盖**：核对配置、认证、共享与 Agent 数据库、历史库、关联归档和旧程序/插件恢复材料。
- **按批准阶段切换运行时**：支持私有 Node 准备、实际进程路径核实，以及满足条件的官方外部升级流程。
- **验证真正使用的链路**：检查插件实际加载、主模型回执、记忆/Wiki，以及 SQLite 中的任务语义变化。
- **完整观察与限定清理**：保留整个约定窗口的故障证据；仅在验收后按授权删除本轮已证明冗余的对象。

不会因为一次升级就开启自动更新，也不把安装成功等同于运行验收通过。旧事务守卫仅供历史记录兼容；评估、技能维护和真实主机升级有各自的授权范围。

本地 Skill 名为 `openclaw-verified-upgrade`；两个平台的安装标识均为 `upgrade-openclaw-safely`：

```bash
clawhub install upgrade-openclaw-safely
skillhub install upgrade-openclaw-safely --namespace user_9c58aca4
```

[ClawHub 条目](https://clawhub.ai/skillmelody/upgrade-openclaw-safely) · [技能说明与离线场景](Skills/openclaw-verified-upgrade/README.zh-CN.md)

源码版本与平台公开版本分别核验，上传回执不代表审核完成；安装前以平台实际版本和审核状态为准。

## 项目定位与许可

| 内容 | 最新入口 | 许可 |
| --- | --- | --- |
| PPT Smith 当前主线 · 5.3.0 | [PPT-Smith 独立仓库](https://github.com/SkillMelody/PPT-Smith) | 以独立仓库为准，当前为 Apache-2.0 |
| Lab 内 PPT 技能 · 3.0.2 | [历史目录](Skills/article-html-to-ppt/) | 保持既有非商用许可 |
| OpenClaw Verified Upgrade · 2.0.0 | [本仓库技能目录](Skills/openclaw-verified-upgrade/) | [MIT-0](Skills/openclaw-verified-upgrade/LICENSE.md) |

仓库其他自有内容继续适用 [MeowClaw Lab 非商用源码许可证](LICENSE)。仅升级技能目录单独按 MIT-0 授权；第三方组件保留各自许可。此处的 PPT 历史目录与独立仓库不互相替代其许可。

由 **MeowClaw Lab / SkillMelody** 维护。
