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

## Resume point

Run the notebook with a new run identity and:

```python
scenario = "additive_drift"
failure_stage = ""
```

Expected results are `SUCCEEDED_WITH_WARNINGS`, one schema-drift event, zero
inserts, three updates, and three retained Bronze rows. Then validate breaking
drift and the two injected failure stages before building the live pipeline.

## Outstanding scope

- additive and breaking schema-drift validation;
- intentional failure after extraction and after target write;
- pipeline orchestration and retry routes;
- FAB-001 SQL configuration resolution and transactional watermark calls;
- sanitized final run evidence.
