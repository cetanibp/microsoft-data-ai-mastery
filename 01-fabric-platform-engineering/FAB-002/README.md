# FAB-002 — Resilient incremental ingestion

FAB-002 implements the first shared ingestion runtime that consumes the FAB-001 control-plane contract.

## Status

In progress. The runtime architecture, credential-free executable contract, transactional SQL state procedures, and Fabric encounter notebook are implemented. The FAB-002 Lakehouse is attached; notebook-level baseline, same-window replay, additive-drift routing, and breaking-drift blocking were exercised in Fabric. Additive-drift replay exposed a duplicate-evidence defect, and the notebook now merges that evidence by object-run identity. Live remediation validation, failure injection, pipeline configuration, transactional watermark integration, and final evidence remain outstanding.

## Issue acceptance criteria

| Criterion | Initial evidence | Status |
|---|---|---|
| Watermark-based incremental loading | Executable lower-exclusive, upper-inclusive extraction window and compare-and-commit state transition | Contract implemented |
| Restart, duplicate handling, and idempotent reprocessing | Crash-after-write replay test and business-key upsert contract | Contract implemented; live same-window replay passed |
| Detect and route schema changes | Notebook blocks missing required columns and writes schema-only additive-drift evidence before publishing the approved projection | Live routes exercised; additive replay remediation pending validation |
| Capture row counts, duration, status, and correlation identifiers | Run result and object-run evidence contract | Contract implemented; notebook result counts validated live |
| Pass intentional failure and recovery tests | Credential-free failure tests complete; live Fabric failure injection remains | In progress |

## First vertical slice

The first live implementation will use the synthetic `ingest-clinical-encounter` object from FAB-001 release `1.0.0`:

- resolve configuration from `ctrl.vw_ActiveIngestionConfiguration`;
- pin environment, release, object, run, object-run, and correlation identities;
- read a timestamp watermark using a lower-exclusive and upper-inclusive window;
- write by the declared encounter business key using idempotent upsert semantics;
- propose a watermark candidate before target publication;
- commit it only after accepted target results and a matching state version;
- abandon it on failure or route a stale commit to recovery;
- record extracted, accepted, rejected, and duplicate counts.

## Repository contents

| Path | Purpose |
|---|---|
| [architecture.md](architecture.md) | Runtime boundaries, invariants, execution flow, recovery cases, and live implementation plan |
| [runtime/incremental_ingestion.py](runtime/incremental_ingestion.py) | Credential-free executable reference contract |
| [Fabric workspace artifacts](workspace/README.md) | Parameterized encounter notebook and pipeline orchestration contract |
| [tests](tests/README.md) | Happy-path, replay, failure, duplicate, telemetry, and concurrency tests |
| [evidence](evidence/README.md) | Evidence index and sanitization rules |

## Contract boundary

The Python reference runtime is not the production Fabric ingestion engine. It makes the safety invariants executable before platform resources are involved. The Fabric implementation must preserve the tested behavior while replacing in-memory adapters with:

- FAB-001 SQL Database control-plane reads and state procedures;
- Fabric managed connections and Variable Library stage resolution;
- a synthetic source adapter;
- a Bronze Delta target;
- durable telemetry and quarantined drift evidence.

## Local validation

From the repository root:

```bash
python 01-fabric-platform-engineering/FAB-002/tests/run_contract_tests.py \
  --output 01-fabric-platform-engineering/FAB-002/evidence/local-contract-test-results.json
```

No credentials, endpoints, Fabric identifiers, patient data, or proprietary metadata are required.
