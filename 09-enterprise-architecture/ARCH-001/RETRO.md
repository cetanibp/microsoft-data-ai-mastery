# ARCH-001 Retrospective

## What became clearer

- The roadmap needs one stable enterprise scenario so that later Fabric, AI, governance, API, and capstone evidence can be evaluated against the same business and operational constraints.
- Architecture requirements are more useful when expressed as measurable targets for availability, recovery, freshness, quality, observability, security, and deployment.
- AI readiness is not a separate platform layer; it depends on governed data, identity-aware retrieval, lineage, quality, telemetry, and safe operational boundaries.
- The scenario must distinguish diagnosis, recommendation, approval, and execution when describing agent capabilities.

## Hardest assumptions to define

- The synthetic scale needed to be challenging enough to drive meaningful capacity and performance decisions without pretending to represent a specific organization.
- Freshness and recovery targets vary by workload, so the baseline uses separate critical and standard requirements.
- Cost attribution could be defined now, but a credible spending limit requires later benchmarking and capacity evidence.
- Regulatory and security constraints needed to be explicit without turning architectural assumptions into legal conclusions.

## What needs validation

- Whether the proposed 15-minute critical-data freshness target is justified by the selected operational use cases.
- Whether a 4-hour RTO and 1-hour RPO are sufficient for every critical analytical workload.
- Which workloads require cross-region disaster recovery.
- Which quality failures must block publication.
- How Fabric capacity should be allocated across engineering, analytics, and AI.
- Which operational actions, if any, should eventually be delegated to an agent.
- The ownership model for cross-domain data products and shared business concepts.

## Decisions to address through ADRs

Issue #3 should establish ADRs or explicit decision prompts for:

1. Platform and workload-boundary strategy
2. Medallion and data-product organization
3. Batch versus event-driven integration
4. Environment isolation and promotion
5. Identity, secrets, and least-privilege access
6. Data quality blocking and warning behavior
7. Observability, correlation, and audit standards
8. Recovery and regional-resiliency strategy
9. AI grounding and access enforcement
10. Agent approval and execution boundaries
11. Capacity allocation and cost attribution
12. Governance ownership and decision rights

## What should improve next

- Validate nonfunctional targets against a representative workload and failure scenarios.
- Add a formal architecture review checklist in issue #3.
- Record consequential choices as ADRs rather than allowing implementation details to become implicit decisions.
- Revise assumptions when implementation, benchmark, security, recovery, or stakeholder-review evidence contradicts them.

## Outcome

ARCH-001 produced a fictional, reusable enterprise scenario; measurable baseline requirements; a technology-neutral context diagram; shared terminology; and a visible decision backlog. The result is suitable as the common architecture context for the remaining mastery roadmap.
