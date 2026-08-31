# FAB-003 — Reconciliation and data-quality gates

FAB-003 adds policy-driven acceptance checks between FAB-002 target publication and watermark commit.

## Status

In progress. The initial design is being established on issue [#7](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/7).

## Objective

Prove that every ingested object can be reconciled, evaluated against versioned quality policies, quarantined when necessary, and either accepted or blocked without losing run identity or incorrectly advancing mutable state.

## Binding upstream contracts

- [FAB-001 control-plane metadata model](../FAB-001/README.md)
- [FAB-002 resilient incremental-ingestion runtime](../FAB-002/README.md)
- [OPS-001 governed delivery foundation](../../02-dataops-devops/OPS-001/README.md)

FAB-003 reuses the activated `QualityPolicy` and `ObjectQualityPolicy` definitions, `run_id` and `object_run_id`, fixed input boundaries, and compare-and-commit watermark protocol. It does not create a competing metadata or execution model.

## Initial vertical slice

The first implementation targets the synthetic `ingest-clinical-encounter` object and will:

1. reconcile source, accepted, rejected, and target counts;
2. evaluate allowlisted aggregate checks;
3. apply `BLOCK` or `WARN` enforcement from the activated policy;
4. quarantine invalid rows with reason codes and run correlation;
5. prevent watermark commit when a required blocking check fails;
6. publish sanitized check results for operational review;
7. prove the contract with credential-free tests before live Fabric validation.

## Issue acceptance criteria

| Criterion | Planned evidence | Status |
|---|---|---|
| Source-to-target count and aggregate checks | Executable quality evaluator and test suite | Planned |
| Blocking versus warning thresholds | Versioned policy evaluation and decision tests | Planned |
| Quarantine with traceability | Synthetic quarantine records correlated to run and object run | Planned |
| Operational quality results | Sanitized result contract and reporting projection | Planned |

## Repository contents

| Path | Purpose |
|---|---|
| [architecture.md](architecture.md) | Boundaries, invariants, decision flow, and evidence contract |
| [runtime](runtime/README.md) | Planned credential-free executable contract |
| [tests](tests/README.md) | Planned acceptance, threshold, quarantine, and recovery scenarios |
| [evidence](evidence/README.md) | Evidence index and sanitization rules |

## Safety boundary

Repository evidence uses only synthetic Northstar data. It must not include credentials, endpoints, workspace or item identifiers, patient data, proprietary metadata, or source payload samples.
