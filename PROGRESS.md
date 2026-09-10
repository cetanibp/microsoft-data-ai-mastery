# Progress Log

## Dashboard

| Measure | Current |
|---|---:|
| Milestones completed | 2 / 5 |
| Epics completed | 1 / 4 |
| Work items completed | 10 |
| Competencies at level 3+ | 7 |
| Competencies at level 4+ | 0 |
| Capstone status | Not started |

## Monthly updates

### 2026-08 — Foundation, governed delivery, and metadata control

**Outcomes**

- Created the mastery roadmap, tracking model, and evidence standards.
- Completed the baseline skills assessment and prioritized the five highest-value gaps.
- Defined Northstar Health System as the common fictional enterprise reference scenario with measurable nonfunctional requirements.
- Established the ADR template, initial architecture decisions, decision register, and reusable architecture-review standard.
- Applied 84 architecture checks to Northstar and approved it with conditions for planning-baseline use.
- Completed OPS-001 and implemented a governed Fabric CI/CD path using GitHub, Fabric Git integration, Fabric Deployment Pipelines, GitHub Actions, OIDC workload identity, protected environments, validation gates, promotion evidence, and recovery evidence.
- Demonstrated a controlled invalid change being blocked, a successful Development-to-Test promotion, Git-based recovery to a known-good revision, and the corrected Production approval gate without deploying to Production.
- Accepted ADR-002 based on implementation and recovery evidence from OPS-001.
- Completed FAB-001 with a versioned ingestion control-plane model, 28-table Fabric SQL Database package, 33 automated tests, live Fabric deployment, and concurrency-safe watermark validation.
- Completed FAB-002 with a metadata-driven Fabric pipeline and notebook, transactional watermark procedures, idempotent Delta publication, schema-drift routing, failure recovery, durable telemetry, and stale-candidate protection.

**Evidence shipped**

- Repository structure, roadmap, scorecard, issue taxonomy, and starter backlog.
- [August 2026 baseline skills assessment](SKILLS.md#baseline-assessment--august-2026).
- [ARCH-001 enterprise reference scenario](09-enterprise-architecture/ARCH-001/README.md).
- [ARCH-003 architecture decisions and review evidence](09-enterprise-architecture/ARCH-003/README.md).
- [OPS-001 CI/CD implementation](02-dataops-devops/OPS-001/README.md).
- [OPS-001 durable release evidence](02-dataops-devops/OPS-001/evidence/README.md).
- [Accepted ADR-002 — Environment isolation and promotion](09-enterprise-architecture/decisions/ADR-002-environment-isolation-and-promotion.md).
- [FAB-001 ingestion control-plane metadata model](01-fabric-platform-engineering/FAB-001/README.md).
- [FAB-001 validation evidence](01-fabric-platform-engineering/FAB-001/evidence/README.md) and [retrospective](01-fabric-platform-engineering/FAB-001/RETRO.md).
- [FAB-002 resilient incremental-ingestion implementation](01-fabric-platform-engineering/FAB-002/README.md), [live Fabric evidence](01-fabric-platform-engineering/FAB-002/evidence/live-fabric-checkpoint.md), and [retrospective](01-fabric-platform-engineering/FAB-002/RETRO.md).

**Skills improved**

- Architecture decisions and tradeoff analysis: 1 → 2 — [ARCH-003 evidence](09-enterprise-architecture/ARCH-003/README.md).
- CI/CD and environment promotion: 1 → 3 — [OPS-001 evidence](02-dataops-devops/OPS-001/README.md).
- Fabric workspace and domain architecture: 1 → 2 — [OPS-001 architecture](02-dataops-devops/OPS-001/architecture.md).
- Metadata-driven ingestion: 1 → 3 — [FAB-001 control-plane evidence](01-fabric-platform-engineering/FAB-001/README.md) and [FAB-002 runtime evidence](01-fabric-platform-engineering/FAB-002/README.md).
- AI-ready data and metadata design: 1 → 2 — [FAB-001 logical model](01-fabric-platform-engineering/FAB-001/metadata-model.md).
- Identity, networking, and platform security: 1 → 2 — [OPS-001 identity boundaries](02-dataops-devops/OPS-001/architecture.md).
- Resiliency, recovery, and continuity: 1 → 2 — [FAB-001 lifecycle and validation](01-fabric-platform-engineering/FAB-001/ownership-and-lifecycle.md).

**What failed or changed**

- The initial roadmap suggested moving directly from the baseline into implementation work. The completed assessment showed that a common scenario and review discipline needed to come first.
- ADR-002 moved from Proposed to Accepted after OPS-001 produced implementation, validation, promotion, approval, and recovery evidence.
- CI/CD and environment promotion now meets the Level 3 threshold because the solution was independently designed, built, tested, deliberately broken, troubleshot, recovered, and documented.
- CI/CD remains below Level 4 because post-deployment notebook verification is still operator-executed and automated drift detection, stateful migration handling, and break-glass testing remain open.
- FAB-001 confirmed that Fabric workspace state and Git branches are separate lifecycle concepts; its isolated workspace reused the existing feature branch.
- Active-configuration results are object/environment pairs rather than distinct object counts.
- Fabric-generated SQL project files add substantial source-control artifacts and require review for unintended churn.
- Definition rollback cannot reverse mutable runtime state; incompatible stateful changes require forward recovery.
- Fabric Git integration did not deploy the FAB-001 seed data automatically; the metadata seed had to be executed before the pipeline could resolve exactly one active configuration.
- Fabric labels the orchestration item as `Pipeline` while its generated Git artifact type is `DataPipeline`; generated source remains the authoritative review surface.
- Reviewing that generated source caught literal failure-path identity mappings that looked correct in the UI but were not expressions.
- A replay exposed non-idempotent additive-drift logging; changing the write to merge by object-run identity eliminated duplicate evidence.
- The live stale-candidate test required two browser tabs, and proved that the losing completion becomes `RECOVERY_REQUIRED` without advancing state.
- Metadata-driven ingestion now meets Level 3 because the shared runtime was independently designed, implemented, deliberately failed, recovered, concurrency-tested, and documented.

**Next focus**

- Implement [#7 — reconciliation and data-quality gates](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/7) using the FAB-001 quality-policy contract and FAB-002 run identities.
- Preserve publication-blocking decisions, quarantine evidence, and run/object-run correlation through quality execution.
- Prepare [#9 — SLOs, observability, and incident response](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/9) to consume the durable execution traces created by FAB-002.

### 2026-09 — Quality acceptance, quarantine, and recovery

**Outcomes**

- Completed FAB-003 with a policy-driven acceptance boundary between target publication and watermark commit.
- Implemented allowlisted BLOCK and WARN contracts, durable SQL decisions/results, hashed quarantine evidence, and a quality-accepted completion wrapper.
- Proved accepted, blocked, watermark-preservation, recovery-replay, duplicate quarantine, same-object-run idempotency, and live warning behavior.
- Captured and sanitized Fabric-generated Pipeline, Notebook, and Lakehouse artifacts.
- Expanded the FAB-003 suite to 33 tests, including generated-pipeline ordering and workspace-identifier sanitization.
- Completed OPS-002 with measurable SLOs, correlated operational telemetry, idempotent evaluation and routing persistence, operational runbooks, and a live stale-candidate recovery exercise.
- Proved a reliability breach, deterministic simulated routing, replay-safe persistence, quality-enforcement integrity, and state-safe orphan recovery in Development.
- Completed FAB-004 with reproducible smoke, steady, 80-million-row peak, and idempotent-replay benchmarks on F256.
- Selected bounded parallelism `PAR4` after it improved median elapsed time by 30.4%–53.6%, reduced median CU by 31.3%–47.7%, preserved correctness, and recorded zero throttling.
- Completed RTI-001 with Eventstream ingestion, Eventhouse contract validation and deduplication, sequence-aware current state, 60-second actionable-condition evaluation, contextual notification, and a four-tile Real-Time Dashboard.
- Proved late, duplicate, malformed, and out-of-order handling plus 59-second query detection and 79-second final notification latency.
- Closed EPIC-FAB-001 and the Fabric Platform & DataOps milestone after all seven child work items and Phase 1 exit evidence were completed.

**Evidence shipped**

- [FAB-003 reconciliation and data-quality gates](01-fabric-platform-engineering/FAB-003/README.md).
- [FAB-003 live and automated evidence](01-fabric-platform-engineering/FAB-003/evidence/README.md).
- [FAB-003 retrospective](01-fabric-platform-engineering/FAB-003/RETRO.md).
- [OPS-002 SLOs, observability, and incident response](02-dataops-devops/OPS-002/README.md).
- [OPS-002 live telemetry and routing checkpoint](02-dataops-devops/OPS-002/evidence/live-development-checkpoint.md), [failure-recovery exercise](02-dataops-devops/OPS-002/evidence/failure-recovery-exercise.md), and [retrospective](02-dataops-devops/OPS-002/RETRO.md).
- [GitHub Actions run 33568120779](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33568120779) validating the generated pipeline.
- [GitHub Actions run 33576595412](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33576595412) validating the synthetic duplicate quarantine window.
- [FAB-004 benchmark decision](01-fabric-platform-engineering/FAB-004/benchmark-results.md), [operation-level evidence](01-fabric-platform-engineering/FAB-004/evidence/README.md), and [retrospective](01-fabric-platform-engineering/FAB-004/RETRO.md).
- [RTI-001 real-time operational monitoring](03-real-time-intelligence/RTI-001/README.md), [live validation](03-real-time-intelligence/RTI-001/evidence/live-development-validation.md), [dashboard and alert evidence](03-real-time-intelligence/RTI-001/evidence/README.md), and [retrospective](03-real-time-intelligence/RTI-001/RETRO.md).

**Skills improved**

- Lakehouse, Delta, and Spark engineering: 1 → 2 — FAB-002 target merge plus [FAB-003 Delta quality and quarantine evidence](01-fabric-platform-engineering/FAB-003/README.md).
- Metadata-driven ingestion: 2 → 3 — FAB-001 definitions, FAB-002 shared runtime, and [FAB-003 policy-driven acceptance](01-fabric-platform-engineering/FAB-003/RETRO.md).
- Resiliency, recovery, and continuity: 2 → 3 — fixed-boundary block, state preservation, replay recovery, concurrency protection, and idempotent evidence across FAB-002 and FAB-003.
- Observability, SLOs, and incident response: 1 → 3 — [OPS-002 measurable objectives, live routing, runbooks, and recovery evidence](02-dataops-devops/OPS-002/README.md).
- Performance and capacity optimization: 1 → 3 — [FAB-004 controlled workload, concurrency, queue, CU, and threshold evidence](01-fabric-platform-engineering/FAB-004/benchmark-results.md).
- Cost estimation and FinOps: 1 → 2 — [FAB-004 normalized-CU and allocated-cost model](01-fabric-platform-engineering/FAB-004/benchmark-results.md#capacity-and-allocated-cost-model).
- Architecture decisions and tradeoff analysis: 2 → 3 — [FAB-004 evidence-backed `SEQ1` versus `PAR4` decision](01-fabric-platform-engineering/FAB-004/benchmark-results.md).
- Real-Time Intelligence: 1 → 3 — [RTI-001 end-to-end implementation, edge-case tests, notification, and dashboard evidence](03-real-time-intelligence/RTI-001/README.md).

**What failed or changed**

- Fabric passed a blank optional Pipeline parameter to the notebook as null; the mapping now normalizes it with `coalesce`.
- Notebook auto-binding wrote a physical workspace ID into generated source. CI rejected the commit, the repository definition was sanitized, and the pipeline suite now checks generated workspace identifiers.
- The encounter object does not have the existing WARN policy assigned in immutable release `1.0.0`. WARN behavior was validated live in an isolated Delta table rather than mutating the approved release or writing a false SQL control-plane decision.
- The original synthetic rows were behind the committed watermark; a later duplicate window produced genuine quarantine evidence without resetting runtime state.
- OPS-002's first routing candidate and persistence logic derived different deduplication keys; live validation exposed the mismatch and the contract was unified.
- A verification query expected `evaluation_status` from the open-breach view; SQL compilation prevented the write, the view contract was corrected, and routing then persisted idempotently.
- Failure-exercise precheck found a genuine orphaned candidate, so the exercise preserved the later accepted winner and abandoned the obsolete attempt instead of injecting another failure or replaying an already-covered boundary.
- Cumulative Capacity Metrics subtraction produced misleading individual CU deltas because of refresh timing and report-window churn; Timepoint Item Detail became the authoritative per-session CU source.
- The first PEAK attempt correctly failed its tier assertion because large-tier parameters were not set explicitly. The corrected run passed, and the validation-only attempt was retained as a documented measurement limitation.
- Interactive `getpass` did not prompt in the Fabric PySpark notebook, so RTI-001 moved Eventstream secret retrieval to Azure Key Vault.
- RTI-001 query authoring exposed an undefined projected scalar and a malformed formatting transfer; both were corrected and the final committed definitions passed seven contract tests.
- Activator was stopped after the live notification test to prevent repeated synthetic alerts.

**Next focus**

- Begin Phase 2 with [#12 — Production-grade Data Operations Agent](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/12), reusing the governed operational telemetry produced in Phase 1.
- Start with [#13 — grounded Foundry application](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13) to establish the retrieval, deployment, and evaluation foundation for the later agent work.

### 2026-09-05 — Learning-gap review and backlog expansion

**Planning outcomes**

- Expanded all 14 previously open issues (#12–#25) with implementation depth, dependencies, evidence expectations, and clear early governance/evaluation increments.
- Created [#45](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45)–[#54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) with labels, milestones, and parent-epic links: four principal builds, three hardening/review/maintenance follow-ups, and three optional advanced extensions.
- Added an explicit capstone implementation owner ([#48](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/48)) and analytical/semantic-model exercise ([#46](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/46)).
- Linked retrospective follow-ups for producer telemetry, deployment automation/drift/state migration, cost experiments, and architecture decisions to executable backlog items.
- Updated roadmap, track indexes, issue catalog, milestone scope, working agreement, and skill advancement expectations.

**Status and evidence boundary**

There are 24 open issues in this dated snapshot: 3 epics and 21 work items, including 3 optional P2 extensions. The completion dashboard above is unchanged: the review produced planning artifacts, not completed implementations or new skill scores. Phase 0 and Phase 1 remain complete. Repository hygiene/CI corrections are tracked in #51 and remain unimplemented by this documentation change.

**Evidence**

- [September learning-gap review and recommendation coverage](tracking/LEARNING_GAP_REVIEW_2026-09.md)
- [Current issue catalog](tracking/STARTER_ISSUES.md)
- [Expanded AI epic](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/12), [expanded governed-data epic](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/18), [expanded capstone epic](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/22)

**Next focus**

1. Publish the minimum #19/#20 corpus, terminology, ownership and access-policy slice.
2. Begin #13 with the initial #16 dataset, rubric, held-out cases, and thresholds before tuning.
3. Queue #45/#47/#49/#51 as bounded delivery/integration increments; keep work in progress at two or fewer issues.
4. Begin #50's Phase 1 reassessment when ready. Keep #52–#54 optional and deferred until the next skill gap warrants them.

The monthly scheduled review begins October 1, 2026, around 8 a.m. Pacific; it recommends changes for review and does not modify the repository automatically.

### 2026-09-05 — AI-001 corpus walkthrough, step 2

- Started the minimum DATA-001/GOV-001 prerequisite for AI-001 with a [draft corpus manifest and field guide](06-ai-ready-data/DATA-001/README.md).
- Selected three existing Northstar operational documents, each pinned to the inspected source commit and file blob SHA.
- Documented proposed ownership, allowed use, access, freshness and update/deletion rules; approval and runtime enforcement remain pending.
- Evidence level: artifact-only validation. No AI deployment, access-enforcement demonstration, issue completion or competency-score change is claimed.
- Next guided step: operational glossary and identity/access matrix, followed by evaluation design before retrieval tuning.

### 2026-09-05 — AI-001 corpus walkthrough, step 3

- Added a [draft operational glossary](06-ai-ready-data/DATA-001/operational-glossary.md) with eight source-informed definitions, conservative aliases, distinctions and revision-pinned evidence.
- Recorded five ambiguity/interpretation examples as development evaluation seeds; these are not executed semantic tests or held-out cases.
- Verified artifact structure and source traceability. The three-source corpus remains unchanged; the glossary is supporting draft metadata with its own version.
- Next guided step: requesting-user versus workload identity and the access matrix. Approval, runtime enforcement, retrieval and full evaluation remain open; no issue closure or skill-score change.

### 2026-09-06 — AI-001 corpus walkthrough, step 4

- Added the [GOV-001 identity/access matrix](07-governance-security/GOV-001/README.md) and JSON policy matching the corpus manifest's existing policy ID.
- Separated requesting-user entitlement, serving-workload access, index-building permissions and corpus-maintainer responsibility; consequential actions remain denied in this baseline.
- Specified cache/revocation checks, sanitized audit fields and eleven unexecuted development scenarios. Documented the public-source limitation and need for a protected synthetic fixture for confidentiality evidence.
- Evidence level: artifact-only structural validation. No identity bindings, resource assignments, enforced authorization, issue closure or skill-score change.
- Next guided step: initial evaluation questions and expected behavior before retrieval tuning. Content/policy review and runtime enforcement remain open.

### 2026-09-06 — AI-001 corpus walkthrough, step 5

- Added [30 evaluation questions and a versioned rubric](04-foundry-ai-engineering/AI-001/evaluation/README.md) before retrieval tuning: supported, ambiguous, stale/ineligible, unauthorized, unanswerable and adversarial cases.
- Allocated 20 development and 10 reserved-from-tuning cases; documented public/author visibility and prior-topic overlap rather than claiming a blind independent holdout.
- Defined source-section retrieval, answer grounding, citation, behavior, latency and variable-cost targets; critical violations override aggregate scores.
- Verified artifact structure and source references only. Runtime fixtures, model evaluation, performance measurement and approval remain unimplemented/pending; no pass results, issue closure or score change.
- Next: review/freeze prerequisites and evaluation targets, then local corpus loading and chunking.

### 2026-09-06 — AI-001 corpus walkthrough, step 6

- Implemented the [local corpus loader and chunking comparison](04-foundry-ai-engineering/AI-001/runtime/README.md) with Python standard library only.
- Verified all three source blob hashes; produced 24 Markdown-section and 15 fixed-window chunks (800 characters with 120 overlap), retaining exact offsets, source sections, pinned citations and deterministic identities.
- [Local evidence](04-foundry-ai-engineering/AI-001/evidence/local-chunk-preparation.json): 13 contract tests passed, including changed-source rejection, path/source safeguards, complete content coverage, fence handling and replay-table preservation.
- Measured preparation tradeoffs only: section chunks preserve the recovery table but can exceed 800 characters; fixed windows duplicate overlap and can split rows. No retrieval-quality winner is claimed.
- Outputs are explicitly offline draft study, not runtime eligible. Content/policy approval and live authorization/freshness remain open; no cloud resources, model calls, reserved evaluation use, issue closure or score change.
- Next: local keyword retrieval over both passage sets using development questions.

### 2026-09-06 — AI-001 Azure AI Search direction selected

- User selected Azure AI Search as the next retrieval platform after comparing managed processing with the local loader/chunking approach.
- Added the [service-discovery walkthrough](04-foundry-ai-engineering/AI-001/azure-search/README.md): inspect a learning service first, then configure access, review the synthetic lab import contract, create indexes and query the prepared passages.
- Retain local source/hash/chunk evidence and plan an Azure-managed preprocessing comparison later. Development/reserved evaluation separation remains unchanged.
- No Azure resources, indexes, uploads or permission changes have been performed. Service tier/region/access are pending; local runtime-ineligible artifacts are not automatically promoted to approved serving content.

### 2026-09-08 — AI-001 Azure retrieval checkpoint

- User-reported RBAC lab setup and final index counts: 24 Markdown-section chunks and 15 fixed windows. User preparation hashes match local evidence.
- Completed manual retrieval review of five supported development questions against both indexes with fixed text-only keyword settings. [Evidence and limitations](04-foundry-ai-engineering/AI-001/evidence/azure-development-retrieval-02.md).
- Found a window result missing the table heading that identifies a prohibited action, truncated closure wording, and heading-only section results. Relevant-section hits alone do not prove sufficient answer context.
- Proposed a structure-aware local chunking experiment. No model evaluation, reserved-case execution, issue closure, skill-score change or serving-readiness claim.

### 2026-09-09 — AI-001 managed Markdown comparison recorded

- Recorded [Azure-managed h2 setup and five-case comparison](04-foundry-ai-engineering/AI-001/evidence/azure-markdown-h2-comparison-03.md), with structured observations, from user-supplied lab responses; execution timestamps were not captured.
- Compared 24 custom sections, 15 fixed windows and 18 managed chunks. Managed h2 retains complete required context within the top five for 5/5 inspected development queries, including table prohibitions, nested verification checks and complete closure wording.
- Ranking remains mixed. Documented the five-layer question ambiguity, different heading placement and REST API versions, and missing live configuration readback.
- Continue with h2 provisionally; capture sanitized configuration and align comparison controls before retrieval changes. No full evaluation pass, reserved-case run, model-answer evidence, serving-readiness claim, issue closure or competency-score change.

### 2026-09-09 — AI-001 live controls and aligned-API comparison

- Recorded [selected live index/indexer/skillset settings, 18-chunk provenance and all 15 repeated queries](04-foundry-ai-engineering/AI-001/evidence/azure-aligned-api-comparison-04.md) from user-supplied lab responses.
- All inspected text analyzers, BM25 settings, synonym maps and scoring profiles match. All 15 required-passage ranks reproduced with API 2026-04-01; context fragmentation persists in the custom baselines.
- Complete pinned URLs and consistent metadata were verified in the readbacks; no independent cloud byte verification is claimed. Managed h2 remains a provisional candidate.
- Prepared the [heading-search experiment specification](04-foundry-ai-engineering/AI-001/azure-search/heading-search-experiment.md), using a separate combined field and declared comparison gates. It is not deployed or executed.
- No model answers, reserved evaluation, serving enforcement, issue closure or skill-score changes.

### 2026-09-09 — AI-001 heading-search experiment completed

- Recorded [checkpoint 05](04-foundry-ai-engineering/AI-001/evidence/azure-heading-search-05.md): user executed an ETag-conditional field addition, 18 successful merges and full document-value readback. Original identities/fields and all false eligibility flags were preserved.
- Captured four reported snapshot/payload hashes and five A/B query cases. Baseline A ranks reproduced; B improved target-write evidence 3→2 and starting identifiers 2→1, with three unchanged and no required-passage regressions. Both arms retain complete required context within top five for 5/5 cases.
- Provisionally prefer text_with_headings_v1 for development under the predeclared gate. No generated-answer or full evaluation pass is claimed.
- Next: [derived-field ingestion maintenance](04-foundry-ai-engineering/AI-001/azure-search/heading-field-maintenance.md). Current population is a one-time merge and is not maintained by the indexer. Full serving/security/lifecycle evidence and ADR-009 remain open; no issue closure or skill-score change.

### 2026-09-10 — AI-001 separate searchable headings

- Recorded [checkpoint 06](04-foundry-ai-engineering/AI-001/evidence/azure-separate-headings-06.md) from user-supplied lab results. The separate arm improves target-write primary evidence 2→1 and matches four other primary ranks; both arms retain complete required context for 5/5.
- Recorded the secondary stale-case checklist regression 3→4 and the persistent active-attempt versus completed-winner ranking problem.
- Documented local Git Bash recovery, cp1252 decoding, matching merge-payload hash and 18-record exact readback with unchanged preexisting fields and false eligibility.
- Provisionally prefer separate searchable headings; updated the maintenance plan accordingly. No automatic indexing maintenance, model answers, reserved evaluation, issue closure or skill-score change is claimed.

# YYYY-MM — Theme

**Outcomes**

- 

**Evidence shipped**

- 

**Skills improved**

- Competency: old score → new score — evidence link

**What failed or changed**

- 

**Next focus**

- 
