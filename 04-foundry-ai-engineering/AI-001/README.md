# AI-001 — Grounded retrieval baseline

Status: draft prerequisites, local preparation, and three-way Azure keyword retrieval comparison recorded; no serving application or model-answer evaluation deployed.

## Guided learning checkpoints

1. Select the initial three Northstar documents.
2. Draft the [corpus manifest and field guide](../../06-ai-ready-data/DATA-001/README.md).
3. Define the [operational glossary](../../06-ai-ready-data/DATA-001/operational-glossary.md).
4. Draft the [identity/access policy](../../07-governance-security/GOV-001/README.md).
5. Define [30 evaluation cases and proposed scoring targets](evaluation/README.md).
6. Run the [local corpus loader and two chunking strategies](runtime/README.md): 13 tests passed; 24 section chunks and 15 fixed-window chunks from three hash-verified sources.

7. Complete [five development retrieval checks across three chunking approaches](evidence/azure-markdown-h2-comparison-03.md): Azure-managed h2 preserves complete required context in the top five for all five inspected questions.

Next: capture sanitized live configuration and align API/analyzer/searchable-heading controls before changing retrieval behavior. The Azure h2 candidate is provisional. Approval, fixtures, vector/hybrid comparison, permission/revocation evidence, model answers, performance, ADR-009 and deployment handoff remain open.

Related: [#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13), [#16](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/16), [#19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20). Evidence includes local executable loader/chunking tests; manual development retrieval checks have run; full application and answer evaluation remain unrun. Draft content/policy approval is unchanged; no issue is complete and no competency scores change.
