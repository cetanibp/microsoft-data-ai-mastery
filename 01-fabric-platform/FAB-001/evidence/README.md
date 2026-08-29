# FAB-001 evidence

## Automated contract validation

The `FAB-001 metadata contract` GitHub Actions workflow runs the credential-free test suite on relevant pull requests and branch changes. Each run uploads a sanitized `ci-contract-test-results.json` artifact containing:

- contract and version;
- PASS or FAIL status;
- test, failure, error, and skipped counts;
- commit SHA and workflow run identifier;
- validation timestamp;
- bounded failure details when applicable.

Generated result files are intentionally ignored by Git. Durable evidence will retain the workflow URL, commit SHA, test count, result, and artifact digest without committing transient run output or credentials.

## Evidence status

| Evidence | Status |
|---|---|
| Local metadata-contract suite | Passed during implementation; superseded by the linked CI run after commit |
| Pull-request workflow | Pending branch commit |
| Fabric SQL Database deployment and execution | Pending live validation |
| Invalid metadata failure injection | Implemented in the automated suite |
| Watermark failure, commit, and concurrency simulation | Implemented in the automated suite |
