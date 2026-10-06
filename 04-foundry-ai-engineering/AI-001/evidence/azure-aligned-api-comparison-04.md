# Aligned-API retrieval and live configuration checkpoint

Recorded 2026-09-09 from user-supplied live configuration and query responses. [Structured observations](azure-aligned-api-comparison-04.json). These are manually reviewed lab results, not independently executed Azure calls. Execution timestamps and pristine raw responses were not captured.

## What was verified

- All three indexes use `en.lucene` for text, no separate index/search analyzers, empty synonym maps and scoring profiles, no default profile, and BM25 with null b/k1 overrides in the readback.
- The two custom indexes also search title, but the experiment explicitly searches only text. Managed h1/h2 fields are not searchable.
- The managed indexer uses Markdown oneToMany parsing through h2, contentAndMetadata extraction, .md selection and zero failed-item tolerances. Content and headings map to separate fields.
- Its ConditionalSkill always returns false; the indexer maps that output to runtime_eligible. This assigns lab metadata; it does not evaluate authorization or freshness.
- All 18 managed chunks share corpus northstar-operations version 0.1.0, the expected manifest hash and source commit. Quality gates has ordinals 1–9, recovery 1–4 and triage 1–5. Paths/blob SHAs are consistent within each document, and every eligibility flag is false.
- A compact follow-up established exactly one complete pinned URL per document, matching its source path. Earlier truncated URLs were not treated as a complete verification.

Stored hashes and pinned URLs establish metadata consistency, not independent cloud-source byte equality. Readbacks capture selected fields, not full resource exports.

## Fixed comparison

All 15 queries now use REST API 2026-04-01, queryType=simple, searchMode=any, searchFields=text, top=5 and count=true. Questions remain verbatim; selected return fields are document_id,text,runtime_eligible. No filter or order-by was added.

| Case | Custom sections | Fixed windows | Managed h2 |
|---|---:|---:|---:|
| AI001-002 target write then failure | 3 | 2 | 3 |
| AI001-003 recovery completion | 2 | 2* | 1 |
| AI001-004 starting identifiers | 1 | 1 | 2 |
| AI001-005 routing-only failure | 1 | 1† | 1 |
| AI001-006 stale candidate | 2 | 1 | 2 |

* Before-closure phrase is still truncated; full checklist absent from top five.  
† Do not do header is still absent, with no restoration elsewhere in the top five.

All 15 required-passage ranks reproduce [checkpoint 03](azure-markdown-h2-comparison-03.md). Managed h2 preserves complete required context in the top five for all five inspected cases. For completion, it returns the full closure text at rank 1 and intact verification checklist at rank 2; the custom section rank 1 contains only the heading/intro.

These observations show no change in the measured ranks after API alignment. They do not prove API versions are equivalent for all queries or remove differences in chunk content, corpus statistics, heading placement or formatting. No cross-index score superiority is claimed.

## Interpretation and next step

Retain managed h2 as a provisional development candidate. Its advantage here is context preservation, not consistently higher ranking. Starting identifiers still ranks 2, while target-write evidence ranks 3. An active competing attempt remains distinct from a stale candidate after a completed winner.

Preserve the ambiguous five-layer query for comparison: four subsection headings group the verification checklist, while six evidence areas appear in the closure sentence. A later wording correction needs a separately versioned case.

Proceed with the [controlled heading-search experiment specification](../azure-search/heading-search-experiment.md). It is prepared but not deployed or executed. Full evaluation, vector/hybrid retrieval, model answers, reserved cases, access/revocation/freshness evidence, latency/cost and ADR-009 remain open. Dataset execution statuses, issue completion and skill scores are unchanged.
