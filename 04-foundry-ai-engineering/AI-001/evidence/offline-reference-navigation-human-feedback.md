# Offline reference navigation: human feedback

Focused navigation and response-wording review completed for local package
`offline-reference-v2-w609x6jv`; the full review template remains incomplete.
This records user feedback separately from automated preservation checks and
historical agent reviews. It is not a complete application evaluation.

## September 21, 2026 — ingestion reference

Case: `AI001-012-C1`.

The user opened `views/AI001-012-C1.md` and was asked to use its passage index
to locate the replay rule after a durable target write, the stop condition
when another attempt owns the boundary, and the distinction between accountable
ownership and execution-attempt ownership.

User feedback: **"easy to find"**.

This supports a positive findability observation for the requested ingestion
checks. It does not separately establish the user's interpretation of the
ownership distinction, full procedural completeness, or readiness to act.
No timing or comparison with the previous presentation was collected.

Before this feedback, fresh offline checks verified unchanged input bytes and
valid input hashes across all five saved cases, reproduction of all saved
Markdown views, and valid internal anchor targets. Both procedure views
preserved all five passages exactly once, with line endings normalized for
Markdown presentation. These checks made no model or network calls and did
not measure human usability.

## September 21, 2026 — watermark reference

Case: `AI001-013-C1`.

The user opened `views/AI001-013-C1.md` and was asked to find the checks for
committing only after acceptance, advancing the watermark version at most
once, and matching the committing run to the accepted occurrence. The prompt
also asked whether verification steps were clearly distinguished from a live
watermark value.

User feedback: **"easy to locate"**.

This supports a positive findability observation for the requested watermark
checks. The reply did not separately assess the live-value distinction, so
that judgment remains pending. No timing or comparison with the previous
presentation was collected.

## September 21, 2026 — clarification and refusal wording

Cases: `AI001-012`, `AI001-013`, and `AI001-025`.

The user opened all three saved responses and was asked: "Are the clarification
questions understandable, and is the refusal clear about what it cannot provide?"

User feedback: **"yes"**.

This records positive wording feedback for the rerun clarification, watermark
clarification, and force-commit refusal. It does not establish retrieval
completeness or validate a corrective procedure.

## Outcome and continuation

Retain the current navigation and response wording for this local reference:
both procedure views received positive findability feedback, and the three
short responses received positive clarity feedback. No presentation change
was requested. This is a focused user review, not a scored five-case
application pass.

The planned consolidation is now recorded in [checkpoint 12](azure-answer-reference-12.md).
The [portable reference](../offline-reference/README.md) reproduces the reviewed
Markdown views from repository files; input chunk IDs are explicitly sanitized.
Selected later experiment outcomes and provenance are archived separately.
Full historical inference packages remain local. Known semantic-review failures
and the force-commit evidence gap are preserved.

## Not assessed in this focused review

- Watermark reference (`AI001-013-C1`): clarity of verification steps versus a
  live watermark value; navigation received positive feedback.
- Full review-template judgments, including interpretation and reading burden.

The original package's human-review template remains unchanged. This partial
feedback does not resolve the force-commit evidence gap, change source
eligibility, or establish an independent external review or application pass.
