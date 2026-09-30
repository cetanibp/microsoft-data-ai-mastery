# Checkpoint 13: force-commit retrieval gap isolated

Executed September 21, 2026 Pacific time (September 22 UTC). Follows
[checkpoint 12](azure-answer-reference-12.md) for AI-001
[#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13).

**Finding: the required passage is indexed and retrievable, but ranks below
five for the original question. The knowledge-base request also exhibits
threshold sensitivity that excludes it even with an eighteen-document limit.**
Keep the existing configuration; neither tested intervention satisfies the
original top-five evidence requirement.

## First frozen comparison

[Diagnostic 01](../evaluation/force-commit-diagnostic-01.md) declared three
existing queries and four retrieval arms before execution. All 20 requests
succeeded: 12 query requests and eight pre/post control reads.

The target is the complete Corrective state action passage from
`northstar-recovery`, verified by exact text hash and pinned source revision.
Numbers below are its position; absent means it was not returned at that limit.

| Query | Direct keyword, top 18 | Direct semantic, top 18 | Knowledge base, max 5 | Knowledge base, max 18 |
|---|---:|---:|---:|---:|
| Original force-commit question | 8 | 9 | Absent | Absent |
| Previously generated automatic rewrite | 8 | 9 | Absent | Absent |
| Source-informed manual diagnostic | 1 | 1 | 1 | 1 |

For the original and automatic queries, both direct-search arms returned ten
documents. The knowledge base returned five or eight respectively. Thus a
larger knowledge-base output window alone did not restore the passage.
Direct semantic responses reported no partial-response reason or type.
The manual query changes command-seeking wording into a question about
documented corrective procedure; its success is not automatic-rewrite success.

The target was present among keyword candidates, so missing ingestion or
complete exclusion from keyword candidate generation is not the explanation
for this controlled run. Semantic ranking placed it one position lower, still
outside the top five. Direct and knowledge-base request contracts are not
identical, so this comparison alone did not establish why their output differed.

## Separately declared follow-up

[Diagnostic 02](../evaluation/force-commit-diagnostic-02.md) was declared after
the first results. It repeated the original-query knowledge-base baseline and
changed one request parameter per intervention. All eleven requests succeeded:
three queries and eight control reads. No stored configuration was changed.

| Original query, max 18 documents | Returned | Target position | Target reranker score |
|---|---:|---:|---:|
| Repeated baseline | 8 | Absent | Not available |
| `rerankerThreshold: 0` | 10 | 9 | 0.044352345 |
| `resultsProcessing: none` | 10 | 8 | Omitted, as expected for this mode |

The repeated baseline reproduced all eight positions and scores from
diagnostic 01. The zero-threshold arm retained the same eight documents and
added two, including the target. Shared-document scores changed slightly and
positions four and five swapped; this is not an exact deterministic slice of
one ranking. The no-rerank arm omitted reranker scores on all ten references,
providing observed evidence that the requested mode took effect.

The API defines `rerankerThreshold` as the score required for response inclusion
and allows per-request reranking controls; see the
[retrieve API reference](https://learn.microsoft.com/en-us/rest/api/searchservice/knowledge-retrieval/retrieve?view=rest-searchservice-2026-08-01-preview).
These observations support threshold sensitivity as a contributor to the
knowledge-base omission. They do not identify the numerical effective default
or prove undocumented internal filtering. The direct-semantic target score
was 1.3647912740707397; do not treat it as interchangeable with the
knowledge-base score or use one to infer the other's threshold.

## Controls, provenance and validation

Both batches used `2026-08-01-preview`, the existing index/source/knowledge
base, the three separate-heading/text search fields, and
`northstar-semantic-v1`. The source was text-only; preflight required no vector
fields or scoring profiles. The knowledge base used minimal effort,
`extractiveData`, one source, and no configured generative models.

All 18 indexed records matched the historical corpus fingerprint before and
after each batch, including source text and false eligibility flags. Full
configuration hashes remained unchanged within each batch. No source upload,
index update, model generation, reserved-case execution or runtime deployment
occurred. Request-level overrides do not change the offline reference's frozen
case inputs or repair its historical missing passage.

The [machine-readable evidence](azure-force-commit-diagnostic-13.json) contains
all 15 query bodies, selected rankings and activity metadata, per-call timing,
raw-response hashes, and script/specification provenance. Corpus and
configuration control calls bring the total to 31 Azure read-only requests.
No tokens, private endpoints or Azure-derived document IDs are exported;
document identities are hashed. Raw service bodies were processed in memory
and are not archived, so their hashes are provenance records rather than
locally replayable responses. Timings include CLI overhead; currency cost
was not measured.

Seven [local contract tests](../tests/test_force_commit_diagnostic.py) passed.
They cover frozen request construction, evaluator-only target data, corpus
drift, exact evidence versus mere heading matches, scope/eligibility limits,
single-option follow-up requests, and stopping after a failed first request.
Tests use synthetic fixtures and make no Azure calls. The earlier
[offline-reference tests](../tests/test_offline_reference.py) remain separate.

## Decision and next learning step

Do not adopt a zero threshold, disable reranking, or expand every answer to
eighteen passages based on one known case. The target remains at rank eight
or nine, so top-five completeness is unresolved. Lowering a threshold can
recover weakly ranked evidence without making it relevant enough to select.

Next, define a development comparison of intent-preserving query expansion
or combined retrieval, with original questions retained and an unchanged
total context budget. Include other supported and ambiguous cases to measure
regressions; keep the source-informed manual query outside automatic-success
metrics. Inspect source support and completeness separately from retrieval
scores before adopting a candidate. A refusal still must not invent SQL or
attribute a corrective procedure to missing evidence.

No issue closure, source approval, ADR acceptance or skill-score change.
