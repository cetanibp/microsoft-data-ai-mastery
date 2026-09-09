# Heading-search A/B experiment: completed lab checkpoint

Recorded 2026-09-09 from user-executed Cloud Shell validation summaries and pasted search responses. [Structured evidence](azure-heading-search-05.json). [Predeclared experiment](../azure-search/heading-search-experiment.md) at commit `84cc4415f9993d3ec2c7351ece3ce39577d3cf3e`; [baseline](azure-aligned-api-comparison-04.md).

## Outcome

Prefer `text_with_headings_v1` for further development experiments. It meets the criteria declared before execution: at least one required-passage rank improvement, no regressions, complete required context in the top five for all five cases, and preserved original records. This is a provisional field choice, not an accepted final ADR-009 decision or serving approval.

| Case | A: text | B: headings + text | Result |
|---|---:|---:|---|
| AI001-002: target write then failure | 3 | 2 | Improved |
| AI001-003: recovery completion | 1 | 1 | Unchanged |
| AI001-004: starting identifiers | 2 | 1 | Improved |
| AI001-005: routing failure after success | 1 | 1 | Unchanged |
| AI001-006: stale candidate after winner | 2 | 2 | Unchanged |

Two improvements, three unchanged, zero required-passage regressions. All five A ranks reproduced the managed h2 baseline. Both arms retained complete required context in the top five for 5/5 cases.

The complete recovery verification checklist stayed at rank 2 for completion. In the stale-candidate case it moved from rank 4 to 3, but the required table remained at rank 2. The first result still concerns an active competing attempt, not a completed winner. Target-write evidence in B also remains below an indirect triage result.

## Implemented and verified in the guided lab

1. Captured the full existing schema and 18 chunks locally; observed an ETag and no preexisting candidate field.
2. Checked indexer schedule/status: schedule null; latest execution success with an end time, 18 processed and zero failed. This was a precheck, not proof that no other actor could write during the experiment.
3. Prepared an additive schema update and 18 merge-only records. The derived value joins nonempty h1, h2 and text using two LF characters, preserving original strings and internal line endings.
4. Applied the schema update using the saved ETag; confirmed the new searchable field and en.lucene analyzer.
5. Submitted merges with existing keys and the new field only. All 18 returned success.
6. Read all records back and compared by key: 18 identities unchanged, original retrievable document fields unchanged, all candidate values match the prepared payload, all eligibility flags false. Search response annotations were excluded from value equality checks.

The generated key values and full infrastructure snapshots remain outside this public evidence. The [structured record](azure-heading-search-05.json) contains the four reported SHA-256 hashes for index-before.json, chunks-before.json, index-with-headings.json and heading-field.merge.json. These are user-side artifact fingerprints, not independent verification or a repository archive of those files.

## Controlled query settings and interpretation

Both arms queried the same index and 18 chunk boundaries using API 2026-04-01, simple query type, any search mode, count=true and top=5. Only searchFields changed between text and text_with_headings_v1. Both returned document identity, h1/h2, original text and runtime eligibility for review.

The unchanged original text remains the citation-bearing passage; the derived field adds searchable ancestry and is not an exact contiguous source substring. Both heading levels were added together, so their individual effects are not isolated.

Preserve the five-layer wording of AI001-003 for historical comparison. The source has four checklist subsection headings and six closure evidence areas. A generated answer would need to explain this distinction, but no generated answer was tested.

One duplicate target-write submission was recognized while completion results were requested. It was not counted as a completion run; correctly labeled completion responses supplied the actual case evidence.

This is a small development comparison, not held-out evaluation or a full relevance/answer rubric score. Different raw search scores or larger match counts do not prove better answer quality. Source-byte equality, runtime authorization, freshness, deletion/revocation, latency and cost remain untested here. Query timestamps and the actual CLI version were not supplied; the earlier indexer run timestamps must not be reused as experiment timestamps.

## Maintenance gap and next step

The new field was populated with a one-time merge and is **not maintained by the current indexer**. Any source/indexer refresh invalidates reliance on the derived snapshot until values are regenerated and verified. Use explicit searchFields; unscoped queries can now include both searchable fields. Query behavior can revert to text without removing the experimental field.

Next, complete [derived-field ingestion maintenance](../azure-search/heading-field-maintenance.md) before expanding retrieval. Preserve the transformation contract, false lab flag, original passages and pinned citations. The maintenance mechanism and lifecycle validation are still pending. No issue closure, skill-score increase, new Azure changes in this documentation turn, or final retrieval/production approval is claimed.
