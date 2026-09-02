# OPS-002 — Failure-recovery exercise

**Environment:** Development  
**Exercise date:** 2026-09-02  
**Data:** Synthetic Northstar control-plane evidence  
**Result:** Passed

## Scenario

The exercise used a real orphaned watermark candidate rather than creating a second synthetic failure. The candidate belonged to a clinical-encounter object attempt that remained `CLAIMED` with a `PROPOSED` watermark after the accepted state had advanced through another attempt.

| Field | Stale attempt | Accepted state |
|---|---|---|
| Object-run identity | `f0c3ae1b-f735-45ac-9e02-6ef2658cc3d9` | `a7e08393-6af8-46e3-90da-5141c086387f` |
| Boundary | `2026-08-30T12:15:00Z` | `2026-08-30T12:23:00Z` |
| Observed/current state version | 0 | 7 |
| Initial status | `CLAIMED` / `PROPOSED` | Committed |

## Detection and triage

The read-only runbook query identified one active candidate whose observed state version was seven revisions behind the current committed version. The accepted boundary was also eight minutes later than the stale candidate's proposed boundary.

The operator classified the attempt as `DUPLICATE_CONFLICT`. This classification preserves the accepted winner and makes the losing attempt terminal without modifying the current watermark.

## Recovery decision

The operator executed the governed failure transition through `ops.usp_FailWatermarkAttempt` with the exercise actor identity `operator:ops-002-exercise`.

Replay was not performed. The committed boundary already covered all data represented by the stale candidate, and replaying an obsolete state-version observation would add risk without advancing recovery.

## Durable results

The transition produced the following terminal state:

| Field | Result |
|---|---|
| Candidate status | `ABANDONED` |
| Resolution reason | `DUPLICATE_CONFLICT` |
| Object-run status | `FAILED` |
| Error classification | `DUPLICATE_CONFLICT` |
| Parent run status | `FAILED` |
| Committed watermark | `2026-08-30T12:23:00Z` |
| State version | 7 |
| Committed object run | `a7e08393-6af8-46e3-90da-5141c086387f` |

The audit stream recorded `WATERMARK_ABANDONED` at `2026-09-02 04:47:12.787018` UTC with the reason `Attempt failed: DUPLICATE_CONFLICT`. Earlier `OBJECT_CLAIMED` and `WATERMARK_PROPOSED` events remained intact, preserving the full attempt history.

## Final verification

The final verification returned:

- zero active `PROPOSED` candidates for the Development clinical-encounter object;
- zero quality-enforcement integrity breaches;
- the recovered occurrence projected as `FAILED`, `UNRELIABLE`, `DUPLICATE_CONFLICT`, `ABANDONED`, and quality enforcement `NOT_APPLICABLE`; and
- the accepted watermark unchanged at `2026-08-30T12:23:00Z`, state version 7.

This proves that detection, triage, terminal failure handling, audit preservation, and state-safe recovery operate together without regressing the accepted data boundary.
