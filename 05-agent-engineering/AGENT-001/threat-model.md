# Read-only tool boundary and future approval requirements

October 6, 2026; local synthetic contract evidence. This supplies design input
for ADR-010 and AGENT-004, without accepting an architecture decision.

| Threat | Boundary and current evidence | Remaining work |
|---|---|---|
| Prompt injection in source output | Free-form fixture text is dropped by explicit projection; injected role/filter/SQL/action parameters are rejected | Test full model/orchestrator behavior with untrusted tool output and additional source types |
| Confused deputy | User and workload grants are separately resolved and intersected; scope is applied during lookup and checked before return; missing and restricted UUIDs share a response | Validated tokens, real downstream access checks and authenticated MCP transport |
| Excessive agency | One exact read and no write/command tool; no retries; late/cancelled data discarded | Enforce total workflow calls, deadlines, retries and cancellation in live adapters |
| Credential/data leakage | No credential arguments; explicit DTO fields; generic errors; audit excludes source bodies | Protected synthetic fixture, production logging checks and network/identity evidence |
| Revocation/cache bypass | Policy resolved for every call; user removal denies the next call; no cache | Measure directory/token propagation; recheck any future cache and policy lifecycle |
| Conflicting/stale evidence | Schema and requested environment/run identity are checked; missing evidence remains unknown | Coherent snapshot, source freshness, recorded-release owner and lineage checks |
| Tool response interpreted as permission | Integrity `PASS` is an observation only; no execution endpoint exists | Evaluate AGENT-002 recommendations and enforce AGENT-004 approvals |

The known-field schema also restricts statuses, UUIDs, hashes and object keys,
so arbitrary prose cannot be smuggled through those fields. This does not
establish resistance of a model consuming other text sources.

## Consequential action contract for AGENT-004

Before any future replay, recovery, state correction, publication or routing
change is executable, authorization must bind all of the following:

- validated requesting user and authorized approver identities;
- action type and canonical argument hash, including exact resource scope;
- environment, recorded metadata release, run/attempt and input-boundary hash;
- current state version and relevant quality/active-attempt preconditions;
- approval issuance/expiry, policy version and a single-use nonce;
- separately scoped execution workload and downstream operation permission.

At execution, recheck current access, approval expiry, single-use nonce and
state preconditions. Reject changed arguments, changed state, revoked access,
wrong environment/resource, replayed approval or a conflicting active attempt.
An integrity breach follows OPS-002 containment and corrective planning.
Neither a user role label nor source/model text can approve a state change.

These are requirements for #17, not implemented action controls. This
increment exposes only `inspect_object_run`. A future action adapter is
disabled until exact-action binding, least privilege and failure tests pass.
