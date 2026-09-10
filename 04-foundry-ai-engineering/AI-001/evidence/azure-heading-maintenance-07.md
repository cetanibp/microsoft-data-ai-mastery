# Heading maintenance — checkpoint 07

Recorded 2026-09-10. Evidence: user-executed Azure lab summaries, manually reviewed; not independently executed. See [structured evidence](azure-heading-maintenance-07.json).

## Outcome

The indexer now maps /sections/h1 to heading_h1_search_v1 and /sections/h2 to heading_h2_search_v1, alongside the original mappings. Automatic population was demonstrated by clearing both searchable copies on the triage Required starting evidence chunk, verifying the null values, then resetting and running ingestion without submitting the saved restore payload.

The fresh probe execution ran from 2026-09-10T19:30:25.004Z to 2026-09-10T19:30:26.285Z: 18 processed, zero failures, errors or warnings. Both headings were restored exactly, including the em dash. All 18 records matched the original snapshot and retained runtime_eligible=false.

## Configuration and troubleshooting

- The prepared two-mapping payload SHA-256 was 6a1d775e13107fa006b74dee7c5cb9e3d29105b13b5c66f5c15fa0e4840565c2.
- Initial update failed during source-access validation; readback retained original mappings.
- A renewed Read/List container SAS was supplied privately. The data-source update preserved other settings. Expiry was suspected, not independently established as the original cause; no storage network change was recorded.
- The next indexer update returned 412. Fresh readback showed only an ETag change, with identical original configuration. A guarded retry with the refreshed ETag succeeded and matched the prepared candidate exactly.
- SAS expiry is 2026-09-11T12:16:18+00:00. Future indexing requires valid source access; the credential itself is not in repository evidence.
- Status initially showed reset and zero processed. Only the subsequent fresh success was treated as execution evidence.

## Validation sequence

1. Preserve all 18 chunks before ingestion. Snapshot captured 2026-09-10T04:28:25.727688+00:00; SHA-256 110a6b2520c2dae6673acf2dd1f74d739f0ed64e69002b2d8192c0fe7cd94932.
2. Reset/run: first success 2026-09-10T04:36:14.7Z–04:36:14.984Z, 18 processed, zero failures/errors/warnings. All values and normalized snapshot hash matched.
3. Recognize that prepopulated copies make that preservation check insufficient to prove population.
4. Merge only the two searchable copies to null on one existing chunk. Readback confirmed only these values changed; other 17 chunks were unchanged. Save a restore payload locally.
5. Reset/run without manual restoration. Fresh execution and full readback proved both values restored and all 18 records equal to baseline.

Raw CLI responses were decoded as utf-8-sig with cp1252 fallback; normalized JSON used ensure_ascii=True. Local raw files were not independently retrieved here. Do not treat chat formatting as a byte-exact archive.

## Boundaries and next work

The mappings populate copies when indexing runs; no periodic schedule has been established. The manual combined field survived these runs unchanged, but its refresh behavior is not maintained by the new mappings.

Next: repeat all five development queries in one batch against separate headings, comparing primary ranks 1,1,1,1,2 and full required evidence with [checkpoint 06](azure-separate-headings-06.md). That repeat is pending, not a result of this update.

Changed-source and absent/empty source-heading fixtures, source deletion/revocation, model answers, held-out evaluation, latency/cost and ADR-009 remain open. A null target-field restoration test is not a missing source-heading test. No issue closure or competency-score change.

See the updated [maintenance guide](../azure-search/heading-field-maintenance.md).
