# Azure AI Search walkthrough

Current status: user reports successful preparation and uploads, with final counts of 24 section documents and 15 window documents. Four user-supplied keyword search responses are summarized in [the first retrieval comparison](../evidence/azure-keyword-comparison-01.md). Live schema equivalence, application authorization/freshness enforcement and formal evaluation remain pending.

## Why use Azure AI Search next?

The local loader/chunking experiment makes source verification and passage boundaries inspectable. The next implementation will use Azure AI Search for keyword retrieval over those prepared passages, then compare managed document processing and vector/hybrid retrieval using the same development questions.

Initial design: two separate lab indexes, one for each chunk strategy, on a suitable learning search service. Treat names and schemas as proposed until service capacity and configuration are known. An index is the searchable collection and field schema; the service is the Azure resource hosting it. An indexer is a separate source-ingestion mechanism, not required when pushing precomputed passages.

Do not automatically promote local artifacts labeled runtime_eligible=false. Before upload, define and review a bounded synthetic lab import contract and keep it separate from authorization to serve users. Content/policy approval, user/workload identity checks and current freshness enforcement remain open.

## Completed user checkpoint: check index capacity

In the selected service, open **Search management > Indexes** and report the number of existing indexes. Free supports at most three indexes. Our proposed two-index comparison fits if zero or one index already exists. If more exist, decide the next approach without deleting unrelated indexes or upgrading the service automatically.

## Proposed index definitions (artifact only)

- [sections.index.json](sections.index.json): `northstar-ops-sections-v1`, for the 24 Markdown-section chunks.
- [windows.index.json](windows.index.json): `northstar-ops-windows-v1`, for the 15 fixed-window chunks.

The schemas have identical fields and analyzers; only the index name differs. Each indexed document represents one chunk. These are versioned create-index request bodies. The user reports creating the corresponding indexes; live schema equivalence remains unchecked. API version selection and live schema acceptance will be checked at the creation step.

| Field setting | Meaning in this experiment |
| --- | --- |
| key | `chunk_id` uniquely identifies each passage for uploads and updates. |
| searchable | `title` and `text` participate in full-text matching using the English Lucene analyzer. |
| filterable | Exact restrictions can use document/version/strategy metadata and draft-state flags. |
| retrievable | Returned text and pinned source URLs let us inspect passages and cite their originals. |

Upload projection contract:
- Copy same-named scalar fields and declared reader roles from each prepared chunk, retaining all false readiness/verification flags and the original mode.
- Map `chunking.strategy` to `chunk_strategy`; serialize the entire `chunking` object into `chunking_json`.
- Map distinct `source_sections[*].section` values to `section_names`; serialize the full original `source_sections` array into `source_sections_json` so heading ancestry and offsets survive.
- Do not upload the original nested properties alongside these projected fields. The JSONL files are not direct Azure upload payloads.
- This mapping is implemented locally by `prepare_upload.py`. There is no network uploader. The intended cloud exercise is restricted to these synthetic/public passages, these two lab indexes, and developer inspection with the signed-in user's RBAC identity. Draft mode and all false readiness flags must remain intact. This does not authorize application serving or establish application access/freshness enforcement.

Filterable role labels are ordinary metadata, not automatic authorization. Hiding a field with retrievable=false does not enforce document access. Azure service roles grant our developer account operations on the service; the proposed application reader/operator policy still needs its own enforcement.

## Upcoming checkpoints

- Select or create the learning search service with explicit region/tier choices.
- Configure suitable Microsoft Entra access for index administration, document loading and querying; map each operation to its required role.
- Prepare a reviewed lab upload projection from our custom chunks, preserving source version, section metadata and policy fields.
- Create isolated indexes and upload the two passage sets, then inspect keyword results using development cases.
- Evaluate managed Markdown/Text Split processing as an alternative; introduce embeddings and vector/hybrid comparisons afterward.
- Implement and demonstrate actual user-level access, freshness, deletion/revocation and cache behavior before claiming a serving-ready assistant.

The existing 13 local tests and 24/15 chunk counts remain valid preparation evidence. No retrieval results exist yet. Reserved cases remain reserved from tuning.

## Learning resources

- [Create an Azure AI Search service](https://learn.microsoft.com/en-us/azure/search/search-create-service-portal) — service, region and tier choices.
- [Connect using Azure roles](https://learn.microsoft.com/en-us/azure/search/search-security-rbac) — distinguish service management, document loading and query permissions.
- [Full-text search quickstart](https://learn.microsoft.com/en-us/azure/search/search-get-started-text) — the indexing and query concepts we will apply.

Resources checked September 6, 2026. Follow the current walkthrough checkpoint rather than deploying the entire quickstart.

- [Index limits](https://learn.microsoft.com/en-us/azure/search/search-limits-quotas-capacity#index-limits) — Free index capacity.
- [Create a search index](https://learn.microsoft.com/en-us/azure/search/search-how-to-create-search-index) — field attributes and schema design.

## Reproduce upload preparation locally

[prepare_upload.py](prepare_upload.py) uses the existing source-hash checks and regenerates both chunk sets. It projects them into the index fields, validates field names/types, checks unique keys and batch limits, and writes Azure REST request bodies. No Azure library, credentials or network calls are used.

From the repository root on the PR branch, using Python 3.10 or later:

```bash
python 04-foundry-ai-engineering/AI-001/azure-search/prepare_upload.py --repo-root . --allow-draft-local
```

Outputs under ignored `AI-001/generated/azure-search/`:
- `sections.upload.json`: 24 records, 40,937 UTF-8 bytes in the checked snapshot.
- `windows.upload.json`: 15 records, 34,793 UTF-8 bytes.
- `summary.json`: source verification, counts, schema/payload SHA-256 hashes and explicit local-only evidence.

The command refuses to reuse an existing output directory. Preserve earlier evidence and use a fresh checkout to reproduce it. The input draft-local flag authorizes local preparation only.

Azure expects a JSON object with a `value` array, with `@search.action: "upload"` on each record. Upload inserts a new key or replaces an existing record with that key; it does not delete obsolete records from older source versions. Future live verification must examine every per-document result and query the resulting index, not assume HTTP success proves all records loaded.

### Local evidence

Python 3.12.13: all 17 tests passed (13 existing corpus tests plus four projection tests). Projection tests check exact preservation of original fields and nested metadata, deterministic payloads, required draft-local opt-in, rejection of promoted flags/wrong strategy, and rejection of schema field/type drift. The run produced 24/15 records with source blob verification PASS. Live upload and retrieval evaluation remain pending; reserved questions were not used.

```bash
python -m unittest discover -s 04-foundry-ai-engineering/AI-001/tests -v
```

Next guided action: open Azure Cloud Shell in Bash, using an existing setup or an ephemeral session, then obtain the PR branch and run this local preparation command. Review the output before the subsequent RBAC upload step.

- [Load an index](https://learn.microsoft.com/en-us/azure/search/search-how-to-load-search-index) explains the request envelope, upload action and per-document results.
- [Cloud Shell quickstart](https://learn.microsoft.com/en-us/azure/cloud-shell/quickstart) explains opening an authenticated browser shell.

## Current next step

Broaden evaluation beyond the first keyword example using supported development questions and fixed settings. The four-run exploratory comparison is preserved in the evidence link above. No overall chunking winner has been selected.
