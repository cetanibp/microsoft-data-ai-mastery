# Runbook — Escalation

## Severity

| Severity | Examples | Initial owner | Acknowledge | Escalate if unacknowledged |
|---|---|---|---:|---:|
| P1 | Unsafe state advancement, blocked run accepted, evidence corruption, sensitive-data leakage, missing Production route | INCIDENT | Immediate | 15 minutes |
| P2 | Critical reliability/freshness/quality breach, critical failed or recovery-required run | INCIDENT or OPERATIONS | 15 minutes | 30 minutes |
| P3 | Duration breach, repeated warning, noncritical degradation | OPERATIONS | 1 hour | 4 hours |
| P4 | Informational state or recovery completion | OPERATIONS | Next review | None |

These are synthetic Northstar targets for the learning implementation.

## Role resolution

Use ownership from the metadata release recorded by the evidence:

- platform execution or telemetry: `INCIDENT` → `OPERATIONS` → `ENGINEERING`;
- quality: `INCIDENT` → `OPERATIONS`, with `SOURCE_STEWARD` and `DATA_PRODUCT` informed;
- freshness or duration: `OPERATIONS` → `ENGINEERING`;
- control integrity: `INCIDENT`, with `ENGINEERING` and `DATA_PRODUCT` involved.

Do not replace a missing route with a personal address. Record `NO_ROUTE`; in Production this becomes a P1 metadata-control defect.

## Escalation package

Provide:

- sanitized business and consumer impact;
- environment, release, object, run, object-run, correlation, and boundary identities;
- category, severity, observed value, target, and error-budget consumption;
- current run, quality, candidate, and watermark status;
- actions attempted and results;
- selected runbook and next decision time; and
- explicit approval requested from the recipient.

## P1 containment

For P1, stop new execution for the affected logical scope through the approved operational control, preserve evidence, prevent manual watermark/state changes, and require two-person review before corrective state action. Suppression is prohibited.

## De-escalation and closure

Severity may be reduced only when control integrity is proven, impact is bounded, and the incident owner records the reason. Close after recovery verification, SLO re-evaluation, stakeholder acceptance, and creation of follow-up work for unresolved causes.
