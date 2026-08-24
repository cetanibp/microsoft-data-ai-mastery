# ADR-001 — Platform and workload boundaries

**Status:** Proposed  
**Date:** 2026-08-23  
**Decision owner:** Bryan Cetani  
**Reviewers:** To be assigned  
**Related issue:** [#3 — ARCH-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3)  
**Related requirements:** Environment isolation, least privilege, availability, performance, cost attribution, governance, and maintainability  

## Decision summary

Northstar Health System will use separate Microsoft Fabric workspaces aligned to environments, domains, and platform responsibilities, with selective capacity isolation when workload risk, performance, security, or service-level evidence justifies it. Workloads may share capacity initially, but capacity placement must remain measurable and reversible.

## Context

Northstar must support development, test, and production; more than 600 managed data objects; up to 1 PB of historical data; batch, event-driven, analytics, and AI workloads; and multiple business domains. The platform must prevent inappropriate cross-environment access, support least privilege, attribute cost, and limit the ability of one workload to affect another.

A decision is required because workspace and capacity boundaries influence security, deployment, governance, performance, reliability, operational ownership, and cost. Allowing the implementation to grow without explicit boundaries would turn early convenience into an implicit enterprise architecture decision.

This ADR defines the initial logical and capacity-boundary strategy. It does not select final workspace names, assign every data product to a workspace, establish capacity sizes, or replace the benchmarking and cost analysis required by later work.

## Decision drivers

- Separate production access from development and test access
- Enforce least privilege and separation of duties
- Support domain-aligned ownership and governed data products
- Protect critical workloads from avoidable resource contention
- Attribute platform cost by environment, workspace, workload, or data product
- Support measurable availability, freshness, and processing-window requirements
- Keep deployment, monitoring, recovery, and support responsibilities understandable
- Avoid unnecessary capacity cost before workload evidence is available
- Permit boundaries and capacity assignments to evolve without redesigning the entire platform

## Options considered

### Option A — One shared workspace and capacity

**Description:**  
Place most platform artifacts, data, analytics, and AI workloads in one workspace backed by a shared capacity.

**Advantages:**

- Lowest initial administration and capacity complexity
- Lowest likely initial platform cost
- Simple artifact discovery for a small implementation

**Disadvantages:**

- Weak environment, ownership, and deployment boundaries
- Difficult least-privilege administration
- Poor cost attribution
- Large operational and security blast radius

**Risks:**

- Resource-intensive workloads can affect critical processing
- Production and nonproduction responsibilities may become mixed
- Domain ownership becomes difficult to enforce

### Option B — Separate workspaces with shared capacity

**Description:**  
Separate environments, domains, and platform responsibilities into workspaces while backing them with one shared capacity.

**Advantages:**

- Stronger logical security and deployment boundaries
- Better ownership and cost visibility than one workspace
- Moderate administrative and financial overhead
- Easier to implement initially

**Disadvantages:**

- Workloads still compete for the same capacity
- Workspace separation alone does not provide performance isolation
- Capacity-level failures can affect many workspaces

**Risks:**

- Critical batch, analytics, real-time, and AI workloads may interfere with one another
- Shared-capacity contention may threaten freshness or availability targets

### Option C — Separate workspaces with selective capacity isolation

**Description:**  
Use environment-, domain-, and responsibility-aligned workspaces. Share capacity when risk and workload evidence permit, and place critical, sensitive, or resource-intensive workloads on isolated capacity when justified.

**Advantages:**

- Strong logical security, governance, ownership, and deployment boundaries
- Capacity isolation can match workload risk and service-level requirements
- Avoids paying for full isolation before it is necessary
- Supports incremental evolution as evidence becomes available
- Provides a path to contain critical or unpredictable workloads

**Disadvantages:**

- Requires capacity governance, monitoring, and placement criteria
- Some shared-capacity contention remains
- More workspace and deployment administration than Options A or B
- Chargeback and operational ownership require explicit standards

**Risks:**

- Isolation decisions could become inconsistent without measurable thresholds
- Under-isolation can harm service levels; over-isolation can waste capacity

### Option D — Dedicated capacity for every workload and environment

**Description:**  
Provide dedicated capacity boundaries for each environment, domain, or major workload category.

**Advantages:**

- Maximum workload and fault isolation
- Clear capacity ownership and cost attribution
- Strong control over performance and scaling

**Disadvantages:**

- Highest cost
- Highest operational and administrative complexity
- Capacity may be substantially underused
- Difficult to justify before workload measurements exist

**Risks:**

- Premature isolation may produce a costly architecture with low utilization
- Numerous capacity boundaries can complicate deployment, monitoring, and support

## Tradeoff assessment

| Criterion | Weight | Option A | Option B | Option C | Option D | Evidence or rationale |
|---|---:|---:|---:|---:|---:|---|
| Security and privacy | 20% | 2 | 4 | 5 | 5 | Separate workspaces improve access and environment boundaries; selective or full isolation can reduce blast radius |
| Reliability and recovery | 15% | 2 | 3 | 4 | 5 | Capacity isolation can contain resource contention and some workload failures |
| Operations and observability | 15% | 4 | 4 | 3 | 2 | Additional boundaries increase monitoring, support, and deployment responsibilities |
| Performance and scalability | 15% | 1 | 2 | 5 | 5 | Selective and full isolation provide the strongest response to measured contention |
| Cost | 15% | 5 | 4 | 3 | 1 | Greater isolation increases capacity and administrative cost |
| Governance | 10% | 2 | 4 | 5 | 5 | Environment and domain boundaries improve ownership, policy, and auditability |
| Maintainability | 10% | 4 | 4 | 3 | 2 | More boundaries create additional configuration and lifecycle management |
| **Weighted total** | **100%** | **2.80** | **3.55** | **4.05** | **3.65** | Option C provides the strongest balanced fit |

Scores use a scale from 1 (poor fit) to 5 (best fit). Scores organize the comparison but do not replace engineering judgment or future evidence.

## Decision

Select **Option C — Separate workspaces with selective capacity isolation**.

Northstar will:

- Separate development, test, and production workspaces.
- Organize production workspaces around business domains and platform responsibilities where this improves ownership, governance, or lifecycle management.
- Apply explicit access, ownership, deployment, data-exposure, and operational-support boundaries.
- Allow compatible workloads to share capacity initially when security, performance, recovery, and service-level risks are acceptable.
- Isolate critical, sensitive, unpredictable, or resource-intensive workloads when monitoring, benchmarking, security review, or service-level evidence justifies it.
- Avoid assuming that every domain or workspace requires dedicated capacity.
- Track utilization and cost by environment, workspace, workload, or data product wherever platform telemetry permits.
- Make workspace-to-capacity placement configurable, documented, and reviewable.

The decision remains **Proposed** because final capacity allocation and isolation thresholds require workload, cost, security, and recovery evidence.

## Consequences

### Positive consequences

- Production, test, and development receive explicit security and deployment boundaries.
- Domain teams can receive clearer ownership without forcing immediate physical isolation.
- Critical workloads have a defined path to stronger isolation.
- Capacity cost can be balanced against measurable service-level needs.
- The architecture can evolve without reorganizing every workspace.
- Workload placement becomes an explicit governance decision rather than an implementation accident.

### Negative consequences

- Northstar must define and operate more workspaces.
- Shared-capacity workloads may still affect one another.
- Capacity placement requires monitoring and periodic review.
- Cross-workspace data access, deployment, and lineage require deliberate design.
- Cost attribution may be approximate where platform telemetry does not provide data-product-level detail.

### Risks and mitigations

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Shared-capacity contention threatens critical processing | Medium | High | Define workload SLOs, monitor utilization and throttling, and isolate workloads when thresholds are exceeded | Platform owner |
| Excessive isolation increases cost and reduces utilization | Medium | High | Require benchmark, risk, or service-level evidence before assigning dedicated capacity | Architecture review board |
| Workspace proliferation increases support complexity | Medium | Medium | Establish naming, ownership, deployment, monitoring, and lifecycle standards | Platform operations |
| Cross-workspace access weakens least privilege | Medium | High | Use explicit identities, approved sharing patterns, access reviews, and audit logging | Security and governance |
| Capacity assignments become inconsistent | Medium | Medium | Publish placement criteria and review assignments on a defined cadence | Platform owner |

## Quality-attribute implications

### Security

Workspace roles, identities, permissions, and production access must follow least privilege and separation of duties. Production access will be distinct from development and test access. Data exposure across workspaces must be explicit, approved, and auditable. Workspace separation does not eliminate the need for data-level authorization, classification, encryption, secret management, and user-context enforcement.

### Reliability

Critical workloads may require isolated capacity when shared-resource contention threatens availability, freshness, or recovery requirements. Workspace and capacity design must support restartability, idempotent processing, recovery procedures, and appropriate fault containment. Capacity isolation does not by itself satisfy regional disaster-recovery requirements.

### Operations

Each workspace and capacity must have an owner, support responsibility, deployment path, monitoring coverage, alert routing, and documented recovery process. Telemetry must correlate capacity behavior with workspace, workload, pipeline, and data-product impact. Platform operations must periodically review placement and utilization.

### Performance

Capacity decisions must consider peak concurrency, batch windows, event rates, AI activity, semantic-model usage, throttling, and queueing. Representative benchmarks are required before final capacity assignments. Critical workloads should have measurable placement and isolation thresholds.

### Cost

Selective isolation costs more than a single shared capacity but should cost less than universal isolation. Cost and utilization should be tracked by environment, capacity, workspace, workload, or data product where possible. Dedicated capacity requires an evidence-based justification and periodic utilization review.

### Governance

Every workspace must have a defined purpose, owner, permitted data classifications, lifecycle, and approval path. Domain boundaries should reinforce data-product accountability without creating unmanaged silos. Cross-workspace sharing and capacity placement decisions must be reviewable and documented.

### Maintainability

Workspace, capacity, security, deployment, and monitoring configuration should be standardized and automated where practical. Environment-specific configuration and secrets must remain separate from deployable source artifacts. Boundaries must be reversible so that workload placement can change without redesigning the logical platform.

## Validation plan

| Validation | Success measure | Evidence | Status |
|---|---|---|---|
| Representative workload benchmark | Critical and standard workloads meet defined freshness and processing-window targets under expected concurrency | Benchmark results and capacity telemetry | Planned |
| Contention and throttling test | Critical workloads remain within agreed SLOs or produce evidence supporting isolation | Load-test results and throttling metrics | Planned |
| Security and access review | Environment and workspace access demonstrate least privilege and separation of duties | Role matrix, access-review evidence, and audit records | Planned |
| Cost comparison | Shared, selective-isolation, and full-isolation scenarios have documented cost and utilization estimates | Capacity and FinOps analysis | Planned |
| Recovery exercise | Workspace and capacity boundaries do not prevent documented replay, recovery, or rollback | Recovery test evidence | Planned |
| Operational review | Every workspace and capacity has ownership, monitoring, alerting, and escalation coverage | Operations checklist and runbook links | Planned |

## Follow-up actions

- [ ] Define workspace naming, ownership, and lifecycle standards.
- [ ] Establish measurable criteria for moving a workload to dedicated capacity.
- [ ] Benchmark representative data engineering, analytics, real-time, and AI workloads.
- [ ] Produce a capacity cost and utilization model.
- [ ] Define approved cross-workspace sharing and access patterns.
- [ ] Validate deployment and environment-promotion design through [#8 — OPS-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8).
- [ ] Record regional resiliency as a separate architecture decision.

## Reconsideration triggers

Revisit this decision when:

- Representative workload testing shows that shared capacity cannot satisfy critical service levels.
- Actual utilization or cost shows that selective isolation is financially inefficient.
- Security or regulatory review requires stronger physical or administrative boundaries.
- A capacity-level incident affects multiple critical workloads.
- Domain ownership or organizational responsibilities materially change.
- Platform capabilities change the cost or effectiveness of workspace and capacity isolation.
- Recovery requirements require different fault or regional boundaries.

## References

- [Northstar enterprise reference scenario](../ARCH-001/README.md)
- [Northstar enterprise context diagram](../ARCH-001/context-diagram.md)
- [ARCH-001 retrospective and decision backlog](../ARCH-001/RETRO.md)
- [Issue #3 — Establish architecture decision records and review checklist](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3)
