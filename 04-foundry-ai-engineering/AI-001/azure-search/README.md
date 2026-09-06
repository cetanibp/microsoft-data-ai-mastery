# Azure AI Search walkthrough — step 7

Status: direction selected; service discovery pending. No Azure resource, index, upload, role assignment or paid operation has been performed.

## Why use Azure AI Search next?

The local loader/chunking experiment makes source verification and passage boundaries inspectable. The next implementation will use Azure AI Search for keyword retrieval over those prepared passages, then compare managed document processing and vector/hybrid retrieval using the same development questions.

Initial design: two separate lab indexes, one for each chunk strategy, on a suitable learning search service. Treat names and schemas as proposed until service capacity and configuration are known. An index is the searchable collection and field schema; the service is the Azure resource hosting it. An indexer is a separate source-ingestion mechanism, not required when pushing precomputed passages.

Do not automatically promote local artifacts labeled runtime_eligible=false. Before upload, define and review a bounded synthetic lab import contract and keep it separate from authorization to serve users. Content/policy approval, user/workload identity checks and current freshness enforcement remain open.

## Current user step: find an existing learning service

1. Open the [Azure portal](https://portal.azure.com/).
2. Search for Azure AI Search and open the search-service list.
3. Check the subscription filter for the subscription used for this learning project.
4. If a suitable learning service exists, inspect its tier, region and existing indexes. Report the tier/region/index count; a screenshot of the overview is also useful.
5. If none exists, report that outcome so the next guided step can choose a name, resource group, region and tier.

No keys, tokens or full subscription identifiers are needed for this step. Do not repurpose a production service or change existing indexes. A lab resource must be chosen before generating service-specific connection instructions.

A Free search service is a candidate for this tiny keyword exercise. Microsoft allows one Free search service per subscription, subject to availability. Later feature, authentication, networking and capacity requirements must be checked against the selected tier. Free Search does not imply that all future embedding, storage or model services are free.

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
