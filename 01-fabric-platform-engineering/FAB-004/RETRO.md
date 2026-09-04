# FAB-004 retrospective

## Outcome

FAB-004 produced a reproducible Microsoft Fabric benchmark across smoke, steady, peak, and idempotent-replay workloads. It compared sequential execution with bounded parallelism and selected `PAR4` using declared correctness, performance, capacity, and throttling thresholds.

## What worked

- Alternating pair order reduced systematic order bias.
- Fresh stopped Spark sessions enabled operation-level CU attribution.
- `Timepoint Item Detail` exposed exact per-session duration, CU, and throttling.
- Synthetic data and sanitized JSON preserved a shareable evidence boundary.
- Median decisions prevented one anomalous or startup-heavy session from controlling the outcome.
- Replay proved zero inserts and duplicates while updating the existing business keys.

## What changed

The initial capacity analysis used cumulative Timepoint Summary subtraction. Report-window churn and delayed aggregation made some workspace and notebook deltas misleading. Timepoint Item Detail later provided exact rows per stopped notebook session and superseded the cumulative method. This correction changed individual CU observations but did not change the standard median or the `PAR4` recommendation.

The PEAK parameters were initially assumed to derive automatically from the scenario. The notebook correctly rejected the mismatched defaults; the large-tier parameters were then supplied explicitly. The validation-only failure was retained as a documented limitation rather than hidden.

## Decision

Use `PAR4` for this workload on F256. It improved median elapsed time by 30.4% to 53.6% and reduced median CU by 31.3% to 47.7% across the measured scenarios, with zero throttling and full correctness.

## Follow-up

- Obtain the applicable F256 hourly price if a dollar allocation is required.
- Add a controlled companion workload before making shared-capacity isolation claims.
- Revalidate after material runtime, layout, workload-shape, or SKU changes.
- Use the same item-detail evidence method in future capacity benchmarks.
