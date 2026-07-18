# Transaction Contract

The guard records transaction intent, classifications, service-action budgets, observations, and recovery decisions. It never invokes OpenClaw, a service manager, or another program.

## Nominal States

PLAN_READY -> CORE_UPDATE_RUNNING -> CORE_APPLIED -> SERVICE_ACTION_RUNNING -> SERVICE_RECONCILED -> COMPLETE

The service action is optional. CORE_APPLIED may proceed directly to observations and completion.

## Core Attempt and Resume

Plan fingerprints the verified CLI path, version, and capabilities. begin-core resamples them. The core counter increments before the command array is returned. A second begin fails without overwriting the prior state. Target present plus non-zero exit is CORE_APPLIED_WITH_POST_FAILURE, never permission for another full update.

classify accepts the documented taxonomy. MIGRATION_NOTICE records evidence without freezing; every other classification freezes mutation. Evidence is a bounded reference, not raw logs or secrets.

resume is read-only. It maps persisted state to a safe next decision, never resets budgets, and never authorizes mutation.

## Service Budget

begin-service requires matching run confirmation, CORE_APPLIED, and one of install, restart, force-install, or bootout. One run can arm one service action total. The agent executes the separately approved action using current help, then calls record-service.

## Stability and Completion

observe stores bounded samples. Completion requires at least three samples spanning 120 seconds, unchanged PID/path/inode, every readiness layer passing, no fatal or external SIGTERM, and no increase in source=update count.

finish computes the stable gate; it does not accept a supplied stability verdict. COMPLETE also requires CLI, gateway, RPC, config, and channel gates.

Store only structured state in the run directory. Keep logs, config content, chat text, and credentials outside it.
