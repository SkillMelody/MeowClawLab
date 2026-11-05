# MeowClaw Lab

[中文](README.md)

Practical Agent workflows and reusable skills. This repository includes **PPT Smith**, for presentations you can keep editing, and **OpenClaw Verified Upgrade**, for upgrades backed by recovery materials, transaction tracking and runtime evidence.

> **For the latest PPT Smith source, installation, portfolio and updates, visit the [PPT-Smith repository →](https://github.com/SkillMelody/PPT-Smith).**
> **Star / Watch that repository** to follow PPT Smith. The PPT skill retained here is the **historical 3.0.2 version**, not the current mainline.

## PPT Smith portfolio

These are real artifacts and rendered previews already published in the dedicated repository. Its current public mainline is **5.3.0**; each example retains its original version and validation scope.

### Xiaomi 2025 Q2 and first-half business review · 36 slides

A complete business presentation spanning the executive summary, performance analysis, action schedule and management decisions. Click the overview to visit the full portfolio.

[![Real rendered overview of a 36-slide business-review template artifact](https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.3-xiaomi-2025-q2-h1-template-36page-overview.jpg)](https://github.com/SkillMelody/PPT-Smith#作品展示)

<table>
  <tr>
    <td width="33%" valign="top"><a href="https://github.com/SkillMelody/PPT-Smith#作品展示"><img src="https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.2-xiaomi-q2-h1-22page-overview.png" alt="22-slide decorative business review overview" width="100%"></a><br><strong>22-slide business review</strong><br>Varied composition with deck-wide consistency</td>
    <td width="33%" valign="top"><a href="https://github.com/SkillMelody/PPT-Smith#作品展示"><img src="https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.1-template-native-4page-2col-overview.png" alt="Four-slide native template component reuse comparison" width="100%"></a><br><strong>4-slide native template reuse</strong><br>Template language and native objects</td>
    <td width="33%" valign="top"><a href="https://github.com/SkillMelody/PPT-Smith#作品展示"><img src="https://raw.githubusercontent.com/SkillMelody/PPT-Smith/3d66f434001c544ff0ac79b7230586b3d0c1690a/assets/samples/v5.1-no-image-policy-page-01.png" alt="Cover from a six-slide policy presentation without image generation" width="100%"></a><br><strong>6-slide policy explanation</strong><br>Native design and actual previews</td>
  </tr>
</table>

[Explore the full portfolio, representative slides and downloadable examples →](https://github.com/SkillMelody/PPT-Smith#作品展示)

<details>
<summary>Provenance and validation limits</summary>

The 36-slide presentation is a user-provided template-route artifact. File inspection and real LibreOffice rendering passed for all 36 slides; this does not certify a new end-to-end generation run with 5.3.0. It contains native shapes, tables and images, with no native data charts. Shape-based data graphics must not be described as editable chart data. Financial facts were not reaudited, and PowerPoint/WPS edit-save-reopen was not tested.

The other examples come from earlier business, native-template and policy cases; they are not relabeled as 5.3.0 tests. Images reference a fixed public commit in the dedicated repository. Original inputs, the user's source deck and full run logs are not uploaded here. See that repository for evidence and case-specific limits.

</details>

## PPT Smith: from materials to editable presentations

Use articles, research reports, PRDs, business data, approved designs or native corporate PPTX templates. The model interprets content and designs pages; fixed tools generate, edit and verify the files.

| Task | Workflow |
| --- | --- |
| Design a presentation from source materials | **create**: plan the narrative, build native pages, render and review |
| Rebuild an approved complete slide design | **recreate**: reconstruct native objects against a frozen design target |
| Preserve an existing native PPTX template | **template**: select, clone and edit source pages while retaining template assets and relationships |

**What changed in 5.3.0:**

- **Edit actual template pages:** clone source layouts, masters and themes before updating text, supported charts/tables, notes and page order.
- **Resume local revisions:** stable slide IDs, frozen templates and revision checks identify the current candidate.
- **Bind evidence to the candidate:** check template preservation, real rendering and independent page review separately. Missing or stale evidence cannot establish final delivery.
- **Keep existing workflows compatible:** retain create / recreate / template and the existing component workflow. Image generation remains optional.

Supported objects, operating systems and target-application acceptance limits are documented in the dedicated repository. Native objects or a successful render alone do not prove every editing capability in the target application.

[Get the latest Skill, examples and installation checks →](https://github.com/SkillMelody/PPT-Smith)
[Read about the historical 3.0.2 copy in this Lab](Skills/article-html-to-ppt/README.en.md)

## OpenClaw Verified Upgrade · 2.0.0

[`openclaw-verified-upgrade`](Skills/openclaw-verified-upgrade/README.md) assesses releases, executes authorized upgrades and preserves evidence to diagnose failures and recovery boundaries. Acceptance covers the actual Gateway, plugins, configuration and critical workflows.

**This release adds:**

- **Official durable transactions:** prefer the official updater and follow the original runId; distinguish core replacement from same-version plugin maintenance.
- **Complete recovery coverage:** inventory config, credentials, shared/Agent databases, historical stores, related archives and recoverable old core/plugin payloads.
- **Approved runtime phases:** prepare private Node, verify real process paths and use the documented external update path only when its conditions hold.
- **Evidence from the intended route:** verify runtime plugin load, primary-model receipts, memory/Wiki and semantic changes in SQLite-backed jobs.
- **Full observation and scoped cleanup:** preserve failures across the agreed interval; remove only authorized, proven-redundant run-owned objects after acceptance.

An upgrade does not implicitly enable automatic updates. Installation success is not runtime acceptance. The old transaction guard remains for historical compatibility; assessment, skill maintenance and host upgrades have distinct authority boundaries.

The local Skill name is `openclaw-verified-upgrade`. Both marketplaces use the installation slug `upgrade-openclaw-safely`:

```bash
clawhub install upgrade-openclaw-safely
skillhub install upgrade-openclaw-safely --namespace user_9c58aca4
```

[ClawHub listing](https://clawhub.ai/skillmelody/upgrade-openclaw-safely) · [Skill guide and offline scenarios](Skills/openclaw-verified-upgrade/README.md)

Source and public marketplace versions are verified separately. An upload receipt is not review approval; check the actual version and review status before installing.

## Project locations and licenses

| Content | Current location | License |
| --- | --- | --- |
| PPT Smith mainline · 5.3.0 | [Dedicated PPT-Smith repository](https://github.com/SkillMelody/PPT-Smith) | Its own license applies; currently Apache-2.0 |
| Historical Lab PPT skill · 3.0.2 | [Historical directory](Skills/article-html-to-ppt/) | Existing non-commercial terms retained |
| OpenClaw Verified Upgrade · 2.0.0 | [Skill directory in this repository](Skills/openclaw-verified-upgrade/) | [MIT-0](Skills/openclaw-verified-upgrade/LICENSE.md) |

Other project-owned repository content retains the [MeowClaw Lab Non-Commercial Source License](LICENSE). Only the upgrade skill directory is separately licensed under MIT-0. Third-party components retain their own licenses. The historical PPT directory and the dedicated repository do not replace each other's license terms.

Maintained by **MeowClaw Lab / SkillMelody**.
