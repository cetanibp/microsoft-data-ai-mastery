# Azure-managed Markdown h2 retrieval checkpoint

Recorded 2026-09-09 from user-supplied lab responses; execution timestamps were not captured. [Structured observations](azure-markdown-h2-comparison-03.json). Builds on the [two-index development baseline](azure-development-retrieval-02.md).

## Setup and provenance

The same three Northstar documents reference source commit `746199302b9a0275e7dba8e1e3c8ca5586043c89`. The baseline has 24 custom Markdown-section chunks and 15 fixed windows (800 characters, 120 overlap). The Azure-managed Markdown `h2` candidate, `northstar-ops-markdown-h2-v1`, contains 18 chunks: quality gates 9, recovery 4, triage 5.

The metadata inspection reported document IDs, heading metadata, ordinal positions, pinned GitHub source URLs and `runtime_eligible=false` for all 18 chunks. Recovery content was inspected in ordinal order. Its complete seven-row table retains the **Do not do** header; the verification introduction and all deeper checklists remain together; the closing **before closure** instruction is complete. This is manual review of supplied responses, not independent byte-level verification of the cloud source against Git.

The five questions were preserved verbatim with `queryType=simple`, `searchMode=any`, `searchFields=text`, `top=5` and `count=true`; no document filter or order-by was used for relevance checks. The earlier baselines used REST API `2024-07-01`; this candidate used `2026-04-01`. The structured file retains exact questions, candidate match counts, required-passage ranks and scores. Raw responses are not archived as pristine API JSON.

## Results

Ranks identify the passage containing the required evidence, not a generated answer.

| Development case | Custom sections | Fixed windows | Azure Markdown h2 | Candidate content review |
|---|---:|---:|---:|---|
| AI001-002: target write then failure | 3 | 2 | 3 | Same fixed boundary, idempotent merge, and both prohibitions intact |
| AI001-003: recovery completion | 2 | 2* | 1 | Full closing instruction; complete verification checklist at rank 2 |
| AI001-004: triage starting identifiers | 1 | 1 | 2 | At least one, all identifier options, and sensitive-information caution intact |
| AI001-005: routing failure after ingestion success | 1 | 1† | 1 | Restore routing and replay evaluator/router; ingestion-rerun prohibition explicit |
| AI001-006: stale candidate after another winner | 2 | 1 | 2 | Keep winner, abandon stale candidate, reconcile, assess replay; no forced commit |

* Fixed window truncated the final before-closure qualifier.  
† Fixed window lost the table header identifying the prohibited action.

Complete required context is present within the candidate's top five for 5/5 inspected questions. This is a narrow manual evidence-completeness result, not full dataset recall, answer groundedness or a production pass. The candidate does not consistently improve ranking: triage starting evidence falls from rank 1 to 2; target-write evidence remains rank 3. Indirect results can outrank the answer-bearing passage.

For stale candidates, the top result concerns another attempt **still active**, whereas the question concerns an attempt that **already won**. A future answer must distinguish those conditions.

## Question ambiguity and context assembly

AI001-003 asks for five layers. The verification checklist has four subsection headings: Execution, Data and quality, State, Observability. The closure sentence names six evidence areas: execution, data, quality, state, observability, ownership. A grounded answer should explain this structure and retain the residual-risk/remediation instruction. Preserve the original query for baseline comparison; version any revised wording separately.

Azure exposes `heading_h2` separately from `text`, while the custom section chunks contain their headings in text. Future model context should include document identity, headings, passage text and pinned citation together. That context assembly has not been implemented or evaluated.

## Interpretation and remaining controls

Continue with Azure-managed h2 as a **provisional development candidate** for preserving these documents' context. No final ADR-009 retrieval decision is made. This checkpoint records the observed managed approach instead of implementing the previously proposed custom structure-aware chunker.

The comparison measures implemented approaches, not chunk size alone: API versions and searchable heading content differ, and live analyzer/schema equivalence has not been verified. Corpus size is small and these five supported cases were already used during development.

Full index, indexer and skillset exports, exact parser configuration, execution dates, CLI version, latency and cost were not captured in the supplied evidence. No vector/hybrid retrieval, generated-answer evaluation, reserved-case execution, approval, access/revocation/freshness enforcement or serving deployment is established. A false eligibility field records draft status; it does not enforce authorization. Existing dataset end-to-end execution statuses remain unchanged.

## Next checkpoint

Capture sanitized live index/indexer/skillset definitions and document analyzer/field differences. Align query API versions and define a controlled searchable-heading comparison before changing retrieval behavior. Then repeat the fixed development questions, reporting ranking regressions as well as content preservation. Preserve both original baseline indexes and results. Vector/hybrid and answer-generation comparisons remain later work.
