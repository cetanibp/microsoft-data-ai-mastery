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

**Status:** In progress  
Target: October–December 2026

- [x] Build metadata-driven ingestion with incremental processing, restartability, schema-drift handling, reconciliation, and reprocessing.
- [x] Implement the initial governed CI/CD and environment-promotion foundation through OPS-001.
- [x] Add tested operational observability and automated quality gates beyond deployment validation.
- [x] Benchmark performance and document capacity/cost tradeoffs.

Exit evidence: a repeatable framework, failure-injection tests, operational dashboard, runbook, ADRs, and benchmark report.

**Progress to date:** OPS-001 established governed Fabric delivery and supported acceptance of ADR-002. FAB-001 through FAB-003 completed the versioned control plane, resilient ingestion runtime, reconciliation, quality gates, quarantine, and recovery evidence. OPS-002 added measurable SLOs, correlated operational telemetry, deterministic simulated routing, runbooks, and a live stale-candidate recovery exercise. FAB-004 completed reproducible steady, peak, and replay benchmarking and selected bounded parallelism `PAR4` with quantified runtime, queue, CU, correctness, throttling, cost-allocation, and limitation evidence. [#11 — real-time operational monitoring](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/11) is now the final planned Phase 1 work item.

## Phase 2 — Production AI and agent engineering

**Status:** Not started  
Target: January–March 2027

- [ ] Build a grounded AI application with retrieval, tool calling, evaluation, tracing, and safety controls.
- [ ] Implement a Data Operations Agent that diagnoses pipeline failures using telemetry and lineage.
- [ ] Add human approval, identity boundaries, adversarial tests, and measurable quality targets.

Exit evidence: eval suite, trace samples, threat model, deployment architecture, operating runbook, and demo.

## Phase 3 — AI-ready data, governance, and data products

**Status:** Not started  
Target: April–June 2027

- [ ] Design governed semantic and metadata layers for safe AI consumption.
- [ ] Implement lineage-aware discovery and policy enforcement.
- [ ] Publish reusable data products through documented APIs or GraphQL.
- [ ] Demonstrate security, privacy, data quality, and responsible-AI controls.

Exit evidence: data contracts, policy matrix, lineage views, API specifications, quality SLOs, and governance playbook.

## Phase 4 — Enterprise architecture and capstone

**Status:** Not started  
Target: July–September 2027

- [ ] Integrate Fabric, AI, agents, governance, observability, and APIs into one enterprise reference solution.
- [ ] Produce cost and capacity models, resiliency design, migration plan, executive narrative, and technical deep dive.
- [ ] Run architecture, security, failure-recovery, and stakeholder-review exercises.

Exit evidence: deployable capstone, architecture pack, demo, executive briefing, engineering handoff, and retrospective.

## Ongoing cadence

- Weekly: ship one evidence-producing increment.
- Monthly: update progress and reassess affected competencies.
- Quarterly: conduct an architecture review and reprioritize the backlog.
- At every milestone: publish a short retrospective covering outcomes, evidence, gaps, and next decisions.
