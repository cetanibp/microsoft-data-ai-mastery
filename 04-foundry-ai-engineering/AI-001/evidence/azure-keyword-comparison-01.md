# First Azure keyword retrieval comparison

Recorded: 2026-09-07. Evidence: user-supplied Azure response bodies and user-reported setup/count checks. The assistant did not connect directly to the search service. This is an exploratory lab observation, not a completed evaluation or serving-readiness claim.

## Setup and ingestion

User confirmed Free / West US, roles-only authentication, both lab indexes created, reproducible preparation hashes, and successful upload responses. Initial count reports were sections=24/windows=0; after an explicit windows upload, the user reported windows=15. Earlier 200 responses cannot be attributed confidently to a particular destination. Full upload responses were not retained. Four pasted search responses demonstrate queryable content with runtime_eligible=false and pinned source URLs.

Manifest SHA-256: 8cfa8f75cc7cbbe505fd09d4ad1696b67b6b3d3c9ce2077568edb1628745ff6e.
Payload SHA-256:
- sections: 409392a74732bf8545a7559736c58341eba68fa2a86e2045edccd9aeb154a269
- windows: eaee154d6d9fe989ed328edf00f814e0014d2d208bd0a1925a89c88ae319b311

REST API: 2024-07-01. Query: watermark quality blocked. queryType=simple, searchMode=any, top=5, count=true. Only index and searchFields varied. No semantic/vector query or model generation was used. Request timestamps, latency and exact CLI version were not captured.

## Results

| Strategy | searchFields | Match count | Explicit FAB-003 blocking rule rank | Distinct sources in top 5 |
| --- | --- | --- | --- | --- |
| Markdown sections | title,text | 17 | 5 | 1 |
| Fixed windows | title,text | 14 | 2 | 3 |
| Markdown sections | text | 14 | Not in returned top 5 | 2 |
| Fixed windows | text | 12 | 5 | 3 |

Explicit rule marker: FAB-003 Initial vertical slice, instruction to prevent watermark commit when a required blocking check fails. This marker is not the dataset's entire required evidence set.

Returned sections/chunks in order:
- sections/title,text: Status; document introduction; Issue acceptance criteria; Objective; Initial vertical slice.
- windows/title,text: introduction/Status/Objective; Initial vertical slice/Issue acceptance criteria; triage Procedure; Issue acceptance criteria/Repository contents; recovery Execution/Data and quality/State/Observability.
- sections/text: Status; document introduction; triage Trigger; Issue acceptance criteria; Objective.
- windows/text: introduction/Status/Objective; triage Procedure; recovery Execution/Data and quality/State/Observability; recovery introduction/Select a pattern; Initial vertical slice/Issue acceptance criteria.

Stable evidence chunk IDs:
- Section explicit rule: 43badcc62d589f6b7be09ca5476a3fc94e6049f0c3bffe83ce66f09c5f1f8f3d
- Window explicit rule: fbaccfa5cfb39f621d4eba35dbc71bf44f4745ad14e90aed92771dd3f86ba2e0
- Window recovery state: 3e55d243c33d2c931febac68338d5946e815f2a3069f50bd0a9f3bc97f939614
- Window recovery patterns: cd3778fbbc674314d74c701582d000225f345770b526431384ea567152286e3c

## Interpretation

Removing title reduced the explicit rule's rank in both strategies. It also brought useful recovery content higher in the window results: State at rank 3 and Select a pattern at rank 4. Therefore tracking one marker's rank alone would miss important evidence improvements.

Development case AI001-001 requires recovery Select a pattern AND State. Their relevant content is visible together in the window/text top five. Window/title,text contains State but not Select a pattern in its top five. Neither section result contains these recovery sections. The exploratory query was manually shortened from the question; do not label these observations as an executed official case, formal recall score, or end-to-end behavior pass.

Window chunks visibly split sentences/tables, but the relevant Quality BLOCK table row and State instructions are intact in the returned passages. Section chunks preserve complete sections. This one example does not establish an overall winner or justify changing the default.

## Next checkpoint

Run broader supported development questions verbatim using fixed query settings and both indexes. Record case ID, source revision, index/schema/payload identifiers, query, ranked chunk IDs and required-evidence coverage. Inspect actual supporting text, not just section_names, because a window can overlap a heading without preserving the needed statement. Keep reserved questions out of tuning. Access/freshness fixtures and answer generation need separate execution support.

Learning: [BM25 scoring and embedded ranking video](https://learn.microsoft.com/en-us/azure/search/index-similarity-and-scoring), [query fields and matching settings](https://learn.microsoft.com/en-us/azure/search/search-query-create).
