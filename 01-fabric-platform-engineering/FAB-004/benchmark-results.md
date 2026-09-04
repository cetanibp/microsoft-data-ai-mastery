# FAB-004 benchmark results and decision

## Executive decision

Select `PAR4` (bounded orchestration parallelism of four) for the tested Northstar synthetic ingestion shape on F256.

Across steady-state, peak, and idempotent-replay workloads, `PAR4` passed correctness, exceeded the required 15% median elapsed-time improvement, stayed below the allowed 25% normalized-CU increase, and recorded no throttling. It was both faster and lower-CU in every scenario median.

## Median results

| Scenario | Rows/run | SEQ1 elapsed | PAR4 elapsed | Elapsed improvement | SEQ1 CU(s) | PAR4 CU(s) | PAR4 CU change |
|---|---:|---:|---:|---:|---:|---:|---:|
| Steady | 4,000,000 | 61.624 | 28.612 | 53.6% faster | 1,042.02 | 579.02 | 44.4% lower |
| Peak | 80,000,000 | 222.616 | 142.647 | 35.9% faster | 2,962.20 | 1,549.47 | 47.7% lower |
| Replay | 4,000,000 | 118.703 | 82.588 | 30.4% faster | 2,321.79 | 1,594.69 | 31.3% lower |

Steady elapsed medians come from the three paired warm comparison runs. Steady CU medians come from three isolated, stopped notebook sessions in Capacity Metrics. Peak CU covers the ingestion session. Replay CU covers both the seed and measured replay phases; replay elapsed covers only the replay phase.

## Operational effects

| Scenario | SEQ1 throughput | PAR4 throughput | Throughput increase | SEQ1 max queue | PAR4 max queue | Queue reduction |
|---|---:|---:|---:|---:|---:|---:|
| Steady | 64,910 rows/s | 139,804 rows/s | 115.4% | 52.98 s | 18.50 s | 65.1% |
| Peak | 359,362 rows/s | 560,824 rows/s | 56.1% | 205.17 s | 117.20 s | 42.9% |
| Replay | 33,697 rows/s | 48,433 rows/s | 43.7% | 105.85 s | 18.49 s | 82.5% |

Every measured run completed with expected accepted rows, zero rejects, zero duplicates, and PASS correctness. Replay runs inserted zero rows and updated the existing four million rows. Capacity Metrics recorded zero throttling seconds.

## Decision-rule evaluation

| Rule | Required | Observed | Result |
|---|---|---|---|
| Correctness and evidence completeness | PASS | All paired runs PASS | PASS |
| Median elapsed improvement | At least 15% | 30.4%–53.6% | PASS |
| Median normalized-CU increase | No more than 25% | 31.3%–47.7% lower | PASS |
| Sustained throttling or rejection | None | None | PASS |
| Capacity-isolation review trigger | Throttling, sustained >=80%, or >20% companion degradation | Not triggered by captured evidence | PASS |

## Capacity and allocated-cost model

Capacity Metrics `Timepoint Item Detail` is the authoritative CU source because it provides one row per stopped notebook operation. Earlier cumulative Timepoint Summary deltas are retained as investigation history but are not used for the final CU decision.

Let `P` be the environment-specific F256 hourly price. Allocated cost is:

`allocated cost = CU seconds / (256 × 3600) × P`

| Scenario | SEQ1 allocated-cost coefficient | PAR4 allocated-cost coefficient |
|---|---:|---:|
| Steady | 0.001130664 × P | 0.000628277 × P |
| Peak | 0.003214193 × P | 0.001681283 × P |
| Replay | 0.002519303 × P | 0.001730349 × P |

A dollar value is intentionally not reported because the actual F256 hourly price was not supplied. These values allocate a share of continuously provisioned F256 cost; they do not claim an incremental per-operation bill.

## Optimization decision

- Use `PAR4` as the default bounded-parallel alternative for the tested ingestion path.
- Keep parallelism explicit and capped at four; do not interpret this result as approval for unbounded concurrency.
- Preserve run identity, fixed seeds, row-count invariants, and operation-level capacity evidence in future tuning.
- Re-run the benchmark after material data-shape, partitioning, Spark-runtime, Lakehouse-layout, or capacity-SKU changes.
- Trigger capacity isolation review if throttling occurs, utilization remains at least 80% for three samples, or a companion critical workload degrades by more than 20%.

## Limitations

- Results apply to synthetic encounter-shaped data, the tested notebooks, and F256.
- Three repetitions support a controlled engineering decision, not a production demand forecast.
- Workspace separation does not isolate capacity.
- Capacity Metrics session CU includes Spark startup and, for replay, the seed phase.
- The first peak SEQ1 session included a validation-only failed attempt before compute; its CU was high, but the three-run median was unaffected.
- No controlled companion critical workload was run, so cross-workload degradation remains unmeasured.
- Actual dollar cost requires the organization's contracted or regional F256 price.
