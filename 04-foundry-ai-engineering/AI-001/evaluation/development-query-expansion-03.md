# Development query-expansion comparison 03

Status: draft pending independent case review, prepared October 1, 2026
Pacific time. **Not frozen and not live-executed.** The
[JSON draft](development-query-expansion-03.json) references the hash-pinned
[supplemental registry](development-cases-02.json). Its six proposed cases
and the [review packet](development-cases-02-review.md) are ready to assess.

[Preparation evidence](../evidence/development-query-expansion-03-preparation.json)
records 49 passing tests and one Windows symlink-privilege skip (50 total),
including seventeen query-expansion contracts. Local source blob hashes and
unchanged query/fusion controls were verified. Review simulations used only
temporary test fixtures; the actual registry remains pending. No Azure
requests or new retrieval results are claimed.

## Question and cohorts

Does the unchanged `question-only-v1` expansion preserve complete relationships
on additional reviewed development questions, and does fusion retain or lose
the expansion's evidence at a five-passage budget?

Report the six new development cases separately from five historical controls
(AI001-001, 011, 012, 013 and 025). Combined eleven-case metrics are secondary.
The proposed cases cover target-write recovery prerequisites, alert repair
and closure, concurrency recovery and closure, two ambiguous questions, and
integrity containment/corrective planning. They were authored by Codex after
checkpoint 15, are source-informed, and currently have no independent review.
Even after review, do not claim independent authorship or a blind test.

Keep the original thirty-case dataset, reserved cases, source corpus and
frozen comparisons 01/02 unchanged. Keep AI001-025 as the unresolved control;
do not add a special force-commit rewrite.

## Retrieval arms and controls

Use comparison 02's unchanged suffix, direct-semantic fields/configuration,
API version, equal-weight RRF constant 60 and deterministic tie-breaking.
Retrieve up to ten original and ten expanded candidates per case. Compare
original, expanded and fused final views, each capped at five passages.
Required identities, assertions and review metadata are evaluator-only.

For each cohort, report completeness with denominators, exact per-case evidence
positions, original/expanded candidate counts, deduplicated union size and
full fused ranks. Report expanded/fused losses against complete original views
and fusion losses against complete expanded views. Do not hide an expansion
gain lost through fusion, as occurred in checkpoint 15.

The proposed maximum is **thirty read-only experiment requests**: twenty-two
queries, six configuration reads and two corpus reads. This increases batch
size to eleven cases; it does not increase final context size. One attempt
per request; no retry, model call, configuration/index write, within-batch
query repair or reserved-case execution. Stop on the established request,
partial-response, identity, eligibility or corpus/configuration controls.

## Review and freeze

Before live execution, a reviewer distinct from the recorded author must
assess the questions, expected behaviors/assertions and evidence mappings.
Record the actual reviewer, date, decision and canonical case hash. Do not
manufacture review or treat local contract validation as semantic review.

After any requested corrections and review, update the registry hash in the
comparison, record the declaration date and set the comparison status to
`frozen_before_live_execution`. Snapshot the approved registry with the spec
and runner/reader at execution. The runner rejects pending review, changed
reviewed case contents, registry-hash drift and mismatched question/evidence
copies before any service request or creation of a live output directory.

## Local preparation

From the repository root:

```powershell
& .\.venv\Scripts\python.exe -B 04-foundry-ai-engineering/AI-001/evaluation/run_development_query_expansion.py --spec 04-foundry-ai-engineering/AI-001/evaluation/development-query-expansion-03.json --validate-only
```

For this draft, `structurally_valid_pending_review` with
`live_execution_ready: false` is the expected result. It proves structural
consistency only and makes zero Azure requests. Live execution remains
unavailable until substantive independent review and freezing are recorded.

## Decision after the future run

Assess each arm on the new-development cohort and report historical controls
separately. Expansion improvement requires increased completeness without
losses from complete originals. A fusion improvement also needs increased
completeness and must report losses from complete expanded contexts. Neutral
or negative results remain results; do not revise this batch to chase a gain.

No retrieval result alone establishes semantic answer support, correct
clarification/refusal, access/freshness enforcement or release readiness.
Those evaluations remain separate. No issue closure, ADR acceptance, source
approval, deployment or skill-score change is authorized by this draft.
