# MeowClawLab

MeowClawLab is a small lab repository for practical OpenClaw skills, workflows, and operational playbooks.

The current focus is reliability-first automation: skills should be easy for ordinary users to invoke, but conservative enough for real systems where gateway availability, config safety, plugins, channels, and agent routing matter.

## Skills

| Skill | Purpose | Status |
| --- | --- | --- |
| [`openclaw-verified-upgrade`](./Skills/openclaw-verified-upgrade/) | A guided, evidence-based OpenClaw upgrade workflow that chooses a target version, checks release risk, creates verified backups, upgrades safely, and validates the running gateway plus critical user paths. | Initial release |

## Design principles

- **User-facing flow should be simple.** Ask only for the upgrade mode: recommended stable version, latest version, or a specific version.
- **Internal flow should be operationally strict.** Do command discovery, release-risk review, backup, controlled execution, and post-upgrade verification.
- **Latest is not automatically best.** Prefer a stable target unless the user explicitly asks for latest or latest fixes a relevant issue.
- **CLI version is not enough.** Always distinguish the installed CLI/package version from the actually running Gateway version.
- **Healthy process is not enough.** Validate config, Gateway health, key plugins/channels, agent routes, and user-critical workflows.
- **Consent matters.** Installing, updating, overwriting, or force-upgrading skills and system components requires explicit user approval.

## Repository layout

```text
MeowClawLab/
├── README.md
├── LICENSE
└── Skills/
    └── openclaw-verified-upgrade/
        ├── README.md
        └── SKILL.md
```

## Using a skill

Copy or install the desired skill directory into your OpenClaw skills path, then ask your agent to use it for the matching task.

For example, `openclaw-verified-upgrade` is intended for prompts like:

```text
Help me safely upgrade OpenClaw.
Upgrade OpenClaw to a stable version and make sure Gateway still works.
Upgrade OpenClaw to version 2026.x.x with backup and rollback planning.
```

## Safety note

These skills may describe operational workflows that affect a running OpenClaw Gateway. Treat upgrades, restarts, rollbacks, config repairs, daemon edits, and skill updates as state-changing actions that require clear authorization and verification.
