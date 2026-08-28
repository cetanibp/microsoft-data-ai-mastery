# Rollback and forward recovery

## Definition rollback

Use definition rollback only when the prior Git revision remains compatible with current data and external contracts.

1. Identify the last known-good merged commit.
2. Revert the release PR through a new PR; never edit Test or Production directly.
3. Pass the same required repository validation.
4. Merge the approved recovery revision to `main`.
5. Synchronize Development and run the Development validation notebook.
6. Deploy Development to Test through the protected OIDC workflow.
7. Run Test validation and confirm stage synchronization.
8. Promote to Production only with a new Production approval and appropriate verification.
9. Retain the forward and recovery commit, run, operation, deployment, and verification evidence.

OPS-001 demonstrated this procedure by promoting contract `1.1.0`, reverting PR #29 through PR #30, and redeploying known-good contract `1.0.0`.

## When rollback is unsafe

Use forward recovery when reversing definitions could corrupt or misinterpret state, including:

- destructive or irreversible schema/data migrations;
- removed or renamed fields already consumed downstream;
- data written in a new incompatible format;
- security, identity, or key rotations;
- external side effects such as messages, API calls, or model actions;
- semantic-model changes paired with incompatible refresh state.

## Forward-recovery controls

Before a stateful release:

- use expand/migrate/contract sequencing;
- maintain backward compatibility during the transition;
- define backups, restore points, or compensating actions;
- make migrations restartable and idempotent;
- validate row counts, contracts, security, and downstream consumers;
- prepare a tested corrective change and owner escalation path.

The release manifest must state whether definition rollback is safe. If it is not, it must link the forward-recovery procedure before approval.
