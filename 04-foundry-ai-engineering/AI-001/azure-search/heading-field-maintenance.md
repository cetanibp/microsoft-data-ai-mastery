# Next increment: maintain the derived heading field

Status: planned, not implemented or executed. Owner work item: AI-001 #13. Depends on the completed [heading-search experiment](../evidence/azure-heading-search-05.md).

## Problem and invariant

text_with_headings_v1 is preferred provisionally for development queries, but its values came from a manual merge. The current indexer maps text and headings independently and only emits the false runtime flag through its skillset. A future refresh must not leave derived text inconsistent with the current source fields.

For every chunk, derive the field by joining nonempty heading_h1, heading_h2 and text, in that order, with exactly two LF characters. Preserve the original strings, including CRLF inside text. Null/empty headings are omitted; text must be a nonempty string. Never derive from the prior combined field.

## Guided next steps

1. Inspect the current skillset, indexer mappings and actual enrichment paths after Markdown one-to-many parsing. Verify current Microsoft documentation before choosing a native enrichment expression or skill. Persist the existing lab false-flag behavior.
2. Prepare a reviewed implementation using those paths. Prefer an in-indexer transformation if it can implement the exact contract. If it cannot, explicitly document and implement a post-indexing derivation stage with a completion check before experiments query the candidate.
3. Validate present, null and empty headings; CRLF and Unicode preservation; and nonempty text. Compare derived values exactly with the existing Python transformation. Do not silently change separators, trim text or introduce placeholders.
4. Apply the bounded implementation through the guided lab, run ingestion and inspect all per-item outcomes. Verify each candidate value matches its current original fields and that original source metadata and runtime_eligible=false remain intact.
5. Rerun on unchanged inputs to check idempotency. Then use a separately versioned synthetic fixture for a changed heading/text, recording old/new hashes and fresh provenance. Keep the frozen baseline corpus and original experiment evidence intact.
6. Check a failed or incomplete derivation: the candidate must not be declared ready for experiments until every expected chunk passes. Record how derived values are regenerated after a source update, and how obsolete chunks are removed in the later source-deletion lifecycle tests.
7. Repeat the five A/B development queries on the original frozen source version after maintenance integration. Record regression or parity, not just indexer success.

## Completion evidence

- Versioned transformation and indexer/skillset or explicit post-index stage configuration.
- Executable transformation validation and user-supplied live ingestion/readback evidence, clearly distinguished.
- Exact parity for all 18 original candidate values, unchanged original fields, and false eligibility flags.
- Unchanged-input replay and a versioned synthetic update case with provenance.
- Failure handling, source-update procedure and separate tracking of untested deletion/revocation behavior.

The readiness check here is for a reproducible development experiment; it does not grant serving authorization. Application access/freshness controls, model answers, held-out evaluation and ADR-009 remain separate open work.
