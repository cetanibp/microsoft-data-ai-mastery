# OPS-002 tests

Run from the repository root:

```bash
python 02-dataops-devops/OPS-002/tests/run_contract_tests.py \
  --output 02-dataops-devops/OPS-002/evidence/local-contract-test-results.json
```

The suite validates the credential-free SLO and routing behavior plus the deployable Fabric SQL Database tables, views, procedures, constraints, evidence hashing, idempotency, environment boundaries, and secret-safe routing aliases.
