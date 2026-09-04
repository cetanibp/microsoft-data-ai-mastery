# FAB-004 live Fabric checkpoint

## Smoke readiness gate — September 3, 2026

The isolated FAB-004 Development workspace was synchronized to `feature/fab-004-performance-benchmark`, assigned to F256, and configured with the environment-local `lh_northstar_data` Lakehouse binding.

`NB_FAB004_BenchmarkOrchestrator` invoked `NB_FAB004_BenchmarkWorker` using the declared `SMOKE` / `SEQ1` contract.

| Observation | Result |
|---|---:|
| Run group | `e4c1b8d7-2fb7-4c40-9a31-6b8c0f0a5d12` |
| Status | SUCCEEDED |
| Correctness | PASS |
| Expected rows | 10,000 |
| Accepted rows | 10,000 |
| Rejected rows | 0 |
| Duplicate rows | 0 |
| Inserted rows | 10,000 |
| Updated rows | 0 |
| Orchestrator elapsed | 21.839068 seconds |
| Worker elapsed | 7.614297 seconds |
| Maximum worker queue | 8.522088 seconds |
| Orchestrator throughput | 457.895 rows/second |

## Interpretation

The smoke gate passed all correctness invariants and proved that the orchestrator can invoke the worker, create the synthetic Delta target, and return correlated sanitized telemetry.

The smoke timing is not used for the `SEQ1` / `PAR4` decision. Queueing and fixed orchestration/session overhead are large relative to a 10,000-row workload, which is precisely why the contract reserves performance conclusions for the standard and peak tiers.

## Final live outcome

The subsequent standard, peak, and replay scenarios each completed three paired repetitions. All measured runs passed row-count and duplicate invariants and recorded zero Capacity Metrics throttling.

`PAR4` is the selected bounded-parallel design. See [the final benchmark report](../benchmark-results.md) and [the evidence index](README.md).
