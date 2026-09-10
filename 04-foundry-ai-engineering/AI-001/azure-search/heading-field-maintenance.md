# Next increment: maintain separate searchable headings

Status: mappings implemented in the guided lab; missing-target restoration verified in [checkpoint 07](../evidence/azure-heading-maintenance-07.md). Changed-source fixtures and retrieval repeat remain pending. Owner: AI-001 #13. Depends on [checkpoint 06](../evidence/azure-separate-headings-06.md).

## Current decision and invariant

Separate searchable headings supersede checkpoint 05's provisional combined-field preference. The copies were originally populated manually; current indexer mappings now populate them during indexing, demonstrated by restoration of two deliberately cleared values. Every indexed chunk must satisfy heading_h1_search_v1 == heading_h1 and heading_h2_search_v1 == heading_h2, preserving Unicode, empty/null values and original text/provenance. Keep runtime_eligible=false.

The earlier combined transformation remains historical evidence; implementing automatic concatenation is deferred. Explicit searchFields must select the intended arm so additional searchable fields cannot accidentally change the comparison.

## Reproduction procedure and remaining validation

1. Capture current indexer, schema, skillset and all 18 records locally. Preserve raw response bytes and decode UTF-8 or the observed cp1252 without replacement. Keep credentials and generated source-location keys outside Git.
2. Verify current Microsoft documentation and the live Markdown paths before preparing additional mappings from /sections/h1 and /sections/h2 to their searchable copies. These paths already supply original heading metadata; verify support for mapping each source to both targets. Preserve existing mappings, source settings and false-flag skill.
3. Prepare a bounded configuration diff and rollback configuration. Check source access and current indexer execution before applying; do not assume an old SAS remains valid.
4. Apply through the guided lab and reprocess the frozen corpus using the documented mechanism. Verify per-item outcomes and exact equality of both heading copies across all 18 records, unchanged original fields/provenance and false flags.
5. Repeat unchanged ingestion to verify idempotency. Use a separately versioned synthetic fixture for changed headings, missing/empty headings and Unicode; do not edit the frozen baseline. Confirm copies refresh with their originals and capture updated source provenance.
6. Define incomplete/failed-population handling: do not declare the development candidate ready until all expected records pass. Track obsolete-chunk deletion and permission/revocation behavior separately.
7. Repeat all five queries in one batch after maintenance, comparing the frozen-source ranks and complete evidence with checkpoint 06. Preserve raw/normalized responses and execution timestamps.

## Completion evidence

Versioned configuration diff, exact readback for all 18 chunks, per-item outcomes, unchanged-input replay, versioned update/null/Unicode fixtures, failure handling and query comparison. Distinguish artifact checks from live user-executed evidence.

Automatic target-field population has been demonstrated. The full lifecycle plan remains incomplete; absent/empty source headings and changed-source fixtures are untested. Broader development questions, model answers, held-out evaluation, serving authorization, latency/cost and ADR-009 remain open.
