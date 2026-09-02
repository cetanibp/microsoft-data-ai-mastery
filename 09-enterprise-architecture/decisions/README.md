# Architecture Decision Register

This register tracks consequential architecture decisions for the Northstar Health System reference scenario and the Microsoft Data + AI Mastery repository.

Use [ADR-000](ADR-000-template.md) for each new decision. Number ADRs sequentially, compare credible options, record consequences and validation evidence, and update this register when status changes.

## Status definitions

| Status | Meaning |
|---|---|
| Template | Reusable record structure rather than a decision |
| Planned | Decision is identified but analysis has not started |
| Proposed | A recommendation is documented, but validation or review remains |
| Accepted | The decision is approved with adequate supporting evidence |
| Rejected | The proposed decision was evaluated and not selected |
| Superseded | A newer ADR replaces the decision |

A Proposed ADR must not be described as validated or accepted. An Accepted ADR should identify the evidence and authority supporting acceptance. A Superseded ADR remains in the repository and links to its replacement.

## Decision register

| ADR | Decision | Status | Priority | Primary reason |
|---|---|---|---|---|
| [ADR-000](ADR-000-template.md) | Reusable ADR template | Template | — | Standardizes decision context, options, tradeoffs, consequences, validation, and reconsideration |
| [ADR-001](ADR-001-platform-and-workload-boundaries.md) | Platform and workload boundaries | Proposed | High | Defines workspace, domain, workload, and capacity-isolation strategy |
| [ADR-002](ADR-002-environment-isolation-and-promotion.md) | Environment isolation and promotion | Accepted | High | Validated by OPS-001 implementation, promotion, approval, and recovery evidence |
| ADR-003 | Medallion and data-product organization | Planned | High | Defines layer, domain, ownership, contract, and publication boundaries |
| ADR-004 | Batch versus event-driven integration | Planned | Medium | Determines which freshness requirements justify event-driven complexity |
| ADR-005 | Identity, secrets, and least-privilege access | Planned | High | Defines identity, access, secret, separation-of-duties, and review controls |
| ADR-006 | Data-quality blocking and warning behavior | Planned | High | Defines which failed checks block publication and which create warnings |
| ADR-007 | Observability, correlation, and audit standards | Planned | High | Defines telemetry, correlation, alerting, retention, and audit evidence |
| ADR-008 | Recovery and regional resiliency | Planned | High | Defines disaster-recovery scope, recovery ownership, and validation |
| ADR-009 | AI grounding and access enforcement | Planned | High | Defines approved knowledge, permission-aware retrieval, citations, filtering, and tracing |
| ADR-010 | Agent approval and execution boundaries | Planned | High | Defines how agents may progress from diagnosis to recommendation, approval, and execution |
| ADR-011 | Capacity allocation and cost attribution | Planned | Medium | Defines capacity placement thresholds, cost models, attribution, budgets, and FinOps controls |
| ADR-012 | Governance ownership and decision rights | Planned | High | Defines owners, stewards, approvers, exceptions, escalation, and change authority |

## Recommended sequencing

The register is a backlog, not a requirement to decide everything immediately. Create each ADR when the related implementation and evidence are close enough to support a credible decision.

1. [Issue #3](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3) established ADR-001, ADR-002, the review checklist, and the Northstar review.
2. [Issue #8](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8) supplied the deployment, approval, and recovery evidence used to accept ADR-002.
3. Create ADR-003 when designing the Fabric data and data-product organization.
4. Create ADR-005 before implementing sensitive-data access.
5. Create ADR-007 alongside operational monitoring and incident-response work.
6. Create ADR-008 before claiming recovery or regional-resiliency readiness.
7. Create ADR-009 and ADR-010 before agents access sensitive data or gain consequential tools.
8. Create ADR-011 when benchmark and utilization evidence can support capacity and cost decisions.
9. Create ADR-012 when named governance roles and decision authorities can be assigned.

## Review and lifecycle rules

- Link each ADR to its issue, requirements, evidence, and related decisions.
- Use Proposed when a direction is selected but implementation, benchmarking, stakeholder approval, or other validation remains incomplete.
- Use Accepted only when the stated validation plan has adequate evidence and the appropriate authority has approved the decision.
- Record negative consequences and accepted risks rather than presenting a decision as universally optimal.
- Revisit an ADR when one of its reconsideration triggers occurs.
- Create a new ADR when a material decision changes; mark the prior record Superseded and retain its history.
- Update this register whenever an ADR is added or changes status.

## Related evidence

- [Northstar reference scenario](../ARCH-001/README.md)
- [ARCH-001 decision backlog](../ARCH-001/RETRO.md#decisions-to-address-through-adrs)
- [Enterprise architecture review checklist](../ARCH-003/architecture-review-checklist.md)
- [Northstar architecture review](../ARCH-003/northstar-architecture-review.md)
