# inspect_object_run — Contract 1.0.0

Evidence class: local synthetic behavior. This is the first AGENT-001
increment, based on the existing FAB-001 tables and OPS-002 triage protocol.

## Inputs and outputs

Only `environment` (`development`, `test`, `production`) and a UUID
`object_run_id` are model-visible arguments. Extra fields are rejected.
There is no SQL, filter, URL, role, identity, prompt, recovery command or
credential parameter. The schema in
[inspect-object-run-v1.schema.json](contracts/inspect-object-run-v1.schema.json)
is validated by `jsonschema` 4.26.0; UUID format checks are explicitly enabled.

The server supplies `TrustedContext`, an absolute monotonic deadline no more
than five seconds away, and a cancellation event outside model arguments.
The response is either the versioned, correlated observation or a structured
error. Error responses contain no record. The record is an explicit field
projection; arbitrary source text and raw exceptions never become output.

| Identity or scope | Origin | Local behavior | Deployment requirement |
|---|---|---|---|
| Requesting user | Synthetic server context | Current user grant required | Validate token issuer, tenant, audience, signature and expiry |
| Agent/workload | Separate synthetic server context | Current workload grant required | Establish workload identity and least downstream privilege |
| Downstream authorization | Server policy resolver | Intersect allowed environments and object keys | Enforce user scope on every path despite workload access |
| Audit correlation | Server UUID | Returned and logged consistently | Bind request, authorization, downstream read and trace |
| Policy version | Server-owned fixture policy | Logged for every evaluated decision | Resolve current policy and measure real revocation propagation |

The first grants cover one environment and one object. They represent a
Cartesian environment/object scope; a future policy with environment-specific
object permissions must use explicit allowed pairs. The backend receives the
trusted object scope and applies it during lookup; membership is also checked
before return. Missing and out-of-scope UUIDs receive the same `NOT_FOUND`
response to avoid revealing a restricted record's existence. A live adapter
must preserve this authorization at its data boundary.

## Resource and failure bounds

| Condition | Contract |
|---|---|
| Maximum backend calls | One per invocation; no retries or hidden fan-out |
| Deadline | Up to five seconds; check before policy, before read and after read |
| Cancellation | Check before/after read; pass event into backend |
| In-flight interruption | Future live adapter must honor cancellation/deadline; synchronous fixture checks alone do not prove interruption |
| Pagination | None; exact UUID lookup returns zero or one record |
| Rate limit | `RATE_LIMITED`, retryable by a separately bounded caller; no automatic retry or backoff |
| Workflow budget | Proposed AGENT-002 limit: six tool calls and thirty seconds; enforcement belongs to the orchestrator |
| Repeat reads | Side-effect-free data access; each invocation emits its own audit event and may observe newer state |
| Cache | None; re-resolve grants on each invocation |
| Denied access | `ACCESS_DENIED`, no returned resource metadata |
| Missing or out-of-scope UUID | `NOT_FOUND`; only after environment authorization |
| Invalid arguments | `INVALID_ARGUMENT`; no backend read |
| Invalid or conflicting record | `INVALID_EVIDENCE`; discard result |
| Dependency/policy failure | `DEPENDENCY_UNAVAILABLE`; suppress exception details |
| Late result | `DEADLINE_EXCEEDED` or `CANCELLED`; discard result |

Malformed evidence and cancellation/deadline errors are not retryable in this
invocation. Retryability is a classification for a later caller, not a retry
instruction. An eventual orchestrator must impose its own total retry and
backoff budget before enabling retries.

## Evidence semantics and source mapping

Run/release/boundary fields come from
[ops.ObjectRun](../../01-fabric-platform-engineering/FAB-001/workspace/sqldb_northstar_control.SQLDatabase/ops/Tables/ObjectRun.sql).
Quality decisions use
[ops.QualityDecision](../../01-fabric-platform-engineering/FAB-001/workspace/sqldb_northstar_control.SQLDatabase/ops/Tables/QualityDecision.sql).
The integrity predicate follows
[ops.vw_OperationalOccurrence](../../01-fabric-platform-engineering/FAB-001/workspace/sqldb_northstar_control.SQLDatabase/ops/Views/vw_OperationalOccurrence.sql):
a block plus accepted terminal status, a committed candidate, or a last
committing ID equal to the inspected attempt is a breach.

Unlike a successful SQL join, an incomplete fixture is not proof of a safe
boundary: null candidate/state evidence produces `UNKNOWN`. The lookup
inspects the specified attempt; it does not assert that this is the latest
logical occurrence. A live adapter must read a coherent snapshot, preserve
the recorded release and correlate quality, candidate and state to that run.
The response timestamp marks local observation time, not source freshness.

The synthetic audit sink records only contract version, correlation UUID,
user/workload UUIDs, policy version, status/error code and backend-call count.
It excludes arguments, raw source records, hashes, prompts and exception text.
Durable audit availability, retention and access controls remain future work.
