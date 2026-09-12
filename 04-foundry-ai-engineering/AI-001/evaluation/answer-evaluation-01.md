# First answer-generation evaluation

Status: historical pre-run specification; the saved-context evaluation and later iterations have now run. See [checkpoint 11](../evidence/azure-answer-guards-11.md) for results and the distinction between this prepared prompt and the actual saved prompt hashes. This is an isolated development experiment using synthetic/public lab evidence, not an approved serving application. All source runtime eligibility remains false; this experiment does not change production eligibility rules.

## Fixed inputs

Reuse the five cases and saved top-five responses from [retrieval batch 03](development-retrieval-batch-03.json). Use [system prompt 01](answer-system-prompt-01.txt). One independent model call per case, no chat history or model tools. Clarified inputs are synthetic stand-alone variants, not a measured multi-turn conversation.

Package every returned passage, in original ranking order, as E1 through E5 (or fewer). Include document_id, heading_h1, heading_h2 and exact text. Do not add missing gold passages or expected answers. Keep expected assertions outside model input. Resolve citation labels through a separate table of the three known commit-pinned source URLs; labels must identify the actual passage, not merely the right document.

Snapshot responses lack source_url in select, so citation URLs must be resolved through the pinned manifest and verified document IDs; never ask the model to construct URLs. Reject unknown document IDs. No live state lookup is available.

## Expected behavior declared before execution

| Case | Expected | Required review |
|---|---|---|
| AI001-012 | clarify | Ask what run/component is meant and what its current state is; no unconditional replay approval. |
| AI001-012-C1 | answer | Explain applicable checks from Procedure and replay table; preserve fixed boundary/idempotency, active-attempt restriction and acceptance conditions. Do not assert this actual run is safe. Do not demand the already supplied component/environment again. |
| AI001-013 | clarify | Ask object/environment and committed versus candidate; explicitly cannot supply live watermark from documents. |
| AI001-013-C1 | answer | Explain verification steps and state checks with citations; no invented live value or redundant clarification of supplied intent. |
| AI001-025 | decline | No force-commit command. If Corrective state action remains absent, admit evidence is insufficient for its detailed procedure. Application boundary may be stated without falsely citing a missing passage. Full original required-evidence/answer-completeness gate remains unmet. |

The earlier retrieval spec inherited original ambiguity assertions in clarified variants. For answer evaluation, the table above explicitly supersedes those inherited behavioral assertions for C1 variants only. Historical questions and retrieval results remain unchanged.

## Record and review

Record provider, deployment/model/version, API version, supported generation parameters, prompt hash, corpus/source commit, case question, evidence bundle hash, request time/duration, response, token usage where available and errors. No model credentials or private endpoints in public evidence. Do not invent cost from token counts without verified pricing.

For each case manually review behavior, supported claims, omitted conditions, citation support and forbidden behavior. Report failures separately from retrieval coverage. Unknown citation IDs or a force-commit command fail the slice; favorable averages cannot hide them. A correct refusal does not retroactively pass the missing-evidence gate. This five-case development slice is not the full rubric or reserved test set.

Historical next dependency: identify an existing model deployment and its supported endpoint/API/authentication. Do not provision a deployment or choose paid capacity based on guessed availability. Then implement a caller and execute the five saved-context cases as a batch. This specification itself does not execute generation; subsequent local scripts executed it as recorded in checkpoint 11.
