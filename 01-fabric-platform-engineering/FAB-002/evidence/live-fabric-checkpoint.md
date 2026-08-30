# FAB-002 live Fabric checkpoint

**Checkpoint date:** 2026-08-30

**Status:** In progress

This checkpoint records sanitized notebook-level validation. It does not claim
that pipeline orchestration or transactional watermark commit is complete.

## Fabric items

- `lh_northstar_fab002` was created with Lakehouse schemas enabled in the
  `FAB-002` workspace folder.
- `lh_northstar_fab002` is attached as the default Lakehouse for
  `NB_FAB002_IncrementalEncounter`.
- The Bronze target resolves to `dbo.bronze_clinical_encounter`.
- Additive-drift evidence will resolve to
  `dbo.fab002_schema_drift_events` when that scenario is first run.

## Completed validation

| Scenario | Extracted | Accepted | In-window duplicates | Inserted | Updated | Target rows | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline fixed window | 4 | 3 | 1 | 3 | 0 | 3 | Passed |
| Same-window replay | 4 | 3 | 1 | 0 | 3 | 3 | Passed |

The replay result confirms that the Delta merge updates the three existing
business keys instead of appending duplicate accepted encounters.

| Drift scenario | Observed behavior | Result |
|---|---|---|
| Additive source column | Approved projection published and schema-only evidence written | Route passed; replay remediation pending |
| Missing required key | Run failed with `BREAKING_SCHEMA_DRIFT`; target remained unchanged | Passed |

Rerunning the same additive-drift object-run identity produced a second
equivalent evidence row with a later detection timestamp. The live test exposed
that the original append was not idempotent. The repository notebook now uses a
Delta merge on `object_run_id`; the existing duplicate still requires one-time
cleanup in the live Lakehouse before the fix is retested.

## Resume point

Synchronize the corrected notebook into Fabric, remove the duplicate live drift
row, and rerun the same additive-drift object-run identity. The evidence table
must remain at one row. Then continue with the two injected failure stages
before building the live pipeline.

## Outstanding scope

- additive-drift idempotency remediation and retest;
- intentional failure after extraction and after target write;
- pipeline orchestration and retry routes;
- FAB-001 SQL configuration resolution and transactional watermark calls;
- sanitized final run evidence.
