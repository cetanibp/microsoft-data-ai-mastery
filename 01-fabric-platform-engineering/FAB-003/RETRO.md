# FAB-003 retrospective — Reconciliation and data-quality gates

**Status:** Complete  
**Issue:** [#7 — FAB-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/7)  
**Completed:** 2026-09-02

## Outcome

FAB-003 inserted a policy-driven acceptance boundary between FAB-002 target publication and watermark commit. The completed vertical slice resolves activated FAB-001 quality policies, evaluates allowlisted reconciliation and aggregate checks, persists idempotent Delta and SQL evidence, records hashed quarantine identities, derives one durable object-run decision, and permits watermark completion only through a quality-accepted wrapper.

The implementation includes a credential-free reference runtime, 33 automated tests, three SQL evidence tables, one operational view, five stored procedures, a Fabric quality notebook, a generated quality-enabled Pipeline, a development Lakehouse, controlled failure injection, and sanitized live evidence.

## What was demonstrated

- Four blocking reconciliation and key checks produced a durable `ACCEPTED` decision before watermark commit.
- A controlled target-count variance produced exactly one failed blocking rule, a durable `BLOCKED` decision, an abandoned candidate, and no watermark or state-version change.
- Replaying the blocked fixed boundary without injection succeeded and advanced the watermark exactly once.
- A synthetic duplicate window extracted two versions of one business key, accepted the latest row, and stored one `DUPLICATE_BUSINESS_KEY` quarantine record.
- Quarantine evidence contained only deterministic identities, reason codes, and 64-character hashes; no raw payload values were stored.
- Replaying the same quarantine write for the same object run retained one row and one distinct quarantine ID.
- The existing WARN contract produced `ACCEPTED_WITH_WARNING`, one warning, zero blocking failures, and `watermark_commit_eligible = true` in an isolated live Delta validation.
- The generated Pipeline calls `ops.usp_CompleteQualityAcceptedWatermarkAttempt`; the original direct completion path is absent.

## Decisions made

### Quality is a durable acceptance boundary

Target writes can occur before validation, but acceptance and mutable-state advancement require a durable quality decision. A notebook result alone cannot authorize watermark commit.

### Policy execution is allowlisted

FAB-001 metadata stores versioned contract references and enforcement modes. FAB-003 owns the executable allowlisted implementation behind those references. Arbitrary SQL, expressions, and executable metadata remain prohibited.

### Blocking and warning outcomes are distinct

A failed or errored required BLOCK check abandons the candidate and closes the run as failed. WARN evidence remains reviewable while retaining commit eligibility.

### Quarantine stores identity, not payload

The operational record stores a deterministic quarantine ID, policy/rule keys, a reason code, the fixed-boundary hash, and a hashed source-record identity. Raw protected values are excluded.

### Generated physical bindings do not belong in Git

Fabric notebook auto-binding wrote a physical workspace ID into generated source. CI rejected it, the repository definition was sanitized, and generated-pipeline tests now enforce zeroed workspace identifiers.

## Challenges and lessons

- An empty optional Pipeline parameter arrived at the notebook as null. The Pipeline now maps `quality_test_mode` through `coalesce`.
- Fabric Git generated the Pipeline and Lakehouse outside the FAB-003 workspace subfolder. Workflow path filters were expanded so later changes still trigger validation.
- Notebook auto-binding can reintroduce physical Lakehouse and workspace identifiers after every Fabric commit. The live workspace attachment and sanitized Git definition must be treated as separate environment-binding layers.
- The encounter object has only the blocking policy assigned in immutable release `1.0.0`. The existing warning policy was therefore validated live in an isolated Delta evidence table rather than falsely attaching it to the released encounter configuration.
- The original synthetic source window was already behind the committed watermark. Adding a later duplicate window enabled a genuine end-to-end quarantine test without resetting state.
- Querying current `WatermarkState` alongside historical decisions shows the latest state for every historical row; candidate boundaries and identities must be used to interpret historical outcomes correctly.

## Limitations

- All data is synthetic; no external source, protected data, credential, or endpoint was used.
- The initial vertical slice covers one timestamp-watermark object and one generated Pipeline.
- Live WARN evaluation proved notebook behavior and Delta evidence, but did not write a SQL control-plane warning decision because the approved release does not assign WARN to the encounter object.
- Physical Lakehouse binding remains a deployment-time workspace concern and is intentionally absent from Git.
- Production-scale reconciliation, distributed capacity behavior, alert routing, SLO evaluation, and long-term analytical retention remain future work.

## Downstream handoff

### Issue #9 — SLOs, observability, and incident response

Issue #9 can consume `ops.vw_QualityResultOperational`, `ops.QualityDecision`, object-run status, correlation identity, result-set hashes, rule durations, warning counts, blocking counts, and watermark outcomes. It should add SLO evaluation, dashboards, alert routing, incident severity, and recovery runbooks without weakening the FAB-003 acceptance boundary.

### Future metadata release

A later governed metadata release may assign the WARN policy to a watermark object or add a quality-enabled full-load coordinator. It must create and activate a new immutable snapshot rather than editing release `1.0.0` in place.

## Evidence

See the [FAB-003 evidence index](evidence/README.md) for automated runs, live accepted/block/recovery/quarantine/warning results, sanitization controls, and remaining operational handoff notes.
