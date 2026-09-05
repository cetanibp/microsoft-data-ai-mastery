# Skills Scorecard

## Rating scale

| Score | Meaning | Evidence threshold |
|---|---|---|
| 0 | Not started | No evidence yet |
| 1 | Aware | Can explain core concepts |
| 2 | Practicing | Has a working guided implementation |
| 3 | Independent | Can design, build, test, and troubleshoot independently |
| 4 | Advanced | Can optimize, govern, and explain tradeoffs across scenarios |
| 5 | Mastery | Can establish standards, mentor others, and defend enterprise decisions with evidence |

## Scorecard

Update scores monthly. Every score of 3 or higher must link to repository evidence.

| Competency | Baseline | Current | Target | Evidence |
|---|---:|---:|---:|---|
| Fabric workspace and domain architecture | 1 | 2 | 5 | [OPS-001 architecture](02-dataops-devops/OPS-001/architecture.md) |
| Lakehouse, Delta, and Spark engineering | 1 | 2 | 4 | [FAB-002 runtime](01-fabric-platform-engineering/FAB-002/README.md) and [FAB-003 quality evidence](01-fabric-platform-engineering/FAB-003/README.md) |
| Warehouse and semantic model engineering | 1 | 1 | 4 | |
| Metadata-driven ingestion | 1 | 3 | 5 | [FAB-001 control plane](01-fabric-platform-engineering/FAB-001/README.md), [FAB-002 runtime](01-fabric-platform-engineering/FAB-002/README.md), and [FAB-003 acceptance gates](01-fabric-platform-engineering/FAB-003/README.md) |
| Performance and capacity optimization | 1 | 3 | 4 | [FAB-004 benchmark decision](01-fabric-platform-engineering/FAB-004/benchmark-results.md) |
| CI/CD and environment promotion | 1 | 3 | 5 | [OPS-001 evidence](02-dataops-devops/OPS-001/README.md) |
| Observability, SLOs, and incident response | 1 | 3 | 5 | [OPS-002 evidence](02-dataops-devops/OPS-002/README.md) |
| Real-Time Intelligence | 1 | 3 | 4 | [RTI-001 end-to-end implementation](03-real-time-intelligence/RTI-001/README.md) |
| Foundry application engineering | 1 | 1 | 4 | |
| Retrieval and grounding | 1 | 1 | 5 | |
| Agent tools and orchestration | 1 | 1 | 5 | |
| Agent evaluation and tracing | 1 | 1 | 5 | |
| Agent security and human oversight | 1 | 1 | 5 | |
| AI-ready data and metadata design | 1 | 2 | 5 | [FAB-001 logical model](01-fabric-platform-engineering/FAB-001/metadata-model.md) |
| Purview governance, lineage, and policy | 1 | 1 | 4 | |
| Data products, contracts, APIs, and GraphQL | 1 | 1 | 4 | |
| Identity, networking, and platform security | 1 | 2 | 4 | [OPS-001 identity boundaries](02-dataops-devops/OPS-001/architecture.md) |
| Resiliency, recovery, and continuity | 1 | 3 | 4 | [FAB-002 recovery](01-fabric-platform-engineering/FAB-002/RETRO.md) and [FAB-003 block/replay evidence](01-fabric-platform-engineering/FAB-003/RETRO.md) |
| Cost estimation and FinOps | 1 | 2 | 4 | [FAB-004 cost model](01-fabric-platform-engineering/FAB-004/benchmark-results.md#capacity-and-allocated-cost-model) |
| Architecture decisions and tradeoff analysis | 1 | 3 | 5 | [ARCH-003 evidence](09-enterprise-architecture/ARCH-003/README.md) and [FAB-004 quantified decision](01-fabric-platform-engineering/FAB-004/benchmark-results.md) |
| Executive and engineering communication | 1 | 1 | 5 | |

## Baseline assessment — August 2026

The baseline is intentionally conservative and only credits capability demonstrated through this repository. Because every baseline score is below 3, no evidence links are required yet. Evidence will be added as prioritized work items produce reviewable designs, implementations, tests, operational artifacts, and retrospectives.

### Five highest-value gaps

The five priorities were selected using four factors: target-score gap, relevance to the enterprise Data + AI architecture goal, dependency value for later work, and ability to produce reusable evidence.

| Priority | Competency gap | Why it is high value | Prioritized work items |
|---:|---|---|---|
| 1 | Architecture decisions and tradeoff analysis | Establishes the scenario, assumptions, decision discipline, and review standard used by every later build. | [#1 ARCH-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/1), then [#3 ARCH-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3) |
| 2 | CI/CD and environment promotion | Converts prototypes into governed, repeatable, testable delivery and directly supports production-grade Fabric work. | [#8 OPS-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8) |
| 3 | AI-ready data and metadata design | Creates the governed semantic foundation required for reliable retrieval, agents, lineage, and data-product consumption. | [#19 DATA-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), followed by [#20 GOV-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20) |
| 4 | Agent tools and orchestration | Builds the safe tool contracts and diagnostic workflow needed for a production-grade Data Operations Agent. | [#14 AGENT-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/14), then [#15 AGENT-002](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/15) |
| 5 | Agent evaluation and tracing | Makes agent quality, safety, latency, cost, and regressions measurable before deployment. | [#16 AGENT-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/16) |

### Prioritization decision

Complete [#1](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/1) and [#3](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/3) first because they define the reference scenario and review method for the remaining work. Then progress through the five gaps in the order above while respecting dependencies within each epic.

### Baseline retrospective

- The initial assessment exposed that the immediate need is not more disconnected training; it is a structured way to turn learning into defensible enterprise architecture evidence.
- Conservative scores prevent professional experience or certifications from being mistaken for repository-demonstrated mastery.
- The roadmap will favor end-to-end builds, failure testing, security, governance, operational evidence, and documented tradeoffs over course completion alone.
- Each completed work item should link its evidence back to this scorecard and record whether the associated competency score changed.
- Reassess the scorecard monthly and only raise a score when the evidence threshold is satisfied.

## Progress reassessment — August 29, 2026

### CI/CD and environment promotion: 1 → 3

[OPS-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/8) now provides independent implementation and troubleshooting evidence across the complete Development-to-Test promotion path:

- GitHub is the source of truth for Fabric item definitions and deployment automation.
- Fabric Git integration and Deployment Pipelines are implemented across separate Development, Test, and Production boundaries.
- GitHub Actions performs validation, predeployment checks, promotion orchestration, and evidence capture.
- Microsoft Entra workload identity federation (OIDC) is used instead of committed long-lived credentials.
- A controlled invalid configuration was demonstrated to block promotion.
- A successful Development-to-Test promotion is reproducible and traceable to a commit and Fabric deployment ID.
- Recovery was demonstrated by reverting Git to a known-good revision and redeploying.
- Protected environments and an explicit Production approval gate were tested without performing a Production deployment.

This satisfies Level 3: the solution was designed, built, tested, deliberately broken, troubleshot, recovered, and documented with durable evidence.

**Why the score is not yet 4:** post-deployment notebook verification remains operator-executed, and automated drift detection, stateful migration handling, and break-glass testing remain future validation areas. Level 4 will require evidence that these broader operational and governance scenarios are handled and that tradeoffs can be demonstrated across multiple deployment patterns.

### Architecture decisions and tradeoff analysis: remains 2

ARCH-003 established a strong ADR and review discipline. OPS-001 has now provided enough implementation evidence for ADR-002 to be accepted, but broader implementation, benchmark, security, cost, recovery, and independent-review evidence is still needed before the overall architecture competency meets the Level 3 threshold.

### FAB-001 reassessment

FAB-001 adds guided implementation and live validation evidence across several competencies:

- **Fabric workspace and domain architecture: 1 → 2.** OPS-001 established the permanent environment topology, and FAB-001 used an isolated feature workspace without creating an unnecessary second branch.
- **Metadata-driven ingestion: 1 → 2.** The repository now contains a tested metadata contract, physical control store, environment resolution, dependencies, multiple load strategies, and failure-safe watermark state. The shared runtime remains Issue #6.
- **AI-ready data and metadata design: 1 → 2.** Stable identities, ownership, SLOs, quality references, and lineage-ready correlation keys provide a reusable governed metadata foundation.
- **Identity, networking, and platform security: 1 → 2.** OPS-001 and FAB-001 define OIDC, least privilege, logical connection references, external secret resolution, and fail-closed validation.
- **Resiliency, recovery, and continuity: 1 → 2.** Definition rollback, forward recovery, state correction, failed-attempt preservation, and stale-write rejection are documented and validated.

These competencies remain below Level 3 because the complete ingestion runtime, enforced database roles, operational scale, and broader recovery scenarios have not yet been implemented.

### Next skill target

The next evidence-producing priority is [#10 — performance, capacity, and cost benchmarking](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/10). It should establish representative workloads, compare design alternatives, and turn runtime and capacity observations into defensible optimization decisions.

## Progress reassessment — September 2, 2026

### Lakehouse, Delta, and Spark engineering: 1 → 2

FAB-002 and FAB-003 provide working guided implementations of parameterized PySpark notebooks, Delta business-key merge, object-run-scoped observations, deterministic Delta evidence, duplicate hashing, and Lakehouse-backed pipeline execution.

**Why the score is not yet 3:** the repository does not yet demonstrate independent performance tuning, partition/file optimization, production-scale Spark diagnostics, or multiple Lakehouse patterns.

### Metadata-driven ingestion: 2 → 3

FAB-001, FAB-002, and FAB-003 now form an end-to-end metadata-driven path:

- immutable environment/release/object/policy definitions;
- shared configuration resolution and fixed-boundary ingestion;
- transactional candidate claim, failure, and compare-and-commit;
- idempotent target publication and drift handling;
- policy-driven reconciliation, blocking, warning, quarantine, and operational evidence;
- deliberate failure, troubleshooting, recovery replay, and concurrency validation.

This satisfies Level 3 because the repository contains a complete shared runtime that was designed, built, tested, deliberately broken, troubleshot, recovered, and documented with live evidence.

**Why the score is not yet 4:** dependency scheduling, production-scale performance, multiple source/target adapters, automated deployment binding, and cross-scenario governance remain open.

### Resiliency, recovery, and continuity: 2 → 3

FAB-002 and FAB-003 demonstrate fixed replayable boundaries, post-write recovery, stale-candidate rejection, exactly-once state advancement, quality-blocked state preservation, recovered-boundary commit, and idempotent evidence.

This satisfies Level 3 because failure and recovery behavior is executable and was verified in the live Fabric control plane rather than described only in architecture documents.

**Why the score is not yet 4:** regional recovery, backup/restore, state migration, capacity failure, disaster simulations, and measured recovery objectives remain future evidence.

### Observability, SLOs, and incident response: 1 → 3

OPS-002 provides an independently implemented operational path across measurable objectives, idempotent evaluations, dashboard projections, deterministic routing, runbooks, and live failure recovery:

- freshness, reliability, duration, quality acceptance, quality enforcement, and alert-latency contracts;
- correlated logical-occurrence telemetry that avoids retry inflation;
- durable evaluation and simulated routing decisions with replay-safe deduplication;
- live reliability-breach detection and deterministic owner/severity routing;
- triage, replay, escalation, recovery, query, and incident-record procedures; and
- a stale-candidate exercise that preserved the accepted watermark and audit history.

This satisfies Level 3 because the solution was designed, built, tested, troubleshot, recovered, and documented with live evidence.

**Why the score is not yet 4:** external delivery integration, scheduled evaluation, multi-scenario threshold optimization, a governed monitoring product, and broader incident simulations remain future evidence.

## Progress reassessment — September 4, 2026

### Performance and capacity optimization: 1 → 3

FAB-004 independently designed, implemented, troubleshot, and documented a reproducible F256 benchmark across steady, peak, and replay workloads. It used alternating paired order, fixed synthetic inputs, operation-level Capacity Metrics evidence, normalized CU, queue and throughput metrics, correctness gates, explicit decision thresholds, and limitations.

**Why the score is not yet 4:** the evidence covers one capacity SKU and workload shape. Level 4 requires tuning across multiple SKUs or data layouts, controlled companion-workload contention, and broader production forecasting.

### Cost estimation and FinOps: 1 → 2

FAB-004 converts operation CU into normalized CU per million rows and an allocated F256 cost coefficient while distinguishing allocated share from incremental billing.

**Why the score is not yet 3:** the environment-specific hourly price was not supplied, so actual dollar allocation, budget variance, and an operational FinOps feedback loop remain unvalidated.

### Architecture decisions and tradeoff analysis: 2 → 3

ARCH-003 established the decision discipline, and FAB-004 applied it to a live implementation choice. The repository now contains declared alternatives, controlled variables, thresholds, multiple scenarios, anomalous-result correction, quantified tradeoffs, a selected design, and explicit limitations.

**Why the score is not yet 4:** broader stakeholder review and cross-platform, security, resiliency, and multi-SKU decisions remain future evidence.

## Progress reassessment — September 5, 2026

### Real-Time Intelligence: 1 → 3

RTI-001 provides an independently implemented and troubleshot real-time operational path:

- custom-endpoint Eventstream ingestion into an Eventhouse;
- a versioned KQL event contract with retention and hot-cache policies;
- contract validation, logical-event deduplication, late-event classification, and sequence-aware current state;
- a low-latency actionable-condition query and 60-second Activator evaluation;
- a four-tile Real-Time Dashboard for state, active conditions, latency, and recent history;
- deliberate late, duplicate, malformed, and out-of-order tests;
- Key Vault–backed secret retrieval with no committed Eventstream connection string; and
- seven passing repository contract tests plus live notification and dashboard evidence.

This satisfies Level 3 because the solution was designed, built, deliberately stressed with edge conditions, troubleshot across notebook, KQL, Activator, and dashboard behavior, and documented with durable evidence.

**Why the score is not yet 4:** the evidence covers one Development workspace, one F256 capacity, synthetic producers, query-time projections, and one notification route. Level 4 requires sustained-load optimization, multiple producers or scenarios, governed production routing, and broader operational ownership.

## Monthly assessment questions

1. What can I now design or troubleshoot without a guide?
2. What production failure modes have I tested?
3. What tradeoffs can I quantify rather than describe abstractly?
4. Which evidence would withstand an architecture review?
5. What is the smallest next build that closes the most important gap?
