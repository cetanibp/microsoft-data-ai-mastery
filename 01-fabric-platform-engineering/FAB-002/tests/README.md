# FAB-002 ingestion-contract tests

This credential-free suite executes the safety contract that the Fabric implementation must preserve.

## Covered behavior

- lower-exclusive and upper-inclusive watermark extraction;
- successful compare-and-commit state advancement;
- empty-window behavior;
- deterministic in-window duplicate handling;
- idempotent target upsert;
- intentional failure after target writes;
- retry without duplicate accepted records;
- failed-attempt watermark preservation;
- stale-candidate rejection;
- correlation identity, boundary hash, counts, status, and duration evidence;
- sanitized missing-column failure.
- deployable SQL procedure structure and transaction boundaries;
- compare-and-commit and failure-state SQL predicates;
- Fabric notebook identity, parameter, window, deduplication, merge, drift, and sanitized-output contracts.

Live tests remain required because repository validation cannot prove Fabric SQL transaction behavior, Delta merge behavior, Lakehouse binding, or actual pipeline retry behavior.

## Run locally

From the repository root:

```bash
python 01-fabric-platform-engineering/FAB-002/tests/run_contract_tests.py \
  --output 01-fabric-platform-engineering/FAB-002/evidence/local-contract-test-results.json
```

The JSON report is ignored locally and retained as a GitHub Actions artifact. Failure details are bounded and contain no source payload values.
