# AI-001 — Grounded retrieval baseline

Status: retrieval tuning deferred on October 6, 2026 at the user's direction; continue with [AGENT-001](../../05-agent-engineering/AGENT-001/README.md). Local preparation, Azure retrieval, bounded model/guard experiments and a portable offline reference are recorded. Fixed-rule expansion completes four of five development contexts, but fusion loses that gain and completes three of five; the force-commit gap remains. No serving application is deployed; no retrieval/guard candidate is ready to adopt. See [current checkpoint 15](evidence/azure-development-query-expansion-15.md) and the [runnable reference](offline-reference/README.md). Comparison 03 remains a draft pending independent review; AI-001 is not complete.

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

## Historical checkpoint 11 — answer and guard evaluations

[Consolidated results](evidence/azure-answer-guards-11.md) record clarification failures, limited automatic-reformulation gains, and local guard implementations through v3. V2/v3 route all five saved cases as intended, but neither accepts either generated procedure answer. V3 confirms schema support; quote and splitting failures block semantic review. The saved compound force-commit reviewer failure remains unresolved.

At checkpoint 11, next work was precomputed source-span selection, source-preserving assertion boundaries, and independently runnable reviewer diagnostics. No reserved evaluation, runtime readiness, issue closure or score change.

## September 21 follow-up — offline reference user review

Later local span-v4, extractive-v5, and offline-reference packages were located in `NorthstarLab`; checkpoint 11 does not include their results. The latest reference package is `offline-reference-v2-w609x6jv`.

[Recorded user feedback](evidence/offline-reference-navigation-human-feedback.md): both procedure views were easy to navigate, and the two clarification responses and force-commit refusal were clear. Fresh offline checks reproduced all five saved views and verified unchanged input bytes/hashes, internal anchor targets, and preservation of all five passages in each procedure view. This focused review supports retaining the presentation; it is not a full application evaluation.

The subsequent repository consolidation is recorded in checkpoint 12 below. The full review template, semantic correctness, force-commit evidence gap, and application readiness remain open.

## Historical checkpoint 12 — portable offline reference

[Results and provenance](evidence/azure-answer-reference-12.md) preserve v4's authentication failure and recovery, the unresolved reviewer false acceptances, and v5's selection-completeness failures. Exact quotations improved copying fidelity; they did not establish semantic support. The model selector omitted required evidence in both procedure cases.

The [offline reference](offline-reference/README.md) replays all five saved cases without Azure or the original lab directory. Its procedure views retain all five passages. Eight fresh contract tests passed, including relocated execution of both output formats. Inputs use explicitly sanitized chunk IDs with recorded hashes; source text and Markdown views are preserved.

Next: expand independently reviewed development cases for complete relationships and investigate the force-commit retrieval gap under a declared comparison. No reserved-case run, deployment, issue closure or score change.

## Historical checkpoint 13 — force-commit ranking and threshold diagnostic

[Controlled results](evidence/azure-force-commit-diagnostic-13.md): the original and automatic queries place Corrective state action at keyword rank 8 and semantic rank 9; default knowledge-base output omits it even at an eighteen-document limit. A separately declared original-query follow-up restores it at rank 9 with an explicit zero threshold and rank 8 with reranking disabled. Both batches preserved the corpus and stored configuration; 31 read-only Azure requests completed and seven local diagnostic tests passed.

This establishes low rank and request-threshold sensitivity, not a top-five fix. Keep the existing configuration and frozen reference. Next: compare intent-preserving query expansion or combined retrieval across development cases with a fixed total context budget. Source-informed manual success, semantic answer support, and reserved evaluation remain separate.

## Historical checkpoint 14 — fixed-budget query expansion and fusion

[Controlled results](evidence/azure-development-query-expansion-14.md): original and manually expanded semantic queries were fused locally while every final context remained capped at five passages. Exact required-evidence completeness improved from three of five to four of five development cases with no regression among the three complete originals. Fusion combined complementary evidence for AI001-012; its original and expanded lists were each incomplete alone.

AI001-025 remains unresolved: its target moved from candidate rank nine to six under expansion and fused to rank eight, still outside five. All eighteen read-only requests succeeded, corpus/configuration controls remained unchanged, and 38 local tests passed with one privilege-dependent skip. This supports further development evaluation, not adoption. Next: fix a query-generation rule independently of expected passages or add independently reviewed development cases before another retrieval run.

## Current checkpoint 15 — fixed-rule query expansion and fusion

[Comparison 02](evaluation/development-query-expansion-02.md) executed with one question-only suffix across the same five development cases, ten candidates per query and five final passages. [Results](evidence/azure-development-query-expansion-15.md): 3/5 original, 4/5 expanded and 3/5 fused complete contexts. Fusion moved AI001-012's required Procedure passage from expanded rank five to fused rank six, losing the expansion gain. AI001-025 remained at candidate rank nine in all three lists. All eighteen experiment requests succeeded; corpus/configuration controls and the frozen spec remained unchanged. No complete original case regressed, but fusion did not meet the declared improvement condition. Next: independently authored/reviewed development cases before another batch; answer-quality evaluation and the force-commit gap remain open.

## Prepared follow-up: review packet and comparison 03

[Six supplemental proposals](evaluation/development-cases-02-review.md) add compound recovery/closure relationships and ambiguous paraphrases. They were authored by Codex after checkpoint 15 and await independent review. [Comparison 03](evaluation/development-query-expansion-03.md) keeps the fixed suffix and five-passage budget, with six new cases reported separately from five historical controls. It is a draft, not frozen or live-executed. The runner checks the supplemental registry hash and blocks live requests until review of the exact case contents is recorded and the comparison is frozen. The original dataset and reserved split are unchanged.
