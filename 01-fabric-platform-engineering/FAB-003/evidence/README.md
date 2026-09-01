# FAB-003 evidence

This folder contains and will continue to collect sanitized, reproducible evidence for reconciliation, quality decisions, quarantine behavior, and watermark protection.

## Current evidence

- [local contract-test output](local-contract-test-results.json): 30 tests passed with no failures or errors;
- [GitHub Actions run 33462357520](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33462357520): 30 tests passed and sanitized evidence was retained as a workflow artifact.

## Planned live evidence

- failure-injection and replay results;
- live Fabric validation checkpoint;
- sanitized operational quality-result examples;
- final acceptance matrix and retrospective links.

## Sanitization

Do not commit credentials, endpoints, workspace or item identifiers, connection values, patient data, proprietary schemas, or raw source/quarantine payloads. Use stable synthetic keys and hashes where correlation evidence is required.
