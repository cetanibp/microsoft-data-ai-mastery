# RTI-001 operational-event contract

## Contract identity

| Property | Value |
|---|---|
| Schema version | `1.0.0` |
| Serialization | UTF-8 JSON |
| Logical event key | `EventId` |
| Object-state key | `ObjectRunId` + highest `SequenceNumber` |
| Time standard | UTC |

## Fields

| Field | KQL type | Required for acceptance | Meaning |
|---|---|---:|---|
| `EventId` | string | Yes | Stable logical event identity |
| `SchemaVersion` | string | Yes | Must equal `1.0.0` |
| `EventType` | string | Yes | Operational transition or observation type |
| `EventTimeUtc` | datetime | Yes | Time the represented event occurred |
| `EmittedAtUtc` | datetime | No | Time the producer emitted the message |
| `SequenceNumber` | long | Yes | Positive ordering value within an object run |
| `Environment` | string | Yes | Environment boundary such as `development` |
| `PipelineName` | string | No | Producing pipeline |
| `ObjectName` | string | No | Governed workload object |
| `RunId` | string | No | Parent pipeline-run identity |
| `ObjectRunId` | string | No | Object-attempt identity |
| `CorrelationId` | string | No | Cross-component diagnostic identity |
| `Status` | string | No | Current or reported execution state |
| `Severity` | string | No | Informational or actionable severity |
| `ErrorClassification` | string | No | Stable failure classification |
| `AcceptedRowCount` | long | No | Accepted business rows |
| `RejectedRowCount` | long | No | Rejected or quarantined business rows |
| `ElapsedSeconds` | real | No | End-to-end workload duration |
| `MaximumWorkerQueueSeconds` | real | No | Maximum observed worker queue time |
| `Details` | dynamic | No | Extensible scenario-specific attributes |

## Validation order

The first matching failure becomes `RejectionReason`:

1. empty `EventId` → `MISSING_EVENT_ID`;
2. unsupported `SchemaVersion` → `UNSUPPORTED_SCHEMA_VERSION`;
3. empty `EventType` → `MISSING_EVENT_TYPE`;
4. null `EventTimeUtc` → `MISSING_EVENT_TIME`;
5. `SequenceNumber` less than 1 → `INVALID_SEQUENCE_NUMBER`;
6. empty `Environment` → `MISSING_ENVIRONMENT`.

Rows with no rejection reason receive `ValidationStatus="ACCEPTED"`; all others receive `REJECTED` and are excluded from accepted and current-state projections.

## Evolution rules

- Producers must continue emitting `1.0.0` until consumers explicitly support another version.
- Additive optional fields belong in `Details` before a physical schema change is justified.
- Breaking type, identity, or required-field changes require a new schema version and parallel consumer support.
- Retrying a logical event must reuse its `EventId`; a new business occurrence must use a new `EventId`.
- Sequence numbers must increase within an `ObjectRunId` and must not encode arrival time.

