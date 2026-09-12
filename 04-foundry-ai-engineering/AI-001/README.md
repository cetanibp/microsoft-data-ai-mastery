# AI-001 — Grounded retrieval baseline

Status: local preparation, Azure retrieval, bounded model-answer/reformulation evaluations and three guard iterations recorded. No serving application is deployed; no guard candidate is ready to adopt. See [current checkpoint 11](evidence/azure-answer-guards-11.md).

## Guided learning checkpoints

1. Select the initial three Northstar documents.
2. Draft the [corpus manifest and field guide](../../06-ai-ready-data/DATA-001/README.md).
3. Define the [operational glossary](../../06-ai-ready-data/DATA-001/operational-glossary.md).
4. Draft the [identity/access policy](../../07-governance-security/GOV-001/README.md).
5. Define [30 evaluation cases and proposed scoring targets](evaluation/README.md).
6. Run the [local corpus loader and two chunking strategies](runtime/README.md): 13 tests passed; 24 section chunks and 15 fixed-window chunks from three hash-verified sources.

7. Complete [five development retrieval checks across three chunking approaches](evidence/azure-markdown-h2-comparison-03.md): Azure-managed h2 preserves complete required context in the top five for all five inspected questions.

8. Record [live configuration, provenance and aligned-API results](evidence/azure-aligned-api-comparison-04.md): all 15 required-passage ranks reproduced.

9. Complete [heading-search A/B checkpoint 05](evidence/azure-heading-search-05.md): two rank improvements, three unchanged, no regressions, with all 18 original records preserved. Prefer text_with_headings_v1 provisionally for development.

10. Separate-heading [checkpoint 06](evidence/azure-separate-headings-06.md) supersedes that provisional preference: one primary rank improvement, four unchanged, complete required context in all five cases, and a secondary checklist regression from rank 3 to 4.

11. [Maintenance checkpoint 07](evidence/azure-heading-maintenance-07.md): indexer mappings restored two deliberately cleared heading copies; all 18 records matched baseline.

At checkpoint 07, next work was to repeat the five retrieval queries in one batch, then complete [changed-source maintenance fixtures](azure-search/heading-field-maintenance.md). The Azure h2 candidate is provisional. Approval, fixtures, vector/hybrid comparison, permission/revocation evidence, model answers, performance, ADR-009 and deployment handoff remain open.

Related: [#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13), [#16](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/16), [#19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20). Evidence includes local executable loader/chunking tests; manual development retrieval checks have run; bounded answer evaluation has now run; full application evaluation remains incomplete. Draft content/policy approval is unchanged; no issue is complete and no competency scores change.

## Historical checkpoint 08

[Post-maintenance retrieval and scoring diagnostic](evidence/azure-post-maintenance-retrieval-08.md) records primary ranks 1,1,2,1,2: identifiers regressed to second; four other primary ranks reproduced. Four repeated samples and a default/global scoring pair produced identical identifier ordering and scores. Cause remains unconfirmed. Keep separate headings/default scoring provisionally; automatic population is verified but rank parity is not. Next: the prepared broader development retrieval batch (AI001-001, 011, 012, 013, 025). No model or reserved evaluation is claimed.

## Historical checkpoint 09 — broader retrieval and corpus verification

[Results](evidence/azure-broader-retrieval-09.md): two of five broader development cases retrieved all declared evidence. Full readback reports all 18 chunks unchanged; the empty H2 is an existing introduction. Prepared original/clarified query pairs plus an unchanged force-commit control in [batch 03](evaluation/development-retrieval-batch-03.json). No model/reserved evaluation, issue closure or score change.

## Historical checkpoint 10 — clarification results

[Clarification results](evidence/azure-clarification-retrieval-10.md): both synthetic variants retrieved all required passages; original gaps and force-commit control reproduced. Fixed Git Bash CRLF handling. [First answer evaluation](evaluation/answer-evaluation-01.md) defines context, prompt and per-case expectations before model execution. Existing model deployment details are the next dependency; no generation or reserved evaluation has run.

## Current checkpoint 11 — answer and guard evaluations

[Consolidated results](evidence/azure-answer-guards-11.md) record clarification failures, limited automatic-reformulation gains, and local guard implementations through v3. V2/v3 route all five saved cases as intended, but neither accepts either generated procedure answer. V3 confirms schema support; quote and splitting failures block semantic review. The saved compound force-commit reviewer failure remains unresolved.

Next: precomputed source-span selection, source-preserving assertion boundaries, and independently runnable reviewer diagnostics. No reserved evaluation, runtime readiness, issue closure or score change.
