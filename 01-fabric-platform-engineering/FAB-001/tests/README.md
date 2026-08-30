# FAB-001 metadata-contract tests

The test suite is credential-free and uses only Python's standard library. It validates the committed SQL package, the machine-readable Northstar metadata fixture, semantic failure paths, environment resolution, and the watermark state-transition contract.

## Run locally

From the repository root:

```bash
python 01-fabric-platform-engineering/FAB-001/tests/run_contract_tests.py \
  --output 01-fabric-platform-engineering/FAB-001/evidence/local-contract-test-results.json
```

The generated report contains test counts, status, commit and workflow identifiers when available, and sanitized failure details. It never contains connection values beyond the synthetic logical aliases in the fixture.

## Validation categories

- Baseline release and Development/Test/Production resolution
- Duplicate and unresolved stable identifiers
- Missing environment configuration
- Disabled source with enabled object
- Secret-like configuration values
- Strategy and watermark compatibility
- Parameter allowlisting and type validation
- Production SLO and ownership requirements
- Self-dependencies and multi-object cycles
- SQL table, foreign-key, constraint, view, seed, and secret-boundary structure
- Watermark proposal, abandonment, successful commit, duplicate commit, and stale-candidate rejection

These tests do not replace live deployment and transaction tests against SQL Database in Microsoft Fabric. They provide a fast pull-request gate before any Fabric resource or credential is required.
