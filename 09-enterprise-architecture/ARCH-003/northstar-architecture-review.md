# Northstar Health System Architecture Review

This review applies the [Enterprise Architecture Review Checklist](architecture-review-checklist.md) to the fictional [Northstar Health System reference scenario](../ARCH-001/README.md).

**Decision:** Approved with conditions as the repository planning baseline.  
**Limitation:** This is not production, security, regulatory, capacity-purchase, or real-data authorization.

## Review information

| Field | Value |
|---|---|
| Architecture | Northstar Health System enterprise Data + AI reference scenario |
| Technical owner and facilitator | Bryan Cetani |
| Business owner | To be assigned for an implementation |
| Reviewers | Self-review complete; independent reviews pending |
| Review date | 2026-08-23 |
| Related issues | [#1](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/1), [#3](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3), [#8](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8) |
| Related ADRs | [ADR-001](../decisions/ADR-001-platform-and-workload-boundaries.md), [ADR-002](../decisions/ADR-002-environment-isolation-and-promotion.md) |
| Architecture version | ARCH-001 baseline and ADRs as of 2026-08-23 |

## Evidence key

- **S1:** [ARCH-001 reference scenario](../ARCH-001/README.md)
- **S2:** [Context diagram, flows, and trust boundaries](../ARCH-001/context-diagram.md)
- **S3:** [ARCH-001 retrospective and decision backlog](../ARCH-001/RETRO.md)
- **D1:** [ADR-001 — Platform and workload boundaries](../decisions/ADR-001-platform-and-workload-boundaries.md)
- **D2:** [ADR-002 — Environment isolation and promotion](../decisions/ADR-002-environment-isolation-and-promotion.md)

A **Pass** means current planning evidence adequately addresses the question. A **Partial** means implementation, measurement, ownership, testing, approval, or other evidence remains incomplete. **N/A** applies only where the technology-neutral baseline has not yet made the relevant design choice.

## 1. Review context

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| CTX-01 | Is the business problem clear? | Pass | S1: Business problem | None for baseline use | Technical owner |
| CTX-02 | Are outcomes measurable? | Partial | S1: Outcomes and NFRs | Add business baselines, targets, and measurement owners | Business owner |
| CTX-03 | Are scope and exclusions explicit? | Pass | S1: Scope and out of scope | Revalidate for each implementation | Architecture owner |
| CTX-04 | Are stakeholders, owners, and reviewers identified? | Partial | S1: Stakeholders | Assign named owners and independent reviewers | Business owner |
| CTX-05 | Are domains, classifications, and authoritative systems identified? | Partial | S1: Domains, security assumptions, open questions | Assign authoritative systems and classifications | Governance |
| CTX-06 | Do diagrams show flows and trust boundaries? | Pass | S2 | Add component and deployment views later | Architecture owner |
| CTX-07 | Are dependencies and integration boundaries documented? | Partial | S2 | Build dependency and failure inventory | Platform owner |
| CTX-08 | Are assumptions and open questions visible? | Pass | S1: Assumptions and unresolved questions | Track resolution through ADRs | Architecture owner |
| CTX-09 | Are measurable NFRs defined? | Pass | S1: Nonfunctional requirements | Validate with stakeholders and tests | Architecture owner |
| CTX-10 | Are consequential decisions and risks linked to ADRs? | Partial | D1, D2, S3 | Complete backlog and record risk authorities | Architecture owner |

## 2. Security and privacy

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| SEC-01 | Are identity and authorization boundaries defined? | Partial | S1: Security assumptions; S2 | Produce identity architecture and permission model | Security |
| SEC-02 | Are least privilege and separation of duties enforced? | Partial | S1; D2 | Validate roles and deployment identities | Security |
| SEC-03 | Are environment access boundaries defined and validated? | Partial | D2 is Proposed | Accept ADR and validate access controls through #8 | Platform security |
| SEC-04 | Are secrets outside source and deployable content? | Partial | S1; D2 | Implement and test secret pattern | Platform security |
| SEC-05 | Is data encrypted in transit and at rest? | Partial | S1: Security assumptions | Verify configuration and key management | Security |
| SEC-06 | Are sensitive-data classifications and handling rules documented? | Partial | S1: PHI and PII assumptions | Define taxonomy and handling rules | Governance |
| SEC-07 | Are nonproduction masking or synthetic-data rules defined? | Pass | S1: Security assumptions and exclusions | Validate before sensitive-data use | Privacy |
| SEC-08 | Are access, changes, approvals, and actions auditable? | Partial | S1: Auditability; D2 | Define audit schema, retention, and tests | Security operations |
| SEC-09 | Are network and boundary flows protected? | Partial | S2: Primary flows | Add network, endpoint, firewall, and egress design | Network security |
| SEC-10 | Are access review, revocation, and emergency procedures defined? | Partial | D2 mentions controlled exceptions | Define review cadence and break-glass procedure | Security |
| SEC-11 | Does AI retrieval enforce user permissions? | Partial | S1 and S2 define the requirement | Implement permission and denial tests | AI security |
| SEC-12 | Do consequential agent actions require approval and least privilege? | Pass | S1: AI safety; S2: Agent boundary | Preserve and test this boundary | AI owner |

## 3. Reliability and recovery

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| REL-01 | Are availability, RTO, and RPO targets defined? | Pass | S1: NFRs | Validate by workload | Service owner |
| REL-02 | Are dependencies, failure modes, and blast radii identified? | Partial | S2; D1 risks | Produce failure-mode analysis | Reliability |
| REL-03 | Are processing and ingestion restartable and idempotent? | Pass | S1: NFRs | Demonstrate with failure tests | Data engineering |
| REL-04 | Are retry, replay, duplicate, and poison behaviors defined? | Partial | S1; S2 | Define workload policies and tests | Data engineering |
| REL-05 | Are backup, restore, retention, and responsibilities defined? | Partial | S1: Recovery and open retention question | Assign responsibilities and controls | Reliability |
| REL-06 | Is regional resilience explicitly decided? | Partial | S1 open question; S3 backlog | Complete recovery ADR | Architecture owner |
| REL-07 | Are partial and downstream failure behaviors defined? | Partial | S1 reliability requirements | Document degraded modes and tests | Reliability |
| REL-08 | Is rollback or forward recovery defined? | Pass | D2 | Implement and test by artifact type | Release owner |
| REL-09 | Are recovery dependencies, access, and communications documented? | Partial | S2 | Create recovery and communication plans | Operations |
| REL-10 | Has recovery been exercised or scheduled? | Partial | D1 and D2 validation plans | Schedule and complete exercises | Reliability |

## 4. Operations and observability

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| OPS-01 | Are service, product, platform, and operations owners identified? | Partial | S1: Stakeholders and ownership assumption | Assign named owners | Business and platform owners |
| OPS-02 | Are logs, metrics, traces, and audit events correlated? | Pass | S1: Observability and auditability NFRs | Define schema and retention | Observability |
| OPS-03 | Are freshness, quality, capacity, performance, failures, and SLOs monitored? | Pass | S1; D1 operations | Implement dashboards | Platform operations |
| OPS-04 | Do critical failures create timely actionable alerts? | Pass | S1: Five-minute alert target | Test alert delivery | Platform operations |
| OPS-05 | Are runbooks, escalation, and support hours documented? | Partial | S1: Maintainability NFR | Create and exercise runbooks | Operations |
| OPS-06 | Are deployments, changes, approvals, and actors recorded? | Pass | D2 | Validate through #8 | Release owner |
| OPS-07 | Can operators diagnose, retry, replay, reconcile, and verify? | Partial | S1 outcomes; S2 flows | Implement tools and failure tests | Platform operations |
| OPS-08 | Are telemetry retention, access, privacy, and cost defined? | Partial | S1 requirements | Define telemetry governance | Security operations |
| OPS-09 | Are monitoring blind spots and degraded behavior identified? | Partial | S1 observability target | Add telemetry failure modes | Observability |
| OPS-10 | Are agent diagnosis, recommendation, approval, and execution separately traced? | Pass | S1 principles; S2; S3 | Validate with trace evidence | AI operations |

## 5. Performance and scalability

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| PER-01 | Are scale, concurrency, latency, throughput, and windows documented? | Pass | S1: Scale assumptions and NFRs | Validate with workloads | Performance |
| PER-02 | Are performance-critical paths identified? | Partial | S2 flows | Identify workload-specific critical paths | Performance |
| PER-03 | Are benchmark scenarios and criteria defined? | Partial | D1 validation plan | Define datasets, load, duration, and pass criteria | Performance |
| PER-04 | Are peak, failure, replay, and recovery loads considered? | Partial | S1; D1 | Add explicit load scenarios | Performance |
| PER-05 | Are contention, throttling, queueing, and concurrency addressed? | Pass | D1 | Establish measured thresholds | Platform owner |
| PER-06 | Are scaling and capacity thresholds measurable? | Partial | D1 follow-ups | Define numeric thresholds | Capacity owner |
| PER-07 | Are large-table, backfill, history, and replay behaviors evaluated? | Partial | S1 includes billion-row tables and 1 PB history | Benchmark these cases | Data engineering |
| PER-08 | Are physical data-layout choices evidence based? | N/A | Baseline is technology neutral | Reassess for implementation designs | Data architecture |
| PER-09 | Are performance regressions detectable around deployment? | Partial | D2 validation plan | Add regression gates | Performance |
| PER-10 | Will assumptions be revised from production-like telemetry? | Pass | S1 assumptions; D1 triggers | Establish review cadence | Architecture owner |

## 6. Cost and FinOps

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| COST-01 | Are primary cost drivers identified? | Partial | S1 cost NFR; D1 | Build complete cost-driver model | FinOps |
| COST-02 | Are expected, peak, and growth costs estimated? | Partial | S1 scale assumptions | Estimate cost scenarios | FinOps |
| COST-03 | Can cost be attributed by environment and workload or product? | Pass | S1 cost NFR; D1 decision | Validate allocation telemetry | FinOps |
| COST-04 | Are budgets, alerts, and limits defined? | Partial | S1 open monthly-cost question | Define guardrails and escalation | Business and FinOps |
| COST-05 | Are utilization, retention, duplication, and waste measurable? | Partial | D1 validation plan | Implement metrics | FinOps |
| COST-06 | Were costs compared across credible options? | Pass | D1 and D2 tradeoff assessments | Replace scores with estimates later | Architecture owner |
| COST-07 | Are resilience, isolation, security, observability, and retention costs explicit? | Partial | D1 and D2 identify but do not quantify them | Quantify control scenarios | FinOps |
| COST-08 | Are rightsizing and scaling opportunities considered? | Partial | D1 selective isolation | Define optimization actions | Capacity owner |
| COST-09 | Are cost ownership and review cadence assigned? | Partial | Attribution required; owners unassigned | Establish FinOps operating model | Business owner |
| COST-10 | Are numeric optimization and reconsideration thresholds defined? | Partial | D1 qualitative triggers | Define numeric thresholds | Capacity and FinOps |

## 7. Governance

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| GOV-01 | Are owners, stewards, technical owners, and approvers assigned? | Partial | S1 stakeholders and ownership assumption | Assign named roles | Governance |
| GOV-02 | Are authoritative sources and shared concepts defined? | Partial | S1 assumption and open question | Define authority and concept governance | Governance |
| GOV-03 | Is lineage captured from source through consumption? | Pass | S1 traceability NFR; S2 controls | Validate implementation | Governance |
| GOV-04 | Are classification, retention, deletion, residency, and holds defined? | Partial | S1 security assumptions | Define rules by data class | Privacy and governance |
| GOV-05 | Are product contracts, versions, consumers, and approvals defined? | Partial | S1 architecture principles | Implement contract standard | Data-product owner |
| GOV-06 | Are quality rules, thresholds, owners, and publication behavior defined? | Partial | S1 quality NFR and open question | Define product-specific controls | Data owner |
| GOV-07 | Are data, metadata, semantics, and AI assets discoverable? | Pass | S1 outcomes and scope | Demonstrate catalog experience | Governance |
| GOV-08 | Are cross-domain and cross-workspace sharing patterns governed? | Pass | D1 governance implications | Define approved patterns and tests | Platform governance |
| GOV-09 | Are exceptions, decision rights, escalation, and expiration defined? | Partial | S3 backlog | Define exception process | Governance owner |
| GOV-10 | Is AI grounding approved, permission aware, and traceable? | Pass | S1 AI NFRs; S2 boundary | Validate retrieval, denial, citations, and traces | AI governance |
| GOV-11 | Are model, prompt, tool, evaluation, and AI-risk changes governed? | Partial | S1 scope | Define AI lifecycle and gates | AI governance |

## 8. Maintainability

| ID | Review question | Status | Evidence | Risk or follow-up | Owner |
|---|---|---|---|---|---|
| MAIN-01 | Are code, configuration, secrets, and environment values separated? | Pass | S1 principles; D2 | Validate through #8 | Platform engineering |
| MAIN-02 | Are components modular, reusable, and consistently named? | Pass | S1 principles | Define naming standards | Architecture owner |
| MAIN-03 | Are deployable artifacts version controlled? | Pass | D2 | Demonstrate through #8 | Release owner |
| MAIN-04 | Are validation, tests, promotion, and post-deployment checks defined? | Pass | D2 | Implement through #8 | Release owner |
| MAIN-05 | Are dependencies, owners, procedures, and recovery steps documented? | Partial | S1 maintainability NFR | Produce inventories and runbooks | Operations |
| MAIN-06 | Are compatibility, versioning, migration, and consumer impact defined? | Partial | Products and APIs are in scope | Define evolution standards | Data-product owner |
| MAIN-07 | Are deprecation, retention, archival, and lifecycle procedures defined? | Partial | S1 open retention question | Define lifecycle procedures | Governance |
| MAIN-08 | Are unsupported customization and technology variation minimized? | Pass | S1 principles | Review exceptions through ADRs | Architecture owner |
| MAIN-09 | Are rollback or forward-recovery procedures maintained and tested? | Partial | D2 requirement | Implement and exercise procedures | Release owner |
| MAIN-10 | Do ADRs contain validation, actions, and reconsideration triggers? | Pass | D1 and D2 | Apply to later decisions | Architecture owner |
| MAIN-11 | Can a team operate without undocumented individual knowledge? | Partial | Documentation required but untested | Validate through independent exercises | Operations |

## Findings summary

| Category | Pass | Partial | Fail | N/A | Blocking risk? |
|---|---:|---:|---:|---:|---|
| Review context | 5 | 5 | 0 | 0 | No for baseline use |
| Security and privacy | 2 | 10 | 0 | 0 | High conditions before implementation |
| Reliability and recovery | 3 | 7 | 0 | 0 | High conditions before implementation |
| Operations and observability | 5 | 5 | 0 | 0 | High conditions before implementation |
| Performance and scalability | 3 | 6 | 0 | 1 | High conditions before capacity decisions |
| Cost and FinOps | 2 | 8 | 0 | 0 | Medium conditions before investment |
| Governance | 4 | 7 | 0 | 0 | High conditions before sensitive-data use |
| Maintainability | 6 | 5 | 0 | 0 | High conditions before production |
| **Total** | **30** | **53** | **0** | **1** | **No blocker to planning-baseline use** |

## Approval conditions

| ID | Finding | Severity | Required action | Owner | Target | Closure evidence |
|---|---|---|---|---|---|---|
| COND-01 | Security and AI authorization controls are unimplemented | High | Complete security architecture, threat review, access matrix, permission tests, and emergency procedures | Security | Future security work | Approved design and tests |
| COND-02 | Recovery scope, ownership, and exercises are incomplete | High | Complete recovery ADR and demonstrate RTO/RPO | Reliability | Future recovery work | ADR and exercise report |
| COND-03 | Capacity and performance are unbenchmarked | High | Test contention, peak, large-table, replay, and regression scenarios | Capacity | D1 validation | Benchmarks and thresholds |
| COND-04 | Cost ceiling, scenarios, and guardrails are undefined | Medium | Produce cost model and FinOps controls | Business and FinOps | Future cost work | Model, budgets, alerts, cadence |
| COND-05 | Governance ownership and policies are incomplete | High | Assign owners, authority, retention, quality behavior, and decision rights | Governance | Future governance work | Ownership matrix and policies |
| COND-06 | Promotion and operational controls are unimplemented | High | Validate delivery, telemetry, runbooks, drift, and recovery failure paths | Platform and operations | [#8](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8) and later work | CI/CD, telemetry, runbooks, tests |

## Final decision

**Outcome:** Approved with conditions as the repository planning baseline.

**Rationale:** ARCH-001 provides the fictional context, scope, flows, trust boundaries, measurable requirements, assumptions, principles, and open questions needed to evaluate subsequent work. D1 and D2 establish the initial decision discipline. Partial ratings are expected because this is a planning baseline rather than an implemented system.

**Blocking risks:** None prevent learning or planning use. COND-01 through COND-06 prevent claims of production readiness, real-data authorization, security or disaster-recovery approval, and capacity-purchase approval.

**Accepted risks:** No production risk is accepted. Incomplete evidence is accepted only for fictional planning-baseline use.

**Next review:** Repeat when an implementation architecture is proposed, a condition closes, requirements materially change, or before any production-readiness claim.

## Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| Technical owner and facilitator | Bryan Cetani | Approved with conditions for planning-baseline use | 2026-08-23 |
| Business owner | To be assigned | Pending | |
| Security or privacy reviewer | To be assigned | Pending | |
| Governance reviewer | To be assigned | Pending | |
| Operations reviewer | To be assigned | Pending | |
| Independent architecture reviewer | To be assigned | Pending | |
