# FAB-002 evidence index

## Current evidence

| Evidence | Purpose | Status |
|---|---|---|
| `ci-contract-test-results.json` workflow artifact | Credential-free runtime safety contract | Pending first branch run |
| Live configuration resolution | Prove FAB-001 release/object resolution | Planned |
| Live successful incremental load | Prove extraction, target publication, and watermark commit | Planned |
| Live intentional failure and replay | Prove state preservation and idempotent recovery | Planned |
| Live schema drift routes | Prove blocking and quarantine behavior | Planned |
| Live telemetry trace | Prove counts, duration, status, and correlation continuity | Planned |

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
