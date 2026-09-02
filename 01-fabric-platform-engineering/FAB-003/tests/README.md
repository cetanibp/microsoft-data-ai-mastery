# FAB-003 validation scenarios

The automated contract suite covers:

1. balanced counts pass;
2. count variance within a warning threshold;
3. blocking count variance prevents acceptance;
4. aggregate tolerance boundary behavior;
5. invalid rows receive deterministic quarantine reason codes;
6. required-check execution error blocks acceptance;
7. warning-only outcomes remain eligible for watermark commit;
8. blocking outcomes preserve committed watermark state;
9. replay does not duplicate results or quarantine evidence;
10. every result retains release, run, object-run, policy, and boundary correlation;
11. SQL tables, constraints, procedures, and the operational view are present;
12. quality and quarantine writes preserve deterministic idempotent identities;
13. completion requires a durable accepted quality decision;
14. the Fabric notebook contains only allowlisted contracts and no physical or secret values;
15. controlled failure injection is restricted to Development;
16. FAB-002 emits hashed duplicate identities rather than raw payload values;
17. the Fabric-generated quality pipeline is a deployable item;
18. quality decision and accepted-wrapper activities precede watermark completion;
19. generated pipeline workspace identifiers are sanitized.

Tests must use only synthetic data and must require no Fabric resource, endpoint, secret, or external package.

Run the suite from the repository root:

```bash
python 01-fabric-platform-engineering/FAB-003/tests/run_contract_tests.py \\
  --output 01-fabric-platform-engineering/FAB-003/evidence/local-contract-test-results.json
```
