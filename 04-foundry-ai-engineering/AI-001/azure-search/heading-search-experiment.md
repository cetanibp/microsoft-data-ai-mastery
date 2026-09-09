# Controlled heading-search experiment

Status: prepared specification, not deployed or executed. Baseline: [aligned-API checkpoint 04](../evidence/azure-aligned-api-comparison-04.md).

## Question and scope

Does including the already extracted h1/h2 headings improve the five development queries when the 18 managed chunk boundaries and source text remain fixed?

Compare two fields on northstar-ops-markdown-h2-v1:
- A: searchFields=text, the existing baseline.
- B: searchFields=text_with_headings_v1, a new field containing heading_h1, heading_h2 and text in that order.

Use one combined field per arm. Searching both original text and its duplicated combined field would introduce another factor. Do not change the original headings' searchable attributes.

## Proposed field and transformation

```json
{
  "name": "text_with_headings_v1",
  "type": "Edm.String",
  "searchable": true,
  "retrievable": true,
  "filterable": false,
  "sortable": false,
  "facetable": false,
  "analyzer": "en.lucene"
}
```

Transformation version 1:
1. Read heading_h1, heading_h2 and text for each existing chunk key.
2. Require text to be a nonempty string; accept null/empty headings by omitting them.
3. Join the nonempty original values with exactly two LF characters. Do not strip, normalize, rewrite, summarize or deduplicate their contents.
4. Preserve original text, headings, chunk identities, provenance and runtime_eligible=false.

This is derived search text with ancestry from three fields, not an exact contiguous source substring. Keep citations attached to the original document. Any future model-context assembly must be evaluated separately.

Microsoft documents that adding a field can be done without rebuilding; changing existing searchable attributes requires a rebuild. Existing documents initially have null values for a new field, so population and readback are required. See [update/rebuild guidance](https://learn.microsoft.com/en-us/azure/search/search-howto-reindex), checked 2026-09-09.

## Guided implementation checkpoints

1. Read the full current index schema and all 18 chunks locally in Cloud Shell. Keep generated keys and full infrastructure definitions out of public evidence. Inspect indexer schedule/status to ensure source updates will not change the corpus during the experiment. Capture UTC time, CLI version and sanitized configuration hashes.
2. Prepare a full schema update from that readback, adding only the proposed field. Preserve all existing definitions. Use the current ETag for concurrency checking; stop on drift. An existing candidate field must match the specification exactly before reuse.
3. Prepare merge-only records containing the existing chunk key and the new field. Do not use upload or mergeOrUpload: a missing key must fail rather than create a partial record. Review the 18 transformations and sanitized examples before submitting.
4. Apply the reviewed schema addition and merge batch in the guided lab. Check every per-document status. Read back all records and verify exact candidate values, 18 unique keys and unchanged original fields. The indexer does not maintain this derived field yet; any source/indexer refresh invalidates the snapshot until it is regenerated and verified.
5. Rerun arm A to verify the baseline after the additive change. Query the five original development questions against each arm using API 2026-04-01 and identical simple/any/top-five settings, changing only searchFields. Return the same original evidence fields for manual context review.
6. Record per-case ranks, required evidence, context completeness, selected field, timestamps and sanitized results. Evaluate all five cases before deciding; no reserved questions or question rewrites.

The addition needs no fourth index. All three existing indexes and their original passages are retained. Explicit searchFields is required for every comparison because unscoped queries can now search the added field.

## Decision criteria declared before execution

- Every original record and field must remain unchanged, with all false eligibility flags retained.
- Arm A must reproduce the documented required-passage ranks before evaluating B.
- B must retain complete required context within top five for all five cases, including prohibitions and closure wording.
- Prefer B for further development only if at least one required-evidence rank improves and none regresses. If results are mixed or unchanged, retain A and document the tradeoff.
- Scores across different fields are not calibrated quality metrics; judge ranks and source support.
- This tests adding both h1 and h2 together; it does not isolate each heading level or establish overall answer quality.

Rollback of query behavior is to search text explicitly. The added field remains until a future planned rebuild; physical field removal requires a rebuild. No index deletion, rebuild, tier change, model deployment or source-policy promotion is part of this experiment.
