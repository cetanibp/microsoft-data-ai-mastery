# Runbook — Recovery selection and verification

## Select a pattern

| Condition | Recovery pattern | Do not do |
|---|---|---|
| Transient execution failure before accepted publication | Correct dependency and use safe replay | Advance watermark or delete attempt evidence |
| Durable target write followed by failure | Replay the same fixed boundary through the idempotent merge | Truncate target or create a new boundary |
| Quality BLOCK | Correct data or contract implementation, then replay; policy changes require a future reviewed release | Bypass, downgrade, or delete the block |
| Stale candidate/concurrent winner | Keep winner, abandon stale candidate, reconcile target, then decide whether replay is necessary | Force stale candidate to commit |
| Metadata/configuration defect | Correct code/config through governed delivery and validate release compatibility | Edit an approved immutable release in place |
| Telemetry or routing failure | Restore telemetry/routing and replay the evaluator/router idempotently | Rerun ingestion when data/state already succeeded |
| Quality-enforcement integrity breach | P1 containment, state reconstruction, two-person corrective plan, and separately governed state recovery | Use normal replay until safety is established |

## Recovery verification

Verify every applicable layer:

### Execution

- terminal status matches the actual outcome;
- attempt history and error classification are retained;
- no competing attempt remains active.

### Data and quality

- accepted and rejected counts reconcile;
- target result is idempotent;
- required rules were evaluated exactly once by stable rule identity;
- quarantine evidence remains hashed and deduplicated;
- no BLOCK decision was accepted.

### State

- candidate is committed only after acceptance, otherwise abandoned;
- watermark version advanced at most once;
- committing object run matches the accepted occurrence;
- append-only state events explain the transition.

### Observability

- operational occurrence reflects the final state;
- quality-enforcement integrity is `PASS`;
- SLO evaluation uses the correct window and evaluator version;
- routing is deduplicated and environment appropriate;
- recovery and acknowledgement timestamps are recorded.

## Corrective state action

Normal replay must not mutate committed state outside the compare-and-commit protocol. If state is already incorrect, stop and create a separately approved corrective plan containing before/after values and hashes, affected boundaries, target reconciliation, actor separation, validation queries, rollback/forward-recovery decision, and permanent audit evidence.

## Completion criteria

Recovery is complete when execution, data, quality, state, observability, and ownership evidence agree. Record residual risks and open remediation work before closure.
