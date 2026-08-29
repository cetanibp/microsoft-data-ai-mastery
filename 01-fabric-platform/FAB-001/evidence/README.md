# FAB-001 evidence

## Automated contract validation

The `FAB-001 metadata contract` GitHub Actions workflow runs the credential-free test suite on relevant pull requests and branch changes. Each run uploads a sanitized `ci-contract-test-results.json` artifact containing:

- contract and version;
- PASS or FAIL status;
- test, failure, error, and skipped counts;
- commit SHA and workflow run identifier;
- validation timestamp;
- bounded failure details when applicable.

Generated result files are intentionally ignored by Git. Durable evidence retains the workflow URL, commit SHA, test count, result, and artifact digest without committing transient output or credentials.

## Contract test evidence — 2026-08-29

| Evidence | Result |
|---|---|
| Commit | `ad2543929ba7965d9f3f21879fbe5b0c33e6449e` |
| [FAB-001 workflow run 33229812935](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33229812935) | PASS |
| Tests | 33 passed; 0 failed; 0 errors; 0 skipped |
| Artifact | `fab-001-contract-33229812935` |
| Artifact ID | `9708110998` |
| Artifact digest | `sha256:bbd634dbe73f3d962a909c4126781c5c70e506580a0d38e100a9083acf79d655` |
| Retention through | 2026-09-28 |
| [Required OPS-001 validation run 33229812942](https://github.com/cetanibp/microsoft-data-ai-mastery/actions/runs/33229812942) | PASS |

## Exercised behavior

- Valid Northstar release and environment resolution
- Development versus Production configuration without code changes
- Duplicate and unresolved stable identifiers
- Missing source and object environment configuration
- Enabled object with disabled source
- Secret-like connection and routing values
- Watermark-policy compatibility
- Parameter allowlisting, type checking, and bounds
- Production SLO and operational ownership requirements
- Self-dependency and multi-object cycle detection
- SQL tables, foreign keys, constraints, views, seed structure, and secret boundary
- Watermark failure abandonment without advancement
- Successful single commit
- Stale concurrent candidate rejection

## Remaining live evidence

- Deploy the SQL package to a Fabric SQL Database in an isolated Development workspace.
- Confirm that the seed resolves 14 active environment/object configurations and zero metadata validation issues.
- Exercise the watermark transaction protocol against the database engine.
- Preserve sanitized deployment and query evidence.

The automated suite proves the repository contract and failure paths without credentials. It does not replace live Fabric SQL Database deployment and transaction validation.
