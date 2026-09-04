# FAB-004 evidence

This folder contains sanitized contract-test and live benchmark evidence.

## Required live evidence

- run manifest with scenario, tier, alternative, repetition, seed, and UTC boundaries;
- raw runtime observations with counts, status, elapsed time, queue time, and throughput;
- Capacity Metrics export or sanitized transcription for the exact run windows;
- paired median comparison and threshold evaluation;
- cost-allocation inputs and results with the F256 hourly price kept environment-specific;
- final optimization and capacity-placement decision;
- declared limitations and anomalous-run explanations.

Do not commit tenant, workspace, capacity, item, connection, user, or endpoint identifiers; credentials; patient data; proprietary metadata; or source payload samples.

## Live Development evidence

- [Live Fabric checkpoint](live-fabric-checkpoint.md) — F256 workspace readiness and smoke-gate interpretation.
- [Smoke result](live-smoke-result.json) — sanitized correlated output for the successful 10,000-row `SMOKE` / `SEQ1` run.
- [Final benchmark decision](../benchmark-results.md) — steady, peak, and replay medians, cost coefficients, optimization decision, and limitations.
- [Authoritative steady CU observations](capacity-item-detail-observations.json) — operation-level Capacity Metrics rows for the isolated standard runs.
- [Steady capacity decision](capacity-isolated-median-summary.json) — isolated standard-session CU median and threshold evaluation.
- [Peak median summary](peak-median-summary.json) and [capacity observations](peak-capacity-observations.json).
- [Replay median summary](replay-median-summary.json) and [capacity observations](replay-capacity-observations.json).
- Raw run JSON and pair summaries are retained for every measured repetition.
