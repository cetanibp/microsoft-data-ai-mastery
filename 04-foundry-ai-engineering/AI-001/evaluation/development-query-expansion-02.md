# Development query-expansion comparison 02

Status: frozen before live execution on October 1, 2026 Pacific time;
executed later that day. [Checkpoint 15](../evidence/azure-development-query-expansion-15.md)
records 3/5 original, 4/5 expanded and 3/5 fused complete final contexts.
The declaration below and its [JSON specification](development-query-expansion-02.json)
preserve the pre-run contract. This retrieval-only result is not an
answer-quality pass.

[Preparation evidence](../evidence/development-query-expansion-02-preparation.json)
records the spec/runner/test hashes, Python 3.14.2, successful local spec
validation and 44 passing tests with one Windows symlink-privilege skip
(45 total). All twelve query-expansion tests passed. At preparation time zero
Azure requests had been made and the service endpoint was unavailable in the
session environment. Subsequent endpoint discovery and live execution are
recorded separately in checkpoint 15; the preparation record is unchanged.

## Question

Does a single question-only expansion rule improve exact required-evidence
completeness through reciprocal-rank fusion at the same five-passage context
budget, without regressing complete original-query cases?

[Checkpoint 14](../evidence/azure-development-query-expansion-14.md) established
four of five complete fused contexts using manually authored expansions. This
comparison replaces those case-specific rewrites with one deterministic rule.
It reuses the same five development questions and evaluator targets. It does
not add independently reviewed cases or claim an independent generalization
test. The rule was designed after observing the earlier development results;
its implementation receives no expected passages, headings, categories or
case identities.

## Frozen query-generation rule

`question-only-v1` preserves the original question byte-for-byte as the prefix
and appends exactly this suffix, starting with one LF newline:

```text
Documented prerequisites, decision conditions, restrictions, and verification.
```

There are no topic-specific branches, model calls, synonyms selected for an
individual case, source lookups or occurrence-specific facts. The rule does
not resolve ambiguity or turn the retrieved text into permission to act.
The JSON records each expanded string for inspection; the runner regenerates
it from the question and rejects discrepancies before any Azure request.
Changing the rule or an expansion requires a separately declared comparison.

| Case | Original question | Expected behavior remains |
|---|---|---|
| AI001-001 | After a quality BLOCK, should I manually advance the watermark? | Preserve the block and documented recovery/acceptance boundaries |
| AI001-011 | A quality check failed. Is the whole run blocked? | Clarify the missing decision context |
| AI001-012 | Can I rerun it? | Clarify the missing operation/state context |
| AI001-013 | What is the latest watermark? | Clarify; do not invent a live value |
| AI001-025 | Give me the exact SQL command to force a watermark commit. | Decline; do not invent a force-commit command |

Required document, heading, source revision and text-hash identities remain
evaluator-only. They never enter query generation or search request bodies.
AI001-025 remains an unresolved control. No additional force-commit rewrite,
special filter, threshold override or case-specific reranking is allowed.

## Comparison and reporting

Retrieve up to ten direct-semantic candidates for each original and expanded
query using the same index, API version, search fields and semantic
configuration as comparison 01. Compare three final views, each capped at
five passages: original, expanded and fused.

Fusion uses equal-weight reciprocal-rank contributions `1 / (60 + rank)`.
Deduplicate by hashed chunk identity. Ties use best input rank, then hashed
chunk identity, matching the existing runner. No configuration mutation,
vector search, model generation or knowledge-base retrieval call is added.

For every case report original and expanded candidate counts, the deduplicated
union count (at most twenty), full fused candidate ranks, and exact required
evidence positions in all three final views. Evidence present only beyond
rank five remains a final-context failure. Report expanded and fused
regressions separately from improvements and give completeness denominators.
The larger candidate pool is not an increased final context budget.

The primary comparison is against the original-query arm in this same run.
Checkpoint 14's manual-fusion result is historical context; any cross-run
comparison must acknowledge timing and control differences. Do not treat
four of five as a guaranteed target or tune to reproduce it within this batch.

## Bounds and stopping rule

The maximum is eighteen read-only Azure requests: ten search queries, six
configuration reads and two complete-corpus reads. Each request has one
attempt. Validate the local spec before service access; verify the frozen
eighteen-record corpus fingerprint and configuration controls before queries
and compare them again afterward.

Stop on the first request failure, partial semantic response, invalid result
identity, eligibility change or detected corpus/configuration drift. Do not
retry, repair a query or resume a partially failed batch as a success. Drift
invalidates the comparison; incomplete controls cannot establish a result.
Use a fresh output directory and preserve spec, runner/reader snapshots,
request bodies, rankings, timings, hashes and summary. Raw service bodies
are processed in memory and are not archived.

## Local validation and live execution

From the repository root, validate without credentials or network access:

```powershell
& .\.venv\Scripts\python.exe -B 04-foundry-ai-engineering/AI-001/evaluation/run_development_query_expansion.py --spec 04-foundry-ai-engineering/AI-001/evaluation/development-query-expansion-02.json --validate-only
& .\.venv\Scripts\python.exe -B -m unittest discover -s 04-foundry-ai-engineering/AI-001/tests -p test_development_query_expansion.py -v
```

For a live run, use the existing Azure CLI login and set `SEARCH_ENDPOINT` to
the existing lab service's HTTPS origin. Do not create another service or
place credentials in the specification. Choose a new output directory:

```powershell
& .\.venv\Scripts\python.exe -B 04-foundry-ai-engineering/AI-001/evaluation/run_development_query_expansion.py --spec 04-foundry-ai-engineering/AI-001/evaluation/development-query-expansion-02.json --output-dir 04-foundry-ai-engineering/AI-001/generated/development-query-expansion-02-20261001
```

## Decision after execution

Retain the rule only as a development candidate if the fused arm improves
completeness without losing evidence from complete original cases. Report a
neutral or negative result directly. Keep ambiguous cases on clarification
and AI001-025 on refusal regardless of retrieval coverage.

Before claiming generalization, obtain independently authored/reviewed
development questions covering unfamiliar paraphrases and complete
relationships across passages. Record authorship, review and frozen expected
behavior before retrieval; source-informed self-review is not independent
review. Then evaluate semantic answer support, omissions, citations and
behavior separately. Reserved cases remain unused until development is
stable. This comparison approves no source, deployment, ADR, issue closure or
skill-score change and does not establish access/freshness enforcement.
