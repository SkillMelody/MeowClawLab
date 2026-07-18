# openclaw-verified-upgrade

A reliability-first OpenClaw upgrade skill.

This skill treats an upgrade as one evidence-backed transaction, not as “run an update command and hope.” Its bundled guard records state and authorization boundaries but never invokes OpenClaw, a service manager, or another program.

## Naming

- ClawHub slug and install identifier: `upgrade-openclaw-safely`
- Local OpenClaw skill key: `openclaw-verified-upgrade`
- Display name: `OpenClaw Verified Upgrade`

The public slug differs because the `openclaw-*` registry namespace is protected. This mapping is intentional and does not create a second local skill.

## When to use

Use this skill when you want to:

- Upgrade OpenClaw safely.
- Choose between latest, a specific version, or a recommended stable version.
- Check release notes before upgrading.
- Avoid breaking a running Gateway, channel, plugin, model, or agent route.
- Recover from a partial or failed OpenClaw upgrade.

## Core idea

**An OpenClaw upgrade is not complete until the running Gateway is verified healthy.**

The skill explicitly distinguishes:

- CLI/package version
- Running Gateway/runtime version
- Service manager path, such as LaunchAgent/systemd/manual process
- Config validity
- Plugin/channel/agent availability
- User-critical workflows

This matters because the CLI can be upgraded while an existing Gateway process continues running an older version.

## Transaction flow

The user should only need to choose:

```text
1. Recommended stable version (default)
2. Latest version
3. Specific version
```

The agent then follows a bounded transaction:

1. Detect the current environment.
2. Discover current OpenClaw commands and semantics.
3. Pick or verify a target version.
4. Review release notes and upgrade risks.
5. Build a checklist of user-critical paths.
6. Check pre-upgrade health.
7. Create a verified local backup.
8. Ask for final confirmation before mutation.
9. Arm and execute the core update once.
10. Record the observed package version even if the command exits non-zero.
11. Classify failures and resume from persisted state instead of rerunning the update.
12. Arm at most one separately approved service action.
13. Collect repeated readiness observations and compute stability.
14. Report evidence or stop safely with a recovery plan.

## Key safeguards

- Latest is not automatically best.
- OpenClaw commands and flags are version-sensitive.
- Command discovery must happen before command execution.
- Command existence is not enough; command semantics must be confirmed.
- Release notes and migration risks must be reviewed before upgrade.
- Backup must be created and read-back verified before mutation.
- One approval does not authorize every recovery action.
- A transaction may begin the core update only once.
- A transaction may arm only one service lifecycle action.
- Target version already present means post-update recovery, never a second full update.
- Retry logic must be failure-classified and capped.
- Rollback requires prior explicit authorization unless already granted.
- Success requires evidence, not just exit code 0.
- Destructive cleanup, config overwrite, daemon edits, reinstall, downgrade, `sudo`, and stop+start each require separate explicit approval.

## Backup requirements

Before changing anything, the agent should create a timestamped local backup manifest containing at least:

- OpenClaw config file.
- Current CLI version/path.
- Gateway/service status.
- Service command/path and running process path when available.
- Config validation result.
- Install/package metadata.
- Critical path baseline.
- Target version and release-risk summary.

If backup creation or read-back verification fails, the upgrade must stop.

## Verification requirements

After upgrade, the agent must verify:

- CLI/package version equals the target.
- Running Gateway/runtime version equals the target, or provide equivalent runtime evidence.
- Running process path matches the upgraded installation.
- Gateway status/connectivity is healthy.
- Config validation or doctor-equivalent check passes.
- Logs show no fresh fatal startup errors.
- Important plugins/channels/agents/routes still work.
- A minimal end-to-end check passes when safe and supported.
- At least three samples span 120 seconds or more with unchanged PID, binary path, and inode.
- Every service/port/RPC/application/channel layer passes, with no new fatal, external SIGTERM, or `source=update` delta.

## Failure behavior

If something fails, the skill requires the agent to:

- Stop mutation immediately.
- Classify the failure.
- Refresh current state before retrying.
- Retry only safe, bounded, recoverable steps.
- Preserve logs and evidence.
- Ask before rollback, config overwrite, daemon edits, reinstall, cleanup, sudo, or downgrade unless pre-authorized.

## Files

- [`SKILL.md`](./SKILL.md) — the actual OpenClaw skill document.
- [`scripts/upgrade-transaction.mjs`](./scripts/upgrade-transaction.mjs) — scanner-safe transaction state guard.
- [`references/transaction-contract.md`](./references/transaction-contract.md) — state, attempt, and completion contract.
- [`references/recovery-contract.md`](./references/recovery-contract.md) — failure taxonomy and recovery boundary.
- [`examples/test-prompts.json`](./examples/test-prompts.json) — current pressure prompts.
- [`test-prompts.json`](./test-prompts.json) — legacy compatibility prompts.

## Publishing note

This skill is intended to be reusable and GitHub-friendly. It should not contain local secrets, user-specific credentials, or hard-coded commands that imply universal compatibility across OpenClaw versions.
