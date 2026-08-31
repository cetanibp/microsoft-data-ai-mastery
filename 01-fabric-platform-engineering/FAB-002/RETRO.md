# FAB-002 retrospective — Resilient incremental ingestion

**Status:** Complete  
**Issue:** [#6 — FAB-002](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/6)  
**Pull request:** [#35](https://github.com/cetanibp/microsoft-data-ai-mastery/pull/35)

**Completed:** 2026-08-30

## Outcome

FAB-002 produced the first shared runtime consumer of the FAB-001 control plane. A Fabric Pipeline resolves one active ingestion configuration, claims a fixed watermark window, executes a parameterized notebook, publishes synthetic encounter rows through an idempotent Delta merge, and completes or abandons the candidate through transactional SQL procedures.

The implementation includes a credential-free executable reference contract, SQL state procedures, a Fabric notebook and generated Pipeline definition, automated artifact tests, schema-drift routing, correlated telemetry, failure injection, and sanitized live evidence.

## What was demonstrated

- A successful first window committed only after target publication.
- Same-window replay updated existing business keys without adding duplicates.
- Additive drift published the approved projection and recorded one schema-only event per object run.
- Breaking drift stopped publication before changing the target.
- A post-write crash left the durable target row in place but preserved the prior watermark.
- Recovery replay updated that row and safely committed the original fixed window.
- Two concurrent candidates for one window produced exactly one winner; the stale object run became `RECOVERY_REQUIRED` and could not overwrite the committed state.
- Pipeline, run, object-run, candidate, correlation, count, status, and timing identities remained traceable across the success and failure paths.

## Decisions made

### The notebook cannot advance state

Only the SQL compare-and-commit procedure can move the watermark. The notebook publishes data and returns sanitized results; orchestration owns the transactional outcome.

### Windows are fixed and replayable

Each attempt pins a lower-exclusive and upper-inclusive boundary before extraction. Recovery reuses that range rather than recalculating it from mutable source state.

### Target publication is idempotent by business key

The Bronze target merges on `encounter_id`. A retry after a durable write updates the existing row, so state recovery does not create a duplicate accepted record.

### Drift evidence is idempotent by object-run identity

Schema-only evidence merges on `object_run_id`. Payloads are excluded, and replaying an attempt cannot append an equivalent event with a different detection timestamp.

## Challenges and lessons

- Fabric Git integration synchronized database definitions but did not execute the FAB-001 metadata seed. Runtime readiness therefore needs both definition and reference-data verification.
- The Fabric UI calls the orchestration item `Pipeline`, while its generated source artifact uses the `DataPipeline` type.
- A blank optional notebook parameter arrived as null. The Pipeline mapping now normalizes it to an empty string.
- Generated-source review caught failure-path `actor_identity` and `correlation_id` values that had been stored as literals rather than expressions.
- Using the Pipeline name as the correlation identity violated the execution-run uniqueness constraint. `@pipeline().RunId` is the unique correlation value; the Pipeline name is only the trigger reference.
- A no-op boundary is intentionally rejected before candidate creation. Concurrent testing must use an upper bound beyond the current committed value.
- The Fabric authoring surface did not offer a second run action while one run was active; separate browser tabs enabled the live concurrency test.

## Limitations

- The source and data are synthetic; no external production source, protected data, credential, or endpoint was used.
- The vertical slice covers one timestamp-watermark object, not dependency scheduling or production-scale parallelism.
- Managed connection and Variable Library promotion across permanent environments remains a later deployment concern.
- The failure procedure currently records safe fallback counts when a failed notebook does not return a parseable exit payload.
- Reconciliation, executable quality gates, SLO evaluation, alert routing, capacity benchmarks, and regional recovery remain downstream work.

## Downstream handoff

### Issue #7 — reconciliation and data-quality gates

Issue #7 should reuse the FAB-002 environment, release, run, object-run, correlation, target, and publication-boundary identities. It should execute FAB-001 quality policies, persist check results, route quarantined records safely, and block publication when a configured gate fails.

### Issue #9 — SLOs, observability, and incident response

Issue #9 should project the durable execution and object-run telemetry into operational views, evaluate FAB-001 SLO definitions, resolve non-secret routing aliases, and demonstrate alert and recovery workflows.

## Evidence

See the [evidence index](evidence/README.md) and [live Fabric checkpoint](evidence/live-fabric-checkpoint.md) for the completed scenario results.
