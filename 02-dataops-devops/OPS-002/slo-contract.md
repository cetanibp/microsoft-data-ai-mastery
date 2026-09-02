# OPS-002 — Service-level objective contract

**Status:** Approved baseline  
**Evaluation window:** Rolling 30 days unless stated otherwise  
**Time standard:** UTC for evidence; schedule deadlines are resolved from the schedule's IANA time zone

## Purpose

This contract makes the Northstar operational objectives reproducible. Each result must retain environment, metadata release, run, object-run, ingestion-object, input-boundary, and correlation identities so an operator can move from an SLO breach to the exact execution and quality evidence.

The contract distinguishes:

- **service health**, measured over logical scheduled occurrences;
- **control integrity**, which has zero tolerance for an unsafe state transition; and
- **operational responsiveness**, measured from detection to creation of an alert-routing decision.

## Logical occurrence and attempt handling

The evaluation grain is a logical occurrence, not a raw retry.

A logical occurrence is identified by:

`environment_id + release_id + ingestion_object_key + run_id + input_boundary_hash`.

If several `ObjectRun` rows represent attempts or an authorized replay of that same occurrence, the evaluator:

1. orders attempts by `attempt_number` and completion time;
2. retains every attempt as evidence;
3. uses the final terminal outcome for reliability and quality acceptance;
4. uses the first successful quality-accepted publication time for freshness;
5. uses elapsed time from the first attempt start through the final terminal outcome for end-to-end duration.

This prevents retries from inflating either the numerator or denominator.

## Approved objectives

| Key | Objective | Target | Window | Breach action |
|---|---|---:|---|---|
| `critical-freshness` | Critical occurrences publish accepted data within 15 minutes of source availability | >= 99% | Rolling 30 days | Critical alert |
| `standard-freshness` | Standard daily occurrences publish accepted data by 6:00 a.m. local time | >= 99% | Rolling 30 days, summarized daily | Critical escalation |
| `ingestion-reliability` | Scheduled occurrences end in an accepted success state | >= 99.5% | Rolling 30 days | Critical escalation |
| `duration-compliance` | Occurrences finish within their configured duration target | >= 95% | Rolling 30 days | Warning alert |
| `quality-acceptance` | Evaluated occurrences complete without a BLOCK decision | >= 99% | Rolling 30 days | Critical alert |
| `quality-enforcement` | BLOCK decisions preserve state and prevent acceptance | = 100% | Per decision and rolling 30 days | Immediate critical escalation |
| `critical-alert-latency` | Critical detections create a durable routing decision within five minutes | = 100% | Per alert and rolling 30 days | Immediate critical escalation |

## Indicator formulas

### Critical freshness

```text
100 * critical occurrences accepted within 15 minutes
    / eligible critical occurrences with a resolved availability time
```

The start timestamp is `source_available_at_utc`. The stop timestamp is the first durable quality-accepted publication time. When a source does not expose availability, the approved scheduled eligibility time is used and the result is marked `SCHEDULE_PROXY`.

### Standard freshness

```text
100 * standard daily occurrences accepted by their local deadline
    / eligible standard daily occurrences
```

The evaluator converts the 6:00 a.m. deadline using the schedule's IANA time zone, including daylight-saving transitions, before comparison in UTC.

### Ingestion reliability

```text
100 * occurrences with final status SUCCEEDED or SUCCEEDED_WITH_WARNINGS
    / eligible scheduled occurrences
```

A quality warning is reliable service. `FAILED`, `RECOVERY_REQUIRED`, unexpected `CANCELLED`, and missing terminal outcomes fail the indicator. A BLOCK decision is reported under quality acceptance and does not become a platform-reliability failure unless execution or control behavior was also incorrect.

### Duration compliance

```text
100 * occurrences with end-to-end duration <= configured target
    / eligible occurrences with a configured duration target
```

End-to-end duration begins at the first attempt's `started_at_utc` and ends at the final terminal outcome. Retry and recovery time therefore remain visible. The standard batch is also reported against the six-hour Northstar processing window as a separate operational KPI.

### Quality acceptance

```text
100 * evaluated occurrences with final decision ACCEPT or ACCEPT_WITH_WARNINGS
    / eligible evaluated occurrences
```

WARN results remain accepted. Any BLOCK decision fails this indicator even when the block correctly protects publication.

### Quality enforcement

```text
100 * BLOCK decisions with no watermark advancement and a nonaccepted terminal outcome
    / all BLOCK decisions
```

A numerator row must prove:

- no committed watermark references the blocked `object_run_id`;
- the candidate boundary is abandoned or remains explicitly recovery-required;
- the object run is not `SUCCEEDED` or `SUCCEEDED_WITH_WARNINGS`; and
- the blocking decision and state evidence retain the same correlation identities.

Any failure is a control-integrity incident, not merely an exhausted error budget.

### Critical-alert latency

```text
100 * critical detections with routing decision created within 5 minutes
    / all critical detections requiring notification
```

The timer begins at the durable breach or critical-failure detection timestamp and stops when the environment-aware routing decision is persisted. External delivery time is reported separately because Development and Test do not contact real destinations.

## Eligibility and exclusions

Included:

- enabled objects expected to run in the evaluated environment;
- scheduled, interval, and event occurrences whose eligibility time falls in the window;
- authorized recovery attempts grouped with their original logical occurrence;
- no-data executions when they complete the full accepted control path.

Excluded only with durable reason and approval evidence:

- planned maintenance declared before the eligibility time;
- an explicitly disabled object;
- a cancelled synthetic failure exercise identified as such;
- duplicate telemetry rows that share the same stable evidence identity.

Not excluded:

- source outages that were not approved maintenance;
- capacity saturation;
- operator error;
- late recovery;
- missing telemetry;
- quality blocks;
- malformed or out-of-order evidence.

An exclusion must retain actor, reason, approval reference, start, end, environment, and affected scope. Silent denominator changes are prohibited.

## Error budgets

| Objective | Allowed miss rate | Interpretation |
|---|---:|---|
| Critical freshness | 1% | Occurrences beyond 15 minutes |
| Standard freshness | 1% | Daily occurrences after 6:00 a.m. |
| Ingestion reliability | 0.5% | Unexpected non-success outcomes |
| Duration compliance | 5% | Occurrences exceeding configured duration |
| Quality acceptance | 1% | Occurrences blocked by quality |
| Quality enforcement | 0% | No unsafe block handling is permitted |
| Critical-alert latency | 0% | Every critical routing decision must be durable within five minutes |

Error-budget consumption is:

```text
actual miss rate / allowed miss rate
```

A value below 1.0 is within budget, 1.0 is exhausted, and above 1.0 is breached. Zero-budget objectives bypass this division and breach on the first miss.

## Environment behavior

| Environment | Evaluation | Routing behavior |
|---|---|---|
| Development | Calculate all indicators | Persist simulated routing decision only |
| Test | Calculate all indicators and exercise runbooks | Persist simulated routing decision only |
| Production | Calculate all indicators | Resolve approved logical routing alias and create notification request |

This public learning implementation models Production behavior but does not connect to a real Northstar destination.

## Existing metadata compatibility

Metadata release 1.0.0 already defines per-run freshness, monthly reliability, duration, and quality contracts. OPS-002 treats those immutable definitions as source configuration and adds analytical aggregate objectives and operational evaluation rules.

The approved 99% aggregate freshness and quality-acceptance objectives, 95% duration-compliance objective, and five-minute alert-latency objective must not be back-written into release 1.0.0. A future metadata release may encode additional definitions and assignments after the evaluator proves the contract.

## Required telemetry gaps

The existing model provides run status, attempt, counts, errors, start/completion time, quality results, decisions, state events, SLO assignments, schedules, and ownership aliases. The operational projection must additionally produce:

- logical occurrence identity;
- resolved eligibility and deadline timestamps;
- source availability timestamp or `SCHEDULE_PROXY` provenance;
- first quality-accepted publication timestamp;
- configured duration target;
- breach detection timestamp;
- routing-decision timestamp;
- exclusion identity and approval evidence;
- evaluation version so historical results remain reproducible.

These are analytical/operational facts. They do not replace the immutable metadata release or mutable watermark state.
