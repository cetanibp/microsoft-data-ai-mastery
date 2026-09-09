# Azure-managed Markdown lab setup

This records the configuration used in the guided lab. See [observed results](../evidence/azure-markdown-h2-comparison-03.md). Credentials and live resource endpoints are omitted; this is not a standalone deployment script.

## Data flow and boundaries

Three original Markdown blobs feed a one-to-many Markdown indexer, then a ConditionalSkill sets the false lab flag before output reaches the third comparison index. Developer-to-Search calls use Entra RBAC. Search-to-Storage uses a short-lived read/list container SAS. Those are different authorization paths. Neither implements the proposed application reader/operator policy.

The private container's custom metadata was populated with document_id, source_url, source_path, source_commit, source_blob_sha, corpus_id, corpus_version and manifest_sha256. Same-named index fields were intended to receive implicit mappings. The live readback confirmed document_id and source_url, but not the other provenance fields.

## Submitted schema

All fields are retrievable. Only text is searchable, with en.lucene. All fields are nonfacetable.

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

## Indexer body

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
6. Capture pristine sanitized query responses, execution timestamps, schema readback and remaining provenance fields for the next experiment. Renew expired source credentials only when further ingestion is needed.

Future changes to source content, parser depth or mappings require update/deletion lifecycle validation; this initial ingestion did not test that behavior. The false flag is metadata, not enforced serving authorization.
