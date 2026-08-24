# Enterprise Architecture Review Checklist

Use this checklist to evaluate consequential Data + AI architecture designs against business requirements and the required quality attributes. Complete it before approving a design and repeat the review when material requirements, risks, dependencies, or platform capabilities change.

**Related issue:** [#3 — ARCH-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3)  
**Reference scenario:** [Northstar Health System](../ARCH-001/README.md)  
**ADR template:** [ADR-000](../decisions/ADR-000-template.md)  

## Review information

| Field | Value |
|---|---|
| Architecture or change | |
| Business owner | |
| Technical owner | |
| Review facilitator | |
| Reviewers | |
| Review date | |
| Related issues | |
| Related ADRs | |
| Architecture version or commit | |
| Proposed outcome | Approved / Approved with conditions / Rework required / Rejected |

## Rating standard

| Status | Meaning |
|---|---|
| Pass | The requirement is addressed with adequate evidence |
| Partial | The direction is reasonable, but evidence or implementation is incomplete |
| Fail | A material requirement is missing or unacceptable |
| N/A | The requirement does not apply and the explanation is recorded |

Every **Partial** or **Fail** must identify the risk, required follow-up, accountable owner, and target date or related issue.

## Approval rules

- Select one final outcome: **Approved**, **Approved with conditions**, **Rework required**, or **Rejected**.
- Do not approve a design with an unresolved failure that creates an unacceptable security, privacy, safety, regulatory, data-integrity, or recovery risk.
- An **Approved with conditions** outcome must list each condition, its owner, due date or related issue, and the evidence required to close it.
- A **Pass** requires evidence. An intention, assertion, or undocumented verbal agreement is not sufficient.
- A **Partial** is appropriate when the design direction is credible but implementation, testing, stakeholder approval, or measurable evidence remains incomplete.
- Use **N/A** only with a written rationale.
- Record consequential decisions and accepted risks in ADRs.

## Evidence standard

Acceptable evidence can include:

- Architecture decision records
- Source-editable diagrams and trust boundaries
- Requirements and service-level objectives
- Identity and access matrices
- Threat models and security reviews
- Data classifications and governance policies
- Automated test results and failure-path evidence
- Performance and capacity benchmarks
- Recovery exercises
- Cost estimates and utilization telemetry
- Deployment and approval records
- Operational logs, metrics, traces, alerts, and dashboards
- Data contracts, quality results, and lineage
- Runbooks, incident records, and retrospectives

Statements such as "the design will be secure," "the platform is scalable," or "recovery is supported" do not constitute evidence without a control, measurable requirement, documented validation plan, or completed test.

## 1. Review context

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| CTX-01 | Is the business problem clearly stated? | | | | |
| CTX-02 | Are desired outcomes measurable? | | | | |
| CTX-03 | Are scope and exclusions explicit? | | | | |
| CTX-04 | Are users, stakeholders, owners, and reviewers identified? | | | | |
| CTX-05 | Are data domains, classifications, and authoritative systems identified? | | | | |
| CTX-06 | Does a current architecture or context diagram show major flows and trust boundaries? | | | | |
| CTX-07 | Are dependencies and external integration boundaries documented? | | | | |
| CTX-08 | Are assumptions and unresolved questions visible? | | | | |
| CTX-09 | Are measurable nonfunctional requirements defined? | | | | |
| CTX-10 | Are consequential decisions and accepted risks linked to ADRs? | | | | |

## 2. Security and privacy

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| SEC-01 | Are identities, authentication methods, and authorization boundaries defined? | | | | |
| SEC-02 | Does the design enforce least privilege and separation of duties? | | | | |
| SEC-03 | Are development, test, and production access boundaries defined? | | | | |
| SEC-04 | Are secrets and credentials stored outside source code and deployable platform content? | | | | |
| SEC-05 | Is data encrypted in transit and at rest? | | | | |
| SEC-06 | Are sensitive-data classifications and handling requirements documented? | | | | |
| SEC-07 | Are masking, synthetic-data, or approval requirements defined for nonproduction data? | | | | |
| SEC-08 | Are access, administrative changes, deployments, approvals, and consequential actions auditable? | | | | |
| SEC-09 | Are network and cross-boundary data flows explicitly protected? | | | | |
| SEC-10 | Are access reviews, revocation, and emergency-access procedures defined? | | | | |
| SEC-11 | When AI is used, does retrieval enforce the requesting user's data permissions? | | | | |
| SEC-12 | When agents are used, do consequential actions require explicit human approval and least privilege? | | | | |

## 3. Reliability and recovery

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| REL-01 | Are availability, RTO, and RPO targets defined by workload criticality? | | | | |
| REL-02 | Are critical dependencies, failure modes, and blast radii identified? | | | | |
| REL-03 | Are ingestion and processing restartable and idempotent? | | | | |
| REL-04 | Are retry, replay, duplicate-handling, and poison-message behaviors defined? | | | | |
| REL-05 | Are backup, restore, retention, and recovery responsibilities defined? | | | | |
| REL-06 | Is regional-resiliency or disaster-recovery scope explicitly decided? | | | | |
| REL-07 | Are partial failure and downstream-unavailability behaviors defined? | | | | |
| REL-08 | Is rollback or forward recovery defined for deployments and data changes? | | | | |
| REL-09 | Are recovery dependencies, access, and communication paths documented? | | | | |
| REL-10 | Has recovery been validated through an exercise or scheduled validation plan? | | | | |

## 4. Operations and observability

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| OPS-01 | Are service, platform, data-product, and operational owners identified? | | | | |
| OPS-02 | Does the design produce correlated logs, metrics, traces, and audit events? | | | | |
| OPS-03 | Are freshness, quality, capacity, performance, failures, and service levels monitored? | | | | |
| OPS-04 | Do critical failures generate timely, actionable alerts? | | | | |
| OPS-05 | Are runbooks, escalation paths, and support hours documented? | | | | |
| OPS-06 | Are deployments, configuration changes, approvals, and actors recorded? | | | | |
| OPS-07 | Can operators diagnose, retry, replay, reconcile, and verify recovery? | | | | |
| OPS-08 | Are telemetry retention, access, privacy, and cost requirements defined? | | | | |
| OPS-09 | Are monitoring blind spots and degraded-observability behavior identified? | | | | |
| OPS-10 | When agents are used, are diagnosis, recommendation, approval, and execution separately traced and authorized? | | | | |

## 5. Performance and scalability

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| PER-01 | Are data volume, growth, concurrency, latency, throughput, and processing-window assumptions documented? | | | | |
| PER-02 | Are performance-critical paths and dependencies identified? | | | | |
| PER-03 | Are representative benchmark scenarios and success criteria defined? | | | | |
| PER-04 | Are expected, peak, failure, replay, and recovery loads considered? | | | | |
| PER-05 | Are workload contention, throttling, queueing, and concurrency limits addressed? | | | | |
| PER-06 | Are scaling and capacity thresholds measurable? | | | | |
| PER-07 | Are large-table, backfill, history, and reprocessing behaviors evaluated? | | | | |
| PER-08 | Are caching, partitioning, indexing, distribution, or data-layout choices evidence based where applicable? | | | | |
| PER-09 | Are performance regressions detectable before and after deployment? | | | | |
| PER-10 | Is there a plan to revise assumptions using production-like telemetry? | | | | |

## 6. Cost and FinOps

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| COST-01 | Are primary platform, storage, processing, networking, observability, and AI cost drivers identified? | | | | |
| COST-02 | Are expected, peak, and growth cost scenarios estimated? | | | | |
| COST-03 | Can cost be attributed by environment, capacity, workload, domain, or data product? | | | | |
| COST-04 | Are budgets, alerts, limits, or other cost guardrails defined? | | | | |
| COST-05 | Are utilization, idle capacity, retention, duplication, and waste measurable? | | | | |
| COST-06 | Were costs compared across credible architecture options? | | | | |
| COST-07 | Are the costs of resiliency, isolation, security, observability, and retention explicit? | | | | |
| COST-08 | Are scaling, shutdown, reservation, or capacity-rightsizing opportunities considered? | | | | |
| COST-09 | Are cost ownership, review cadence, and optimization responsibilities assigned? | | | | |
| COST-10 | Are thresholds defined for optimization, isolation, or architecture reconsideration? | | | | |

## 7. Governance

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| GOV-01 | Are business owners, data owners, stewards, technical owners, and approvers identified? | | | | |
| GOV-02 | Are authoritative sources and shared business concepts defined? | | | | |
| GOV-03 | Is lineage captured from source through transformation and consumption? | | | | |
| GOV-04 | Are classification, retention, deletion, residency, and legal-hold requirements defined? | | | | |
| GOV-05 | Are data-product contracts, consumers, versions, and change-approval rules defined? | | | | |
| GOV-06 | Are data-quality rules, thresholds, ownership, and blocking-versus-warning behavior defined? | | | | |
| GOV-07 | Are data, metadata, semantic definitions, and AI assets discoverable? | | | | |
| GOV-08 | Are cross-domain, cross-workspace, and external-sharing patterns governed? | | | | |
| GOV-09 | Are policy exceptions, decision rights, escalation, and expiration documented? | | | | |
| GOV-10 | When AI is used, is grounding limited to approved, permission-aware, traceable knowledge? | | | | |
| GOV-11 | Are model, prompt, tool, evaluation, and AI-risk changes governed when applicable? | | | | |

## 8. Maintainability

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| MAIN-01 | Are code, configuration, secrets, and environment-specific values separated? | | | | |
| MAIN-02 | Does the design use modular, reusable, and consistently named components? | | | | |
| MAIN-03 | Are deployable artifacts and infrastructure definitions stored in version control? | | | | |
| MAIN-04 | Are automated validation, tests, promotion, and post-deployment checks defined? | | | | |
| MAIN-05 | Are dependencies, owners, operating procedures, and recovery steps documented? | | | | |
| MAIN-06 | Are compatibility, versioning, migration, and consumer-impact expectations defined? | | | | |
| MAIN-07 | Are deprecation, retention, archival, and lifecycle procedures defined? | | | | |
| MAIN-08 | Are unsupported customization and unnecessary technology variation minimized? | | | | |
| MAIN-09 | Are rollback or forward-recovery procedures maintainable and tested? | | | | |
| MAIN-10 | Do ADRs identify validation plans, follow-up actions, and reconsideration triggers? | | | | |
| MAIN-11 | Can a qualified team operate and change the design without relying on undocumented individual knowledge? | | | | |

## Findings summary

| Category | Pass | Partial | Fail | N/A | Blocking risk? |
|---|---:|---:|---:|---:|---|
| Review context | | | | | |
| Security and privacy | | | | | |
| Reliability and recovery | | | | | |
| Operations and observability | | | | | |
| Performance and scalability | | | | | |
| Cost and FinOps | | | | | |
| Governance | | | | | |
| Maintainability | | | | | |
| **Total** | | | | | |

## Risks and conditions

| ID | Finding | Severity | Required action or approval condition | Owner | Target date or issue | Closure evidence |
|---|---|---|---|---|---|---|
| | | Critical / High / Medium / Low | | | | |

## Final decision

**Outcome:** Approved / Approved with conditions / Rework required / Rejected

**Rationale:**  

**Blocking risks:**  

**Conditions for approval:**  

**Accepted risks and approving authority:**  

**Next review trigger or date:**  

## Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Business owner | | | |
| Technical owner | | | |
| Security or privacy reviewer | | | |
| Governance reviewer | | | |
| Operations reviewer | | | |
| Architecture reviewer | | | |
