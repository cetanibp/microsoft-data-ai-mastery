# FAB-001 — Ingestion control-plane metadata model

FAB-001 designs and validates the metadata contract that will drive Northstar's shared Microsoft Fabric ingestion framework.

## Status

Complete. The logical and physical models, automated contract tests, live Fabric SQL Database deployment, watermark transaction validation, governance guidance, evidence, and downstream handoff are complete.

## Evidence index

| Evidence | Purpose | Status |
|---|---|---|
| [Architecture requirements and principles](architecture.md) | Records inherited decisions, downstream contracts, requirements, boundaries, validation scenarios, and design principles | Complete |
| [Logical metadata model](metadata-model.md) and [Mermaid ER source](metadata-model.mmd) | Defines entities, relationships, cardinality, lifecycle, environment resolution, dependencies, and safe watermark transitions | Complete |
| [Fabric SQL Database package](sql/README.md) | Implements 28 definition, runtime, and audit tables; three views; synthetic Northstar release 1.0.0; and rollback-safe live validation | Deployed and validated |
| [Automated metadata-contract tests](tests/README.md) | Proves semantic validation, environment resolution, failure paths, SQL structure, and watermark state behavior | 33 tests passed |
| [Configuration and secrets boundary](configuration-and-secrets.md) | Defines ownership across Git, Variable Libraries, managed connections, runtime state, secrets, and evidence | Complete |
| [Ownership and lifecycle](ownership-and-lifecycle.md) | Defines roles, approval, activation, versioning, rollback, forward recovery, and state correction | Complete |
| [Validation evidence](evidence/README.md) | Records CI artifacts, live database structure, active resolution, dependencies, validation issues, and transaction results | PASS |
| [Retrospective and downstream handoff](RETRO.md) | Summarizes outcomes, decisions, lessons, limitations, and contracts for issues #6, #7, and #9 | Complete |

## Implemented contract

- Immutable, full-snapshot metadata releases with source commit and content hash
- Development, Test, and Production resolution without orchestration-code changes
- Logical connection and routing references with an external credential boundary
- FULL, WATERMARK, APPEND, and SNAPSHOT strategies
- Directed dependency, schedule, execution-policy, SLO, quality, and ownership metadata
- Separate definition, activation, runtime-state, and audit lifecycles
- Optimistic compare-and-commit watermark protocol
- Fail-closed semantic validation
- Stable environment, release, run, object-run, and correlation identities

## Validation summary

| Validation | Result |
|---|---:|
| Automated tests | 33 passed; 0 failed |
| Fabric SQL Database deployment | PASS |
| User tables / views / foreign keys | 28 / 3 / 47 |
| Active environment/object configurations | 14 |
| Dependency edges | 3 |
| Metadata validation issues | 0 |
| Failed-attempt state preservation | PASS |
| Successful watermark compare-and-commit | PASS |
| Stale-write rejection | PASS |
| Correlated audit evidence | PASS |

The live validation used the isolated `Northstar Data Platform - FAB-001` workspace and `sqldb_northstar_control`. Synthetic transaction-test data was rolled back.

## Relationship to other work

- [Issue #8](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8) supplies the accepted Git, environment, deployment, identity, and credential boundaries.
- [Issue #6](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/6) consumed this contract in the completed [FAB-002 resilient ingestion runtime](../FAB-002/README.md).
- [Issue #7](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/7) will consume quality-policy and publication-gate references.
- [Issue #9](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/9) will consume SLO, ownership, schedule, event, and correlation metadata.

No real organizational credentials, endpoints, patient data, or proprietary metadata are used.
