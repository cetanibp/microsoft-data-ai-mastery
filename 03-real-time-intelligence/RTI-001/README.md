# RTI-001 — Real-time operational monitoring

RTI-001 implements an end-to-end Microsoft Fabric Real-Time Intelligence path for Northstar operational events. It ingests execution telemetry through an Eventstream, validates and deduplicates events in an Eventhouse, detects actionable conditions with Activator, and presents current state plus recent history in a Real-Time Dashboard.

## Status

Complete in the Development workspace on F256. Live validation proved normal ingestion, low-latency actionable-condition detection, dashboard visualization, and deliberate late, duplicate, malformed, and out-of-order event handling.

## Implemented items

| Item | Fabric name | Purpose |
|---|---|---|
| Eventstream | `es_northstar_operational_events` | Accept custom-endpoint JSON events and route them to the Eventhouse |
| Eventhouse | `eh_northstar_operations` | Host the operational KQL database |
| KQL database | `kqldb_northstar_operations` | Store raw events and expose validated, accepted, and current-state functions |
| Notebook | `nb_rti001_event_generator` | Generate sample, edge-case, and alert-test events without storing credentials |
| KQL queryset | `qs_northstar_operational_monitoring` | Detect recent actionable failures and expose alert context |
| Activator | `act_northstar_operational_alerts` | Evaluate every 60 seconds and notify on each actionable event |
| Real-Time Dashboard | `rtd_northstar_operational_monitoring` | Visualize object-run state, actionable conditions, latency, and recent events |

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| Representative events, schema, and retention | PASS | Versioned 20-field contract; 30-day retention and 7-day hot cache |
| Low-latency operational detection | PASS | Query detection in 59 seconds; final notification evidence in 79 seconds |
| Current state and recent history | PASS | Four-tile live dashboard with 24-hour operational history |
| Late, duplicate, malformed, and out-of-order tests | PASS | All four edge conditions produced the expected behavior |

## Design guarantees

- `EventId` is the logical event identity; accepted duplicates collapse to the newest ingested physical record.
- `ObjectRunId` and `SequenceNumber` determine current object-run state, so arrival order does not override logical order.
- Contract-invalid rows remain observable through `OperationalEventValidated()` with a rejection reason.
- Events more than five minutes behind ingestion time are marked late but remain accepted when otherwise valid.
- Actionable detection covers `FAILED`, `QUALITY_BLOCKED`, and `RECOVERY_REQUIRED`, plus `ERROR` or `CRITICAL` severity.
- The Eventstream connection string is retrieved at runtime from Azure Key Vault and is not committed.

## Repository contents

| Path | Purpose |
|---|---|
| [architecture.md](architecture.md) | Components, data flow, state logic, and security boundary |
| [event-contract.md](event-contract.md) | Versioned schema and validation semantics |
| [workspace](workspace/README.md) | Fabric-generated item definitions |
| [evidence](evidence/README.md) | Sanitized live results and screenshots |
| [tests](tests/README.md) | Dependency-free contract checks |
| [RETRO.md](RETRO.md) | Lessons, decisions, limitations, and follow-up |

## Local validation

From the repository root:

```bash
python 03-real-time-intelligence/RTI-001/tests/run_contract_tests.py \
  --output 03-real-time-intelligence/RTI-001/evidence/local-contract-test-results.json
```

