# Azure-managed Markdown lab setup

This records the configuration used in the guided lab. See [observed results](../evidence/azure-markdown-h2-comparison-03.md). Credentials and live resource endpoints are omitted; this is not a standalone deployment script.

## Data flow and boundaries

Three original Markdown blobs feed a one-to-many Markdown indexer, then a ConditionalSkill sets the false lab flag before output reaches the third comparison index. Developer-to-Search calls use Entra RBAC. Search-to-Storage uses a short-lived read/list container SAS. Those are different authorization paths. Neither implements the proposed application reader/operator policy.

The private container's custom metadata was populated with document_id, source_url, source_path, source_commit, source_blob_sha, corpus_id, corpus_version and manifest_sha256. Same-named index fields were intended to receive implicit mappings. [Checkpoint 04](../evidence/azure-aligned-api-comparison-04.md) now records all 18 chunks' populated provenance values and one complete pinned URL per document. Values are consistent; cloud blob bytes were not independently verified.

## Submitted schema

The original schema below made only text searchable, with en.lucene; all fields are retrievable and nonfacetable. [Checkpoint 05](../evidence/azure-heading-search-05.md) added the searchable/retrievable text_with_headings_v1 string field using en.lucene. The original fields and values remain intact.

| Field | Type | Additional attributes |
|---|---|---|
| chunk_id | Edm.String | key, filterable |
| text | Edm.String | searchable |
| heading_h1, heading_h2 | Edm.String | filterable |
| ordinal_position | Edm.Int32 | sortable |
| document_id, source_commit, corpus_id, corpus_version, manifest_sha256 | Edm.String | filterable |
| source_url, source_path, source_blob_sha | Edm.String | none |
| runtime_eligible | Edm.Boolean | filterable |

The generated one-to-many key mapping was left implicit. These generated keys differ from the local loader's content/configuration-derived hashes and can encode source locations; avoid publishing them as sanitized evidence.

## Indexer body (does not maintain the new derived field)

```json
{
  "name": "northstar-markdown-h2-indexer",
  "dataSourceName": "northstar-markdown-blob-source",
  "targetIndexName": "northstar-ops-markdown-h2-v1",
  "skillsetName": "northstar-markdown-lab-flags",
  "parameters": {
    "maxFailedItems": 0,
    "maxFailedItemsPerBatch": 0,
    "configuration": {
      "dataToExtract": "contentAndMetadata",
      "indexedFileNameExtensions": ".md",
      "parsingMode": "markdown",
      "markdownParsingSubmode": "oneToMany",
      "markdownHeaderDepth": "h2"
    }
  },
  "fieldMappings": [
    {"sourceFieldName": "/content", "targetFieldName": "text"},
    {"sourceFieldName": "/sections/h1", "targetFieldName": "heading_h1"},
    {"sourceFieldName": "/sections/h2", "targetFieldName": "heading_h2"},
    {"sourceFieldName": "ordinal_position", "targetFieldName": "ordinal_position"}
  ],
  "outputFieldMappings": [
    {"sourceFieldName": "/document/lab_runtime_eligible", "targetFieldName": "runtime_eligible"}
  ]
}
```

## Skillset body

```json
{
  "name": "northstar-markdown-lab-flags",
  "skills": [{
    "@odata.type": "#Microsoft.Skills.Util.ConditionalSkill",
    "name": "set-lab-status",
    "context": "/document",
    "inputs": [
      {"name": "condition", "source": "= true"},
      {"name": "whenTrue", "source": "= false"},
      {"name": "whenFalse", "source": "= false"}
    ],
    "outputs": [{"name": "output", "targetName": "lab_runtime_eligible"}]
  }]
}
```

The skill creates a Boolean output rather than relying on conversion of string-valued blob metadata. The user returned false for all 18 indexed records.

## Reproduction checkpoints

1. Use the pinned corpus and existing source-hash validation before uploading original Markdown.
2. Supply the matching custom metadata and a private, read/list source credential outside Git.
3. Create the data source and submitted schema, then the skillset and indexer. All three comparison indexes already exist in the exercised lab; preserve the baselines.
4. Inspect indexer status, then query actual count and metadata. Successful processing alone does not prove field correctness.
5. Inspect the four recovery chunks in ordinal order before rerunning the exact five development questions in the structured evidence.
6. Capture pristine sanitized query responses, execution timestamps, full schema snapshots for the next experiment. Selected live configuration and provenance readbacks are now recorded in checkpoint 04. Renew expired source credentials only when further ingestion is needed.

Future changes to source content, parser depth or mappings require update/deletion lifecycle validation; this initial ingestion did not test that behavior. The false flag is metadata, not enforced serving authorization.

## Current maintenance boundary

text_with_headings_v1 was populated by merge-only updates after schema addition. The indexer/skillset above still handles the original mappings and lab flag. Complete [derived-field maintenance](heading-field-maintenance.md) before relying on the candidate following source refreshes. Explicitly choose text or text_with_headings_v1 in development queries.
