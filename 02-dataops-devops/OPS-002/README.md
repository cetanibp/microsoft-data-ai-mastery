# OPS-002 — SLOs, observability, and incident response

**Status:** In progress  
**Related issue:** [#9 — OPS-002](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/9)  
**Milestone:** Fabric Platform & DataOps

## Objective

Turn the durable execution, state, and quality evidence produced by FAB-002 and FAB-003 into measurable service-level indicators, breach evaluations, operational views, alert-routing decisions, and tested recovery procedures.

## Binding inputs

- [ARCH-001 Northstar requirements](../../09-enterprise-architecture/ARCH-001/README.md)
- [FAB-001 metadata and ownership model](../../01-fabric-platform-engineering/FAB-001/README.md)
- [FAB-002 resilient incremental ingestion](../../01-fabric-platform-engineering/FAB-002/README.md)
- [FAB-003 quality acceptance boundary](../../01-fabric-platform-engineering/FAB-003/README.md)
- [OPS-001 governed delivery](../OPS-001/README.md)

OPS-002 consumes the existing environment, release, run, object-run, correlation, quality, quarantine, state-event, SLO, and ownership identities. It must not create a competing execution identity or weaken the quality-gated watermark protocol.

## Approved initial scope

| Capability | Planned evidence | Status |
|---|---|---|
| Freshness, reliability, duration, and quality SLOs | [SLO contract](slo-contract.md) with explicit calculation rules | Approved |
| Operational telemetry | [Telemetry architecture](architecture.md) with correlated projections and durable evaluation | Designed |
| Alert routing | [Routing contract](alert-routing.md) with severity, ownership, deduplication, and environment rules | Designed |
| Incident response | Triage, replay, escalation, and recovery runbooks | Planned |
| Failure-recovery exercise | Injected failure with detection and recovery evidence | Planned |

## Implementation sequence

1. Approve measurable SLO and error-budget contracts.
2. Add operational evaluation tables and views without mutating metadata release 1.0.0.
3. Evaluate synthetic run and quality evidence with credential-free tests.
4. Add environment-aware routing decisions; Development and Test record notifications but do not page.
5. Build an operational dashboard/query pack.
6. Write runbooks and perform a documented failure-recovery exercise.
7. Publish evidence, retrospective, and issue closure links.

## Design constraints

- Metadata release 1.0.0 is immutable. Changes to definition rows require a future reviewed release.
- A logical scheduled occurrence is counted once even when it has multiple attempts or replays.
- WARN quality outcomes remain accepted and do not reduce ingestion reliability.
- A BLOCK quality outcome reduces quality acceptance but is not automatically classified as a platform failure.
- A blocking decision must never advance the committed watermark.
- Routing uses logical owner aliases; no personal email address, endpoint, credential, or tenant identifier is committed.
- Development and Test produce evaluation and routing evidence without contacting a real operational destination.
- Repository evidence contains only synthetic Northstar data.

## Repository contents

| Path | Purpose |
|---|---|
| [slo-contract.md](slo-contract.md) | Approved indicators, objectives, calculation rules, exclusions, and error budgets |
| [architecture.md](architecture.md) | Operational evidence flow, durable records, projections, and safety boundaries |
| [alert-routing.md](alert-routing.md) | Severity, ownership, suppression, deduplication, and environment behavior |

Additional implementation, tests, evidence, runbooks, and retrospective files will be added as the work progresses.
