# ARCH-003 Retrospective

## What became clearer

- Architecture decision records must distinguish a recommended direction from an accepted and validated decision.
- Weighted scoring helps structure tradeoff discussions, but it does not replace engineering judgment, stakeholder review, benchmarks, tests, or operational evidence.
- An architecture can be approved as a planning baseline without being approved for production implementation.
- Requirements and principles are not equivalent to implemented controls or completed validation.
- Review outcomes need explicit scope so that planning approval is not mistaken for security, regulatory, recovery, capacity-purchase, or real-data authorization.
- Consequential decisions are most credible when recorded near the implementation work that can provide evidence.

## What was hardest

- Creating one checklist broad enough for enterprise review without making every incomplete implementation check automatically blocking.
- Rating proposed controls honestly when their direction is sound but implementation and independent-review evidence are absent.
- Preserving Northstar as a useful fictional scenario without implying that it represents a production healthcare architecture.
- Comparing cost, security, reliability, performance, operations, governance, and maintainability without pretending that ordinal scores are quantified proof.
- Keeping the ADR backlog useful instead of prematurely deciding all twelve topics.

## What the review exposed

The completed Northstar assessment recorded 30 Pass, 53 Partial, zero Fail, and one N/A rating across 84 questions. The high number of Partial ratings is expected: the scenario contains measurable requirements and credible architectural direction, but most implementation, benchmark, ownership, operational, cost, security, recovery, and independent-review evidence does not yet exist.

Six conditions remain open:

1. Security, identity, access, secrets, networking, and AI authorization
2. Recovery scope, ownership, dependency behavior, and recovery exercises
3. Performance, contention, large-table, replay, and capacity benchmarks
4. Cost ceiling, scenarios, budgets, alerts, ownership, and optimization thresholds
5. Governance ownership, authoritative sources, retention, quality-publication behavior, and decision rights
6. CI/CD, telemetry, runbooks, drift detection, and failure recovery

## What still requires validation

- ADR-001 requires representative workload, contention, security, cost, utilization, and recovery evidence.
- ADR-002 requires implementation and failure-path evidence from [#8 — OPS-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8).
- Northstar's six architecture-review conditions remain open.
- Independent security, governance, operations, business, and architecture reviews remain pending.
- Proposed decisions must not move to Accepted until their validation evidence and approval authority are adequate.

## What should improve next

- Implement Issue #8 and use its evidence to reevaluate ADR-002.
- Define numeric thresholds where ADR-001 currently uses qualitative isolation, performance, and cost triggers.
- Create future ADRs when related implementation work is close enough to provide credible evidence.
- Reapply the review checklist when a material implementation architecture is proposed.
- Replace ordinal tradeoff scores with measured performance, reliability, security, and cost evidence where possible.
- Test failure paths, recovery behavior, access denial, environment drift, and operational documentation rather than evaluating only happy paths.

## Skill assessment

**Architecture decisions and tradeoff analysis: level 1 → level 2**

The repository now contains a reusable ADR standard, two applied decision records, explicit tradeoff scoring, validation plans, reconsideration triggers, an 84-question review standard, and a completed evidence-based architecture assessment.

Level 3 is not yet supported because the decisions remain Proposed and the related implementation, testing, troubleshooting, independent review, and validation evidence are incomplete.

## Outcome

ARCH-003 converted the Northstar requirements and decision backlog into a repeatable architecture-decision and review system. Future work can now be evaluated consistently across security, reliability, operations, performance, cost, governance, and maintainability while preserving a clear distinction between proposed direction, validated evidence, and production approval.
