# FAB-003 — Reconciliation and quality-gate architecture

**Status:** Complete

**Related issue:** [#7 — FAB-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/7)

## Decision summary

Quality evaluation is an acceptance boundary inside the existing FAB-002 object-run lifecycle. Target writes may occur before evaluation, but publication acceptance and watermark commit occur only after all required blocking checks pass.

Warning checks preserve evidence without preventing acceptance. Blocking failures preserve committed watermark state and route rejected data or the affected boundary for governed recovery.

## Invariants

1. Every quality evaluation resolves the same environment, metadata release, run, object run, ingestion object, and fixed input boundary as ingestion.
2. Only activated, versioned, allowlisted quality policies can execute.
3. Quality metadata contains declarative parameters, never arbitrary SQL or executable expressions.
4. Count accounting is explicit: extracted rows must resolve to accepted, rejected, duplicate, or otherwise classified outcomes.
5. A required blocking failure prevents watermark commit.
6. A warning never silently changes into a blocking decision.
7. Quarantine evidence preserves correlation and reason codes without exposing protected payloads.
8. Replaying the same object run does not duplicate check results or quarantine evidence.
9. Terminal decisions and check results are append-only or idempotently keyed for auditability.
10. Failure to execute a required check is itself a blocking quality outcome.

## Initial check types

| Check type | Purpose | Initial behavior |
|---|---|---|
| `ROW_COUNT_BALANCE` | Reconcile extracted outcomes | Require extracted = accepted + rejected + duplicate |
| `TARGET_COUNT` | Compare accepted scope with published target scope | Exact or percentage variance threshold |
| `NULL_RATE` | Measure missing required values | Maximum percentage threshold |
| `DISTINCT_KEY` | Detect duplicate business keys | Maximum duplicate count or rate |
| `MIN_VALUE` | Validate a lower aggregate bound | Numeric or timestamp comparison |
| `MAX_VALUE` | Validate an upper aggregate bound | Numeric or timestamp comparison |
| `SUM_VALUE` | Reconcile an allowlisted numeric measure | Absolute and/or percentage tolerance |

The first executable increment may implement a subset, but the policy shape must remain extensible without accepting arbitrary executable content.

## Decision flow

1. Resolve active quality policies in declared order.
2. Compute source and target observations for the fixed object-run boundary.
3. Evaluate each check against its versioned threshold.
4. Persist the observation, expected condition, result, severity, and correlation identities.
5. Route row-level failures to quarantine when required.
6. Derive one object-run quality decision:
   - `ACCEPTED`: all required checks passed;
   - `ACCEPTED_WITH_WARNING`: no blocking failure and at least one warning;
   - `BLOCKED`: a blocking check failed or could not execute.
7. Permit watermark compare-and-commit only for accepted decisions.
8. Preserve the candidate and committed state on blocked outcomes for recovery.

## Evidence contract

Each check result records:

- environment and metadata release;
- `run_id`, `object_run_id`, ingestion object, and attempt;
- policy key, policy version, check type, and ordinal;
- fixed boundary hash;
- observed value, comparison operator, threshold, and tolerance;
- `PASS`, `WARN`, `FAIL`, or `ERROR`;
- enforcement mode and publication decision;
- evaluation timestamps and duration;
- sanitized failure classification.

Quarantine evidence additionally records a deterministic quarantine identity, reason code, source record identity hash, boundary hash, and run correlation. Raw protected values are excluded from repository evidence.

## Recovery behavior

| Outcome | Publication decision | Watermark effect | Recovery |
|---|---|---|---|
| All required checks pass | Accept | Eligible to commit | None |
| Warning check fails | Accept with warning | Eligible to commit | Operational review |
| Blocking check fails | Block | Unchanged | Correct data or policy, then replay fixed boundary |
| Required check errors | Block | Unchanged | Repair evaluator/configuration, then replay |
| Failure after target write | Not yet accepted | Unchanged | Idempotent replay and re-evaluation |

## Deployable component mapping

| Responsibility | Artifact |
|---|---|
| Resolve activated policy reference | `ops.usp_ResolveQualityPolicy` |
| Execute allowlisted contract | `NB_FAB003_QualityGate` |
| Preserve notebook evidence | Idempotent Delta quality-result and quarantine tables |
| Persist transactional results | `ops.usp_RecordQualityCheckResult` and `ops.usp_RecordQuarantineEvidence` |
| Derive and enforce decision | `ops.usp_FinalizeQualityDecision` |
| Require acceptance before state advancement | `ops.usp_CompleteQualityAcceptedWatermarkAttempt` |
| Publish operational review surface | `ops.vw_QualityResultOperational` |

The FAB-001 policy rows remain unchanged. Their versioned `contract_reference` resolves to an allowlisted contract owned by FAB-003, so the approved metadata release is consumed rather than rewritten. Arbitrary SQL and executable metadata remain prohibited.
