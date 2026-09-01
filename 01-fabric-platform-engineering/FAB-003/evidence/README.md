# FAB-003 evidence

This folder contains and will continue to collect sanitized, reproducible evidence for reconciliation, quality decisions, quarantine behavior, and watermark protection.

## Current evidence

- [local contract-test output](local-contract-test-results.json): 30 tests passed with no failures or errors;
- [GitHub Actions run 33462357520](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33462357520): 30 tests passed and sanitized evidence was retained as a workflow artifact.

## Live Fabric checkpoint — 2026-09-01

- Reused the isolated `Northstar Data Platform - FAB-002` workspace and switched it to `feature/fab-003-quality-gates` only after confirming there were no uncommitted workspace changes.
- Created the development Lakehouse `lh_northstar_data` and attached it as the default for both FAB-002 and FAB-003 notebooks.
- Confirmed all nine FAB-003 SQL objects were deployed in `sqldb_northstar_control`: three tables, one operational view, and five stored procedures.
- Created and validated `PL_FAB003_QualityGate` from the proven FAB-002 pipeline. The direct completion activity was removed and replaced by policy resolution, quality evaluation, idempotent SQL result/quarantine persistence, durable decision finalization, and conditional use of the quality-accepted watermark wrapper.
- The initial preflight run exposed a platform binding detail: an empty optional pipeline parameter arrived as null. The `quality_test_mode` mapping now normalizes null to an empty string with `coalesce`.
- The preflight candidate was explicitly abandoned through `ops.usp_FailWatermarkAttempt`; its committed watermark remained `2026-08-30T12:18:00Z`.
- The corrected baseline run to the synthetic upper boundary `2026-08-30T12:20:00Z` completed successfully through the quality-enabled pipeline.

The successful pipeline status is a checkpoint, not final acceptance evidence. The next session must query the durable decision, check results, operational view, and committed watermark before starting the controlled blocking run.

## Remaining live evidence

- durable SQL evidence for the successful accepted run and its watermark commit;
- controlled blocking and warning decisions;
- hashed quarantine and idempotent replay results;
- final acceptance matrix and retrospective links.

## Resume point

1. Query `ops.vw_QualityResultOperational`, `ops.QualityDecision`, the latest object run/candidate, and `ops.WatermarkState` to capture the accepted run and confirm the committed boundary is `2026-08-30T12:20:00Z`.
2. Run `PL_FAB003_QualityGate` with the next synthetic upper boundary and `quality_test_mode = BLOCK_TARGET_COUNT`; prove that the durable decision is `BLOCKED` and the committed watermark does not advance.
3. Complete warning, quarantine, and replay validation.
4. Commit the Fabric-generated pipeline, notebook bindings, and Lakehouse item to the feature branch, then rerun CI and complete the final review/retrospective.

## Sanitization

Do not commit credentials, endpoints, workspace or item identifiers, connection values, patient data, proprietary schemas, or raw source/quarantine payloads. Use stable synthetic keys and hashes where correlation evidence is required.
