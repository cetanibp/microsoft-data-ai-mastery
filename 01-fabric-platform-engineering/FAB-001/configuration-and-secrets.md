# FAB-001 — Configuration and secrets boundary

**Status:** Complete  
**Related issue:** [#5 — FAB-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/5)  
**Inherited lifecycle:** [OPS-001](../../02-dataops-devops/OPS-001/README.md) and [ADR-002](../../09-enterprise-architecture/decisions/ADR-002-environment-isolation-and-promotion.md)

## Purpose

This guide defines where every configuration class belongs and how shared ingestion code resolves an environment without embedding credentials, endpoints, workspace identifiers, or environment-specific code. FAB-001 extends the accepted OPS-001 boundary; it does not create a competing configuration or promotion mechanism.

The governing rule is:

> Git stores approved definitions, Fabric supplies stage context, the control plane resolves logical runtime intent, managed connections supply access, and runtime tables store mutable state.

## Systems of record

| Configuration class | System of record | Examples | Git allowed? |
|---|---|---|---:|
| Deployable schema and validation logic | Git | DDL, views, constraints, validation scripts | Yes |
| Approved metadata release | Git-reviewed seed or migration | source/object keys, policies, schedules, SLOs, ownership | Yes, when synthetic or approved and non-sensitive |
| Safe stage context | Fabric Variable Library | environment name, release ring, quality threshold, destructive-test policy | Yes, with unusable defaults and reviewed value sets |
| Active stage selection | Fabric workspace | active Variable Library value set | No; remains stage-specific |
| Automation routing | Protected GitHub Environment variables | tenant, application, deployment-pipeline, stage, and workspace identifiers | No repository literal |
| Connection endpoint and authentication | Fabric managed connection or approved secret/identity boundary | server, database, credential, token, certificate | No |
| Logical connection and landing references | `ctrl` metadata | `connection-ehr-reader-development`, `landing-clinical-test` | Yes, as non-resolving logical keys |
| Runtime execution state | `ops` schema | run status, proposed and committed watermarks | No definition commit |
| Append-oriented operational evidence | `audit` schema and governed release evidence | state event, actor, reason, correlation ID | Durable evidence only; never tokens |
| Business or protected data | Governed Bronze/Silver/Gold stores | source payloads, patient or financial facts | Never in the control plane |

## Existing OPS-001 stage contract

FAB-001 consumes the established `vl_northstar_environment` Variable Library rather than defining another environment selector.

| Variable | Purpose | Required behavior |
|---|---|---|
| `environment_name` | Selects Development, Test, or Production resolution | Must match one `ctrl.Environment.environment_code` |
| `release_ring` | Identifies lifecycle posture | Must use the stage-appropriate reviewed value |
| `minimum_quality_pct` | Supplies the stage validation threshold | May become stricter through promotion |
| `allow_destructive_tests` | Controls destructive validation | Must be `false` outside Development |
| `validation_contract_version` | Identifies the validation contract | Must be supported by the deployed runtime |

Default values remain deliberately unusable where practical. A missing active value set must fail closed instead of silently selecting Development or Production.

New safe stage variables may be added only when a real runtime requirement cannot be represented by approved metadata, Fabric autobinding, or a managed connection. Additions require the same OPS-001 PR validation and promotion lifecycle.

## Control-plane configuration contract

### Versioned definitions

The following entities describe approved intent and are release-scoped:

- `ctrl.MetadataRelease`
- source systems, source objects, and target objects;
- ingestion objects and load policies;
- watermark definitions;
- schedules and execution policies;
- dependencies;
- SLO and quality-policy assignments;
- ownership assignments;
- environment-specific object and source configuration.

Approved definitions are immutable. A material change creates a new release rather than updating an approved release in place.

### Logical references

The model intentionally stores logical keys such as:

- `connection-ehr-reader-development`;
- `landing-clinical-test`;
- `route-pharmacy-order-production`;
- `store-bronze`.

A logical key is safe only when it cannot independently grant access or disclose a protected endpoint. It must be resolved at runtime through an authorized Fabric item, managed connection, Variable Library, deployment rule, or other approved platform registry.

The control plane must never store the resolved credential, access token, connection string, private endpoint, or secret-store value.

### Mutable runtime state

The `ops` schema is operational state, not stage configuration:

- `ops.ExecutionRun` records the resolved release and configuration hash for a run;
- `ops.ObjectRun` records object attempts and outcomes;
- `ops.WatermarkState` stores only the last committed boundary;
- `ops.WatermarkCandidate` stores proposed boundaries until committed or abandoned.

A deployment must not overwrite runtime state. Schema rollback is not a substitute for state recovery.

## Runtime resolution sequence

1. Read the active `vl_northstar_environment` value set.
2. Validate that `environment_name` is configured and recognized.
3. Resolve exactly one active `ctrl.EnvironmentRelease` for that environment.
4. Query `ctrl.vw_ActiveIngestionConfiguration` using the resolved environment.
5. Reject the run if `ctrl.vw_MetadataValidationIssue` returns a blocking issue for the selected release.
6. Resolve each logical connection reference through the authorized Fabric connection boundary.
7. Capture environment, release, object, correlation ID, and a non-sensitive configuration hash in `ops.ExecutionRun`.
8. Execute with the least-privilege runtime identity.
9. Append state-transition evidence without recording credentials or protected payloads.

No pipeline or notebook branch is permitted to hard-code a Development, Test, or Production endpoint. The same approved code follows this sequence in every stage.

## Fail-closed validation

Runtime selection must stop before source access when any of the following is true:

- the active Variable Library value set is missing or `unconfigured`;
- the stage name does not match one known environment;
- zero or multiple active releases resolve;
- the release is not approved or active for the stage;
- an enabled object has an unresolved source, target, policy, schedule, SLO, or required owner;
- a logical connection reference is blank, malformed, or cannot be resolved;
- metadata contains a value shaped like a secret, connection string, credential, or protected endpoint;
- a Production object is missing required operational ownership;
- dependency validation detects a self-reference, cycle, or inconsistent release;
- a runtime request attempts to use a superseded or rejected release.

A failure records a sanitized issue code, stable entity key, correlation ID, and recovery owner. It must not echo connection details, tokens, query payloads, or protected data.

## Prohibited repository and metadata content

The following values are prohibited in Git, seed data, control-plane definitions, logs, test fixtures, and retained evidence:

- passwords, access keys, client secrets, refresh tokens, bearer tokens, and SAS tokens;
- private keys, certificates with private material, or credential files;
- complete connection strings;
- real server names, database endpoints, storage URLs, or private network addresses unless separately approved as public architecture metadata;
- tenant, workspace, Fabric item, or physical connection identifiers embedded in deployable definitions;
- patient, employee, financial, or proprietary source metadata;
- query results or error text containing protected payload values.

Names such as `password_key` or `secret_reference` are also discouraged because they invite accidental value storage. Prefer a neutral, constrained logical key such as `connection_reference_key`.

## Authentication and authorization

| Identity | Minimum capability |
|---|---|
| Metadata deployment identity | Apply reviewed schema and approved releases; no normal runtime-state mutation |
| Ingestion runtime identity | Read active `ctrl` projections; insert/update narrowly scoped `ops` records; append `audit` events |
| Operator | Read definitions and state; invoke approved recovery procedures with actor and reason |
| Monitoring identity | Read approved operational projections; no mutation |
| CI/CD identity | Promote Fabric definitions through OPS-001 using OIDC; no stored client secret |

Authentication uses managed identity, workload identity federation, managed connections, or another approved short-lived identity mechanism. Static credentials are not a fallback configuration method.

## Change ownership

| Change | Primary owner | Required control |
|---|---|---|
| Metadata schema or validation rule | Platform engineering | PR, automated contract tests, compatibility review |
| Approved metadata release | Metadata owner plus domain steward | PR, semantic validation, approval reference |
| Variable Library definition or value set | Platform engineering | OPS-001 validation and promotion |
| Active stage value-set selection | Environment operator | Post-deployment stage verification |
| Managed connection or secret | Security/platform administrator | Approved secret rotation and access review |
| Runtime-state correction | Authorized operator | Forward-recovery procedure, actor, reason, audit event |
| Production promotion | Release owner and required reviewer | Protected environment approval and retained evidence |

## Safe examples

Allowed committed metadata:

```text
environment_code = development
connection_reference_key = connection-ehr-reader-development
landing_zone_key = landing-clinical-development
routing_alias = route-clinical-encounter-development
```

Prohibited committed values:

```text
Server=tcp:real-server.example;Database=Clinical;Password=...
https://storage-account.example/container?sv=...&sig=...
Bearer eyJ...
workspace_id = <physical production workspace identifier>
```

## Verification checklist

Before activating a metadata release:

- [ ] Contract tests pass with no secret-like values.
- [ ] The active stage value set is explicit and not `unconfigured`.
- [ ] Exactly one approved release resolves for the environment.
- [ ] `ctrl.vw_MetadataValidationIssue` returns no blocking issues.
- [ ] All logical connection references resolve through approved managed boundaries.
- [ ] The runtime identity has only required read/write permissions.
- [ ] Logs and evidence contain stable keys and correlation IDs, not resolved values.
- [ ] Production approval includes the release, validation, risk, and recovery decision.
- [ ] Stateful changes identify forward-recovery behavior.
