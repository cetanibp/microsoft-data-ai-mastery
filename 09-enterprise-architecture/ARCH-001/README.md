# ARCH-001 — Enterprise Reference Scenario

**Organization:** Northstar Health System (fictional)  
**Domain:** Multi-hospital healthcare delivery  
**Status:** Baseline reference scenario  
**Related issue:** [#1 — ARCH-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/1)

## Purpose

This scenario provides a stable enterprise context for the architecture decisions, platform implementations, governance controls, AI engineering, and capstone work in this repository. All organizations, volumes, requirements, and operating assumptions are fictional and intended for learning.

## Business problem

Northstar Health System operates hospitals, clinics, and supporting corporate services. Data is distributed across clinical, financial, operational, workforce, and external systems. Existing batch-oriented and point-to-point integrations make it difficult to deliver timely, governed data products, diagnose failures consistently, and introduce AI capabilities safely.

Northstar needs an enterprise Data + AI platform that provides trustworthy analytics, reusable data products, operational monitoring, and governed AI-agent access while meeting healthcare security, availability, recovery, quality, and audit requirements.

## Desired outcomes

- Reduce the time required to onboard new data sources and data products.
- Improve data freshness, quality, lineage, ownership, and discoverability.
- Provide governed enterprise data products for analytics and applications.
- Support near-real-time operational monitoring for selected use cases.
- Enable grounded AI assistants and bounded operational agents.
- Standardize deployment, observability, recovery, and governance across environments.
- Make platform capacity, service levels, and cost drivers measurable.

## Stakeholders and users

| User or stakeholder | Primary need |
|---|---|
| Executive leaders | Trusted organizational KPIs, risks, and strategic insights |
| Clinical leaders | Clinical quality, safety, utilization, and outcome information |
| Operational leaders | Timely capacity, throughput, and service monitoring |
| Analysts and data scientists | Discoverable, documented, governed data |
| Data engineers | Repeatable ingestion, transformation, testing, and recovery |
| AI engineers | Approved knowledge, bounded tools, evaluations, and traces |
| Application teams | Stable, versioned data products and APIs |
| Security and governance teams | Classification, lineage, access control, policy, and auditability |
| Platform support teams | Monitoring, diagnosis, replay, escalation, and runbooks |
| Data owners and stewards | Clear accountability for definitions, quality, access, and change |

## Data domains

- Clinical
- Patient access and scheduling
- Revenue cycle and claims
- Supply chain and pharmacy
- Workforce
- Finance
- Facilities and operational telemetry
- Enterprise reference and master data

## Scope

The reference platform includes ingestion, storage, transformation, orchestration, data quality, metadata, lineage, semantic access, analytics delivery, governed APIs, AI grounding, agent tools, observability, deployment, and operational recovery.

The scenario covers development, test, and production environments and supports both on-premises and cloud-hosted source systems during a phased migration.

## Out of scope

- Replacing transactional systems of record
- Autonomous clinical diagnosis or treatment decisions
- Use of real patient data in this public repository
- Production deployment to an actual healthcare organization
- Unapproved write access by AI assistants or agents
- Final vendor or product selection before tradeoffs are evaluated

## Scale assumptions

| Characteristic | Initial planning assumption |
|---|---:|
| Hospitals | 20 |
| Clinics and outpatient locations | 150 |
| Source systems | 40+ |
| Managed data objects | 600+ |
| Daily batch volume | 500 GB |
| Historical data | 1 PB |
| Largest tables | Billions of rows |
| Standard batch processing window | 6 hours |
| Peak operational event rate | 5,000 events per second |
| Analytics users | 2,000 |
| Concurrent platform users | 200 |

These figures are synthetic planning assumptions. Later performance and cost work must validate whether the architecture can meet them.

## Regulatory, privacy, and security assumptions

- HIPAA and HITECH requirements apply to workloads that process protected health information.
- The enterprise platform may process protected health information and personally identifiable information.
- Least-privilege access and separation of duties are required.
- Data must be encrypted in transit and at rest.
- Data access, deployments, approvals, administrative changes, and agent tool actions must be auditable.
- Data retention and deletion requirements vary by domain and record class.
- Nonproduction environments must use synthetic, masked, or explicitly approved data.
- AI retrieval and responses must respect the requesting user's data permissions.
- AI systems must not independently make clinical decisions.
- Human approval is required before consequential operational actions.
- Secrets and credentials must be stored outside source code and platform content.

These statements are architectural assumptions for a fictional scenario and are not legal advice.

## Nonfunctional requirements

| Category | Initial requirement |
|---|---|
| Availability | Production analytical services achieve 99.9% monthly availability |
| Recovery | Critical analytical services target an RTO of 4 hours and RPO of 1 hour |
| Critical freshness | Selected operational data is available within 15 minutes of source availability |
| Standard batch freshness | Standard daily data is available to consumers by 6:00 a.m. local time |
| Data quality | Critical data products pass required blocking checks before publication |
| Ingestion reliability | At least 99.5% of scheduled executions complete successfully each month |
| Restartability | Failed processing can resume or replay without duplicating accepted records |
| Idempotency | Reprocessing the same valid input produces the same accepted business result |
| Security | Workloads use least privilege, managed identities where supported, centralized secrets, and encryption |
| Auditability | The platform records access, changes, deployments, approvals, and agent actions with correlation identifiers |
| AI grounding | Material factual responses cite approved enterprise evidence |
| AI safety | Write-capable or otherwise consequential agent actions require explicit human approval |
| Observability | Critical failures generate correlated telemetry and actionable alerts within 5 minutes |
| Traceability | Published data can be traced to its source, transformations, quality results, and accountable owner |
| Cost management | Platform costs can be attributed by environment and workload or data product |
| Deployment | Changes are validated and promoted through development, test, and production with rollback evidence |
| Maintainability | Operational procedures, ownership, dependencies, and recovery steps are documented and reviewable |

These are baseline targets. Subsequent ADRs and benchmark evidence may refine them.

## Architecture principles

- Prefer governed, reusable platform capabilities over isolated point solutions.
- Treat data products as owned services with contracts, quality targets, and consumer documentation.
- Separate code, environment configuration, and secrets.
- Design ingestion and transformations for restartability and idempotent reprocessing.
- Make security, lineage, quality, observability, and cost part of the design rather than later additions.
- Begin agent capabilities with read-only diagnosis and recommendations.
- Require explicit approval and least privilege for consequential actions.
- Use measurable evidence to accept, reject, or revise architecture decisions.

## Assumptions

- Microsoft Fabric and Azure are preferred platforms, but component choices require documented tradeoff analysis.
- Existing source systems remain the systems of record.
- Some sources remain on-premises during a phased migration.
- Batch and event-driven integration are both required.
- The learning implementation uses only synthetic or approved public data.
- The initial operational agent is diagnostic and read-only.
- Data-product ownership is assigned to business-aligned domain teams with platform support.
- Central security and governance teams define enterprise guardrails.
- Platform capabilities are promoted through development, test, and production.
- Requirements will be refined when benchmark, security, recovery, and stakeholder-review evidence becomes available.

## Unresolved questions

1. Which workloads require cross-region disaster recovery?
2. Which data domains genuinely require near-real-time processing?
3. What are the authoritative systems for shared business concepts?
4. What retention and deletion periods apply to each data class?
5. Which consumers require row-level or column-level security?
6. How should capacity be divided among data engineering, analytics, and AI workloads?
7. What maximum monthly platform cost should the architecture target?
8. Which operational actions could an agent eventually execute?
9. Who owns each data product and approves contract changes?
10. What evidence is required before an AI capability may access sensitive data?
11. Which failures must block publication rather than generate warnings?
12. Which service-level targets justify premium capacity or additional regional redundancy?

## Evidence

- [Enterprise context diagram](context-diagram.md)
- [Scenario glossary](glossary.md)
- [Retrospective](RETRO.md)
