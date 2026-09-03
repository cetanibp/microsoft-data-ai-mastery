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
