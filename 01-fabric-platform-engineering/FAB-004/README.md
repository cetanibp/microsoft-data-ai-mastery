# FAB-004 — Performance, capacity, and cost benchmarking

FAB-004 establishes a reproducible benchmark for the Northstar Fabric ingestion path built in FAB-002 and extended in FAB-003.

## Status

In progress. The initial workload and measurement contract targets the isolated FAB-004 Development workspace on an F256 capacity. Live results have not yet been collected.

## Benchmark question

For representative synthetic incremental-ingestion workloads, when does bounded parallel execution provide enough elapsed-time benefit to justify its additional capacity pressure compared with sequential execution?

## Design alternatives

| Alternative | Maximum parallelism | Purpose |
|---|---:|---|
| `SEQ1` | 1 | Establish the lowest-contention baseline |
| `PAR4` | 4 | Test bounded parallelism without assuming unlimited capacity |

The comparison changes only orchestration parallelism. Data shape, row generation, transformations, target behavior, telemetry, repetition count, and capacity remain fixed within each paired run.

## Workload coverage

| Scenario | Tier | Objects | Rows per object | Measured rows | Purpose |
|---|---|---:|---:|---:|---|
| Smoke | `smoke` | 1 | 10,000 | 10,000 | Validate setup and evidence capture; excluded from comparison |
| Steady state | `standard` | 4 | 1,000,000 | 4,000,000 | Represent a normal multi-object ingestion window |
| Peak | `large` | 8 | 10,000,000 | 80,000,000 | Expose queueing, contention, throttling, and scaling behavior |
| Replay | `standard` | 4 | 1,000,000 | 4,000,000 | Measure idempotent merge cost and verify no duplicate publication |

All rows are synthetic. No patient data, proprietary metadata, credentials, physical workspace identifiers, endpoints, or source payload samples belong in repository evidence.

## Success criteria

1. Every measured run completes with the expected accepted, rejected, duplicate, and target counts.
2. Replay leaves the target business-key count unchanged and creates no duplicate accepted record.
3. Every measured run captures elapsed time, throughput, queue time, CU seconds, CU seconds per million rows, throttling indicators, run identity, alternative, scenario, tier, and repetition.
4. Each measured scenario completes three paired repetitions in the declared `SEQ1`/`PAR4` order.
5. `PAR4` is preferred only when median elapsed time improves by at least 15% and median normalized CU consumption is no more than 25% worse than `SEQ1`.
6. A capacity-isolation review is triggered when the peak scenario records throttling/rejection, at least 80% observed utilization for three consecutive samples, or more than 20% critical-workload runtime degradation during controlled contention.

Performance thresholds are decision rules, not reasons to discard an otherwise valid run. A slower or more expensive result is evidence supporting the other alternative.

## Evidence plan

- Pipeline/notebook telemetry supplies run identity, timestamps, counts, status, and scenario dimensions.
- The Microsoft Fabric Capacity Metrics app supplies operation-level CU seconds, utilization, and throttling evidence for the bounded run window.
- Raw sanitized observations are stored as CSV or JSON; the committed summary is generated from those observations.
- Allocated cost is reported as a model, not as incremental billing: `CU seconds / (256 × 3600) × F256 hourly price`.
- Actual hourly pricing is an environment input and is never hard-coded into the benchmark contract.

## Repository contents

| Path | Purpose |
|---|---|
| [benchmark-spec.md](benchmark-spec.md) | Experimental controls, execution order, measurements, formulas, and decision rules |
| [config/workloads.json](config/workloads.json) | Machine-readable workload contract |
| [runtime/benchmark_contract.py](runtime/benchmark_contract.py) | Dependency-free manifest validation and derived workload calculations |
| [tests](tests/README.md) | Contract-test instructions and coverage |
| `evidence/` | Sanitized local and live benchmark results |

## Local validation

From the repository root:

```bash
python 01-fabric-platform-engineering/FAB-004/tests/run_contract_tests.py \
  --output 01-fabric-platform-engineering/FAB-004/evidence/local-contract-test-results.json
```
