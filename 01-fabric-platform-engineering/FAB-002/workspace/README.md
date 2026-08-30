# FAB-002 Fabric workspace artifacts

## Items

| Item | Purpose |
|---|---|
| `NB_FAB002_IncrementalEncounter` | Execute one fixed encounter watermark window and idempotently merge it into a Bronze Delta table |

The notebook requires a default Lakehouse. Its repository definition intentionally contains no physical Lakehouse, workspace, connection, or tenant identifier. Attach the isolated FAB-002 Lakehouse after the feature workspace is connected to Git; enable Lakehouse auto-binding before later promotion.

## Orchestration contract

The Fabric Data Pipeline for the first vertical slice must execute these activities in order:

1. Resolve `ingest-clinical-encounter` through `ops.usp_ResolveWatermarkContext`.
2. Capture a fixed source upper bound.
3. Generate run, object-run, candidate, and correlation IDs and the SHA-256 boundary/configuration hashes.
4. Call `ops.usp_BeginWatermarkAttempt` before target publication.
5. Run `NB_FAB002_IncrementalEncounter` with the pinned identities and boundaries.
6. Parse its sanitized JSON result.
7. On success, call `ops.usp_CompleteWatermarkAttempt` with the returned counts.
8. On failure, call `ops.usp_FailWatermarkAttempt`; retry according to the active execution policy.

The pipeline definition will be captured from Fabric Git integration after the live activities and failure routes are configured and validated. This avoids hand-authoring opaque item identifiers or unsupported pipeline JSON.

## Notebook parameters

| Parameter | Meaning |
|---|---|
| `environment_name` | Active stage code |
| `release_id` | Pinned FAB-001 metadata release ID |
| `run_id` / `object_run_id` | Durable execution identities |
| `correlation_id` | Cross-system trace identity |
| `lower_bound` / `upper_bound` | Fixed ISO-8601 extraction window |
| `scenario` | `baseline`, `replay`, `additive_drift`, or `breaking_drift` |
| `failure_stage` | Empty, `AFTER_EXTRACT`, or `AFTER_TARGET_WRITE` |
| `target_table` | Bronze Delta target name |
| `drift_table` | Schema-only drift evidence table name |

## Safety boundaries

- Only synthetic rows are embedded in the notebook.
- Drift evidence records schema names and classifications, never rejected payloads.
- Drift evidence merges by `object_run_id`, so replaying one attempt does not append a duplicate event.
- The notebook cannot advance a watermark; only the SQL compare-and-commit procedure can.
- A target-write failure or injected crash leaves the candidate uncommitted.
- Replaying the same window uses Delta `MERGE` on `encounter_id`.
