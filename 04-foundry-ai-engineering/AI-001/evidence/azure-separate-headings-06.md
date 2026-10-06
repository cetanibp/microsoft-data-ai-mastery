# Separate searchable headings — checkpoint 06

Recorded: 2026-09-10. Evidence: user-supplied lab responses, manually reviewed. See [structured observations](azure-separate-headings-06.json) and the earlier [combined-field experiment](azure-heading-search-05.md).

## Result and provisional decision

Prefer separate searchable headings for the next development increment. On the same 18 managed h2 chunks, the primary passage improved once and matched four times; required context remained complete within top five for all five cases.

| Question | Combined primary rank | Separate primary rank |
|---|---:|---:|
| Failure after target write | 2 | 1 |
| Recovery completion | 1 | 1 |
| Triage starting identifiers | 1 | 1 |
| Routing failure | 1 | 1 |
| Stale candidate after another winner | 2 | 2 |

Primary evidence ranked first for 3/5 combined and 4/5 separate queries. Recovery completion's full checklist remained second in both. For the stale-candidate question, the supporting verification checklist regressed from third to fourth. The primary table stayed second; the active-competing-attempt stop condition still ranked first, despite differing from a completed winner.

This supersedes checkpoint 05's provisional combined-field preference, not its recorded results. It is not a final ADR-009 decision or generated-answer quality result.

## Controlled comparison

Both arms used API 2026-04-01, simple query type, any search mode, top five, count enabled, no filter/orderby and the original five questions. The combined arm searched text_with_headings_v1 only. The separate arm searched heading_h1_search_v1,heading_h2_search_v1,text only. No custom scoring profile or field weighting was added. Compare ranks and completeness rather than raw score increases across field layouts.

The two additive Edm.String fields are searchable/retrievable with en.lucene and hold exact original heading copies. Original heading metadata and text remain intact. These copies let the existing lab compare layouts without rebuilding the original heading fields. A clean future schema is a separate decision.

## Mutation and recovery evidence

The schema submission initially produced an error; later inspection showed both fields present with the intended settings. Do not describe that submission as a confirmed successful conditional update. A new Cloud Shell session lost access to the original snapshot directory. The user recovered a fresh baseline locally using VS Code Git Bash, Azure CLI 2.90.0 and Python 3.14.2.

The rebuilt 18-record merge payload matched the earlier reported SHA-256:
`4a349c8323de838e09c0def36a67c15669f9f336d7ae0a560d11b612455ac5ca`.

All 18 merges succeeded. Subsequent readback reported unchanged chunk identities, preexisting fields and combined values; separate heading copies matched originals and every runtime_eligible flag remained false. This preservation check uses the recovered local pre-merge baseline.

Windows CLI response bytes required cp1252 decoding when utf-8-sig failed. The workflow preserved raw responses, parsed JSON strictly, and wrote UTF-8 JSON with ensure_ascii=True. It did not replace undecodable bytes or silently normalize source strings. Local raw files are not included in this repository; pasted results contain formatting artifacts and are not byte-exact archives.

## Content findings and limitations

- Target-write and routing tables preserve the recovery actions and Do not do column.
- Triage retains at least one, all identifier options, and the sensitive-information restriction.
- Recovery closure retains before closure and the full nested checklist. The original five-layer question remains ambiguous: four checklist headings, six closure evidence areas.
- Stale-candidate handling preserves keep winner, abandon stale candidate, reconcile target, assess replay, and no forced stale commit.
- Five development cases do not establish broader generalization, answer grounding, access enforcement, latency or cost. Reserved questions remain unused.
- Both heading candidates were populated manually. The current indexer has not been changed to maintain them. The false flag is lab metadata, not serving authorization.

## Next increment

Follow [heading maintenance](../azure-search/heading-field-maintenance.md) for the separate copies. Preserve the frozen corpus and explicit searchFields controls, validate unchanged and changed-source ingestion, then expand development cases before generated-answer evaluation. AI-001, ADR-009 and skill scores remain unchanged in completion status.
