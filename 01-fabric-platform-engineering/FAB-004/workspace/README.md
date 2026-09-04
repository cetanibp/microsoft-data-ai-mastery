# FAB-004 Fabric workspace artifacts

## Items

| Item | Purpose |
|---|---|
| `NB_FAB004_BenchmarkWorker` | Generate one deterministic synthetic object workload, publish or replay it through an idempotent Delta merge, and return sanitized object metrics |
| `NB_FAB004_BenchmarkOrchestrator` | Enforce the workload contract and execute workers with `SEQ1` or `PAR4` concurrency |

Both notebooks require the same default development Lakehouse. Their Git definitions intentionally omit physical Lakehouse, workspace, capacity, connection, tenant, and user identifiers.

## Smoke parameters

Run `NB_FAB004_BenchmarkOrchestrator` with:

| Parameter | Value |
|---|---|
| `environment_name` | `development` |
| `benchmark_run_group_id` | New UUID for the smoke run |
| `scenario_id` | `SMOKE` |
| `alternative_id` | `SEQ1` |
| `scale_tier` | `smoke` |
| `repetition` | `0` |
| `object_count` | `1` |
| `rows_per_object` | `10000` |
| `seed` | `20260902` |
| `worker_notebook` | `NB_FAB004_BenchmarkWorker` |
| `target_prefix` | `fab004_benchmark` |
| `reset_targets` | `true` |

The smoke run is valid when the orchestrator returns `correctness_status=PASS`, `accepted_row_count=10000`, zero rejected and duplicate rows, and one passing worker result. It validates readiness but is excluded from the `SEQ1`/`PAR4` comparison.
