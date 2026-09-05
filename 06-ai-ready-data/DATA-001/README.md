# DATA-001 — Northstar corpus readiness

## Step 2: first corpus manifest

Status: draft, artifact-only evidence. This increment supports [#19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19), the access prerequisite from [#20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20), and [AI-001 #13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13). None of those issues is complete.

[corpus-manifest.json](corpus-manifest.json) selects three existing Northstar documents: the FAB-003 overview, OPS-002 triage runbook, and OPS-002 recovery runbook. The original files remain authoritative. Linked files are not automatically included.

## Why we create this first

A retrieval system needs to know which documents are eligible, which version it used, and whether the requesting user may see them. A manifest is a machine-readable inventory that gives future ingestion and retrieval code those inputs. It does not train a model or enforce permissions by itself.

A small initial corpus makes it practical to check answers by hand. It is deliberately incomplete: these documents reference SQL queries, replay and escalation procedures outside this selection. An answer requiring those details must report insufficient evidence until the additional source is reviewed and added. Documentation alone does not establish the cause or current state of a live incident.

## Read the fields

| Field | Meaning and reason |
|---|---|
| schema_version | Version of the JSON structure; a future loader can reject unsupported formats. |
| corpus_id / corpus_version | Stable collection name and version of its selected sources/policies. Bump the corpus version when either changes. |
| status / approval | Draft and pending review; reading a document is distinct from approving it for retrieval. Approval fields remain null. |
| purpose / scope_exclusions | The assistant's intended knowledge task and its boundaries. |
| default_policy | Shared proposed rules inherited by all three documents through inherits_policy. |
| owner / owner_scope | The lab repository maintainer accountable for reviewing this collection; this is not an enterprise ownership assignment. |
| classification / approved_use | Synthetic lab documentation intended for read-only documentation Q&A. approved_use names the proposed purpose; approval.status governs whether approval exists. |
| access | Proposed reader roles, default denial, and a policy identifier. Roles are logical labels, not existing Entra groups or working access controls. |
| freshness | Proposed 30-day content review plus a source check before every index build. These are lab design choices, not Microsoft requirements or existing automation. |
| lifecycle | Intended update, deletion and revocation behavior for future code. |
| document_id | Stable identity, such as northstar-recovery, independent of title or file path changes. |
| source_path / source_url | Repository location and immutable citation link for the selected version. |
| source_commit / source_blob_sha | Commit identifies the repository snapshot; blob SHA identifies the file contents at that snapshot. They detect different kinds of change. |
| coverage | Topics this particular source can support. |
| source_inspected_on | Date the source was read for this draft; not the source publication date or an approval. |
| content_approved_on / next_review_due_on | Unset until content approval. The due date will be approval date plus the proposed review interval. |
| runtime_ready | False until the remaining prerequisites and runtime gates are implemented and demonstrated. |

## Walk through one record

Find document_id = northstar-recovery. Its title is the recovery runbook and its URL opens the pinned version, even if main later changes. All three records inherit the same draft policy.

The question “Should I advance the watermark manually after a quality block?” is supported by the recovery runbook's Quality BLOCK row and State verification section. The expected answer rejects bypassing the block, describes correction and replay, and cites the supporting sections. Later evaluation will check both source retrieval and answer correctness.

## Proposed operating rules to implement later

1. Before enabling indexing, approve each selected source and the shared policy; fill in approval dates and calculate the next review dates.
2. Check path existence and blob identity against the pinned commit. Before a new current-content build, compare each file with the current approved branch. Unrelated repository commits do not imply the file changed.
3. A changed, removed, revoked or overdue source is ineligible for current answers until review. Review changes through a PR, update its revision, bump corpus_version, and rebuild affected chunks and embeddings.
4. Map authenticated users to authorized roles using trusted application identity context. Keep the application's workload identity separate. Apply current access policy before content reaches model context, including cache hits. Never accept a caller-supplied role as proof.
5. For deletion/revocation, deny the document first, remove indexed chunks/embeddings and cached answers, and verify absence from retrieval, citations and sensitive logs. A retained historical manifest does not authorize continued use of a revoked source.
6. Store only sanitized experiment metadata and manifest versions where allowed. Define detailed retention periods with the access-policy increment; do not duplicate source bodies or preserve deleted sensitive content in evidence.

These are documented requirements, not proven runtime behavior. The draft has no loader, deployed index, scheduled review, authentication or permission enforcement.

## Learning resources

- [Microsoft Learn: Introduction to retrieval-augmented generation concepts](https://learn.microsoft.com/en-us/training/modules/rag-fundamentals/) — read “Prepare data for retrieval.”
- [Microsoft Foundry: RAG and indexes](https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation) — explains retrieval, citations and access checks.
- [Microsoft video: RAG and Vector Databases](https://learn.microsoft.com/en-us/shows/generative-ai-for-beginners/retrieval-augmented-generation-rag-and-vector-databases-generative-ai-for-beginners) — conceptual grounding and retrieval walkthrough.

Resources checked September 5, 2026. This JSON format and its proposed 30-day review interval are Northstar design choices, not a Microsoft-mandated schema.

## Evidence and next checkpoint

Artifact validation checks JSON parsing, three unique document IDs, source paths/blob SHAs against the pinned Git tree, revision-pinned URLs, shared policy references, pending approval and runtime_ready=false. These checks do not prove retrieval, freshness or access behavior.

Next walkthrough: define the operational glossary and the requesting-user/workload-identity/access matrix. Then prepare representative evaluation questions and pass thresholds before retrieval tuning. The broader #19/#20 work and #13 acceptance criteria remain open. No skill scores change.
