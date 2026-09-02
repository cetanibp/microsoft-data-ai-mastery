# FAB-003 Fabric workspace artifacts

## Items

| Item | Purpose |
|---|---|
| `NB_FAB003_QualityGate` | Resolve an allowlisted quality contract, evaluate the fixed FAB-002 object-run boundary, persist idempotent Delta evidence, and return a publication decision |
| `PL_FAB003_QualityGate` | Run FAB-002 ingestion, persist quality evidence, finalize the durable decision, and commit the watermark only through the quality-accepted wrapper |

The notebook requires the same default Lakehouse used by FAB-002. Its Git definition contains no physical workspace, Lakehouse, connection, or tenant identifier.

## Live binding checkpoint

The isolated development workspace uses `lh_northstar_data` as the default Lakehouse for both notebooks. The live pipeline was created and validated in Fabric on 2026-09-01. Its Fabric-generated definition and the workspace bindings still need to be committed through Fabric Git integration after the remaining live scenarios pass.

Fabric can pass an empty optional pipeline parameter as null. The live pipeline therefore maps `quality_test_mode` with `@coalesce(pipeline().parameters.quality_test_mode, '')` before invoking the quality notebook.

## Pipeline integration

Insert the quality gate after `NB_FAB002_IncrementalEncounter` succeeds and before any watermark completion call:

1. Call `ops.usp_ResolveQualityPolicy` for the current `object_run_id`.
2. Run `NB_FAB003_QualityGate` with the resolved policy rows, FAB-002 result counts, fixed boundary hash, and duplicate identity hashes.
3. For each returned `quality_results` row, call `ops.usp_RecordQualityCheckResult`.
4. For each returned `quarantine_records` row, call `ops.usp_RecordQuarantineEvidence`.
5. Call `ops.usp_FinalizeQualityDecision` with the expected result count and result-set hash.
6. If `watermark_commit_eligible` is true, call `ops.usp_CompleteQualityAcceptedWatermarkAttempt`.
7. If it is false, do not call another failure procedure: finalization already abandoned the candidate and closed the run as failed.

Calling the original FAB-002 completion procedure directly is prohibited for this quality-enabled path. The wrapper requires a durable accepted decision before delegating to the existing concurrency-safe compare-and-commit procedure.

## Parameters

The notebook receives the existing FAB-002 identities and counts plus:

- `input_boundary_hash`;
- `quality_policy_json` from `ops.usp_ResolveQualityPolicy`;
- `duplicate_identity_hashes_json` from FAB-002 output;
- Delta evidence table names;
- `quality_test_mode`, which is empty normally and permits controlled blocking or required-observation failure only in Development.

## Durable evidence

- Delta tables preserve notebook-produced results even when SQL persistence or later pipeline activity fails.
- `ops.QualityCheckResult`, `ops.QualityDecision`, and `ops.QuarantineEvidence` provide the transactional operational record.
- `ops.vw_QualityResultOperational` publishes correlated results consumed by the OPS-002 observability views and evaluations.
- Quarantine evidence stores hashes and reason codes, never raw protected payloads.
