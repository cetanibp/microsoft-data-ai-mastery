# Runbook — Triage

## Trigger

Use this runbook for an SLO breach, failed or recovery-required run, quality block, P1 control-integrity condition, missing telemetry, or routing defect.

## Required starting evidence

Capture at least one stable identifier:

- alert routing decision or deduplication key;
- SLO evaluation;
- object run;
- run or correlation ID; or
- environment, object, and time window.

Do not paste source payloads, credentials, endpoints, personal addresses, or sensitive error details into the incident record.

## Procedure

1. Record acknowledgement time and operator identity.
2. Use `queries.sql` to locate the routing decision, evaluation, occurrence, and quality/state evidence.
3. Confirm the environment and metadata release recorded by the evidence. Do not substitute the currently active release.
4. Determine whether the occurrence is still in progress. An active `CLAIMED`, `EXTRACTING`, `VALIDATING`, or `PUBLISHING` occurrence is not replayed.
5. Classify the primary category:
   - execution failure;
   - freshness or duration breach;
   - quality block or warning;
   - watermark concurrency/recovery condition;
   - telemetry or routing failure; or
   - quality-enforcement integrity breach.
6. Check `ops.vw_QualityEnforcementIntegrity` before any recovery action.
7. Identify the fixed input boundary, candidate status, committed state version, and last committing object run.
8. Determine affected downstream objects and consumer deadlines.
9. Resolve the accountable owner from the run's release-scoped ownership metadata.
10. Assign severity using the escalation runbook.
11. Select the recovery pattern and document why alternatives were rejected.

## Stop conditions

Stop and escalate as P1 when:

- a blocked decision has a committed candidate or accepted terminal status;
- `WatermarkState.committed_object_run_id` references a blocked run;
- evidence identities conflict or hashes do not reconcile;
- a credential or sensitive payload appears in telemetry;
- the required release, boundary, or owner cannot be established; or
- another active attempt owns the same boundary.

## Completion criteria

Triage is complete when the incident record contains category, severity, environment, release, occurrence identity, fixed boundary, current state, impact, owner, selected recovery pattern, and the evidence supporting each conclusion.
