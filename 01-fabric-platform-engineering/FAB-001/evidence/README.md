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

## Live Fabric SQL Database deployment — 2026-08-29

The SQL package was deployed to the isolated `Northstar Data Platform - FAB-001` workspace and committed to the existing `feature/fab-001-control-plane-design` branch. The deployment used the Fabric SQL Database item `sqldb_northstar_control` and synthetic Northstar metadata only.

| Validation | Result |
|---|---:|
| Deployment | PASS |
| User tables | 28 |
| Views | 3 |
| Foreign keys | 47 |
| Check constraints | 80 |
| Default constraints | 7 |
| Active environment/object configurations | 14 |
| Dependency edges | 3 |
| Metadata validation issues | 0 |

Validated views:

- `ctrl.vw_ActiveIngestionConfiguration`
- `ctrl.vw_MetadataValidationIssue`
- `ctrl.vw_ObjectDependencyEdge`

The zero-row result from `ctrl.vw_MetadataValidationIssue` confirms that the deployed synthetic release has no unresolved or inconsistent configuration.

## Live watermark transaction validation — 2026-08-29

The rollback-safe `110_validate_watermark_protocol.sql` script exercised the mutable state model directly against Fabric SQL Database. All synthetic changes were enclosed in one transaction and rolled back after validation.

| Scenario | Expected | Actual | Result |
|---|---|---|---|
| Failed attempt preserves committed state | Initial value; version 0 | Initial value; version 0 | PASS |
| Successful compare-and-commit | 1 affected row; version 1 | 1 affected row; state verified = 1 | PASS |
| Stale candidate rejected | 0 affected rows | 0 affected rows | PASS |
| Audit evidence appended | 3 events | 3 events | PASS |

This proves that a failed attempt does not advance the committed boundary, a successful attempt advances it exactly once, stale optimistic-concurrency writes are rejected, and each state outcome can append correlated audit evidence.

## Validation conclusion

The automated suite proves the repository contract and failure paths without credentials. The live deployment additionally proves that Fabric SQL Database accepts the physical package, resolves the expected active metadata without validation issues, and enforces the intended watermark state-transition behavior.
