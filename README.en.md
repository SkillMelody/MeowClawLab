# MeowClawLab

> 中文版本: [README.md](./README.md)

MeowClawLab is a small lab repository for practical OpenClaw skills, workflows, and operational playbooks.

The current focus is reliability-first automation: skills should be easy for ordinary users to invoke, while remaining conservative enough for real systems where Gateway availability, config safety, plugins, channels, agent routing, and final delivery quality matter.

## Skills

| Skill | Purpose | Status |
| --- | --- | --- |
| [`openclaw-verified-upgrade`](./Skills/openclaw-verified-upgrade/) | A guided, evidence-based OpenClaw upgrade workflow that chooses a target version, checks release risk, creates verified backups, upgrades safely, and validates the running Gateway plus critical user paths. | Published |
| [`article-html-to-ppt`](./Skills/article-html-to-ppt/) | Turns articles, Markdown drafts, HTML pages, WeChat drafts, and review-approved manuscripts into formal, brand-consistent slide decks with HTML preview, PPTX / Feishu Slides export paths, and verification handoff. | Published |

## Design Principles

- **User-facing flow should be simple.** Users should state the goal, not wrestle with low-level commands, platform permissions, or export mechanics.
- **Internal flow should be operationally strict.** Capability checks, risk review, backups when needed, controlled execution, and result verification should happen before completion is claimed.
- **Latest is not automatically best.** For upgrade workflows, prefer a stable target unless the user explicitly asks for latest or latest fixes a relevant issue.
- **Created does not mean final.** For docs, slides, videos, apps, and other deliverables, distinguish `Created`, `Rendered`, `Read back`, and `Final`.
- **Source boundaries matter.** External articles, images, screenshots, reconstructed visuals, and quoted material must keep their usage boundaries; reference material should not be presented as owned evidence.
- **Consent matters.** Installing, updating, overwriting, force-upgrading, restarting, rolling back, uploading, or publishing requires explicit authorization.

## Repository Layout

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

## Using A Skill

Copy or install the desired skill directory into your OpenClaw skills path, then ask your agent to use it for the matching task.

For example, `openclaw-verified-upgrade` is intended for prompts like:

```text
Help me safely upgrade OpenClaw.
Upgrade OpenClaw to a stable version and make sure Gateway still works.
Upgrade OpenClaw to version 2026.x.x with backup and rollback planning.
```

`article-html-to-ppt` is intended for prompts like:

```text
Turn this WeChat article into Feishu Slides.
Convert this Markdown draft into a formal brand-consistent PPT.
Create the presentation storyboard and HTML preview before exporting to slides.
```

## Safety Note

These skills may interact with a running OpenClaw Gateway, external platforms, document uploads, slide generation, or public publishing. Upgrades, restarts, rollbacks, config repairs, daemon edits, skill updates, Feishu uploads, and GitHub publishing are state-changing actions that require clear authorization and verification.
