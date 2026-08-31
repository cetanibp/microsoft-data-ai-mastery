# FAB-002 — Incremental-ingestion runtime architecture

**Status:** In progress

**Related issue:** [#6 — FAB-002](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/6)

**Upstream contract:** [FAB-001](../FAB-001/README.md)

**Reference scenario:** [Northstar Health System](../../09-enterprise-architecture/ARCH-001/README.md)

## Objective

Implement one shared, metadata-driven runtime that can incrementally ingest a source object, safely restart after partial failure, replay without duplicating accepted business records, route schema drift, and preserve complete operational identity.

The first vertical slice targets the synthetic `ingest-clinical-encounter` object. Later objects must use the same runtime path and adapters rather than copied object-specific orchestration.

## Binding upstream decisions

FAB-002 consumes rather than redefines:

- `ctrl.vw_ActiveIngestionConfiguration` for active environment/object resolution;
- immutable metadata release identity and configuration hash;
- `ops.ExecutionRun` and `ops.ObjectRun` for run evidence;
- `ops.WatermarkState` and `ops.WatermarkCandidate` for mutable boundaries;
- optimistic compare-and-commit watermark behavior;
- logical connection references with credentials outside Git and the control plane;
- OPS-001 environment, identity, promotion, and secret boundaries.

## Runtime invariants

1. A run pins one environment and one approved metadata release for its lifetime.
2. Every object attempt has a unique object-run identity and attempt number.
3. The input boundary is immutable and hashable for an attempt.
4. Timestamp extraction uses `watermark > lower_bound AND watermark <= upper_bound`.
5. The upper bound is captured before extraction and does not move during the attempt.
6. Target publication is idempotent by the declared business key.
7. A watermark candidate is proposed separately from the committed state.
8. Failure never advances committed watermark state.
9. Watermark commit occurs only after the corresponding target result is accepted.
10. Commit succeeds only if the state version still matches the version observed by the candidate.
11. A stale commit becomes `RECOVERY_REQUIRED`; it is never silently overwritten.
12. Every terminal outcome records correlation identity, counts, status, duration, and a sanitized error classification when applicable.

## Component boundaries

| Component | Responsibility | Initial implementation |
|---|---|---|
| Configuration resolver | Resolve one active environment/object configuration and pin its release | FAB-001 SQL view |
| Source adapter | Discover schema, capture upper bound, and extract the fixed window | Synthetic encounter source |
| Drift classifier | Compare discovered and approved contracts | Blocking or quarantine route |
| Target adapter | Idempotently publish accepted rows | Bronze Delta merge by `encounter_id` |
| State coordinator | Propose, abandon, and compare-and-commit watermarks | FAB-001 operational tables plus constrained procedures |
| Evidence writer | Persist counts, timings, statuses, and identities | FAB-001 operational/audit tables |
| Orchestrator | Enforce ordering, retries, timeout, and terminal status | Shared Fabric pipeline and notebook |

## Execution flow

```text
Resolve configuration and pin release
                 |
                 v
Create run identity and read committed watermark
                 |
                 v
Capture upper bound and extract the fixed window
                 |
                 v
Compare discovered schema with the approved contract
        |                              |
        | blocking drift/failure       | accepted projection
        v                              v
Record failure and              Propose watermark candidate
preserve watermark                       |
                                        v
                              Merge into Bronze by business key
                                        |
                       +----------------+----------------+
                       |                                 |
                       | target failure                  | target accepted
                       v                                 v
              Abandon candidate and            Compare-and-commit candidate
              preserve watermark                        |
                                             +----------+----------+
                                             |                     |
                                             | stale version       | accepted
                                             v                     v
                                      Recovery required     Record success
```

The committed watermark changes only on the final accepted path. Every failure
or stale-state path leaves it unchanged and retains the fixed window for safe
recovery.

## Replay and failure behavior

| Failure point | Durable target effect | Watermark effect | Required recovery |
|---|---|---|---|
| Before extraction | None | Unchanged | Retry same or newly captured safe window |
| During extraction | None | Unchanged | Retry fixed input boundary when available |
| After extraction, before target write | None | Unchanged; proposed candidate abandoned | Replay same window |
| During target write | Partial writes may exist | Unchanged; candidate abandoned | Replay same window through idempotent upsert |
| After target write, before watermark commit | Accepted rows may exist | Unchanged | Replay; upsert produces updates/no-ops rather than duplicates |
| Concurrent state change before commit | Accepted rows may exist | Stale candidate rejected | Re-resolve state and classify overlap before forward recovery |
| After successful commit | Accepted rows durable | Advanced exactly once | A duplicate trigger extracts no already-committed rows |

## Duplicate contract

Duplicates are evaluated at two boundaries:

- within one extracted window, retain the row with the greatest watermark for a business key;
- at the Bronze target, merge by business key so replay updates the existing record rather than appending another accepted record.

Two rows with the same business key and watermark but conflicting payloads are ambiguous. The live implementation must quarantine or fail them according to the activated policy; it must not select one nondeterministically.

## Schema-drift routes

| Drift class | Example | Route | Watermark rule |
|---|---|---|---|
| No drift | Approved columns and compatible types | Publish | Eligible to commit |
| Additive, policy allows quarantine | New nullable source column | Quarantine drift evidence; publish approved projection | Commit only when all rows are accounted for |
| Breaking | Missing key/watermark column or incompatible type | Block | Preserve committed state |
| Ambiguous contract | Renamed column or conflicting type inference | Block and require owner review | Preserve committed state |

Schema evidence must contain column names, normalized types, classification, policy, object identity, and correlation ID. It must not contain source values or protected payload samples.

## Telemetry contract

Each object attempt records:

- environment, release, run, object-run, object, attempt, and correlation identifiers;
- fixed lower and upper boundaries plus their hash;
- extracted, accepted, rejected/quarantined, inserted, updated, and duplicate counts;
- start, completion, and duration;
- terminal status and sanitized error classification;
- candidate and committed state versions;
- schema fingerprint and drift classification.

Issue #9 may project this evidence into SLOs and alerts, but it must retain these identities.

## Security and cost boundaries

- Use only synthetic source and target data for repository and learning evidence.
- Resolve credentials through Fabric managed connections or approved identities; never log them.
- Do not place endpoints, workspace IDs, connection strings, access tokens, or payload samples in Git evidence.
- Bound extraction by a fixed window and use configured connection concurrency to avoid unbounded source pressure.
- Record row counts and duration so later capacity and cost analysis can use measured evidence.

## Validation plan

| Scenario | Credential-free contract | Live Fabric |
|---|---:|---:|
| First successful watermark window | Required | Passed |
| Empty subsequent window | Required | Passed |
| Duplicate rows in one source window | Required | Passed |
| Crash after target write, before commit | Required | Passed |
| Retry without duplicate accepted records | Required | Passed |
| Failed attempt preserves watermark | Required | Passed |
| Stale candidate rejected | Required | Required |
| Breaking schema drift blocked | Planned | Passed |
| Additive drift quarantined | Planned | Passed |
| Counts, duration, status, and correlation trace | Required | Passed |

## First implementation increment exit criteria

- Architecture and safety invariants are reviewable.
- The reference contract is executable using only the Python standard library.
- Automated tests prove happy path, empty window, in-window deduplication, crash-after-write recovery, state preservation, stale commit rejection, and telemetry identity.
- CI emits sanitized machine-readable test evidence.
- No Fabric resource or credential is required.
