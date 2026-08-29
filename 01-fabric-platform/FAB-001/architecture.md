# FAB-001 — Control-plane architecture requirements and principles

**Status:** In progress  
**Related issue:** [#5 — FAB-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/5)  
**Reference scenario:** [Northstar Health System](../../09-enterprise-architecture/ARCH-001/README.md)

## Purpose

This document establishes the requirements and design principles for the Northstar ingestion control plane before the logical and physical metadata models are created. The control plane must allow shared Fabric orchestration code to discover what to load, how to load it, when it is due, what it depends on, which service levels apply, and who owns recovery.

The control plane stores metadata and state. It does not contain business data, credentials, or source-specific executable code.

## Existing decisions inherited by FAB-001

| Source | Binding decision or requirement | Effect on the control plane |
|---|---|---|
| Northstar reference scenario | 40+ source systems, 600+ managed objects, 500 GB daily, billion-row tables, and a six-hour batch window | The model must support large inventories, selective execution, concurrency, and varied load strategies |
| Northstar security assumptions | Least privilege, auditability, nonproduction data controls, and externalized credentials | Metadata contains logical connection references only; sensitive values remain outside committed definitions |
| Northstar reliability requirements | 99.5% scheduled-run reliability, restartability, and idempotent replay | Watermark state, attempt identity, and safe restart semantics must be explicit |
| Northstar freshness requirements | Critical data within 15 minutes and standard batch data by 6:00 a.m. local time | Schedules and SLOs must support both latency- and deadline-based targets |
| ADR-001 | Separate workspaces by environment, domain, and responsibility, with measurable capacity placement | Metadata must preserve environment and ownership boundaries without duplicating pipeline code |
| ADR-002 / OPS-001 | Git is the source for deployable definitions; Development, Test, and Production use approved promotion | Versioned metadata definitions must follow the same PR and promotion lifecycle |
| OPS-001 | Fabric Variable Libraries provide stage values; GitHub Environment variables provide automation routing | The control plane references stage configuration without embedding workspace IDs, tenant IDs, credentials, or access tokens |
| OPS-001 | Rollback is appropriate for definitions; stateful changes may require forward recovery | Definition versions and mutable runtime state must have separate lifecycle rules |

## Downstream consumer contracts

### Issue #6 — resilient incremental ingestion

The ingestion runtime must be able to resolve:

- the active source and target object definition for an environment;
- the load strategy and supported strategy parameters;
- the watermark column, data type, comparison behavior, and overlap policy;
- the last committed watermark and the run that committed it;
- dependencies and execution eligibility;
- retry, timeout, priority, and concurrency behavior;
- the logical connection reference;
- the owner and recovery guidance.

Metadata reads must be deterministic for a run. Mutable watermark state must advance only after successful acceptance of the corresponding data.

### Issue #7 — reconciliation and data-quality gates

The quality runtime must be able to resolve:

- which quality or reconciliation policy applies to an object;
- blocking versus warning behavior;
- thresholds and effective versions;
- quarantine and traceability expectations;
- the SLO or publication decision affected by a failed check;
- ownership and escalation routing.

FAB-001 defines policy references and lifecycle boundaries. Issue #7 will implement the check engine and result processing.

### Issue #9 — SLOs, observability, and incident response

The operations layer must be able to resolve:

- freshness, reliability, duration, and quality objectives;
- evaluation windows, time zones, and severity;
- operational owner and escalation path;
- schedule and expected-completion context;
- correlation keys that connect object, metadata version, run, quality result, and release evidence.

FAB-001 defines objectives and identifiers. Issue #9 will implement telemetry, evaluation, alert routing, and runbooks.

## Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | Represent source systems independently from individual source objects |
| FR-02 | Represent source and target objects with stable identifiers rather than names as relational keys |
| FR-03 | Support full, watermark, append, and snapshot load strategies |
| FR-04 | Permit strategy-specific parameters while rejecting unknown or unsafe parameters |
| FR-05 | Represent directed dependencies and detect self-references and cycles before activation |
| FR-06 | Support schedules, time zones, activation windows, priorities, and concurrency groups |
| FR-07 | Represent freshness, reliability, duration, and quality SLOs with effective versions |
| FR-08 | Associate accountable engineering, source, data-product, and incident owners |
| FR-09 | Resolve Development, Test, and Production configuration without changing orchestration code |
| FR-10 | Enable or disable a source or object by environment |
| FR-11 | Keep watermark definitions separate from mutable watermark values |
| FR-12 | Associate every run with the exact approved metadata version it used |
| FR-13 | Support draft, approved, active, superseded, retired, and rejected lifecycle outcomes |
| FR-14 | Preserve change reason, actor, approval, and effective timestamps |
| FR-15 | Reject incomplete or inconsistent metadata before runtime selection |
| FR-16 | Allow selective execution by object, source, domain, schedule, dependency, or recovery request |
| FR-17 | Provide stable correlation identifiers across ingestion, quality, operations, and deployment evidence |
| FR-18 | Support synthetic Northstar seed data without real endpoints or organizational details |

## Nonfunctional requirements

| ID | Requirement | Initial design response |
|---|---|---|
| NFR-01 Security | No secret values in Git, seed data, metadata definitions, logs, or evidence | Store only logical connection references |
| NFR-02 Reliability | State transitions must be atomic, retry-safe, and auditable | Use explicit status and compare-before-advance rules |
| NFR-03 Restartability | Failed work can resume or replay without silently skipping or duplicating accepted data | Preserve committed and proposed watermark context separately |
| NFR-04 Idempotency | Reprocessing the same valid input produces the same accepted business result | Define run identity, input boundary, and commit semantics |
| NFR-05 Scale | Support at least 40 sources and 600 active objects without object-specific code | Use normalized definitions and set-based selection |
| NFR-06 Performance | Metadata lookup must not materially consume the six-hour batch window | Index selection keys and return only runnable configuration |
| NFR-07 Auditability | Changes and state transitions are traceable to actor, reason, time, and correlation ID | Use immutable history or append-only event records where appropriate |
| NFR-08 Maintainability | Common changes are data changes, not pipeline edits | Prefer declarative policies with constrained strategy types |
| NFR-09 Portability | Logical design remains usable if the physical Fabric storage choice changes | Separate the contract from product-specific DDL |
| NFR-10 Testability | Invalid definitions and unsafe transitions can be exercised without live sources | Provide synthetic seeds and automated contract tests |
| NFR-11 Recoverability | Definition rollback and state recovery are handled explicitly | Version definitions; use controlled state correction or forward recovery |
| NFR-12 Observability | Metadata identity is carried into downstream telemetry | Require object, version, environment, and run correlation keys |

## System-of-record boundaries

| Information | System of record | Prohibited content |
|---|---|---|
| Logical metadata definitions | Git-reviewed FAB-001 definitions promoted through Fabric lifecycle | Credentials, access tokens, real protected data |
| Active stage values | Fabric Variable Library or supported deployment configuration | Deployable code forks per environment |
| Automation routing | Protected GitHub Environment variables | Values embedded in Fabric item definitions |
| Connection authentication | Fabric managed connection, Key Vault, or approved identity boundary | Secret values in metadata tables or repository files |
| Mutable execution state | Runtime control-plane store | Manual edits without actor, reason, and audit evidence |
| Release evidence | GitHub and Fabric deployment evidence defined by OPS-001 | Tokens or sensitive configuration |
| Business data | Bronze, Silver, Gold, or governed data-product stores | Payload data copied into control-plane tables |

## Design principles

1. **Stable identity over mutable names.** Relationships use surrogate or immutable business identifiers; display names may change.
2. **Definitions are not runtime state.** Approved intent and mutable execution state have different tables, permissions, and recovery procedures.
3. **One orchestration path across environments.** Environment selection changes data, connections, and routing—not pipeline or notebook logic.
4. **Configuration references, secrets do not.** Metadata may name a managed connection but never store its credential.
5. **Deterministic run snapshots.** A run resolves one approved metadata version and retains that identity for its lifetime.
6. **Watermarks commit after accepted outcomes.** Starting or extracting a run never advances the committed boundary.
7. **Invalid metadata fails before work begins.** Referential, lifecycle, dependency, strategy, and environment checks run before activation.
8. **Declarative but constrained.** Prefer enumerated strategies and validated parameters over arbitrary SQL or executable expressions.
9. **Dependencies form a validated directed acyclic graph.** Cycles and unresolved predecessors cannot become active.
10. **SLOs and ownership are first-class metadata.** Every production object has measurable expectations and accountable owners.
11. **Audit events are append-oriented.** Corrections preserve prior evidence and identify the reason and actor.
12. **Recovery is designed, not inferred.** Each strategy declares restart, replay, and forward-recovery expectations.
13. **Least privilege follows boundaries.** Definition maintainers, runtime identities, operators, and approvers receive distinct permissions.
14. **Synthetic evidence is sufficient for the public repository.** Demonstrations prove behavior without exposing organizational details.
15. **Downstream extensibility is explicit.** Quality, telemetry, lineage, cost, and agent diagnosis can reference the same stable identifiers.

## Required validation scenarios

The completed design must support automated tests for:

1. a valid Development configuration resolving differently from Test without code changes;
2. a full-load object and a watermark-load object;
3. a multi-object dependency chain;
4. missing source, target, owner, schedule, SLO, or environment references;
5. a self-dependency and a multi-object cycle;
6. duplicate active definitions for the same environment and logical object;
7. an unsupported load strategy or invalid strategy parameter;
8. an unresolved or secret-like connection value;
9. proposed watermark advancement followed by failure and safe restart;
10. successful watermark commit with complete audit identity;
11. use of a superseded or unapproved metadata version;
12. an object whose quality failure blocks publication and one whose warning does not.

## Decisions required during logical modeling

The next increment must resolve and document:

- the initial physical control-plane store in Fabric;
- bundle-level versus row-level metadata versioning;
- how flexible strategy parameters are represented without permitting arbitrary executable content;
- dependency scope across schedules, domains, and environments;
- schedule representation and time-zone rules;
- concurrency and priority semantics;
- watermark lease, proposal, and commit transitions;
- the minimum ownership and escalation model;
- whether audit history uses temporal snapshots, append-only events, or both.

## Exit criteria for this inventory

This requirements inventory is complete when the logical model maps every functional requirement to one or more entities or validation rules, and each downstream issue can consume the model without adding a contradictory control-plane concept.
