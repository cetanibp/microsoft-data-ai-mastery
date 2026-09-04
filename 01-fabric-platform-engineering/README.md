# Fabric Platform Engineering

Store ingestion frameworks, Spark/Delta patterns, performance experiments, capacity analysis, and platform architecture evidence here.

## Work items

- [FAB-001 — Ingestion control-plane metadata model](FAB-001/README.md) — completed design, Fabric SQL Database package, contract tests, live validation, governance guidance, and downstream handoff.
- [FAB-002 — Resilient incremental ingestion](FAB-002/README.md) — completed shared runtime with transactional watermarks, idempotent replay, schema-drift routing, correlated telemetry, and live failure, recovery, and concurrency evidence.
- [FAB-003 — Reconciliation and data-quality gates](FAB-003/README.md) — completed policy-driven reconciliation, blocking and warning decisions, deterministic quarantine, watermark protection, recovery replay, and operational evidence.
- [FAB-004 — Performance, capacity, and cost benchmarking](FAB-004/README.md) — completed reproducible F256 smoke, steady, 80-million-row peak, and replay benchmarks; selected bounded parallelism `PAR4` with quantified elapsed-time, queue, CU, correctness, throttling, cost-allocation, and limitation evidence.
