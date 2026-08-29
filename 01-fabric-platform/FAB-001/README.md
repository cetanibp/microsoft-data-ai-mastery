# FAB-001 — Ingestion control-plane metadata model

FAB-001 designs and validates the metadata contract that will drive Northstar's shared Microsoft Fabric ingestion framework.

## Status

In progress. Requirements, design principles, the logical model, and the Fabric SQL Database physical package are drafted. Automated metadata-contract tests are the next increment.

## Evidence index

| Evidence | Purpose | Status |
|---|---|---|
| [Architecture requirements and principles](architecture.md) | Records inherited decisions, downstream contracts, requirements, boundaries, validation scenarios, and design principles | Drafted |
| [Logical metadata model](metadata-model.md) and [Mermaid ER source](metadata-model.mmd) | Defines entities, relationships, cardinality, lifecycle, environment resolution, dependencies, and safe watermark transitions | Drafted |
| [Fabric SQL Database package](sql/README.md) | Implements 28 definition, runtime, and audit tables; resolution and validation views; and synthetic Northstar release 1.0.0 | Drafted and statically validated |
| Automated metadata-contract tests | Proves validation and state-transition behavior | Pending |
| Environment and secrets guidance | Documents configuration ownership and prohibited content | Pending |
| Ownership and lifecycle guidance | Documents roles, approvals, versioning, rollback, and recovery | Pending |
| Validation evidence | Records test results and exercised scenarios | Pending |
| Retrospective | Summarizes outcome, limitations, and follow-up work | Pending |

## Relationship to other work

- [Issue #8](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8) supplies the accepted Git, environment, deployment, and credential boundaries.
- [Issue #6](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/6) will consume the model for resilient ingestion.
- [Issue #7](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/7) will consume quality-policy references.
- [Issue #9](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/9) will consume SLO, ownership, schedule, and correlation metadata.

No real organizational credentials, endpoints, patient data, or proprietary metadata are used.
