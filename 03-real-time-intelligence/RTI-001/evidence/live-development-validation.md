# RTI-001 live Development validation

## Environment

| Property | Value |
|---|---|
| Validation date | 2026-09-05 UTC |
| Fabric capacity | F256 |
| Workspace | `Northstar Data Platform - RTI-001` |
| Data classification | Synthetic operational telemetry |

## Representative ingestion

Event `36f503cc-ba88-4df7-b5c7-2067c297ac62` was emitted at `2026-09-04T23:01:34.3318950Z` and ingested at `2026-09-04T23:02:29.6698055Z`. The initial end-to-end ingestion latency was 55 seconds and the event retained the expected `OBJECT_RUN_COMPLETED` / `SUCCEEDED` values.

## Edge-case batch

Correlation ID: `RTI-001-EDGE-59c1ee68-35f1-4791-ad1a-a5fcaa1f6108`

| Assertion | Expected | Observed | Status |
|---|---:|---:|---|
| Physical events | 7 | 7 | PASS |
| Logical accepted events | 5 | 5 | PASS |
| Rejected events | 1 | 1 | PASS |
| Late events | 1 | 1 | PASS |
| Duplicate physical copies | 2 | 2 | PASS |

For out-of-order object run `de8e5c95-bb57-42a3-a5b4-4ec5c33655cb`, the current-state function selected sequence 2 with `FAILED` / `STATUS_CHANGED`, even though it arrived before sequence 1. Status: PASS.

## Actionable-query detection

Event `7b0e46d1-c179-42ce-962f-ac756a49cf2f` used correlation ID `RTI-001-ALERT-6f36c54d-ea06-4a10-8606-c2669d18a550` and status `QUALITY_BLOCKED`. It was emitted at `2026-09-05T01:43:38.8286220Z`, ingested at `2026-09-05T01:43:40.2023278Z`, and detected at `2026-09-05T01:44:37.2887663Z`.

| Measure | Result |
|---|---:|
| Ingestion latency | 2 seconds |
| Query detection latency | 59 seconds |
| Alert threshold | Within the 2-minute actionable window |
| Status | PASS |

## Activator notification

The final notification test used event `110a9d78-bc22-4117-abfa-8ace987e040c` and correlation ID `RTI-001-ALERT-9180e01e-a7d8-439f-812a-9cb0a7f5334d`. The event was emitted at `2026-09-05T01:51:32Z`, ingested at `01:51:35Z`, and activated at `01:52:51Z`, for 79 seconds from emission to notification. The message included the required event, correlation, pipeline, object, status, severity, error-classification, emission, ingestion, and detection-latency fields. Status: PASS.

## Dashboard

The saved 24-hour dashboard showed:

- current object-run distribution across `RUNNING`, `FAILED`, `QUALITY_BLOCKED`, and `SUCCEEDED`;
- four active actionable conditions;
- maximum, P50, and P95 ingestion latency over time; and
- recent accepted and rejected events with actionable rows highlighted.

The committed screenshot confirms the dashboard was saved successfully. Status: PASS.

