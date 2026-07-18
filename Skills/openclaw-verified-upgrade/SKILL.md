---
name: "openclaw-verified-upgrade"
description: "Use when upgrading OpenClaw or recovering from partial updates, gateway failures, migrations, service drift, channel failures, or version mismatch."
---

# OpenClaw Verified Upgrade

## Core Contract

Treat each upgrade as one evidence-backed transaction. Completion requires the selected package version, running gateway, configuration, critical routes, and a stability window.

Use the bundled transaction guard before a core package mutation. The guard never executes commands. Supply facts already verified from the current CLI and help output:

    node {baseDir}/scripts/upgrade-transaction.mjs plan \
      --target <exact-version> \
      --cli-path <absolute-path> \
      --cli-version <current-version> \
      --capabilities tag,no-restart,yes,json

Read references/transaction-contract.md and references/recovery-contract.md before apply, recovery, or rollback.

## Hard Invariants

1. One run may begin the core update at most once. Record refused reentry without overwriting the original running or terminal state.
2. If the observed package version equals the target, never run another full update command.
3. Never call control-plane update.run from a Skill-controlled transaction.
4. Discover current command help before using version-sensitive flags.
5. Use no-restart only when current help proves support; keep package mutation and gateway lifecycle separate.
6. No verified backup, no core mutation.
7. Stop for another updater, incomplete handoff, active transaction lock, or repeated unexplained source=update.
8. The Skill is the sole gateway lifecycle owner for its transaction.
9. Use at most one service reconciliation action per approval. Never chain install, start, and restart.
10. A ready line is not completion; require repeated stability checks.
11. Failure freezes mutation. Preserve evidence and obtain separate approval for recovery or rollback.
12. Never auto-delete state, sessions, migration sources, databases, plugins, skills, credentials, or service definitions.
13. Never use sudo for user-level service repair.
14. Never claim success without fresh evidence.

## Modes

- plan: discovery plus transaction record; default when the user only says upgrade.
- apply: one approved core update attempt, then separately controlled service reconciliation.
- status: inspect a run without mutation.
- recover: classify and propose one recovery action; action-specific approval is required.
- rollback: always separate approval; package and configuration rollback are distinct.
- collect: gather bounded, redacted evidence with existing safe tools; do not repair.

The guard implements plan, status, begin-core, record-core, classify, resume, begin-service, record-service, observe, and finish. It writes structured state and authorization records but never invokes OpenClaw, a service manager, or another program.

## Workflow

### Discover and Review

Record CLI path/version, install source, package root, config/state paths, service manager and command, gateway process/path/version, plugins/channels, active work, update settings, restart-log cursor, and critical user routes.

Read current help for update, backup, doctor, gateway lifecycle/status, and channel status. Record supported flags and success semantics. Do not infer capabilities.

Resolve vague stable/latest requests to an exact version. Review release, runtime, configuration, migration, gateway, plugin, channel, model/auth, and rollback impact. Risk is LOW, MEDIUM, HIGH, or BLOCKER.

Define the pre-upgrade baseline and critical paths. If degraded, repair first or obtain explicit approval to continue against a named degraded baseline.

### Plan

Run plan with the exact target and verified CLI snapshot. Keep the run id. Review the stored fingerprint, backup plan, downtime, and recovery limits.

Create and verify a narrow backup using commands proven by current help. Verify exit status, archive existence, non-zero size, manifest, and read-back. Record inclusions and exclusions.

Present current version, target, risk, downtime, verified backup, rollback authority, critical checks, and run id. Wait for explicit apply approval.

### Arm and Execute Once

Immediately before the core command, resample CLI path/version and help capabilities, then pass the same fields to begin-core:

    node {baseDir}/scripts/upgrade-transaction.mjs begin-core \
      --run <run-id> --confirm <run-id> \
      --cli-path <absolute-path> \
      --cli-version <current-version> \
      --capabilities tag,no-restart,yes,json

If refused, stop. Never bypass the guard or create a replacement run just to retry.

Execute exactly the returned command array without shell concatenation.

After execution, resample the installed package version even on non-zero exit:

    node {baseDir}/scripts/upgrade-transaction.mjs record-core \
      --run <run-id> --exit-code <code> --observed-version <version>

Target present plus later failure means post-update recovery, not a second update.

### Classify, Resume, and Reconcile Once

Record a fresh failure classification before recovery:

    node {baseDir}/scripts/upgrade-transaction.mjs classify \
      --run <run-id> --kind <classification> --evidence <bounded-reference>

After interruption or gateway restart, call resume. It returns a decision but never executes it:

    node {baseDir}/scripts/upgrade-transaction.mjs resume --run <run-id>

Inspect the service definition and process. Choose one action only: restart when correct and loaded; install when missing; force-install with separate approval for definition drift; or observe if already starting.

Arm the one approved action before executing it with current, verified CLI semantics:

    node {baseDir}/scripts/upgrade-transaction.mjs begin-service \
      --run <run-id> --confirm <run-id> --action <install|restart|force-install|bootout>

Record its result immediately:

    node {baseDir}/scripts/upgrade-transaction.mjs record-service \
      --run <run-id> --result <pass|fail>

The guard permits one service action total. Never chain lifecycle actions.

### Verify and Observe

Record at least three real observations spanning 120 seconds. Use stable process identity and all readiness layers:

    node {baseDir}/scripts/upgrade-transaction.mjs observe \
      --run <run-id> --at <ISO-8601> --gateway-pid <pid> \
      --binary-path <absolute-path> --binary-inode <inode> \
      --service pass --port pass --rpc pass --app pass --channels pass \
      --fatal no --sigterm no --source-update-count <count>

The guard computes stability from the samples. It requires unchanged PID/path/inode, every readiness layer passing, no fatal or external SIGTERM, and no increase in source=update evidence.

Record completion only with all gates:

    node {baseDir}/scripts/upgrade-transaction.mjs finish \
      --run <run-id> --cli pass --gateway pass --rpc pass \
      --config pass --channels pass

## Failure Routing

Classify before mutation:

- UPDATE_COMPETITION: another updater, lock, or incomplete handoff.
- CORE_UPDATE_FAILED: target package is absent.
- CORE_APPLIED_WITH_POST_FAILURE: target is installed but later checks fail.
- MIGRATION_NOTICE: non-blocking; record only.
- MIGRATION_LOCKED: do not restart, fix, or remove the lock.
- MIGRATION_BLOCKED: gateway refuses ready; freeze and propose precise recovery.
- SERVICE_DEFINITION_DRIFT: service and CLI/runtime paths or arguments differ.
- GATEWAY_EXTERNAL_SIGTERM: ready followed by clean external termination.
- READINESS_FAILED: process or port exists but RPC/application checks fail.
- STABILITY_FAILED: repeated samples are not stable.
- MANUAL_INTERVENTION_REQUIRED: action budget is exhausted or safe automation is unavailable.

Recovery, rollback, configuration restoration, migration-source rename, plugin disable/update, force install, and credential repair each require separate approval.

For duplicate legacy migration sources, use only a path explicitly named by logs, verify realpath is inside an allowed root, back up the single target, and propose a timestamped rename. Never delete databases or use broad globs.

Default orphan transcript cleanup to No unless proven to block the transaction and separately authorized.

## Final Report

Report result, from/to versions, run id, target rationale, backup, CLI and gateway paths/versions, service manager, configuration/doctor results, critical paths, stability, commands, attempt counts, classifications, rollback state, remaining risks, and required user action.

If a check was not run, say not checked.
