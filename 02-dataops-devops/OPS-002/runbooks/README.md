# OPS-002 operational runbooks

Use these runbooks with the synthetic Northstar operational model.

| Runbook | Use |
|---|---|
| [Triage](triage.md) | Confirm the detection, scope impact, and classify the incident |
| [Replay](replay.md) | Safely replay an idempotent fixed-boundary occurrence |
| [Escalation](escalation.md) | Resolve severity, accountable roles, acknowledgement, and escalation |
| [Recovery](recovery.md) | Select and verify the correct recovery pattern |
| [Incident record](incident-record-template.md) | Capture evidence, decisions, timestamps, and closure |
| [Query pack](queries.sql) | Read-only correlated operational queries |

## Invariants

- Never advance a watermark to make an alert disappear.
- Never change or delete quality, execution, routing, or state evidence.
- Preserve `environment_id`, `release_id`, `run_id`, `object_run_id`, `correlation_id`, and `input_boundary_hash`.
- Replay only a fixed, reviewed boundary through the approved FAB-002/FAB-003 path.
- A quality block requires correction or explicit policy change through a future reviewed release; it is not bypassed operationally.
- A quality-enforcement integrity breach is P1, cannot be suppressed, and stops replay until state safety is established.
- Development and Test routing is simulated. This public project does not contact a real destination.

## Standard sequence

1. Acknowledge and open an incident record.
2. Run read-only triage queries.
3. Confirm severity, scope, owner, and control integrity.
4. Contain unsafe or competing execution.
5. Select replay or another recovery pattern.
6. Verify accepted publication, watermark outcome, telemetry, and SLO state.
7. Record recovery timestamps, residual risk, and follow-up work.
8. Close only after evidence is durable and the owner accepts the result.
