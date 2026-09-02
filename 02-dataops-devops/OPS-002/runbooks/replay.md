# Runbook — Safe replay

## Purpose

Replay an eligible fixed-boundary occurrence through the existing idempotent FAB-002/FAB-003 path without duplicating accepted records or advancing unaccepted state.

## Preconditions

All conditions must be true:

- triage is complete and an incident owner is assigned;
- quality-enforcement integrity is `PASS` or not applicable;
- no other occurrence is active for the same environment, object, and boundary;
- the original `environment_id`, `release_id`, `run_id`, `object_run_id`, `correlation_id`, and `input_boundary_hash` are known;
- the original candidate is `ABANDONED` or explicitly recovery-required, not `COMMITTED` by another run;
- the target merge/idempotency contract still applies;
- the definition release is still replay-compatible with current runtime state;
- the failure cause is corrected or intentionally reproduced for an approved exercise; and
- replay authorization and reason are recorded.

## Prohibited shortcuts

- Do not update `WatermarkState` directly.
- Do not mark a candidate committed manually.
- Do not change an immutable release or quality decision.
- Do not generate a new boundary merely to avoid the failed one.
- Do not disable a BLOCK rule or convert it to WARN operationally.
- Do not delete target, quarantine, or telemetry evidence before replay.

## Procedure

1. Record the pre-replay state using the query pack.
2. Confirm the original fixed boundary and source-evidence hash.
3. Confirm the target contains no conflicting accepted business state. Existing rows written by the failed attempt must be safe for the declared merge contract.
4. Invoke the approved quality-enabled recovery path using the original object-run identity and boundary. The recovery execution must identify itself as recovery in the parent run/audit evidence.
5. Allow extraction, idempotent publication, required quality evaluation, decision finalization, and compare-and-commit to execute in their normal order.
6. Do not call watermark completion directly; only the quality-accepted wrapper may commit state.
7. After completion, verify:
   - exactly one logical accepted business result;
   - one durable quality decision for the object run;
   - required quarantine evidence remains idempotent;
   - candidate and watermark state agree;
   - terminal object-run status is correct;
   - correlation identities remain unchanged; and
   - operational views show the recovered outcome.
8. Re-evaluate affected SLOs and persist/reroute only new or changed decisions.

## Replay failure

If replay fails again, preserve all evidence, stop repeated manual retries, update the incident timeline, and escalate based on cumulative impact. A third attempt requires explicit incident-owner approval in this learning contract.

## Completion criteria

Replay is complete only when data, quality, state, telemetry, and SLO evidence reconcile. Successful pipeline completion alone is insufficient.
