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

## Evidence follow-up — September 5, 2026

The learning-gap review linked each remaining decision to implementation and review owners. Existing statuses above remain unchanged pending decision records and required validation. In particular, quality, observability and capacity evidence is available to support drafting, but a completed implementation issue does not automatically accept an ADR. [ARCH-004](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50) owns the dated reassessment and condition reconciliation.

| Decision | Evidence or required validation | Follow-up owner issues |
|---|---|---|
| ADR-001 platform/workload boundaries | Workspace and F256 evidence exists; wider contention/isolation claims remain unvalidated | [#50](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50), optional [#54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) |
| ADR-003 data-product organization | Implemented analytical grain, ownership, publication and semantic contracts | [#19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), [#46](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/46) |
| ADR-004 batch versus events | Actual pipeline event integration and measured freshness/complexity tradeoffs | [#47](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/47) |
| ADR-005 identity/secrets/access | User/workload identity, network boundaries, authorization and denial tests | [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20), [#45](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45), [#49](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49) |
| ADR-006 quality blocking/warning | FAB-003 provides live gates, warning and quarantine evidence for a draft | [#50](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50) using [#7](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/7) |
| ADR-007 observability/audit | OPS-002/RTI-001 provide evidence; producer integration and governed routing remain | [#50](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50), [#47](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/47) |
| ADR-008 recovery/regional resilience | Restore data and control state, measure RTO/RPO, distinguish lab simulation from regional readiness | [#23](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/23), [#24](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/24), [#49](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49) |
| ADR-009 grounding/access enforcement | Corpus lifecycle, retrieval comparison, citations, access/revocation and traces | [#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13), [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20) |
| ADR-010 approval/execution | Typed tools, action binding, state recheck, least privilege and replay protection | [#14](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/14), [#17](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/17) |
| ADR-011 capacity/cost | FAB-004 supports a bounded decision draft; actual cost model and optional contention evidence deepen it | [#50](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50), [#23](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/23), optional [#54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) |
| ADR-012 governance authority | Product ownership, stewardship, exceptions, retention and policy enforcement | [#19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20) |

### Original approval-condition follow-up

This is a tracking map, not a replacement for the August 23 architecture review or a new approval. Reassess each condition against actual evidence in #50 and the final #24 review.

| Original condition | Follow-up issues |
|---|---|
| COND-01 security/AI authorization | [#14](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/14), [#17](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/17), [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20), [#45](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45) |
| COND-02 recovery scope and objectives | [#23](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/23), [#24](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/24), [#49](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49) |
| COND-03 capacity/performance | Completed [#10](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/10) evidence; [#46](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/46) and optional [#53](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/53), [#54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) for wider scenarios |
| COND-04 cost ceiling and controls | [#23](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/23) baseline; optional [#54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) feedback loop |
| COND-05 governance ownership/policy | [#19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20), [#21](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/21) |
| COND-06 delivery/operations | Completed [#8](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8), [#9](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/9), [#11](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/11) evidence; [#45](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45), [#47](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/47), [#49](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49), [#51](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/51) remaining depth |
