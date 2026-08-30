# FAB-002 — Resilient incremental ingestion

FAB-002 implements the first shared ingestion runtime that consumes the FAB-001 control-plane contract.

## Status

In progress. The initial runtime architecture and credential-free executable contract are implemented. Fabric pipeline/notebook implementation, live failure injection, schema-drift routing, and final evidence remain outstanding.

## Issue acceptance criteria

| Criterion | Initial evidence | Status |
|---|---|---|
| Watermark-based incremental loading | Executable lower-exclusive, upper-inclusive extraction window and compare-and-commit state transition | Contract implemented |
| Restart, duplicate handling, and idempotent reprocessing | Crash-after-write replay test and business-key upsert contract | Contract implemented |
| Detect and route schema changes | Blocking and quarantine behavior defined in the architecture | Planned |
| Capture row counts, duration, status, and correlation identifiers | Run result and object-run evidence contract | Contract implemented |
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
