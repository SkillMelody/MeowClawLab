# Recovery Contract

## Taxonomy

MIGRATION_NOTICE records only. MIGRATION_LOCKED, MIGRATION_BLOCKED, DUPLICATE_SOURCE_RECOVERABLE, UPDATE_COMPETITION, SERVICE_DEFINITION_DRIFT, GATEWAY_EXTERNAL_SIGTERM, READINESS_FAILED, STABILITY_FAILED, CORE_UPDATE_FAILED, CORE_APPLIED_WITH_POST_FAILURE, and MANUAL_INTERVENTION_REQUIRED freeze mutation.

A duplicate-source rename is never automatic. Propose one path-specific timestamped rename only after separate authorization, realpath containment, and backup verification. Never delete databases or use broad globs.

## Resume Boundary

resume can return VERIFY_BACKUP_AND_CONFIRM, RECORD_EXISTING_CORE_RESULT, RECONCILE_SERVICE_OR_OBSERVE, RECORD_EXISTING_SERVICE_RESULT, COLLECT_STABILITY_OBSERVATIONS, STOP_WITH_EVIDENCE, or NO_ACTION. These are decisions, not commands or approvals.

## Deferred Automation

This Skill intentionally does not embed a subprocess runner, temporary LaunchAgent, systemd unit, restart loop, migration renamer, installer, or rollback executor. Those host mutations require current command discovery, action-specific approval, bounded execution, and separate safety review.

Do not claim a full unattended Harness. Use the transaction guard with supervised execution until an independently reviewed coordinator satisfies those controls.
