# Development query-expansion comparison 01

Status: frozen before live execution on September 29, 2026. This is a
retrieval-only development comparison. It makes no model calls and uses no
reserved evaluation cases.

## Question

Can a manually authored, intent-preserving query expansion improve required
evidence coverage without increasing the five-passage context budget or
regressing already complete development cases?

Five existing development questions are retained exactly. Each receives one
declared expansion that adds generic retrieval vocabulary without adding
occurrence-specific facts or naming expected source sections. Direct semantic
search retrieves ten candidates for the original and expanded query. The
comparison evaluates three five-passage views:

1. Original semantic top five.
2. Expanded semantic top five.
3. Reciprocal-rank fusion of both candidate lists, capped at five.

The fused arm has a larger candidate pool, but every arm has the same final
context budget. Candidate depth and final context depth are reported
separately.

## Cases and expansions

| Case | Category | Declared expansion |
|---|---|---|
| AI001-001 | supported | After a quality BLOCK, what documented recovery and state-commit controls determine whether the watermark may be manually advanced? |
| AI001-011 | ambiguous | When a pipeline quality check fails, what documented decision evidence determines whether the whole run is blocked? |
| AI001-012 | ambiguous | What documented information and checks are required before deciding whether an operation can be rerun? |
| AI001-013 | ambiguous | What documented state and verification information is needed to determine the latest watermark? |
| AI001-025 | unanswerable | What documented controls and governed corrective process apply to a request to force a watermark commit with SQL? |

Expected evidence identities, exact text hashes and revisions are evaluator
inputs only. They must not appear in search bodies. Retrieval completeness
does not change expected answer behavior: ambiguous cases still require
clarification, and AI001-025 still requires refusal rather than an invented
command.

## Bounds and stopping rule

The batch permits ten semantic query requests, six configuration reads and two
full-corpus control reads: eighteen read-only Azure requests total. Each
request has one attempt. The runner stops on the first request failure, partial
semantic response, corpus drift or configuration drift. There is no retry or
within-batch query editing.

The comparison is not a release gate. It does not test generated answers,
access control, freshness, latency, cost, source approval or serving behavior.
Do not run reserved cases or adopt the expansion/fusion strategy from this
single development batch.
