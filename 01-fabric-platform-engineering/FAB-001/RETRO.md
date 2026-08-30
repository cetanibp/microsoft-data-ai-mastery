# FAB-001 retrospective — Ingestion control-plane metadata model

**Status:** Complete  
**Issue:** [#5 — FAB-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/5)  
**Pull request:** [#32](https://github.com/cetanibp/microsoft-data-ai-mastery/pull/32)  
**Completed:** 2026-08-29

## Outcome

FAB-001 produced and validated a versioned ingestion control-plane contract for the synthetic Northstar Health System scenario. The design replaces object-specific orchestration assumptions with stable metadata that later Fabric pipelines and notebooks can resolve by environment, release, object, policy, dependency, schedule, SLO, and owner.

The completed implementation includes:

- architecture requirements and design principles;
- logical entity model and Mermaid ER source;
- a Fabric SQL Database physical package;
- 28 definition, runtime, and audit tables;
- three active-resolution and semantic-validation views;
- synthetic release `1.0.0`;
- FULL, WATERMARK, APPEND, and SNAPSHOT load strategies;
- 14 active environment/object configurations across Development, Test, and Production;
- a three-edge dependency graph;
- automated contract and SQL-structure tests;
- a rollback-safe live watermark transaction test;
- configuration, secrets, ownership, lifecycle, rollback, and recovery guidance;
- sanitized CI and live Fabric evidence.

## What was demonstrated

### Automated validation

The FAB-001 workflow executed 33 tests with:

- 33 passed;
- 0 failures;
- 0 errors;
- 0 skipped.

The suite exercised valid resolution, stage differences without code changes, invalid references, disabled sources, secret-like values, parameter validation, ownership and SLO requirements, dependency cycles, SQL package structure, watermark abandonment, successful commit, and stale concurrency rejection.

### Live Fabric SQL Database deployment

The package was deployed to the isolated `Northstar Data Platform - FAB-001` workspace in `sqldb_northstar_control`.

| Structural check | Result |
|---|---:|
| User tables | 28 |
| Views | 3 |
| Foreign keys | 47 |
| Check constraints | 80 |
| Default constraints | 7 |
| Active environment/object configurations | 14 |
| Dependency edges | 3 |
| Metadata validation issues | 0 |

### Live watermark protocol

The rollback-safe live test returned four PASS results:

- a failed attempt preserved the initial value and state version;
- a successful compare-and-commit affected exactly one row and advanced to version 1;
- a stale candidate affected zero rows;
- three correlated audit events were appended inside the test transaction.

All synthetic test mutations were rolled back.

## Decisions made

### SQL Database in Microsoft Fabric is the initial control store

The control plane is a transactional operational workload with small relational reads, concurrent state transitions, constraints, indexes, and atomic compare-and-commit behavior. Fabric SQL Database fits this workload better than Warehouse as the primary mutable store.

Warehouse or Lakehouse remains appropriate for longer-term analytical operations history.

### Releases are immutable full snapshots

Northstar's expected metadata scale is small enough that full release snapshots are simpler and safer than row-level version chains. A complete release improves deterministic reconstruction, review, validation, rollback assessment, and run traceability.

### Definition and state lifecycles are separate

Git-reviewed definitions, environment activation, execution state, and watermark state require different permissions and recovery behavior. Definition rollback cannot silently modify or reverse runtime state.

### Environment behavior is data-driven

The same orchestration code resolves Development, Test, and Production through the OPS-001 Variable Library stage contract plus `ctrl.EnvironmentRelease`, source configuration, and object configuration. Environment-specific code branches are prohibited.

### Connections are logical references

The database contains safe logical keys only. Fabric managed connections, approved identity boundaries, and external configuration resolve physical access. Credentials, endpoints, workspace IDs, and protected data are excluded from committed definitions and evidence.

### Watermark updates use optimistic concurrency

A proposed boundary is committed only after accepted data and a matching state version. Failure abandons the candidate without advancing state. A stale candidate is rejected and routed to recovery.

## What worked well

- Starting from downstream requirements made the model directly consumable by ingestion, quality, and operations work.
- Stable release-scoped keys created strong relational integrity without embedding executable SQL in metadata.
- Synthetic Northstar data demonstrated realistic variation without exposing organizational details.
- The validation view and Python contract validator provided complementary database and repository safeguards.
- Running the DDL in a real Fabric SQL Database caught the difference between theoretical compatibility and platform acceptance.
- The isolated feature workspace allowed live validation without contaminating the permanent Development workspace or creating an unnecessary additional Git branch.
- The rollback-safe transaction test produced credible state-transition evidence without leaving test records behind.
- Reusing OPS-001 avoided competing configuration, identity, and promotion patterns.

## Challenges and lessons

### Workspace and branch concepts must remain distinct

Fabric's “branch out to new workspace” flow would have created another Git branch and inherited unrelated branch content. The safer validation pattern was:

- manually create an isolated workspace;
- connect it to the existing feature branch;
- scope Git integration to the FAB-001 workspace folder.

Future issue walkthroughs should state this distinction before workspace creation.

### Active configurations are not object counts

The active view returned 14 rows because it resolves object/environment pairs: five Development, five Test, and four Production. Validation expectations should always describe the result grain.

### Database source control generates substantial artifacts

Fabric generated the SQL project representation for the database item, increasing the PR file count. This is expected for the platform-managed source-control model but should be reviewed for unintended generated churn.

### Schema rollback is not state rollback

The model makes this explicit, but future implementation must operationalize it through stored procedures, permissions, and recovery runbooks. A Git revert alone is insufficient for incompatible stateful changes.

## Limitations

FAB-001 defines and validates the control-plane contract; it does not implement the complete runtime.

Remaining implementation boundaries include:

- shared ingestion orchestration and source/target adapters;
- production-grade stored procedures for activation and watermark commit;
- database roles and grants enforced in deployed environments;
- automated dependency scheduling;
- source schema discovery and drift processing;
- data-quality execution and quarantine;
- telemetry export, SLO calculation, alert routing, and incident automation;
- automated environment drift detection;
- backup, restore, business-continuity, and regional recovery validation;
- performance and concurrency testing at 600-object production scale.

The synthetic Production configuration demonstrates resolution only. No real Production system, credential, endpoint, or protected data was used.

## Downstream handoff

### Issue #6 — resilient incremental ingestion

Issue #6 should consume:

- `ctrl.vw_ActiveIngestionConfiguration`;
- `ctrl.vw_ObjectDependencyEdge`;
- environment and release identities;
- source, target, load, execution, schedule, and owner contracts;
- `ops.ExecutionRun` and `ops.ObjectRun`;
- `ops.WatermarkState` and `ops.WatermarkCandidate`;
- the compare-and-commit protocol;
- correlation and audit requirements.

Issue #6 may extend runtime columns and add constrained procedures, but it should preserve stable identities, release pinning, idempotent boundaries, and failure-safe watermark behavior.

### Issue #7 — reconciliation and data-quality gates

Issue #7 should consume:

- `ctrl.QualityPolicy`;
- `ctrl.ObjectQualityPolicy`;
- quality SLO definitions and publication-blocking flags;
- object, release, environment, run, and object-run correlation keys;
- blocking versus warning enforcement;
- quarantine requirements and contract references.

Issue #7 owns check execution, result storage, quarantine processing, and publication decisions. It should not redefine ingestion object identity or release semantics.

### Issue #9 — SLOs, observability, and incident response

Issue #9 should consume:

- schedule and expected-completion context;
- `ctrl.SloDefinition` and `ctrl.ObjectSlo`;
- `ctrl.OwnerGroup` and `ctrl.ObjectOwnership`;
- run, object-run, state-event, release, and correlation identities;
- non-secret routing aliases;
- severity and breach policy.

Issue #9 owns telemetry projection, SLO evaluation, alert routing, dashboards, runbooks, and incident evidence. It should resolve routing aliases through the approved external boundary.

## Recommended next step

Proceed to [Issue #6](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/6) because it is the first runtime consumer of this foundational contract. Implement one shared orchestration path and begin with the timestamp-watermark object, retaining the FAB-001 release and state-transition identities throughout execution.

## Evidence

See [evidence/README.md](evidence/README.md) for CI runs, artifact identifiers, structural deployment results, active-resolution results, and live watermark transaction evidence.
