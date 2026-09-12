# Checkpoint 11: answer, reformulation and guard evaluations

Recorded September 12, 2026 for [AI-001 #13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13) and draft [PR #56](https://github.com/cetanibp/microsoft-data-ai-mastery/pull/56).

**Decision: continue development; no candidate is ready to adopt.** Local scripts executed bounded inference against the existing Azure deployment and read-only knowledge-base retrieval. These are observed development results with agent review, not an independent external evaluation or deployed application. This checkpoint supersedes earlier statements that model evaluation had not run; it does not rewrite those historical checkpoints.

## Scope and provenance

The saved five-case specification was reused: AI001-012, AI001-013 and AI001-025, plus the explicitly synthetic AI001-012-C1 and AI001-013-C1 clarifications. C1 context is fictional supplied test input, not information inferred about a real run. Expected headings, gold passages and expected behavior stayed outside model inputs. Original questions remained separate from generated retrieval queries. No reserved cases were executed.

The existing `northstar-answer-dev` deployment was used with the saved configured model/version `gpt-4.1-mini` / `2025-04-14`, Responses v1, Entra authentication, `store=false`, and bounded output tokens. Responses may report the deployment alias rather than independently confirm the underlying version. Azure CLI 2.90.0 and Python 3.14.2 were verified in the command environment. No tokens, keys or connection strings are included in repository evidence.

Knowledge-base comparisons used API `2026-08-01-preview`, Minimal effort, `extractiveData`, no knowledge-base model, the same source settings and five-document output limit. Search used `heading_h1_search_v1,heading_h2_search_v1,text` and `northstar-semantic-v1`. The reformulation batch verified unchanged knowledge-base/source configuration and all 18 corpus records, including `runtime_eligible=false`. Later guard batches reused saved retrieval rather than making new retrieval calls. This authorized lab use does not implement or demonstrate serving-time access enforcement.

[Machine-readable results and source-file hashes](azure-answer-guards-11.json) identify the local evidence directories and selected archived outcomes. Full requests, raw/normalized responses, scripts, test logs, timings and hash inventories remain under the operator's `NorthstarLab` directory; they are not published or made portable by this documentation commit. The JSON is an offline export of selected records, not a fresh cloud run. Decode uses UTF-8-sig first, then strict cp1252; generated JSON uses UTF-8, ASCII escaping and LF newlines.

## Answer baselines and retrieval diagnostics

- Both saved answer-prompt batches answered the ambiguous rerun and latest-watermark questions instead of reliably clarifying. Citation-list/text agreement passed 3/5 in the initial batch and 4/5 with prompt v2; that mechanical metric does not prove citation support or answer quality.
- The original force-commit question missed **Corrective state action** in knowledge-base results, including expanded-output inspection. A source-informed manual reformulation retrieved it at position 1. This was a manual diagnostic, not evidence of automatic reformulation success.
- Automatic reformulation used only the original question and one general prompt, with one call per case. Required-chunk coverage increased from 3/5 to 4/5 complete cases (7/9 to 8/9 required passages). For the three original questions alone, coverage increased 1/3 to 2/3; the two synthetic variants stayed 2/2.
- The automatic force-commit query still missed Corrective state action. Some rewrites dropped explicit constraints or lost supplementary passages. Better retrieval did not resolve ambiguity or establish a supported answer.

## Guard progression

| Batch | Observed result | Unresolved failure |
|---|---|---|
| Initial guards | 3/5 final behavior-label matches; separate saved-answer audit caught the watermark citation mismatch | Model gate overclarified both C1 procedures; rerun clarification assumed a watermark topic. Reviewer accepted all five saved answers, including an unsupported generalization. |
| Guard v2 | Local rules recorded exact original-question spans; 5/5 intended gate routes. Reviewer diagnostics matched 6/7 expectations. | Both answers withheld: fenced JSON/synthesized quotes and non-exact whitespace formatting. Original compound force-commit answer D07 remained overaccepted. |
| Guard v3 | Deployment accepted all three schema-constrained calls; 3/3 responses passed structural checks | Both answers withheld: synthesized ellipsis quote and an exact 275-character quote exceeding the frozen 220-character cap. Splitter omitted a semicolon; no semantic review ran. |

V2 and v3 each had 3/5 final behavior-label matches and **0/2 accepted generated procedure answers**. Gate routing, output shape, quotation identity, assertion support and answer completeness have different denominators. A refusal does not satisfy the missing corrective-procedure requirement. Passing a structural check is not a full answer-quality pass.

V2 reviewer controls included two supported claims and five unsupported claims. It accepted both supported controls and rejected four unsupported examples, but accepted the actual saved compound failure. The cited recovery table forbids forcing a stale candidate under a specific condition; it does not establish the broader claim that the runbook explicitly prohibits every forced watermark commit or every protocol bypass. Protocol references cannot supply that missing attribution.

V3 splitting preserved three sentence-sized parts for D07 but did not separate all assertions in its second sentence. D01 lost only a semicolon: this violated the frozen exact-character coverage rule, but is not evidence of a semantic reversal. The failed split blocked the batched reviewer stage. **V3 provides no new reviewer-accuracy score.** Failed outputs were not repaired, retried or rescored as successes.

## Execution and validation

| Batch | Model calls | Input tokens | Output tokens | Total tokens |
|---|---:|---:|---:|---:|
| Initial saved-context answer evaluation | 5 | 5,638 | 1,077 | 6,715 |
| Answer prompt v2 | 5 | 7,573 | 1,162 | 8,735 |
| Automatic reformulation | 5 | 836 | 86 | 922 |
| Initial guards plus separate saved-answer audit | 10 | 6,165 | 554 | 6,719 |
| Guard v2 | 9 | 7,874 | 1,868 | 9,742 |
| Guard v3 | 3 | 4,424 | 1,227 | 5,651 |

Automatic reformulation additionally made ten paired retrieval calls plus read-only configuration/corpus checks. Guard v2 made two answer calls and seven reviewer diagnostics. Guard v3 made two answer calls and one splitting call; five conditional calls were skipped after validation failures. Timings include CLI/authentication overhead; service activity is retained separately where available. Token counts are not a measured currency cost, and these small heterogeneous batches do not establish p95 latency.

Initial guards passed 12 local unit tests and five separate citation fixture assertions. V2 passed 12 gate tests; v3 passed 12 schema/quote/splitting tests. These counts describe distinct recorded checks, not 41 independent end-to-end cases. Exact-quote checks cannot establish entailment, and a same-model reviewer can repeat the generator's errors. The rules were developed using known failures, so success on these development inputs does not establish generalization.

Existing evidence hashes and repository state were preserved during the experiments. The documentation consolidation subsequently fast-forwarded the local branch to the existing remote head before editing. This checkpoint changes no cloud configuration, runtime eligibility, dataset execution status, issue completion, ADR acceptance or skill scores.

## Retrospective and next increment

Prompts improved some formatting and routing behavior but did not reliably enforce source copying or semantic support. Local validation exposed these failures and withheld answers; it also reduced answer availability when benign formatting or length differences violated the fixed contract. Both safety and availability must be measured.

1. Precompute source spans with IDs and provenance. Let the model select spans; assemble quotations locally instead of asking it to recopy source text.
2. Preserve text through boundary selection when splitting claims. Define punctuation handling before execution, and measure atomicity separately from character coverage.
3. Run reviewer diagnostics independently so one invalid split does not prevent inspection of all other cases. Keep D07 as a required development negative control.
4. Expand gate tests for unfamiliar paraphrases, negation and compound procedure/live-value requests. Retain the frozen reserved set until development stabilizes.
5. Integrate only after a portable harness, full assertion/completeness review, access/freshness/injection controls and a deployment handoff are ready. Changed-source heading fixtures, vector/hybrid comparison, full rubric, supported-answer latency/cost, ADR-009 and #13 completion remain open.

API-format references consulted during v3: [Azure structured outputs](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/structured-outputs) and [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs). Live results establish acceptance of the submitted schemas on this deployment only.
