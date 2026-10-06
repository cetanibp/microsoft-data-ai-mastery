# Supported development retrieval checkpoint: AI001-002 through AI001-006

Recorded 2026-09-08 from user-supplied Azure search responses. [Structured observations](azure-development-retrieval-02.json). This extends [the first keyword experiment](azure-keyword-comparison-01.md).

## Fixed comparison

Questions were sent verbatim with REST API 2024-07-01, queryType=simple, searchMode=any, searchFields=text, top=5 and count=true to each existing index. These are manual retrieval-component checks, not end-to-end case executions. Source snapshot and manifest hash are in the structured evidence.

| Case | Sections: required passage rank | Windows: required passage rank | Finding |
| --- | --- | --- | --- |
| 002 target write then failure | 3 | 2 | Both preserve relevant row and headers. |
| 003 recovery completion | 2 | 2 | Window retains assertions but loses final before-closure qualifier. |
| 004 starting identifiers | 1 | 1 | Both retain list, at-least-one qualifier and caution. |
| 005 routing-only failure | 1 | 1 | Section preserves prohibition; window lacks Do not do header. |
| 006 stale candidate | 2 | 1 | Both preserve full relevant row and headers. |

Both strategies retrieved text overlapping the required source section in all five cases. That alone is insufficient: window case 005 lacks explicit context identifying the prohibited action. Cases 002/003/004/006 satisfy the listed assertions on manual text review, with case 003's additional context defect recorded separately. Do not convert these observations into a full rubric score or model-answer safety result.

## Concrete failure modes

1. Heading-only section chunks occupy ranks without the child content needed to answer. Recovery verification ranked first in case 003 with only an instruction to verify every applicable layer. Runbook — Triage appears as a standalone heading in other runs.
2. Character windows cut sentences and table rows. Case 003 cuts the closure timing phrase. Case 005 preserves the routing row but omits the column headings that distinguish recommended and prohibited actions.
3. Overlap does not ensure the needed adjacent chunk is retrieved. In case 005 none of the five returned passages supplies the recovery table header. In case 006 the full header-bearing chunk is first and a partial duplicate appears fourth.
4. A high-ranked related condition is not automatically applicable. Case 006 section rank 1 concerns an active competing attempt, whereas rank 2 addresses a stale candidate after another winner.

## Proposed next increment (historical)

Superseded by the observed [Azure-managed h2 checkpoint](azure-markdown-h2-comparison-03.md). The custom structure-aware implementation below was a proposal, not completed work.

Prepare a structure-aware candidate locally: retain table rows with column headers; avoid standalone heading-only passages by combining appropriate parent/child content; retain sentence boundaries, source offsets and pinned citations. Preserve the two baseline indexes. A third lab index is a later candidate, subject to checking that the remaining slot is still free. No new chunker, index, paid resource or source-policy approval was created in this checkpoint.

Any synthesized repeated headers must be traceable to source spans; do not label transformed text as a single exact contiguous source substring. Compare against the fixed baseline questions and document regressions. No overall strategy winner is selected.

Learning: [Microsoft chunking techniques and context considerations](https://learn.microsoft.com/en-us/azure/search/vector-search-how-to-chunk-documents). The hand-written 800-character windows in this experiment are not a test of Azure's built-in Text Split skill, which can respect sentence boundaries.
