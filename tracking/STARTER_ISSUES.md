# Starter Issues

These items are ready to create as GitHub Issues. IDs are stable planning identifiers, independent of GitHub issue numbers.

## Foundation & Baseline

### ARCH-001 — Define the enterprise reference scenario

Labels: `area:enterprise-architecture`, `type:design`, `priority:p0`, `effort:M`

- [ ] Define business problem, users, data domains, scale, and regulatory assumptions.
- [ ] Define availability, recovery, latency, quality, security, and cost requirements.
- [ ] Publish a context diagram and glossary.
- [ ] Record assumptions and unresolved questions.

### ARCH-002 — Complete the baseline skills assessment

Labels: `area:enterprise-architecture`, `type:assessment`, `priority:p0`, `effort:S`

- [ ] Score every competency in `SKILLS.md`.
- [ ] Link evidence for every score of 3 or higher.
- [ ] Identify the five highest-value gaps.
- [ ] Convert gaps into prioritized work items.

### ARCH-003 — Establish architecture decision records and review checklist

Labels: `area:enterprise-architecture`, `type:documentation`, `priority:p1`, `effort:S`

- [ ] Add an ADR template and initial decisions.
- [ ] Cover security, reliability, operations, performance, cost, governance, and maintainability.
- [ ] Apply the checklist to the reference scenario.

## Fabric Platform & DataOps

### EPIC-FAB-001 — Production-grade metadata-driven Fabric ingestion

Labels: `area:fabric`, `area:dataops`, `type:epic`, `priority:p0`, `effort:XL`

Required evidence: architecture, metadata model, implementation, automated tests, failure-injection results, telemetry dashboard, runbook, and retrospective.

### FAB-001 — Design the ingestion control-plane metadata model

Labels: `area:fabric`, `type:design`, `priority:p0`, `effort:M`

- [ ] Model sources, objects, dependencies, load strategies, watermarks, schedules, and SLAs.
- [ ] Support environment-specific configuration without code changes.
- [ ] Document versioning, secrets boundaries, and operational ownership.

### FAB-002 — Implement resilient incremental ingestion

Labels: `area:fabric`, `type:build`, `priority:p0`, `effort:L`

- [ ] Support watermark-based incremental loading.
- [ ] Handle restart, duplicate records, and idempotent reprocessing.
- [ ] Detect and route schema changes.
- [ ] Capture row counts, duration, status, and correlation identifiers.
- [ ] Pass intentional failure and recovery tests.

### FAB-003 — Add reconciliation and data-quality gates

Labels: `area:fabric`, `area:dataops`, `type:build`, `priority:p1`, `effort:M`

- [ ] Implement source-to-target count and aggregate checks.
- [ ] Define blocking versus warning thresholds.
- [ ] Quarantine invalid data and preserve traceability.
- [ ] Publish quality results for operational review.

### OPS-001 — Build CI/CD and environment promotion

Labels: `area:dataops`, `type:build`, `priority:p0`, `effort:L`

- [ ] Separate code, configuration, and secrets.
- [ ] Add automated validation and deployment checks.
- [ ] Demonstrate dev-to-test promotion and rollback.
- [ ] Document branching, approvals, and release evidence.

### OPS-002 — Define SLOs, observability, and incident response

Labels: `area:dataops`, `type:design`, `priority:p1`, `effort:M`

- [ ] Define freshness, reliability, duration, and quality SLOs.
- [ ] Create operational telemetry and alert routing.
- [ ] Write triage, replay, escalation, and recovery runbooks.
- [ ] Run and document a failure-recovery exercise.

### FAB-004 — Benchmark performance, capacity, and cost

Labels: `area:fabric`, `type:assessment`, `priority:p1`, `effort:M`

- [ ] Define representative workloads and test data volumes.
- [ ] Measure runtime, concurrency, resource use, and cost drivers.
- [ ] Compare at least two design alternatives.
- [ ] Publish optimization decisions and limitations.

### RTI-001 — Implement a real-time operational monitoring scenario

Labels: `area:real-time`, `type:build`, `priority:p2`, `effort:L`

- [ ] Ingest representative events with documented schema and retention.
- [ ] Detect an operational condition with low-latency alerting.
- [ ] Visualize current state and recent history.
- [ ] Test late, duplicate, malformed, and out-of-order events.

## AI & Agent Engineering

### EPIC-AI-001 — Production-grade Data Operations Agent

Labels: `area:foundry`, `area:agents`, `type:epic`, `priority:p0`, `effort:XL`

Required evidence: tool contracts, grounded knowledge, eval suite, traces, security model, approval workflow, deployment architecture, runbook, and demo.

### AI-001 — Build a grounded retrieval baseline

Labels: `area:foundry`, `type:build`, `priority:p0`, `effort:L`

- [ ] Define an approved knowledge corpus and freshness process.
- [ ] Implement retrieval with citations and access boundaries.
- [ ] Create a representative evaluation dataset.
- [ ] Measure groundedness, relevance, and failure modes.

### AGENT-001 — Design safe operational tool contracts

Labels: `area:agents`, `area:governance-security`, `type:design`, `priority:p0`, `effort:M`

- [ ] Define read-only diagnostic tools before write-capable tools.
- [ ] Specify inputs, outputs, validation, identity, audit, and error behavior.
- [ ] Threat-model prompt injection, excessive agency, and data leakage.
- [ ] Define approval requirements for consequential actions.

### AGENT-002 — Implement pipeline-failure diagnosis

Labels: `area:agents`, `type:build`, `priority:p0`, `effort:L`

- [ ] Correlate pipeline status, logs, lineage, configuration, and history.
- [ ] Produce ranked hypotheses with supporting evidence.
- [ ] Recommend bounded recovery actions.
- [ ] Test known, ambiguous, and novel failure cases.

### AGENT-003 — Add evaluations, tracing, and regression gates

Labels: `area:agents`, `area:dataops`, `type:build`, `priority:p0`, `effort:L`

- [ ] Define quality, safety, latency, and cost metrics.
- [ ] Add offline and scenario-based evaluations.
- [ ] Capture traces without leaking secrets or sensitive data.
- [ ] Fail deployment when critical regression thresholds are exceeded.

### AGENT-004 — Implement human approval and least privilege

Labels: `area:agents`, `area:governance-security`, `type:build`, `priority:p1`, `effort:M`

- [ ] Separate diagnostic, recommendation, and execution permissions.
- [ ] Require approval for consequential actions.
- [ ] Record actor, rationale, evidence, decision, and result.
- [ ] Test denied, expired, replayed, and out-of-scope requests.

## AI-Ready Data & Governance

### EPIC-DATA-001 — Governed AI-ready data products

Labels: `area:ai-ready-data`, `area:governance-security`, `area:data-products-apis`, `type:epic`, `priority:p1`, `effort:XL`

Required evidence: contracts, semantic metadata, lineage, policy matrix, API specification, quality SLOs, security tests, and consumer guide.

### DATA-001 — Define an AI-ready semantic and metadata layer

Labels: `area:ai-ready-data`, `type:design`, `priority:p1`, `effort:L`

- [ ] Define business concepts, measures, synonyms, ownership, freshness, and quality signals.
- [ ] Document how agents discover and interpret governed data.
- [ ] Test ambiguous terminology and conflicting definitions.

### GOV-001 — Implement lineage-aware access and governance controls

Labels: `area:governance-security`, `type:build`, `priority:p1`, `effort:L`

- [ ] Map identities, roles, data classifications, and policy decisions.
- [ ] Demonstrate lineage from source through AI response or API output.
- [ ] Test unauthorized access and sensitive-data handling.
- [ ] Document audit and exception processes.

### API-001 — Publish a governed data product API

Labels: `area:data-products-apis`, `type:build`, `priority:p1`, `effort:L`

- [ ] Define a versioned data contract and consumer SLOs.
- [ ] Implement authentication, authorization, validation, and throttling.
- [ ] Add contract, error, and performance tests.
- [ ] Publish consumer documentation and change policy.

## Enterprise Capstone

### EPIC-CAP-001 — Integrated enterprise Data + AI platform capstone

Labels: `area:capstone`, `area:enterprise-architecture`, `type:epic`, `priority:p0`, `effort:XL`

Required evidence: deployable reference solution, architecture pack, ADRs, security and governance model, capacity/cost model, resiliency exercise, executive briefing, technical walkthrough, and retrospective.

### CAP-001 — Produce the capstone architecture and delivery plan

Labels: `area:capstone`, `area:enterprise-architecture`, `type:design`, `priority:p1`, `effort:L`

- [ ] Define target architecture, increments, dependencies, risks, and decision gates.
- [ ] Include identity, networking, data, AI, integration, observability, governance, and operations.
- [ ] Estimate capacity, cost, recovery objectives, and delivery effort.

### CAP-002 — Run an architecture review and failure-recovery exercise

Labels: `area:capstone`, `type:assessment`, `priority:p1`, `effort:M`

- [ ] Review against nonfunctional requirements and the architecture checklist.
- [ ] Inject at least three representative failures.
- [ ] Measure detection and recovery outcomes.
- [ ] Record gaps, decisions, and remediation work.

### CAP-003 — Deliver executive and engineering presentations

Labels: `area:capstone`, `area:enterprise-architecture`, `type:documentation`, `priority:p1`, `effort:M`

- [ ] Create a 10-minute executive narrative focused on outcomes, risk, and investment.
- [ ] Create a 30-minute technical walkthrough focused on design and evidence.
- [ ] Capture questions, feedback, and revisions from a practice review.

