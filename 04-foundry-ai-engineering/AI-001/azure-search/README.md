# Azure AI Search walkthrough — steps 7–10

Status: user reports an existing Free service in West US, role-based authentication, and completion of the service-scoped Search Service Contributor / Search Index Data Contributor assignment step. These are user-reported setup checkpoints; no successful Azure API request has been observed. Index capacity remains unknown. No index has been created or uploaded by this implementation.

## Why use Azure AI Search next?

The local loader/chunking experiment makes source verification and passage boundaries inspectable. The next implementation will use Azure AI Search for keyword retrieval over those prepared passages, then compare managed document processing and vector/hybrid retrieval using the same development questions.

Initial design: two separate lab indexes, one for each chunk strategy, on a suitable learning search service. Treat names and schemas as proposed until service capacity and configuration are known. An index is the searchable collection and field schema; the service is the Azure resource hosting it. An indexer is a separate source-ingestion mechanism, not required when pushing precomputed passages.

Do not automatically promote local artifacts labeled runtime_eligible=false. Before upload, define and review a bounded synthetic lab import contract and keep it separate from authorization to serve users. Content/policy approval, user/workload identity checks and current freshness enforcement remain open.

## Current user step: check index capacity

In the selected service, open **Search management > Indexes** and report the number of existing indexes. Free supports at most three indexes. Our proposed two-index comparison fits if zero or one index already exists. If more exist, decide the next approach without deleting unrelated indexes or upgrading the service automatically.

## Proposed index definitions (artifact only)

- [sections.index.json](sections.index.json): `northstar-ops-sections-v1`, for the 24 Markdown-section chunks.
- [windows.index.json](windows.index.json): `northstar-ops-windows-v1`, for the 15 fixed-window chunks.

The schemas have identical fields and analyzers; only the index name differs. Each indexed document represents one chunk. These are draft create-index request bodies, not deployed resources. API version selection and live schema acceptance will be checked at the creation step.

| Field setting | Meaning in this experiment |
| --- | --- |
| key | `chunk_id` uniquely identifies each passage for uploads and updates. |
| searchable | `title` and `text` participate in full-text matching using the English Lucene analyzer. |
| filterable | Exact restrictions can use document/version/strategy metadata and draft-state flags. |
| retrievable | Returned text and pinned source URLs let us inspect passages and cite their originals. |

Future upload projection contract:
- Copy same-named scalar fields and declared reader roles from each prepared chunk, retaining all false readiness/verification flags and the original mode.
- Map `chunking.strategy` to `chunk_strategy`; serialize the entire `chunking` object into `chunking_json`.
- Map distinct `source_sections[*].section` values to `section_names`; serialize the full original `source_sections` array into `source_sections_json` so heading ancestry and offsets survive.
- Do not upload the original nested properties alongside these projected fields. The JSONL files are not direct Azure upload payloads.
- This describes a prospective mapping only; no uploader or cloud-import approval is implemented. Review the bounded lab import contract before sending content.

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
