# Force-commit retrieval diagnostic 01

Declared September 21, 2026, before new live execution. This is a bounded
read-only investigation of development case AI001-025. It does not change
the source corpus, indexes, eligibility, expected answer, or reserved dataset.

Execution completed; see [checkpoint 13](../evidence/azure-force-commit-diagnostic-13.md).
The declaration below is preserved as the pre-run comparison contract.

## Question and existing evidence

Why does the saved query "Give me the exact SQL command to force a watermark
commit." fail to retrieve **Corrective state action**?

[Checkpoint 11](../evidence/azure-answer-guards-11.md) records that neither
the original nor the automatic rewrite found the required passage. A
source-informed manual query found it at rank one. Earlier expanded-output
inspection also missed it for the original query. These facts establish
wording sensitivity, not which retrieval stage excluded the passage.

## Frozen comparison

The [machine-readable specification](force-commit-diagnostic-01.json) fixes
three existing queries: original, saved automatic rewrite, and saved manual
diagnostic. Each runs through four arms:

| Arm | Request | Purpose |
|---|---|---|
| lexical18 | Direct simple search, top 18 | Inspect keyword candidates across this 18-record corpus. |
| semantic18 | Direct semantic search, top 18 | Inspect semantic ordering and reranker scores. |
| kb5 | Existing knowledge base, maximum 5 documents | Repeat the saved output window. |
| kb18 | Same knowledge base, maximum 18 documents | Inspect the larger window independently. |

API `2026-08-01-preview`, search fields, and semantic configuration match
the saved knowledge-base experiment. Direct search uses `searchMode=any`.
The knowledge-base API has no search-mode parameter, so direct search is a
diagnostic comparison, not a claim of identical internal execution.

Before the 12 requests, read index, knowledge-base and knowledge-source
configuration plus the full corpus. Require minimal extractive retrieval
with no knowledge-base models, no scoring profiles or vector fields, and
the exact 18-record historical corpus fingerprint. Repeat these four reads
afterward. Budget: 20 total requests, one attempt each, no model-generation
calls or automatic retries. A failure stops the batch; a later recovery must
use a new output directory and retain the unsuccessful run.

The target definition stays in evaluator logic, outside search request bodies.
A hit requires document identity, heading, original revision and exact text
hash; a matching heading alone cannot pass. Original questions and the two
synthetic clarification cases in the offline reference remain unchanged.

## Interpretation declared before execution

- Missing from lexical18: investigate candidate generation; reranking cannot
  by itself supply an absent candidate.
- Present lexically but moved below five by semantic ranking: a ranking effect,
  provided semantic execution completed without a partial-response fallback.
- Present in kb18 but not kb5: an observed output-window effect. Independent
  calls and service variability limit causal claims.
- Different direct-semantic and knowledge-base results: inspect returned
  activity and request contracts before attributing the discrepancy.
- Manual success: source-informed diagnostic only, not automatic reformulation
  success. It changes the command-seeking question into a procedural query.
- Corpus/configuration drift invalidates the comparison. Authentication failure
  yields no new retrieval conclusion.

Semantic ranking reranks existing candidates rather than searching the entire
corpus afresh; see [Microsoft's semantic ranking overview](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview).
Minimal effort disables LLM query planning; see [retrieval reasoning effort](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-how-to-set-retrieval-reasoning-effort).
Knowledge-base search behavior and output processing are documented in
[the retrieve API guide](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-how-to-retrieve).
Documentation checked September 21, 2026. Actual service responses remain the
evidence for this specific configuration; rank scores do not prove answer support.

## Run and inspect

Use an existing Azure CLI login and set `SEARCH_ENDPOINT` to the existing lab
Search service origin. The runner never prints or exports tokens. From the
repository root, choose a new output directory on each execution:

```bash
python -m unittest discover -s 04-foundry-ai-engineering/AI-001/tests -p test_force_commit_diagnostic.py -v
python 04-foundry-ai-engineering/AI-001/evaluation/run_force_commit_diagnostic.py --output-dir 04-foundry-ai-engineering/AI-001/generated/force-commit-diagnostic-01
```

The output contains the frozen specification and runner, request bodies,
per-call metadata, sanitized rankings, and `summary.json`. It stores hashes
of raw responses rather than raw bodies, endpoints or CLI authentication
diagnostics. Chunk identities are hashed; source text is represented by its
hash. This enables rank inspection without publishing Azure storage addresses.
The summary must say `completed` and show unchanged configuration and corpus
before results are interpreted. A partial semantic response must be reported
as a limitation, not scored as a semantic-ranking result.

Any retrieval improvement still leaves the response boundary unchanged: no
force-commit command, and no attribution to a passage that was not retrieved.
