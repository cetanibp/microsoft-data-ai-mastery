# FAB-002 evidence index

## Current evidence

| Evidence | Purpose | Status |
|---|---|---|
| `ci-contract-test-results.json` workflow artifact | Credential-free runtime safety contract | Passed on feature branch |
| [Live Fabric checkpoint](live-fabric-checkpoint.md) | Sanitized Lakehouse binding, baseline, and replay results | Baseline and replay passed |
| Live configuration resolution | Prove FAB-001 release/object resolution | Passed for Development release `1.0.0` |
| Live successful incremental load | Prove extraction, target publication, and watermark commit | Passed end to end through the Fabric pipeline |
| Live intentional failure and replay | Prove state preservation and idempotent recovery | Notebook failures and replay passed; transactional pipeline pending |
| Live schema drift routes | Prove blocking and quarantine behavior | Notebook routes and additive replay passed |
| Live telemetry trace | Prove counts, duration, status, and correlation continuity | Durable successful pipeline trace passed; failure trace pending |

Generated local and CI result JSON files are intentionally ignored. CI uploads them as retained workflow artifacts so transient run identity does not create repository churn.

## Sanitization rules

Evidence may contain:

- synthetic object and field names;
- counts, timings, statuses, hashes, and opaque correlation IDs;
- metadata release versions and Git commit identifiers.

Evidence must not contain:

- credentials, tokens, connection strings, or secret values;
- tenant, workspace, Fabric item, or physical endpoint identifiers;
- real patient, employee, financial, or organizational data;
- source or rejected-row payload samples.
