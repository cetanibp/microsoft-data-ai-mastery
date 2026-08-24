# ADR-002 — Environment isolation and promotion

**Status:** Proposed  
**Date:** 2026-08-23  
**Decision owner:** Bryan Cetani  
**Reviewers:** To be assigned  
**Related issues:** [#3 — ARCH-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3), [#8 — OPS-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8)  
**Related requirements:** Environment isolation, least privilege, deployment validation, approval, auditability, reproducibility, rollback, and maintainability  

## Decision summary

Northstar Health System will use separate development, test, and production workspaces with version-controlled artifacts and automated, approved promotion. Environment configuration and secrets will remain separate from deployable content, production changes will require validation and approval, and every release will retain deployment and recovery evidence.

## Context

Northstar's Fabric, data, analytics, API, and AI capabilities must be promoted through development, test, and production without mixing access, configuration, secrets, or operational responsibilities. Production changes must be reproducible, validated, auditable, and recoverable.

A decision is required because informal or manual promotion creates environment drift, inconsistent testing, undocumented production changes, and weak rollback evidence. Environment separation alone improves access control but does not make deployments repeatable. Automation alone does not provide adequate safety unless validation, approvals, configuration boundaries, and recovery controls are defined.

This ADR defines the initial environment and promotion strategy. It does not select every CI/CD product, prescribe one deployment mechanism for every artifact type, or define detailed branching and release procedures. Those controls will be implemented and tested through Issue #8.

## Decision drivers

- Separate production access from development and test access
- Enforce least privilege and separation of duties
- Keep deployable artifacts under version control
- Make releases reproducible and traceable to an approved source version
- Validate changes before production promotion
- Keep environment configuration and secrets outside deployable source content
- Record deployment identifiers, approvals, results, timestamps, and actors
- Support rollback or forward recovery
- Reduce environment drift and unauthorized direct changes
- Accommodate stateful data, schema, semantic-model, API, and AI changes
- Provide a controlled emergency-change process
- Avoid unnecessary tenant or capacity isolation without evidence

## Options considered

### Option A — One workspace with naming conventions and manual changes

**Description:**  
Use one workspace for development, testing, and production-like artifacts, distinguishing them through names or folders and applying changes manually.

**Advantages:**

- Lowest initial complexity
- Lowest administrative and capacity cost
- Fast for small experiments

**Disadvantages:**

- No meaningful environment or access isolation
- High risk of production-impacting mistakes
- Difficult to validate and reproduce releases
- Configuration, secrets, and lifecycle states can become mixed
- Weak audit and recovery evidence

**Risks:**

- Development activity can affect production
- Unauthorized or untested changes may be released
- Naming conventions can be applied inconsistently

### Option B — Separate workspaces with manual promotion

**Description:**  
Use distinct development, test, and production workspaces, but copy or recreate changes between environments manually.

**Advantages:**

- Stronger access and environment boundaries
- Moderate implementation complexity
- Lower automation effort
- Better than a single workspace for production protection

**Disadvantages:**

- Manual releases are difficult to reproduce
- High risk of missed artifacts or inconsistent configuration
- Deployment results and approvals may not be recorded consistently
- Environment drift remains likely

**Risks:**

- Test and production may receive different changes
- Manual mistakes can cause outages or incomplete releases
- Rollback may depend on undocumented knowledge

### Option C — Separate workspaces with automated, approved promotion

**Description:**  
Use distinct development, test, and production workspaces. Store deployable artifacts in version control, run automated validation, deploy to test, require production approval, promote through a controlled process, and record release and recovery evidence.

**Advantages:**

- Strong access, environment, and deployment boundaries
- Reproducible and auditable releases
- Consistent validation and approval
- Reduced environment drift
- Supports repeatable rollback or forward recovery
- Provides a foundation for governed platform delivery

**Disadvantages:**

- Requires CI/CD standards, engineering, and maintenance
- Artifact types may require different deployment mechanisms
- Stateful data changes require specialized handling
- Approval gates can increase delivery time

**Risks:**

- Automation errors can distribute an incorrect change consistently
- Incomplete test coverage can create false confidence
- Unsupported or stateful artifacts may require manual controls

### Option D — Separate tenants or dedicated capacities for every environment

**Description:**  
Use separate administrative or physical platform boundaries for development, test, and production in addition to controlled automated promotion.

**Advantages:**

- Maximum environment and resource isolation
- Strong containment of capacity and administrative failures
- Clear cost and ownership boundaries

**Disadvantages:**

- Highest capacity and administrative cost
- More complex identity, networking, governance, monitoring, and deployment
- Greater risk of environmental differences
- Difficult to justify before risk and workload evidence exists

**Risks:**

- Isolation can create operational overhead without proportional benefit
- Environment parity becomes harder to maintain
- Capacity may be underused

## Tradeoff assessment

| Criterion | Weight | Option A | Option B | Option C | Option D | Evidence or rationale |
|---|---:|---:|---:|---:|---:|---|
| Security and privacy | 20% | 1 | 4 | 5 | 5 | Separate environments and controlled promotion reduce inappropriate production access and change risk |
| Reliability and recovery | 15% | 2 | 3 | 5 | 5 | Automated validation, release evidence, and recovery procedures improve deployment reliability |
| Operations and observability | 15% | 3 | 3 | 5 | 2 | Option C provides consistent release telemetry without the operational overhead of universal physical isolation |
| Performance and scalability | 5% | 4 | 4 | 4 | 5 | Promotion strategy has limited direct performance impact; dedicated capacities provide the most resource isolation |
| Cost | 10% | 5 | 4 | 3 | 1 | Automation requires engineering effort; universal isolation has the highest platform cost |
| Governance | 15% | 1 | 3 | 5 | 5 | Versioned, approved, auditable releases provide strong governance evidence |
| Maintainability | 20% | 2 | 3 | 5 | 2 | Standardized automation and configuration separation reduce drift and manual knowledge |
| **Weighted total** | **100%** | **2.20** | **3.35** | **4.75** | **3.55** | Option C provides the strongest balance of control, repeatability, and cost |

Scores use a scale from 1 (poor fit) to 5 (best fit). Scores organize the comparison but do not replace implementation and recovery evidence.

## Decision

Select **Option C — Separate workspaces with automated, approved promotion**.

Northstar will:

- Maintain separate development, test, and production workspaces.
- Use development as the normal authoring environment.
- Treat version control as the source for deployable artifacts.
- Run automated validation before an artifact can be promoted.
- Deploy and verify changes in test before production promotion.
- Require explicit approval for production releases.
- Supply environment-specific configuration during deployment rather than embedding it in deployable content.
- Store secrets and credentials outside source code and platform content.
- Retain deployment identifiers, source versions, approvals, actors, timestamps, validation results, and deployment outcomes.
- Perform post-deployment verification in production.
- Document rollback or forward-recovery procedures appropriate to each artifact and change type.
- Restrict direct test and production changes to controlled exceptions.
- Provide an auditable emergency-change process followed by reconciliation with version control.

The normal promotion flow is:

```mermaid
flowchart LR
    Dev["Development"] --> Validate["Automated validation"]
    Validate --> Test["Test"]
    Test --> Approval["Production approval"]
    Approval --> Prod["Production"]
    Prod --> Verify["Post-deployment verification"]
```

This decision remains **Proposed** until Issue #8 implements and validates the promotion process.

## Consequences

### Positive consequences

- Production is protected from normal development activity.
- Releases are traceable to a source version and recorded approval.
- Test and production receive changes through a consistent process.
- Environment-specific configuration and secrets remain separated.
- Validation failures can stop promotion before production impact.
- Deployment, verification, and recovery evidence becomes reusable architecture and operational proof.
- The process supports incremental automation across different artifact types.

### Negative consequences

- CI/CD implementation and maintenance require engineering effort.
- Some Fabric or stateful artifacts may require specialized deployment handling.
- Production releases take longer when validation and approvals are required.
- Environment drift must be detected rather than assumed absent.
- Rollback may be unsafe for destructive or stateful data changes.
- Emergency changes require additional reconciliation and review.

### Risks and mitigations

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Incomplete testing allows a defective release | Medium | High | Define required unit, integration, security, compatibility, smoke, and post-deployment checks | Engineering owner |
| Automation applies an incorrect change consistently | Medium | High | Use protected sources, change review, deployment previews, approval gates, and scoped identities | Platform engineering |
| Environment-specific configuration causes drift | Medium | High | Parameterize configuration, validate expected values, and run drift detection | Platform engineering |
| Destructive data or schema change cannot be rolled back | Medium | High | Require compatibility analysis, backup or recovery plan, staged rollout, and forward-recovery procedure | Data owner |
| Direct production change bypasses the process | Low | High | Restrict production permissions, audit changes, and define break-glass controls | Security and platform operations |
| Deployment identity has excessive access | Medium | High | Use separate least-privilege identities by environment and periodically review access | Security |
| Unsupported artifact requires manual deployment | Medium | Medium | Document a controlled manual procedure with the same validation, approval, evidence, and reconciliation requirements | Release owner |

## Quality-attribute implications

### Security

Development, test, and production will use separate access assignments and deployment identities. Production deployment identities must have only the permissions required for promotion. Secrets will be retrieved from approved secret storage rather than committed or embedded. Production approvals, direct changes, emergency access, and deployment activity must be auditable.

### Reliability

Automated validation, test deployment, post-deployment verification, and recovery preparation reduce deployment-related failures. Every release must identify whether rollback is safe or forward recovery is required. Stateful changes must preserve restartability, idempotency, compatibility, and recovery expectations.

### Operations

Release telemetry must include source version, deployment identifier, environment, actor or identity, approval, start and finish times, validation results, outcome, and correlation identifier. Failed releases must generate actionable status and follow documented escalation and recovery procedures. Emergency changes must be reconciled with version control.

### Performance

The promotion process must detect changes that could threaten processing windows, latency, concurrency, or capacity behavior. Performance-sensitive releases may require representative benchmark or regression evidence before production approval. Deployment activity should avoid unnecessary interference with critical workloads.

### Cost

CI/CD automation creates implementation and maintenance costs but reduces manual release effort, deployment failures, and recovery time. Separate workspaces do not automatically require dedicated capacity. Deployment and test resources should be measured and included in cost attribution.

### Governance

Every deployable change must have an accountable owner, source version, review, validation evidence, approval when required, and recorded outcome. Data-contract, schema, security, retention, classification, and ownership changes require appropriate governance review. Direct production changes are controlled exceptions.

### Maintainability

Deployable artifacts, tests, configuration definitions, and deployment procedures should be versioned. Environment-specific values and secrets must remain separate. Common validation and deployment behavior should be standardized while allowing specialized handling for different artifact types. Recovery procedures must be documented and exercised.

## Validation plan

| Validation | Success measure | Evidence | Status |
|---|---|---|---|
| Source-to-test promotion | Approved source version deploys reproducibly to test | Pipeline run, source version, deployment manifest, and test results | Planned |
| Test-to-production promotion | Only validated and approved changes reach production | Approval record, production deployment run, and artifact comparison | Planned |
| Configuration and secret separation | No environment secret is present in source; correct environment values are supplied securely | Secret scan, configuration validation, and identity evidence | Planned |
| Failed-validation behavior | A deliberately invalid change is blocked before production | Failure-path test and pipeline evidence | Planned |
| Failed-deployment recovery | A controlled failure produces actionable telemetry and successful rollback or forward recovery | Failure record, alert, recovery steps, and verification | Planned |
| Environment drift detection | Unauthorized or unexpected differences are identified | Drift report and remediation evidence | Planned |
| Direct-change control | Normal users cannot directly modify production; emergency access is audited | Access matrix and break-glass test evidence | Planned |
| Stateful-change validation | Schema or data change demonstrates compatibility and recovery behavior | Migration test, data validation, and recovery evidence | Planned |

## Follow-up actions

- [ ] Implement repository, branching, and review conventions through [#8 — OPS-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8).
- [ ] Define the required automated validation suite.
- [ ] Establish environment-specific configuration and secret patterns.
- [ ] Implement test and production promotion with approval evidence.
- [ ] Define artifact-specific rollback and forward-recovery procedures.
- [ ] Test failed validation, failed deployment, drift, and emergency-change scenarios.
- [ ] Establish deployment telemetry and release-retention standards.
- [ ] Document governance requirements for schema, contract, security, and AI changes.

## Reconsideration triggers

Revisit this decision when:

- Platform limitations prevent reliable automated promotion for critical artifact types.
- Deployment evidence shows that the promotion process cannot meet required recovery or release targets.
- Security review requires stronger tenant, network, capacity, or administrative isolation.
- Approval gates create unacceptable delivery delays without corresponding risk reduction.
- Environment drift remains material despite automated controls.
- A new platform capability materially simplifies promotion, validation, or rollback.
- Regulatory, operational, or organizational responsibilities materially change.

## References

- [Northstar enterprise reference scenario](../ARCH-001/README.md)
- [Northstar enterprise context diagram](../ARCH-001/context-diagram.md)
- [ADR-001 — Platform and workload boundaries](ADR-001-platform-and-workload-boundaries.md)
- [Issue #3 — Establish architecture decision records and review checklist](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3)
- [Issue #8 — CI/CD and environment promotion](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8)
