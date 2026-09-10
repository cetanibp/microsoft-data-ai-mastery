# AI-001 — Broader retrieval checkpoint 09

Evidence: user-supplied lab summaries, manually reviewed; [structured results](azure-broader-retrieval-09.json). No independent access to local raw files or Azure is claimed.

## Purpose and value

Chunking checks prevent loss of instructions and qualifications. Heading comparisons test whether document structure improves evidence retrieval. The null-field/reindex probe proves searchable heading maintenance. Snapshot comparison separates content changes from ranking issues. Broader development questions expose missing evidence before a model is asked to answer.

These checks support a maintainable, measurable retrieval component. They do not establish answer correctness, current operational state, authorization, latency, cost, or production readiness.

## Results

| Case | Required evidence ranks | All required chunks in top five |
|---|---|---|
| AI001-001: BLOCK and watermark | Select a pattern 4; Recovery verification 2 | Yes |
| AI001-011: failed quality check | Initial vertical slice 1 | Yes |
| AI001-012: can I rerun it? | Procedure missing; Select a pattern 2 | No |
| AI001-013: latest watermark | Procedure missing; Recovery verification 5 | No |
| AI001-025: force-commit SQL | Corrective state action missing | No |

Two of five cases contain all declared required evidence. Missing evidence is a retrieval gap, not an observed generated-answer failure. For AI001-012 only two results were returned; increasing top alone cannot recover a third match in that response.

The subsequent full-corpus comparison reports the same 18 identities and all fields unchanged from the maintenance baseline, with counts 9/4/5 and all runtime flags false. The empty H2 belongs to the existing quality-gates introductory paragraph at ordinal 1. The earlier assumption that every quality-gates chunk had a named H2 was incorrect; no new chunk or drift was found. This does not independently explain the historical identifier-ranking change.

## Next bounded experiment

[Clarification batch 03](../evaluation/development-retrieval-batch-03.json) contains two unchanged ambiguous questions, two explicitly synthetic clarification variants and the unchanged force-commit control. [Git Bash runner](../evaluation/run-development-batch-03.sh) saves requests and raw/normalized results to a new local directory. It performs search requests only and does not modify Azure configuration or indexed documents.

The variants measure retrieval after supplying missing intent; they do not prove that an application asks the right clarification. The watermark variant requests a verification procedure, not a live value. Preserve original results even if variants improve. Stop after this batch and use its results to define the clarification/context assembly behavior; do not tune endlessly on a single case.

Source-change lifecycle fixtures, answer generation/citations, access/freshness controls, vector/hybrid comparison, performance, ADR-009 and full issue completion remain open. No reserved cases or skill scores changed.
