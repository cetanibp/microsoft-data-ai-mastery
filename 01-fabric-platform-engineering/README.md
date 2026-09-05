# Fabric Platform Engineering

Store ingestion frameworks, Spark/Delta patterns, performance experiments, capacity analysis, and platform architecture evidence here.

## Work items

- [FAB-001 — Ingestion control-plane metadata model](FAB-001/README.md) — completed design, Fabric SQL Database package, contract tests, live validation, governance guidance, and downstream handoff.
- [FAB-002 — Resilient incremental ingestion](FAB-002/README.md) — completed shared runtime with transactional watermarks, idempotent replay, schema-drift routing, correlated telemetry, and live failure, recovery, and concurrency evidence.
- [FAB-003 — Reconciliation and data-quality gates](FAB-003/README.md) — completed policy-driven reconciliation, blocking and warning decisions, deterministic quarantine, watermark protection, recovery replay, and operational evidence.
- [FAB-004 — Performance, capacity, and cost benchmarking](FAB-004/README.md) — completed reproducible F256 smoke, steady, 80-million-row peak, and replay benchmarks; selected bounded parallelism `PAR4` with quantified elapsed-time, queue, CU, correctness, throttling, cost-allocation, and limitation evidence.

## Planned work — September 5, 2026

Preserve completed FAB-001 through FAB-004 evidence. DATA-002 supplies the analytical serving/model layer; FAB-005/FAB-006/FIN-001 are optional advanced capstone extensions.

| Issue | Outcome | Scope |
|---|---|---|
| [#46](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/46) | DATA-002 — Build an analytical data product and tested semantic model | Required planned work |
| [#52](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/52) | FAB-005 — Extend ingestion with CDC, deletes, and source evolution | Optional P2 extension |
| [#53](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/53) | FAB-006 — Tune Spark and Delta layouts across a second workload | Optional P2 extension |
| [#54](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/54) | FIN-001 — Measure shared-capacity contention and operational FinOps | Optional P2 extension |

Implementation evidence will be added under each planning ID as work is completed. These links represent backlog scope, not completed capability. See the [learning-gap review](../tracking/LEARNING_GAP_REVIEW_2026-09.md) for dependencies and evidence expectations.
