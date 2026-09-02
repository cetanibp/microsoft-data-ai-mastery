# OPS-002 — Alert-routing contract

**Status:** Proposed for implementation

## Purpose

Convert a durable operational detection into an environment-aware, owner-resolved, deduplicated routing decision. The contract separates detection, routing, and external delivery so evidence remains testable without contacting a real destination.

## Severity model

| Severity | Condition | Initial response |
|---|---|---|
| `P1` | Quality-enforcement integrity violation, unsafe state advancement, or telemetry corruption hiding a critical failure | Immediate critical escalation |
| `P2` | Critical freshness/reliability/quality breach, failed or recovery-required critical run, or missing critical telemetry | Critical alert |
| `P3` | Duration breach, accepted quality warning above threshold, or noncritical operational degradation | Warning alert |
| `P4` | Informational state, recovery completion, or budget-consumption notice | Record only |

A P1 condition does not wait for a rolling-window error budget.

## Owner resolution

Resolution is deterministic and uses the metadata release recorded by the run or evaluation.

| Detection category | Primary role | Secondary role |
|---|---|---|
| Platform execution or telemetry | `INCIDENT`, then `OPERATIONS` | `ENGINEERING` |
| Quality block or repeated warning | `INCIDENT`, then `OPERATIONS` | `SOURCE_STEWARD` and `DATA_PRODUCT` |
| Freshness or duration | `OPERATIONS` | `ENGINEERING` |
| Control-integrity violation | `INCIDENT` | `ENGINEERING` and `DATA_PRODUCT` |

If the preferred role is absent, the resolver falls back in the documented order. If no valid alias exists, it records `NO_ROUTE`; this is itself a P1 metadata-control defect for Production.

## Environment behavior

| Environment | Delivery mode | Permitted result |
|---|---|---|
| Development | `SIMULATED` | Durable routing evidence only |
| Test | `SIMULATED` | Durable routing and runbook-exercise evidence |
| Production | `NOTIFICATION_REQUESTED` | Durable request referencing an approved alias |

No direct external destination is stored in the control database. A private environment-specific integration may resolve the alias after the durable decision is created.

## Deduplication

The routing deduplication key is a SHA-256 hash of:

```text
environment_id
+ ingestion_object_key or platform scope
+ detection_category
+ severity
+ evaluation window end or object_run_id
+ routing_alias
```

Repeated evaluation or replay returns the existing routing decision. A new window, new occurrence, severity change, or resolved-then-recurring condition creates a new decision.

## Suppression rules

Allowed suppression requires:

- a matching preapproved telemetry exclusion;
- a non-P1 condition;
- the exclusion scope and effective interval to cover the detection;
- actor, reason, approval reference, and expiry;
- a persisted `SUPPRESSED` routing decision.

Not suppressible:

- quality-enforcement violations;
- unsafe watermark advancement;
- missing or invalid Production routing metadata;
- secret or sensitive-data leakage;
- evaluator evidence-hash mismatch.

## Timing

The five-minute alert-latency objective measures from durable detection time to persisted routing-decision time.

| Stage | Included in SLO |
|---|---|
| Breach or failure detection | Starts timer |
| Owner and alias resolution | Included |
| Deduplication and suppression decision | Included |
| Routing-decision persistence | Stops timer |
| External connector delivery | Reported separately |
| Human acknowledgement and recovery | Incident KPI, not alert-latency SLO |

## Minimum routed context

A routing decision references, without embedding sensitive payloads:

- environment and metadata release;
- ingestion object or platform scope;
- run, object-run, and correlation identity when applicable;
- category, severity, observed value, target, and window;
- sanitized error classification;
- owner role and logical routing alias;
- dashboard/query reference and runbook key;
- detection and routing timestamps;
- deduplication key.

## Escalation model

| Severity | Unacknowledged escalation target |
|---|---:|
| P1 | 15 minutes |
| P2 | 30 minutes |
| P3 | Next operational review or 4 hours |
| P4 | None |

Acknowledgement is modeled in the runbook/evidence phase. This public implementation does not page a real person or service.
