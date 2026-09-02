# FAB-003 — Reconciliation and data-quality gates

FAB-003 adds policy-driven acceptance checks between FAB-002 target publication and watermark commit.

## Status

In progress. The architecture, credential-free executable contract, durable SQL control-plane extension, Fabric quality-gate notebook, and live quality-enabled pipeline are implemented. Thirty-three automated tests cover policy validation, reconciliation, decisions, quarantine, replay, transactional evidence, completion gating, deployable artifact structure, and secret boundaries. Live accepted, blocked, watermark-preservation, recovery-replay, hashed quarantine, and same-object-run idempotency paths passed. Governed live warning validation and final evidence remain open.

## Objective

Prove that every ingested object can be reconciled, evaluated against versioned quality policies, quarantined when necessary, and either accepted or blocked without losing run identity or incorrectly advancing mutable state.

## Binding upstream contracts

- [FAB-001 control-plane metadata model](../FAB-001/README.md)
- [FAB-002 resilient incremental-ingestion runtime](../FAB-002/README.md)
- [OPS-001 governed delivery foundation](../../02-dataops-devops/OPS-001/README.md)

FAB-003 reuses the activated `QualityPolicy` and `ObjectQualityPolicy` definitions, `run_id` and `object_run_id`, fixed input boundaries, and compare-and-commit watermark protocol. It does not create a competing metadata or execution model.

## Initial vertical slice

The deployable vertical slice targets the synthetic `ingest-clinical-encounter` object and will:

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
| Source-to-target count and aggregate checks | Executable evaluator, Fabric notebook, and tests | Live accepted and blocked paths passed |
| Blocking versus warning thresholds | Versioned allowlisted contracts and decision tests | Live block passed; warning pending |
| Quarantine with traceability | Hashed, idempotent Delta and SQL evidence | Live quarantine and idempotent replay passed |
| Operational quality results | Durable tables and operational SQL view | Accepted and blocked results verified live |

## Repository contents

| Path | Purpose |
|---|---|
| [architecture.md](architecture.md) | Boundaries, invariants, decision flow, and evidence contract |
| [runtime](runtime/README.md) | Credential-free executable contract |
| [workspace](workspace/README.md) | Fabric notebook and pipeline integration contract |
| [tests](tests/README.md) | Acceptance, threshold, quarantine, replay, state-protection, and deployable-artifact scenarios |
| [evidence](evidence/README.md) | Evidence index and sanitization rules |

## Safety boundary

Repository evidence uses only synthetic Northstar data. It must not include credentials, endpoints, workspace or item identifiers, patient data, proprietary metadata, or source payload samples.

## Local validation

From the repository root:

```bash
python 01-fabric-platform-engineering/FAB-003/tests/run_contract_tests.py \\
  --output 01-fabric-platform-engineering/FAB-003/evidence/local-contract-test-results.json
```
