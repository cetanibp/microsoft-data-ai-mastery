# FAB-004 benchmark specification

## Fixed environment

| Dimension | Required value |
|---|---|
| Platform | Microsoft Fabric |
| Environment | Development |
| Workspace | Isolated temporary FAB-004 branch workspace |
| Capacity | F256 (`256` capacity units) |
| Data | Synthetic encounter-shaped rows only |
| Runtime lineage | FAB-002 ingestion and FAB-003 acceptance contracts |

Physical workspace, capacity, tenant, item, connection, and user identifiers are recorded only in private execution notes when operationally necessary. They are not committed.

## Controlled variables

For each paired comparison, keep these values constant:

- synthetic seed and encounter data shape;
- object count and rows per object;
- fixed input boundaries;
- target table layout and merge key;
- Spark/runtime configuration other than declared parallelism;
- capacity SKU and workspace placement;
- quality rules and telemetry behavior;
- measured repetition count.

The independent variable is orchestration concurrency: `SEQ1` uses one active object and `PAR4` allows four.

## Scale tiers

| Tier | Objects | Rows per object | Total rows | Use |
|---|---:|---:|---:|---|
| `smoke` | 1 | 10,000 | 10,000 | Readiness only |
| `standard` | 4 | 1,000,000 | 4,000,000 | Steady state and replay |
| `large` | 8 | 10,000,000 | 80,000,000 | Peak workload |

The large tier is gated: run it only after smoke and standard correctness pass and no uncontrolled workload is active on the capacity.

## Execution order

1. Confirm the workspace is synchronized to the FAB-004 feature branch and attached to F256.
2. Confirm the default Lakehouse and required control-plane/runtime items are bound without committing physical identifiers.
3. Run the smoke scenario once with `SEQ1`; exclude it from the comparison.
4. Run each measured scenario three times, alternating paired order to reduce systematic cache/order bias:
   - repetition 1: `SEQ1`, then `PAR4`;
   - repetition 2: `PAR4`, then `SEQ1`;
   - repetition 3: `SEQ1`, then `PAR4`.
5. Use the same seed and fixed boundaries within a pair.
6. Allow the capacity to return to the declared ready state before the next measured pair.
7. Export sanitized capacity and runtime observations for the exact run windows.
8. Validate evidence completeness before computing a decision.

## Measurements

| Metric | Unit | Source | Formula or rule |
|---|---|---|---|
| Elapsed time | seconds | Runtime telemetry | completion UTC minus start UTC |
| Queue time | seconds | Runtime telemetry | execution start minus submitted UTC |
| Throughput | rows/second | Derived | accepted rows divided by elapsed seconds |
| CU consumption | CU seconds | Capacity Metrics | sum for correlated operations in the run window |
| Normalized CU | CU seconds/million rows | Derived | CU seconds divided by accepted rows in millions |
| Peak utilization | percent | Capacity Metrics | maximum observed utilization sample in the run window |
| Throttling | count/state | Capacity Metrics | observed delay, rejection, or throttling indicators |
| Correctness | pass/fail | Control and target evidence | counts and state invariants match the scenario |
| Allocated cost | USD | Derived | `CU seconds / (256 × 3600) × F256 hourly price` |

Allocated cost estimates utilization share on a continuously provisioned F256. It does not claim that one operation created an equivalent incremental bill.

## Summary statistics

- Report the median of the three measured repetitions for elapsed time, throughput, queue time, CU seconds, and normalized CU.
- Preserve every raw observation; do not report only the best run.
- Calculate elapsed-time improvement as `(SEQ1 median - PAR4 median) / SEQ1 median`.
- Calculate normalized-CU change as `(PAR4 median - SEQ1 median) / SEQ1 median`.
- Call out cold-start, caching, Spark-session, or unrelated-capacity effects rather than silently excluding them.

## Decision rules

Select `PAR4` for the tested workload when:

- all correctness and evidence-completeness checks pass;
- median elapsed-time improvement is at least 15%;
- median normalized CU seconds are no more than 25% higher than `SEQ1`;
- no sustained throttling or rejection occurs.

Otherwise retain `SEQ1` as the default and document the failing threshold. A later test may evaluate another bounded value, but it must be a new declared alternative rather than an undocumented tuning change.

Initiate a capacity-isolation review when any of these occur:

- delay or rejection throttling is observed;
- utilization is at least 80% for three consecutive captured samples;
- a controlled companion critical workload degrades by more than 20%;
- the peak workload cannot meet its declared processing window after orchestration tuning.

## Limitations to preserve

- Results apply to the tested synthetic ingestion shape and F256 capacity, not every Fabric workload.
- Shared-capacity cost is allocated, not directly metered as an incremental per-run charge.
- Workspace separation does not provide capacity isolation.
- Three repetitions characterize this exercise but are not a production forecasting model.
- Capacity Metrics attribution can span multiple Fabric operations; correlation and exact UTC windows are required.
