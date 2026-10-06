# Force-commit diagnostic 02: request-level reranking controls

Execution completed; see [checkpoint 13](../evidence/azure-force-commit-diagnostic-13.md).
The declaration below is preserved as the pre-run comparison contract.

Declared September 21, 2026 after diagnostic 01 completed. Its original-query
target appeared at rank 8 in direct lexical search and rank 9 in direct
semantic search, but not in knowledge-base output at either limit. The corpus
and configuration remained unchanged. This follow-up preserves those results.

The [frozen specification](force-commit-diagnostic-02.json) uses only the
unchanged original question and repeats the eighteen-result knowledge-base
baseline. Two additional requests change one source parameter each:

- `rerankerThreshold: 0` tests threshold sensitivity.
- `resultsProcessing: none` tests the path with reranking disabled; no
  threshold is set in this arm.

The [retrieve API](https://learn.microsoft.com/en-us/rest/api/searchservice/knowledge-retrieval/retrieve?view=rest-searchservice-2026-08-01-preview)
documents these request parameters. The [retrieve guide](https://learn.microsoft.com/en-us/azure/search/agentic-retrieval-how-to-retrieve)
states that disabling reranking preserves underlying order while other limits
and deduplication still apply. Check returned reranker scores to assess whether
the requested mode took effect. These parameters affect individual requests;
the stored source and knowledge-base configuration are not changed.

Use the same pre/post configuration and historical-corpus controls as
[diagnostic 01](force-commit-diagnostic-01.md). Budget: three retrieval requests
and eight control reads, eleven total, one attempt each, no model generation.
If baseline ordering changes, report instability. A target restored only by
the threshold or reranking intervention supports sensitivity to that option;
it does not prove an undocumented service default or a particular internal
filter. If neither restores the target, that hypothesis remains unsupported.
A restored result below rank five still does not satisfy the original window.

```bash
python 04-foundry-ai-engineering/AI-001/evaluation/run_force_commit_diagnostic.py --spec 04-foundry-ai-engineering/AI-001/evaluation/force-commit-diagnostic-02.json --output-dir 04-foundry-ai-engineering/AI-001/generated/force-commit-diagnostic-02
```

Keep diagnostic 01 unchanged and use a fresh output directory. Do not adopt
either intervention as a retrieval configuration from this single case.
