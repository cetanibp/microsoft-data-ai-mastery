# RTI-001 retrospective

## Outcome

RTI-001 established the repository's first end-to-end Fabric Real-Time Intelligence implementation. The solution connects event production, streaming ingestion, contract validation, deduplication, ordered current state, low-latency detection, notification, and live visualization.

## What worked

- A small versioned event contract carried the run, object-run, correlation, quality, error, duration, queue, and row-count context needed by operations.
- Query-time validation preserved malformed evidence without allowing it into accepted or current-state projections.
- Event identity and object-run sequence solved different problems cleanly: `EventId` handled retry duplicates while `SequenceNumber` handled out-of-order state.
- The two-minute query window combined with 60-second Activator evaluation produced notification within 79 seconds in the live test.
- A single dashboard combined present state, alert volume, latency trend, and detailed recent history.
- Key Vault retrieval kept the Eventstream connection string out of notebook source and Git history.

## What changed

- Interactive `getpass` did not prompt reliably in the Fabric PySpark notebook, so secret handling moved to Azure Key Vault.
- The first KQL count query referenced `TotalRowCount` after an aggregation that did not define it; the query was corrected to use explicit summarized measures.
- Dashboard query text was re-entered after a malformed formatting transfer caused a KQL syntax error.
- The Activator created from the trigger pane inherited the default name `My activator`; it was renamed to `act_northstar_operational_alerts` before completion.
- Activator was stopped after validation to prevent repeated synthetic notifications.

## Decisions and limitations

- Use query-time validation and deduplication for this exercise because it keeps the raw stream observable and the behavior easy to review. Higher sustained scale may justify update policies or materialized views.
- Retain operational data for 30 days with 7 days hot. Compliance or long-term incident evidence requires a separate governed archive.
- The implementation proves one F256 Development workspace and one synthetic workload shape; it does not establish multi-region recovery, sustained throughput limits, or production notification ownership.
- The `OperationalEventRejected` table is provisioned for future physical quarantine, while current contract-invalid evidence remains queryable in `OperationalEventRaw` through `OperationalEventValidated()`.

## Follow-up

- Connect FAB-002 through FAB-004 producers to the shared event contract.
- Move alert recipients and escalation policy into governed environment configuration.
- Add sustained-load and failure-injection tests before production use.
- Evaluate update policies or materialized views when event volume makes query-time projection materially expensive.

