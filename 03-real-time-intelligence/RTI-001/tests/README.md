# RTI-001 contract tests

The dependency-free suite validates the committed Fabric definitions rather than calling a live tenant.

Coverage includes:

1. required raw and rejected tables;
2. 30-day retention and 7-day hot cache;
3. validation, deduplication, late-event, and highest-sequence functions;
4. custom-endpoint Eventstream routing to `OperationalEventRaw`;
5. Key Vault secret retrieval without a committed connection string;
6. actionable-query status, severity, lookback, and latency context;
7. 60-second Activator evaluation and rule identity;
8. four required dashboard tiles and their core query projections.

Run from the repository root:

```bash
python 03-real-time-intelligence/RTI-001/tests/run_contract_tests.py \
  --output 03-real-time-intelligence/RTI-001/evidence/local-contract-test-results.json
```

