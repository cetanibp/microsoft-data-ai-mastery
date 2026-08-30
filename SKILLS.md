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
| Lakehouse, Delta, and Spark engineering | 1 | 1 | 4 | |
| Warehouse and semantic model engineering | 1 | 1 | 4 | |
| Metadata-driven ingestion | 1 | 2 | 5 | [FAB-001 evidence](01-fabric-platform/FAB-001/README.md) |
| Performance and capacity optimization | 1 | 1 | 4 | |
| CI/CD and environment promotion | 1 | 3 | 5 | [OPS-001 evidence](02-dataops-devops/OPS-001/README.md) |
| Observability, SLOs, and incident response | 1 | 1 | 5 | |
| Real-Time Intelligence | 1 | 1 | 4 | |
| Foundry application engineering | 1 | 1 | 4 | |
| Retrieval and grounding | 1 | 1 | 5 | |
| Agent tools and orchestration | 1 | 1 | 5 | |
| Agent evaluation and tracing | 1 | 1 | 5 | |
| Agent security and human oversight | 1 | 1 | 5 | |
| AI-ready data and metadata design | 1 | 2 | 5 | [FAB-001 logical model](01-fabric-platform/FAB-001/metadata-model.md) |
| Purview governance, lineage, and policy | 1 | 1 | 4 | |
| Data products, contracts, APIs, and GraphQL | 1 | 1 | 4 | |
| Identity, networking, and platform security | 1 | 2 | 4 | [OPS-001 identity boundaries](02-dataops-devops/OPS-001/architecture.md) |
| Resiliency, recovery, and continuity | 1 | 2 | 4 | [FAB-001 lifecycle and validation](01-fabric-platform/FAB-001/ownership-and-lifecycle.md) |
| Cost estimation and FinOps | 1 | 1 | 4 | |
| Architecture decisions and tradeoff analysis | 1 | 2 | 5 | [ARCH-003 evidence](09-enterprise-architecture/ARCH-003/README.md) |
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

## August 2026 evidence reassessment

The scorecard remains conservative and credits demonstrated repository evidence rather than certifications or professional experience alone.

- **CI/CD and environment promotion reached level 3.** OPS-001 includes a working multi-environment Fabric lifecycle, required validation, OIDC authentication, Test promotion, Production approval/preflight, rollback, and retained evidence.
- **Metadata-driven ingestion reached level 2.** FAB-001 independently validates the control-plane model and state contract, but the shared ingestion runtime remains Issue #6.
- **Fabric workspace architecture, AI-ready metadata design, platform security, and recovery reached level 2.** The repository now contains guided working designs and live validation; broader scenarios, enforced production permissions, and operational scale evidence are still required for level 3.

The next score increase should come from FAB-002 only after the runtime demonstrates restartability, idempotency, dependency handling, partial-failure recovery, and concurrency behavior.

## Monthly assessment questions

1. What can I now design or troubleshoot without a guide?
2. What production failure modes have I tested?
3. What tradeoffs can I quantify rather than describe abstractly?
4. Which evidence would withstand an architecture review?
5. What is the smallest next build that closes the most important gap?
