# Branching and change governance

## Normal change flow

1. Start from current `main`.
2. Create a short-lived `feature/*`, `fix/*`, or `revert-*` branch.
3. For Fabric authoring, branch to a temporary developer workspace. One active branch maps to one workspace.
4. Commit dependent Fabric items together when practical.
5. Open a pull request to `main`.
6. Require `Validate Fabric definitions`, current-with-main status, and resolved conversations.
7. Merge only the reviewed, passing tree; delete the branch and temporary workspace after use.

`main` is the release source. Test and Production are never Git-connected development targets.

## Protected-main controls

The `Protect main` ruleset:

- requires pull requests;
- requires `Validate Fabric definitions`;
- requires branches to be current;
- requires conversation resolution;
- prevents deletion and force pushes;
- has no bypass actors.

Zero PR approvals are required because this is a single-maintainer learning repository. Production authorization is a separate protected-environment control. A team implementation should require an independent PR reviewer and enable Production self-review prevention.

The direct initial commit was a one-time bootstrap needed to establish Fabric definitions. All subsequent changes used feature or revert PRs.

## Direct changes and emergencies

Normal direct changes to Test or Production are prohibited. If an emergency requires an out-of-band change:

1. Record the incident, owner, reason, scope, and approval.
2. Capture the before/after definition and operational evidence.
3. Apply the smallest safe change with time-bounded privileged access.
4. Verify service recovery.
5. Reconcile the change into Git immediately through a PR.
6. Redeploy or compare stages to remove drift.
7. Complete a retrospective and access review.

An emergency change is incomplete until Git and the affected stage agree.

