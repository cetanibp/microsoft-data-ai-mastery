# Checkpoint 15: fixed-rule query expansion and fusion

Executed October 1, 2026 Pacific time (October 2 UTC). Follows the manually
expanded fixed-budget comparison in [checkpoint 14](azure-development-query-expansion-14.md).

**Finding: the fixed question-only expansion raises exact required-evidence
completeness from three of five to four of five development cases, but fusion
loses that gain and remains at three of five. The force-commit gap remains.**

## Frozen comparison

[Comparison 02](../evaluation/development-query-expansion-02.md) fixed one
suffix for all five existing development questions before execution. Query
generation received only the original question and the fixed rule; required
evidence identities remained evaluator-only. Each original and expanded
semantic query retrieved up to ten candidates. Original, expanded and
reciprocal-rank-fused final views each retained at most five passages.

The frozen canonical spec hash matched the
[preparation record](development-query-expansion-02-preparation.json).
All eighteen read-only experiment requests succeeded: ten search queries,
six configuration reads and two full-corpus reads, each with one attempt.
An additional Azure resource inventory read located the existing service
before the batch; it is not part of the eighteen experiment requests. No
model call, reserved-case execution, configuration mutation or index write
occurred. Raw service bodies were processed in memory and were not archived.

## Results

Positions are exact required passages in each final five-passage view. The
union column counts deduplicated candidates before the final context cap.

| Case | Original top five | Expanded top five | Fused top five | Original / expanded candidates | Candidate union |
|---|---:|---:|---:|---:|---:|
| AI001-001 | 1, 3 | 2, 3 | 1, 3 | 10 / 10 | 11 |
| AI001-011 | 4 | 4 | 4 | 10 / 10 | 10 |
| AI001-012 | missing, 1 | 5, 1 | missing, 1 | 2 / 10 | 10 |
| AI001-013 | 5, 4 | 2, 3 | 2, 3 | 7 / 10 | 10 |
| AI001-025 | missing | missing | missing | 10 / 10 | 10 |

Completeness is **3/5 original, 4/5 expanded and 3/5 fused**. Neither the
expanded nor fused arm loses completeness on any of the three complete
original-query cases: **0/3 original-baseline regressions** for each arm.
Fusion nevertheless loses one complete expanded-query case, AI001-012.
The declared regression metric compares against complete original cases;
its zero does not mean fusion preserved every expansion improvement.

For AI001-012, the original query again returned only two candidates.
The expansion retained Select a pattern first and brought Procedure into
fifth place. Fusion kept Select a pattern first but moved Procedure to sixth.
Thus the required passage exists in the larger pool while the final context
remains incomplete. The recorded source ranks and full fused ordering make
this displacement inspectable; it is not a corpus omission. The original
question still requires clarification even when expanded retrieval is complete.

For AI001-025, Corrective state action ranked ninth in the original,
expanded and fused candidate lists. It remained outside every five-passage
view. The fixed suffix did not reproduce checkpoint 14's manually expanded
rank-six candidate or repair the force-commit gap. No within-batch rewrite
or additional query was attempted.

## Controls and provenance

The exact eighteen-record corpus fingerprint matched the historical baseline
before and after execution. Index, knowledge-base and knowledge-source hashes
also matched before and after, and the canonical configuration hashes matched
checkpoint 14. Original-query required-evidence positions reproduced that
checkpoint. These controls support the within-run comparison; the historical
manual expansions were not a simultaneous arm in this batch.

[Selected JSON evidence](azure-development-query-expansion-15.json) records
per-case positions, complete-view counts, candidate unions, full fused ranks,
request metrics, controls and hashes. Request, ranking, summary and runner/reader
snapshot files remain under local ignored
`generated/development-query-expansion-02-20261001`.

The preparation suite recorded 44 passing tests and one Windows symlink-privilege
skip (45 total), including twelve query-expansion contracts. The runner and
test code were not changed for this execution. Local contract tests and a
completed retrieval experiment do not establish answer correctness or
application readiness.

## Decision and next step

The fixed-rule fused arm did not improve completeness, so this batch does
not meet the declared condition for retaining it as an improved fusion
candidate. Expansion alone remains a development observation worth testing
on independently authored/reviewed questions; it is not an adopted retrieval
configuration. The rule was designed after earlier results and the same five
known cases were reused.

Next, obtain and freeze independently reviewed development questions with
unfamiliar phrasing and relationships spanning multiple passages. Compare
original retrieval, this unchanged fixed expansion and fusion in a separately
declared batch, reporting fusion losses relative to both original and expanded
views. Do not tune another suffix or force-commit rewrite on this executed
batch. Semantic answer support, clarification/refusal, access/freshness and
reserved evaluation remain separate work.

No source approval, issue closure, ADR acceptance, deployment or skill-score
change.
