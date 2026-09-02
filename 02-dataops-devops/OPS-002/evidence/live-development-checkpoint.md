# OPS-002 — Live Development telemetry and routing checkpoint

**Environment:** Development  
**Data:** Synthetic Northstar control-plane evidence  
**Result:** Passed

## Deployment verification

Fabric Git synchronization deployed all 12 OPS-002 SQL objects successfully:

- 3 tables;
- 6 views; and
- 3 stored procedures.

## Operational projection

`ops.vw_OperationsDashboard` correlated 12 existing clinical-encounter occurrences:

| Outcome | Count |
|---|---:|
| In progress | 1 |
| Correctly quality-blocked | 1 |
| Failed without quality decision | 2 |
| Recovery required | 1 |
| Successful without quality decision | 4 |
| Successful and quality accepted | 3 |

The existing blocked quality decision projected as:

- object-run status `FAILED`;
- reliability status `QUALITY_BLOCKED`;
- quality-enforcement status `PASS`; and
- watermark candidate status `ABANDONED`.

`ops.vw_QualityEnforcementIntegrity` returned one `PASS` and no breach, proving that the blocked decision did not advance state.

## SLO persistence and replay

The quality-enforcement evaluation produced:

| Numerator | Denominator | Observed | Target | Result |
|---:|---:|---:|---:|---|
| 1 | 1 | 100% | 100% | PASS |

The first call to `ops.usp_RecordSloEvaluation` inserted the evaluation. Replaying the identical evaluator version, scope, window, and source-evidence hash returned the existing evaluation without inserting a duplicate.

## Reliability breach

Terminal Development evidence produced:

| Numerator | Denominator | Observed | Target | Error-budget consumption | Result |
|---:|---:|---:|---:|---:|---|
| 8 | 11 | 72.727273% | 99.5% | 54.545454 | BREACH |

The correctly enforced quality block counted as reliable platform behavior while still reducing the separate quality-acceptance indicator.

## Alert routing

The breach resolved deterministically to:

| Field | Result |
|---|---|
| Detection category | RELIABILITY |
| Severity | P2 |
| Owner role | OPERATIONS |
| Owner group | data-operations |
| Routing alias | route-data-operations |
| Delivery mode | SIMULATED |
| Decision | ROUTED |

The candidate and persisted deduplication keys matched. The first persistence inserted one decision; replay returned the existing decision. The breach then projected as `DECIDED`, with zero remaining routing candidates.

No real notification destination was contacted.

## Failure and correction

The first routing verification query referenced an `evaluation_status` column that the open-breach view did not expose. SQL compilation rejected the batch before routing persistence, leaving the breach `UNROUTED` and the candidate intact. A corrected batch then persisted and replayed the decision successfully.

The open-breach view now exposes its explicit `BREACH` status, and the automated suite checks that contract.

## Completion link

The final [failure-recovery exercise](failure-recovery-exercise.md) used the operational query pack and runbooks to resolve a real orphaned candidate without changing the accepted watermark.
