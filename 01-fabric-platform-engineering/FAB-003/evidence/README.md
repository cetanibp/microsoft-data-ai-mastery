# FAB-003 evidence

This folder contains and will continue to collect sanitized, reproducible evidence for reconciliation, quality decisions, quarantine behavior, and watermark protection.

## Current evidence

- [local contract-test output](local-contract-test-results.json): 30 tests passed with no failures or errors;
- [GitHub Actions run 33462357520](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33462357520): 30 tests passed and sanitized evidence was retained as a workflow artifact;
- [GitHub Actions run 33568120779](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33568120779): 33 tests passed, including generated-pipeline ordering and workspace-identifier sanitization;
- [GitHub Actions run 33576595412](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33576595412): 33 tests passed after adding the sanitized synthetic duplicate window.

## Live Fabric checkpoint — 2026-09-01

- Reused the isolated `Northstar Data Platform - FAB-002` workspace and switched it to `feature/fab-003-quality-gates` only after confirming there were no uncommitted workspace changes.
- Created the development Lakehouse `lh_northstar_data` and attached it as the default for both FAB-002 and FAB-003 notebooks.
- Confirmed all nine FAB-003 SQL objects were deployed in `sqldb_northstar_control`: three tables, one operational view, and five stored procedures.
- Created and validated `PL_FAB003_QualityGate` from the proven FAB-002 pipeline. The direct completion activity was removed and replaced by policy resolution, quality evaluation, idempotent SQL result/quarantine persistence, durable decision finalization, and conditional use of the quality-accepted watermark wrapper.
- The initial preflight run exposed a platform binding detail: an empty optional pipeline parameter arrived as null. The `quality_test_mode` mapping now normalizes null to an empty string with `coalesce`.
- The preflight candidate was explicitly abandoned through `ops.usp_FailWatermarkAttempt`; its committed watermark remained `2026-08-30T12:18:00Z`.
- The corrected baseline run to the synthetic upper boundary `2026-08-30T12:20:00Z` completed successfully through the quality-enabled pipeline. Durable evidence showed `ACCEPTED`, four passing blocking rules, a committed candidate, and state version `5`.
- The controlled `BLOCK_TARGET_COUNT` run produced one failed `TARGET_COUNT` rule, a durable `BLOCKED` decision, an abandoned candidate with `QUALITY_GATE_BLOCKED`, and no watermark advancement.
- Replaying the same `12:20` to `12:21` boundary without failure injection succeeded, committed the recovered candidate, and advanced state exactly once to version `6`.
- A `12:21` to `12:23` synthetic window extracted two versions of one business key, accepted the latest row, persisted one `DUPLICATE_BUSINESS_KEY` quarantine record containing only 64-character hashes, and committed state version `7`.
- Replaying the identical quarantine write for the same object run retained one row and one distinct deterministic quarantine ID.
- The existing `reference-count-warning` contract was evaluated live in an isolated Delta evidence table: observed target variance `50`, threshold `LE 1`, result `WARN`, decision `ACCEPTED_WITH_WARNING`, zero blocking failures, and watermark eligibility retained. It was intentionally not persisted as a SQL decision because release `1.0.0` does not assign that policy to the encounter object.
- Fabric Git captured the generated pipeline and Lakehouse items. Notebook auto-binding initially exposed a physical workspace identifier; the repository definitions were sanitized, pipeline contract coverage was added, and CI passed with 33 tests.

## Completion summary

- Accepted, blocked, recovery-replay, hashed quarantine, same-object-run idempotency, operational review, and isolated warning behavior are validated.
- The generated Pipeline and Lakehouse definitions are committed, notebook physical bindings are sanitized, and 33 automated tests pass.
- Final decisions, lessons, limitations, and the Issue #9 handoff are recorded in [RETRO.md](../RETRO.md).

## Sanitization

Do not commit credentials, endpoints, workspace or item identifiers, connection values, patient data, proprietary schemas, or raw source/quarantine payloads. Use stable synthetic keys and hashes where correlation evidence is required.
