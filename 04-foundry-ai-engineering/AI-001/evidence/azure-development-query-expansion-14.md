# Checkpoint 14: fixed-budget query expansion and fusion

Executed September 29, 2026 Pacific time (September 30 UTC). Follows the
force-commit diagnostic in [checkpoint 13](azure-force-commit-diagnostic-13.md).

**Finding: reciprocal-rank fusion of the original and declared expanded
queries raises exact required-evidence completeness from three of five to four
of five development cases at the same five-passage context budget. The
force-commit case remains incomplete.**

## Frozen comparison

[Comparison 01](../evaluation/development-query-expansion-01.md) declared five
existing development questions and one manual, intent-preserving expansion per
question before execution. Each query retrieved up to ten direct-semantic
candidates. Original, expanded and reciprocal-rank-fused views were each
capped at five passages. Required document, heading, revision and text-hash
identities remained evaluator-only.

All eighteen read-only requests succeeded: ten queries, six configuration
reads and two complete-corpus reads. No retry, model call, reserved question,
configuration mutation or index write occurred.

## Results

Positions below are exact required passages in the final five-passage view.
Multiple positions in one cell correspond to multiple required passages.

| Case | Original top five | Expanded top five | Fused top five | Complete after fusion |
|---|---:|---:|---:|---:|
| AI001-001 | 1, 3 | 1, 3 | 1, 3 | Yes |
| AI001-011 | 4 | 3 | 3 | Yes |
| AI001-012 | missing, 1 | 1, missing | 3, 1 | Yes |
| AI001-013 | 5, 4 | 1, 2 | 2, 3 | Yes |
| AI001-025 | missing | missing | missing | No |

The original AI001-012 query again returned only two candidates and retained
Select a pattern at rank one. Its expansion returned ten candidates, placing
Procedure first and Select a pattern sixth. Neither query alone was complete
at five; fusion retained both at ranks three and one. This is complementary
retrieval, not proof that an answer should skip clarification.

The three complete original cases did not regress. AI001-013 is complete in
this direct-semantic baseline, unlike the earlier keyword-only checkpoint;
those retrieval modes are not a controlled single-variable comparison.

For AI001-025, the target moved from direct-semantic candidate rank nine to
rank six under the declared expansion and fused to rank eight. It remained
outside every five-passage view. This reproduces the original rank-nine
observation from checkpoint 13 and does not solve the force-commit gap.

## Controls and interpretation

The exact eighteen-record corpus fingerprint matched before and after. Index,
knowledge-base and knowledge-source hashes were also unchanged. The selected
[JSON evidence](azure-development-query-expansion-14.json) records positions,
controls, timings and hashes for the frozen spec, runner, tests and local
summary. Request, ranking and metric files remain in the local
`development-query-expansion-01-20260929` directory; raw service bodies were
processed in memory and were not archived.

The result supports retaining fixed-budget fusion as a development candidate,
not adopting it as a release configuration. These expansions were manually
written for known questions. Evidence coverage does not establish semantic
answer support, correct clarification/refusal behavior, source eligibility,
access/freshness enforcement or application readiness.

Next, test a query-generation rule that is fixed independently of individual
expected passages, or add independently reviewed development cases before
another retrieval run. Preserve five final passages, report the larger fused
candidate pool separately, and keep AI001-025 as an unresolved control. Do not
tune another force-commit rewrite within this batch.

No issue closure, source approval, ADR acceptance or skill-score change.
