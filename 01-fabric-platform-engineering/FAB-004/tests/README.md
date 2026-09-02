# FAB-004 contract tests

The tests validate that the committed benchmark manifest remains aligned with the approved F256 experimental contract.

Coverage includes:

1. synthetic-only data classification;
2. F256 capacity declaration without committed pricing;
3. `SEQ1` and `PAR4` alternatives;
4. smoke, standard, and large workload totals;
5. steady, peak, and replay paired repetitions;
6. alternating pair order;
7. required runtime, capacity, cost-driver, and correctness metrics;
8. decision and capacity-review thresholds;
9. F256 allocated-cost calculation.

Run from the repository root:

```bash
python 01-fabric-platform-engineering/FAB-004/tests/run_contract_tests.py \
  --output 01-fabric-platform-engineering/FAB-004/evidence/local-contract-test-results.json
```
