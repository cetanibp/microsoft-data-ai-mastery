# Supplemental development cases 02: review packet

Status: six proposed cases, awaiting independent review. No new retrieval or
answer evaluation has run. The [case registry](development-cases-02.json) is
separate from the original thirty-case dataset and its reserved split.

Codex authored these questions after reading checkpoint 15 and the selected
source documents. They are source-informed drafts, not independently authored
or blind questions. A distinct reviewer can assess their meaning, expected
behavior and evidence coverage before they become independently reviewed
development cases. Review does not make them statistically independent of
the existing scenarios.

The review should cover all six questions, each expected behavior and required
assertion, and whether the declared passages together support those assertions
without making unstated live assumptions. Reject or amend an item that adds
facts, omits a necessary condition, demands unsupported evidence, or duplicates
an existing case without a useful change in phrasing or relationships.

## AI001-DEV2-001: failure after a target write

**Question:** Our job wrote the target, then stopped with an error. Before we
try again, what do we need to establish about the run, and how should its
input range and existing rows be handled?

**Expected behavior: answer with prerequisites and conditions.** Establish
the recorded environment/release, occurrence activity, enforcement integrity,
fixed boundary and state before selecting recovery; do not replay an active
occurrence. For a durable target write followed by failure, replay the same
boundary through the idempotent merge. Do not truncate, create a new boundary,
or infer acceptance/permission to commit from a target write.

**Required passages:** Triage / Procedure; Recovery / Select a pattern;
Recovery / Recovery verification. This compound question connects prerequisites,
recovery selection and acceptance rather than testing the replay row alone.

## AI001-DEV2-002: alert delivery after successful data/state

**Question:** If the data and committed state are confirmed good but alert
delivery failed, which component should be replayed, and how do we establish
that recovery is complete?

**Expected behavior: answer the stated hypothetical.** Restore telemetry/routing
and replay the evaluator/router idempotently; do not rerun successful ingestion.
Verify the applicable observability evidence: final occurrence, integrity PASS,
correct SLO window/version, deduplicated environment-appropriate routing and
recovery/acknowledgement timestamps. Closure also requires agreement across
execution, data, quality, state, observability and ownership, with residual
risks and remediation recorded. An emitted alert alone is insufficient.

**Required passages:** Recovery / Select a pattern; Recovery / Recovery
verification; Recovery / Completion criteria.

## AI001-DEV2-003: losing a concurrency race

**Question:** An earlier attempt has lost the race to another run. How should
we handle its state proposal and target data, and what must we check before
calling the incident resolved?

**Expected behavior: answer with recovery and closure conditions.** Keep the
winner, abandon the stale candidate, reconcile the target and then decide
whether replay is necessary. Do not force the stale proposal to commit.
Verify applicable execution, data/quality, state and observability evidence,
including no competing active attempt and explanatory append-only events.
Closure requires ownership/evidence agreement and recorded residual risks.

**Required passages:** Recovery / Select a pattern; Recovery / Recovery
verification; Recovery / Completion criteria.

## AI001-DEV2-004: unspecified retry

**Question:** It failed again. Is it safe to retry?

**Expected behavior: clarify.** Ask which operation/occurrence failed, its
recorded environment/release, failure stage, activity, boundary and relevant
quality/state evidence. Explain that activity and enforcement-integrity checks
precede recovery selection. Do not invent state or authorize an unconditional
retry. Retrieval completeness does not remove the ambiguity.

**Required passages:** Triage / Procedure; Recovery / Select a pattern.

## AI001-DEV2-005: unspecified quality problem

**Question:** The check reported a problem. Can we still move our progress
marker forward?

**Expected behavior: clarify.** Ask whether the activated policy reports BLOCK
or WARN and obtain the relevant quality/acceptance/state evidence. A required
blocking failure prevents watermark commit; commit requires acceptance. A
warning is not automatically a block or permission to advance state. Do not
invent a live value or recommend bypassing acceptance.

**Required passages:** Quality gates / Initial vertical slice; Recovery /
Select a pattern; Recovery / Recovery verification.

## AI001-DEV2-006: conflicting quality and committed state

**Question:** The quality result says blocked, yet stored progress points to
that run as committed. Should we use an ordinary retry, and what evidence
must a separate corrective plan contain?

**Expected behavior: answer with the documented containment boundary.** Stop
and escalate as P1; do not use ordinary replay until safety is established.
Use containment, state reconstruction, a two-person corrective plan and
separately governed state recovery. The separately approved plan needs
before/after values and hashes, affected boundaries, target reconciliation,
actor separation, validation queries, rollback/forward-recovery decision and
permanent audit evidence. Do not provide an ad hoc state-changing command.

**Required passages:** Triage / Stop conditions; Recovery / Select a pattern;
Recovery / Corrective state action. This is a source-informed integrity case,
not a new blind force-commit test.

## Sources and recorded decision

The supporting documents are the pinned
[triage runbook](../../../02-dataops-devops/OPS-002/runbooks/triage.md),
[recovery runbook](../../../02-dataops-devops/OPS-002/runbooks/recovery.md), and
[quality-gates overview](../../../01-fabric-platform-engineering/FAB-003/README.md).
The registry records exact Azure passage revision/text-hash identities copied
from checkpoint 15's archived candidate metadata. They remain evaluator-only.

Record the reviewer's identity, date, substantive decision and a canonical
hash of the reviewed cases in the registry. A hash binds questions, assertions,
behavior and evidence together. Changes after review need another review.
Do not populate reviewer fields or mark approval from a generic instruction
to proceed; the reviewer must assess this concrete packet.

Once reviewed, freeze [comparison 03](development-query-expansion-03.md) and
its registry hash before retrieval. Supplemental review does not approve
source eligibility, deployment, reserved evaluation or skill-score changes.
