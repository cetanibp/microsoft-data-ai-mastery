# OPS-001 retrospective

## Outcome

OPS-001 successfully implemented and exercised a Fabric-native hybrid lifecycle: protected Git source, credential-free validation, OIDC authentication, Development-to-Test deployment, stage-specific configuration, Production approval, evidence capture, and Git-revert recovery.

## What worked

- Safe `unconfigured` defaults made missing stage configuration fail visibly.
- The repository validator blocked an unsafe Production value before promotion.
- OIDC removed the need for a stored client secret.
- GitHub Environment variables kept routing identifiers out of deployable definitions.
- Fabric Deployment Pipeline operations returned traceable deployment and operation IDs.
- Reverting the release PR produced a reproducible rollback through the same controls.
- Temporary branch workspaces prevented shared Development changes and were deleted after use.

## Problems found and corrected

### Ruleset availability

The private repository initially could define but not enforce branch rules under the account plan. The repository was made public after checking that it contained no credentials or organizational secrets, enabling effective ruleset enforcement.

### Production reviewer rule

The first Production preflight ran without waiting because the required-reviewer rule had not been saved. The run was recorded as a failed control test, no Production deployment occurred, and the environment protection rule was corrected. The repeated preflight recorded an explicit approval before job execution.

### Evidence download durability

Workflow artifacts have finite retention. Durable manifests therefore retain run links, commit SHAs, Fabric IDs, names, and cryptographic artifact digests without retaining credentials.

## Current limitations

- Post-deployment notebook validation is an operator-executed gate; a future increment should start and poll the notebook through a supported Fabric job API.
- Production deployment was intentionally not performed; Production OIDC, routing, access, and approval were validated by preflight.
- The representative package contains a Variable Library and notebook, not stateful schema or data migrations.
- Single-maintainer approval permits self-review. A team should require independent PR and Production reviewers.

## Improvements

1. Automate notebook smoke execution and ingest its returned JSON into the promotion artifact.
2. Add drift comparison between expected Git definitions and Fabric stages.
3. Add dependency-aware selective deployment for larger solutions.
4. Add environment-specific workload identities when production risk warrants stronger separation.
5. Exercise an expand/migrate/contract data change and forward recovery.
6. Export release evidence to durable centralized storage when retention requirements exceed GitHub artifact retention.

## ADR result

Implementation evidence supports accepting ADR-002 Option C: separate workspaces with automated, approved promotion. The evidence also confirms ADR-002's warning that automation must be paired with validation, approvals, configuration boundaries, and tested recovery.

