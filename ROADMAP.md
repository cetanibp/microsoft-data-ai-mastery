# Roadmap

This roadmap emphasizes applied engineering and architecture rather than additional certification accumulation. Dates are planning targets and can be adjusted based on workload and platform access.

## Phase 0 — Foundation and baseline

**Status:** Complete — August 2026  
Target: September 2026

- [x] Establish repository conventions, issue templates, scorecard, and monthly review cadence.
- [x] Create a reference enterprise scenario and nonfunctional requirements.
- [x] Complete a baseline self-assessment with evidence links.
- [x] Publish the first architecture context diagram and decision log.

Exit evidence: a prioritized backlog, baseline skill scores, defined capstone scenario, and an architecture review checklist.

**Outcome:** Phase 0 completed ahead of the planning target. ARCH-001, ARCH-002, and ARCH-003 established the Northstar reference scenario, conservative evidence-based skills baseline, ADR discipline, and reusable 84-question architecture review standard.

## Phase 1 — Fabric platform engineering and DataOps

**Status:** Complete — September 2026  
Target: October–December 2026

- [x] Build metadata-driven ingestion with incremental processing, restartability, schema-drift handling, reconciliation, and reprocessing.
- [x] Implement the initial governed CI/CD and environment-promotion foundation through OPS-001.
- [x] Add tested operational observability and automated quality gates beyond deployment validation.
- [x] Benchmark performance and document capacity/cost tradeoffs.

Exit evidence: a repeatable framework, failure-injection tests, operational dashboard, runbook, ADRs, and benchmark report.

**Progress to date:** OPS-001 established governed Fabric delivery and supported acceptance of ADR-002. FAB-001 through FAB-003 completed the versioned control plane, resilient ingestion runtime, reconciliation, quality gates, quarantine, and recovery evidence. OPS-002 added measurable SLOs, correlated operational telemetry, deterministic simulated routing, runbooks, and a live stale-candidate recovery exercise. FAB-004 completed reproducible steady, peak, and replay benchmarking and selected bounded parallelism `PAR4` with quantified runtime, queue, CU, correctness, throttling, cost-allocation, and limitation evidence. RTI-001 completed the phase with versioned operational-event ingestion, edge-condition handling, low-latency detection and notification, and a live current-state/history dashboard.

## Phase 2 — Production AI and agent engineering

**Status:** Ready to start — scope expanded September 5, 2026  
Target: January–March 2027 (planning horizon; start ready work now)

- [ ] Build a grounded AI application with retrieval, tool calling, evaluation, tracing, and safety controls.
- [ ] Implement a Data Operations Agent that diagnoses pipeline failures using telemetry and lineage.
- [ ] Add human approval, identity boundaries, adversarial tests, and measurable quality targets.

- [ ] Provision and deploy the AI application reproducibly through [AI-002](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45), with smoke tests, evaluation gates, identity/network validation, and rollback.
- [ ] Connect existing lab pipeline producers to real-time monitoring and diagnosis through [RTI-002](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/47).
- [ ] Automate Fabric deployment verification, drift/state-migration controls, and RTI regression maintenance through [OPS-003](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/49) and [OPS-004](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/51).

**Entry sequence:** complete only the minimum corpus/terminology/access slice of #19/#20, then #13 with the initial #16 dataset and rubric. Continue through #14/#15, complete evaluations and #17 controls, and integrate delivery. No full-governance-epic dependency is imposed on starting retrieval.

Exit evidence: comparative retrieval results, held-out eval suite, direct/MCP tool comparison, bounded workflow, trace samples, threat model, exact-action authorization tests, reproducible deployment and rollback, live pipeline-to-diagnosis evidence, operating runbook, and demo.

## Phase 3 — AI-ready data, governance, and data products

**Status:** Not started  
Target: April–June 2027

- [ ] Design governed semantic and metadata layers for safe AI consumption.
- [ ] Implement lineage-aware discovery and policy enforcement.
- [ ] Publish reusable data products through documented APIs or GraphQL.
- [ ] Demonstrate security, privacy, data quality, and responsible-AI controls.

- [ ] Build [DATA-002](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/46): an analytical star schema, historical dimensions, tested semantic measures, consumer access checks, and a measured storage-mode comparison.
- [ ] Demonstrate retrieval/index/cache permission revocation and data lifecycle, plus API consumer compatibility and deprecation behavior.

Exit evidence: discoverable metadata, implemented analytical/semantic product, data contracts, policy matrix and enforcement tests, lineage, API specifications and consumer tests, quality SLOs, and governance playbook.

## Phase 4 — Enterprise architecture and capstone

**Status:** Not started  
Target: July–September 2027

- [ ] Integrate Fabric, AI, agents, governance, observability, and APIs into one enterprise reference solution.
- [ ] Produce cost and capacity models, resiliency design, migration plan, executive narrative, and technical deep dive.
- [ ] Run architecture, security, failure-recovery, and stakeholder-review exercises.

**Required delivery sequence:** [CAP-001 plan](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/23) → [CAP-004 build/deploy](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/48) → [CAP-002 recovery/review](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/24) → [CAP-003 presentations](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/25). [ARCH-004](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/50) starts with the Phase 1 evidence reassessment and follows decisions through integration.

- [ ] Restore accepted data and control-plane state consistently, measure RTO/RPO, and rehearse migration/cutover with rollback or forward recovery.
- [ ] Publish dated pricing assumptions and a measured manual-versus-agent diagnosis comparison, separating estimates and allocated costs from realized savings.

Exit evidence: clean-environment deployment, integration manifest, end-to-end tests, restoration/cutover evidence, architecture pack, dated cost/value analysis, demo, executive briefing, engineering handoff, and retrospective.

## Optional advanced extensions

[FAB-005 CDC and deletes](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/52), [FAB-006 Spark/Delta tuning](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/53), and [FIN-001 shared-capacity FinOps](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) provide additional evidence across scenarios. They are P2 extensions associated with the capstone horizon, not core epic exit gates or prerequisites for #13. Replan them if capacity or workload constraints require a later horizon.

See the [September 2026 learning-gap review](tracking/LEARNING_GAP_REVIEW_2026-09.md) for complete recommendation coverage and dependency details.

## Ongoing cadence

- Weekly: ship one evidence-producing increment.
- Monthly: update progress and reassess affected competencies.
- Quarterly: conduct an architecture review and reprioritize the backlog.
- At every milestone: publish a short retrospective covering outcomes, evidence, gaps, and next decisions.
