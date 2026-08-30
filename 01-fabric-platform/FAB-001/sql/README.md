# FAB-001 SQL package

These scripts implement the proposed Northstar ingestion control-plane model for SQL Database in Microsoft Fabric.

## Deployment order

1. `001_create_schemas.sql`
2. `010_create_definition_tables.sql`
3. `020_create_runtime_tables.sql`
4. `030_create_views.sql`
5. `100_seed_northstar.sql`

Run the deployment scripts against an empty Fabric SQL Database named `sqldb_northstar_control` in the appropriate isolated workspace. The scripts do not create a database, Fabric item, workspace, connection, or credential.

After deployment, run `110_validate_watermark_protocol.sql` as a rollback-safe live validation. It is not part of schema deployment and leaves no test data behind.

## Package contents

| Script | Purpose |
|---|---|
| `001_create_schemas.sql` | Creates the `ctrl`, `ops`, and `audit` schemas |
| `010_create_definition_tables.sql` | Creates immutable release-scoped definitions and relational constraints |
| `020_create_runtime_tables.sql` | Creates isolated execution, watermark, and append-only audit structures |
| `030_create_views.sql` | Creates active configuration resolution and semantic validation views |
| `100_seed_northstar.sql` | Creates synthetic release `1.0.0` with representative environments, sources, strategies, dependencies, schedules, SLOs, policies, and ownership |
| `110_validate_watermark_protocol.sql` | Proves failed-attempt safety, successful compare-and-commit, stale-write rejection, and audit correlation inside a rolled-back transaction |

## Expected seed result

The active-configuration query returns 14 rows:

- five Development objects;
- five Test objects;
- four Production objects;
- the low-latency facility event is deliberately disabled in Production to demonstrate environment-specific configuration without code changes.

The metadata-validation query returns zero rows. Any returned row is a blocking definition issue for this release.

The seed demonstrates:

- FULL, WATERMARK, APPEND, and SNAPSHOT strategies;
- timestamp and numeric watermark policies;
- a three-object dependency chain;
- daily, interval, and event schedules;
- blocking and warning quality policies;
- freshness, reliability, duration, and quality SLOs;
- required production ownership;
- logical stage-specific connection, landing, and routing references.

## Deployment and immutability

Fabric source control and Deployment Pipelines govern database schema promotion. Approved metadata releases are inserted through reviewed, idempotent release scripts. Existing approved release rows are not updated in place; a changed definition creates a new release.

The SQL Database deployment mechanism preserves existing data while applying compatible schema changes. A change that could lose data requires explicit migration and recovery handling rather than a definition rollback.

The scripts intentionally do not include a hand-authored SQL project file. Fabric source-control integration generates and manages the project metadata for the SQL database item.

## Security boundary

Committed metadata may contain only safe logical keys. The following remain external:

- server or service endpoints;
- tenant, workspace, item, and physical connection identifiers;
- usernames, passwords, tokens, keys, and connection strings;
- patient, employee, financial, or other real organizational data.

Fabric Variable Libraries, managed connections, protected GitHub Environment variables, and approved identity or secret stores resolve those values according to the OPS-001 boundary.

## Runtime permissions

The implementation uses distinct responsibility boundaries:

| Role | Definition access | Runtime access | Audit access |
|---|---|---|---|
| Metadata deployment identity | Deploy reviewed schema and approved releases | No normal execution writes | Append release activation evidence |
| Ingestion runtime identity | Read active `ctrl` views | Insert and update narrowly scoped `ops` rows | Append events |
| Operator | Read definitions and runtime state | Execute approved recovery procedures | Append reasoned recovery evidence |
| Analyst or monitoring identity | Read approved projections | Read only | Read only |

Direct updates to approved definition rows or historical audit events are prohibited by operating policy.

## Validation boundary

Relational constraints reject invalid keys, enumerations, ranges, and unsafe literal shapes. `ctrl.vw_MetadataValidationIssue` adds cross-row semantic checks. Automated tests validate:

- dependency cycles;
- release immutability;
- parameter bounds and allowed values;
- required data-product ownership;
- environment mismatch rejection;
- watermark proposal, abandonment, and compare-and-commit behavior.

The live Fabric validation additionally confirms:

- 28 user tables, three views, and 47 foreign keys deploy successfully;
- the seed resolves 14 active environment/object configurations and zero validation issues;
- a failed attempt leaves the committed watermark unchanged;
- a successful compare-and-commit advances state exactly once;
- a stale candidate affects zero state rows;
- correlated audit events are appended for each outcome.
