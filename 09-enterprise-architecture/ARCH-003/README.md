# ARCH-003 — Architecture Decisions and Review Standard

**Status:** Complete  
**Completed:** 2026-08-23  
**Related issue:** [#3 — ARCH-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3)  
**Reference scenario:** [Northstar Health System](../ARCH-001/README.md)  

## Purpose

ARCH-003 establishes a repeatable method for recording consequential architecture decisions, evaluating tradeoffs, reviewing designs across enterprise quality attributes, and separating planning approval from production readiness.

## Deliverables

### Architecture decisions

- [ADR template](../decisions/ADR-000-template.md)
- [ADR-001 — Platform and workload boundaries](../decisions/ADR-001-platform-and-workload-boundaries.md)
- [ADR-002 — Environment isolation and promotion](../decisions/ADR-002-environment-isolation-and-promotion.md)
- [Architecture decision register and backlog](../decisions/README.md)

ADR-001 remains **Proposed** pending workload, capacity, cost, security, and recovery evidence. ADR-002 is **Accepted** based on the implementation, promotion, approval, and recovery evidence produced by OPS-001.

### Architecture review

- [Reusable enterprise architecture review checklist](architecture-review-checklist.md)
- [Completed Northstar architecture review](northstar-architecture-review.md)

The checklist contains 84 evidence-based checks covering:

- Review context
- Security and privacy
- Reliability and recovery
- Operations and observability
- Performance and scalability
- Cost and FinOps
- Governance
- Maintainability

The Northstar review resulted in:

| Result | Count |
|---|---:|
| Pass | 30 |
| Partial | 53 |
| Fail | 0 |
| N/A | 1 |
| **Total** | **84** |

**Outcome:** Approved with conditions as the repository planning baseline. The review does not authorize production deployment, security or regulatory approval, capacity purchasing, or use of real patient or proprietary data.

### Retrospective

- [ARCH-003 retrospective](RETRO.md)

## Acceptance evidence

| Acceptance criterion | Evidence |
|---|---|
| Add an ADR template and initial decisions | ADR-000, ADR-001, ADR-002, and the decision register |
| Cover security, reliability, operations, performance, cost, governance, and maintainability | Reusable 84-question architecture review checklist |
| Apply the checklist to the reference scenario | Completed Northstar review with evidence, risks, conditions, and outcome |

## Skill impact

The work supports raising **Architecture decisions and tradeoff analysis** from level 1 to level 2. It provides a working guided implementation, but not yet the independent implementation, testing, troubleshooting, and accepted validation evidence required for level 3.

## Next work

1. Implement [#8 — OPS-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8).
2. Use delivery and failure-path evidence from Issue #8 to reevaluate ADR-002.
3. Create later ADRs when related implementation evidence can support a credible choice.
4. Reapply the checklist when a material implementation architecture is ready.
