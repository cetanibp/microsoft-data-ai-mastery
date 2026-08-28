# Release process

## Pull-request gate

Every candidate must pass the credential-free validator, which checks:

- required Fabric metadata and parseable JSON;
- Variable Library names, types, safe defaults, value sets, and policy values;
- notebook Python syntax and required configuration-contract behavior;
- obvious secret-bearing keys and private-key or storage-key text.

The controlled negative test proved that Production `allow_destructive_tests=true` fails validation and blocks merge.

## Development gate

1. Merge the approved PR to `main`.
2. Update the Development workspace from Git.
3. Confirm the Development value set is active.
4. Run `NB_OPS001_EnvironmentValidation`.
5. Require a PASS and a clean Git state.

## Test promotion

Run `Promote Fabric content` from `main` with:

- target environment: `test`
- mode: `preflight` for identity/routing checks or `deploy` to promote
- a release note containing the change and short commit SHA

The workflow validates adjacent forward stages, target workspace assignment, and API access before deployment. It then invokes the Fabric Deployment Pipeline API, polls asynchronous completion, and uploads sanitized JSON evidence.

After deployment, confirm the Test value set is active and run the validation notebook. Retain the notebook result and confirm Development/Test stage synchronization.

## Production promotion

1. Validate Test and confirm the release/recovery plan.
2. Run the workflow from `main` with target `production`.
3. GitHub must pause for the `production` required reviewer.
4. Review the commit, Test evidence, risk, and recovery plan.
5. Approve or reject the pending job.
6. Use `preflight` to verify authorization without deployment, or `deploy` for an approved release.
7. Run Production post-deployment verification and retain evidence.

OPS-001 exercised Production approval and preflight only; it did not deploy content to Production.

## Required release evidence

- approved commit SHA and PR;
- validation workflow and result;
- actor or workload identity;
- target GitHub environment;
- Fabric deployment and operation IDs for deployments;
- stage names and orders;
- pre/post-deployment notebook results;
- GitHub artifact name and digest;
- approval record for Production;
- rollback or forward-recovery decision.

Evidence artifacts are retained for 30 days in GitHub Actions. Durable identifiers and links are indexed in the repository and Issue #8.

