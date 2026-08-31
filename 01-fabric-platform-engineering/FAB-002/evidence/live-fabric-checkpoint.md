# FAB-002 live Fabric checkpoint

**Checkpoint date:** 2026-08-30

**Status:** In progress

This checkpoint records sanitized notebook-level validation and the first
successful transactional pipeline run. Pipeline failure/retry validation and
final evidence are not yet complete.

## Fabric items

- `lh_northstar_fab002` was created with Lakehouse schemas enabled in the
  `FAB-002` workspace folder.
- `lh_northstar_fab002` is attached as the default Lakehouse for
  `NB_FAB002_IncrementalEncounter`.
- `PL_FAB002_IncrementalEncounter` is configured in the `FAB-002` folder and
  its Fabric-generated source definition is committed to the feature branch.
- The Bronze target resolves to `dbo.bronze_clinical_encounter`.
- Additive-drift evidence will resolve to
  `dbo.fab002_schema_drift_events` when that scenario is first run.

## Completed validation

| Scenario | Extracted | Accepted | In-window duplicates | Inserted | Updated | Target rows | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline fixed window | 4 | 3 | 1 | 3 | 0 | 3 | Passed |
| Same-window replay | 4 | 3 | 1 | 0 | 3 | 3 | Passed |
| Recovery after post-write failure | 4 | 3 | 1 | 0 | 3 | 3 | Passed |
| Empty window | 0 | 0 | 0 | 0 | 0 | 3 | Passed |

The replay result confirms that the Delta merge updates the three existing
business keys instead of appending duplicate accepted encounters.

| Drift scenario | Observed behavior | Result |
|---|---|---|
| Additive source column | Approved projection published and schema-only evidence written once per object run | Passed after idempotency fix and retest |
| Missing required key | Run failed with `BREAKING_SCHEMA_DRIFT`; target remained unchanged | Passed |

Rerunning the same additive-drift object-run identity initially produced a
second equivalent evidence row with a later detection timestamp. The live test
exposed that the original append was not idempotent. The repository notebook
now uses a Delta merge on `object_run_id`; after one-time cleanup and notebook
synchronization, replay retained exactly one event.

| Failure scenario | Observed behavior | Durable table result | Result |
|---|---|---|---|
| After extraction | Failed with the expected injected error before publication | Bronze 3; drift events 1 | Passed |
| After target write | Failed with the expected injected error after an idempotent merge | Bronze 3; drift events 1 | Passed |
| Recovery replay | Completed with 0 inserts and 3 updates | Bronze 3; drift events 1 | Passed |

## Transactional pipeline validation

The live pipeline executes this success path:

```text
Resolve_Context
  -> Set_ObjectRunId
  -> Set_CandidateId
  -> Compute_BoundaryHash
  -> Begin_Attempt
  -> Run_IncrementalNotebook
  -> Complete_Attempt
```

`Fail_Attempt` is connected to the notebook failure path and remains to be
validated with an injected pipeline failure.

| Check | Observed result |
|---|---|
| Active configuration | Development release `1.0.0`; one exact object match |
| Fixed window | `2026-01-01T00:00:00Z` exclusive through `2026-08-30T12:15:00Z` inclusive |
| Object counts | 4 extracted; 3 accepted; 0 rejected |
| Execution status | `SUCCEEDED` |
| Object-run status | `SUCCEEDED` |
| Candidate status | `COMMITTED` |
| Committed watermark | `2026-08-30T12:15:00Z` |
| State version | `1` |

The pipeline must map `correlation_id` to `@pipeline().RunId`; mapping the
pipeline name instead caused a uniqueness failure during authoring and was
corrected before the successful run.

## Resume point

Validate the pipeline failure path using the next window ending at
`2026-08-30T12:16:00Z`. The injected post-write failure
must abandon its candidate without advancing state version `1`; a recovery run
over the same window must then commit state version `2` without duplicate target
rows.

## Outstanding scope

- live pipeline failure, retry, and recovery routes;
- sanitized final run evidence.
