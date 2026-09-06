# GOV-001 — Identity and access prerequisite

## Step 4: who is asking, and what may the application do?

**Status: draft design; no deployed identity bindings or access enforcement.** This bounded increment supports [GOV-001 #20](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/20), [DATA-001 #19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19) and [AI-001 #13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13). Broader governance remains open.

The [machine-readable policy](access-policy.json) defines the policy ID already referenced by the [corpus manifest](../../06-ai-ready-data/DATA-001/corpus-manifest.json). It elaborates the existing proposed reader/operator access for the same three documents. The corpus source selection and version remain unchanged.

## Two different identities

**Requesting user:** the person asking a question. Authentication establishes who they are; authorization decides which content and operations they may use.

**Workload identity:** the application process connecting to a downstream service, such as a search index. Its credentials enable the service connection. They do not establish the human caller's document permissions.

For example, an application's identity may be able to query an index containing documents for several teams. Before any result enters model context, the application must constrain retrieval to documents this user may read. Supplying a role name in a prompt is not authentication. A model instruction saying “do not reveal restricted data” is not a replacement for retrieval authorization.

Azure managed identity is a proposed way to authenticate the future Azure-hosted workload without application-managed passwords or keys, where the services support it. Hosting, concrete role assignments, tenant/group identifiers and SDK choices belong to the deployment increment; none is configured here.

## Proposed matrix

“Conditional” means all approval, identity, source eligibility and resource-scope requirements in access-policy.json must pass. Every permission is planned, not currently implemented.

| Actor | Read documentation answers | Query index for user | Rebuild approved index | Propose policy changes | Execute pipelines / change watermarks / grant access |
|---|---|---|---|---|---|
| northstar-reader | Conditional | Through application only | Deny | Deny | Deny |
| northstar-operator | Conditional | Through application only | Deny | Deny | Deny |
| Unknown, anonymous or unassigned user | Deny | Deny | Deny | Deny | Deny |
| Retrieval workload | No independent user entitlement | Conditional on both user and workload authorization | Deny | Deny | Deny |
| Separate indexing workload | Deny | Deny | Conditional | Deny | Deny |
| Corpus maintainer responsibility | Requires separate reader/operator role | Deny | Deny | Reviewed repository process | Deny through assistant |

Readers and operators deliberately have identical permissions for the initial documentation baseline. The operator label does not enable recovery tools. #14/#17 will define and enforce any future consequential tool permissions.

The indexing process needs a different resource permission scope from the serving process: it prepares approved content and writes index entries. The serving process should read/query its required index scope without index-write permission. Indexing remains subject to source approval even though it has no interactive end user.

Maintaining a corpus is a governance responsibility, not an automatic application access grant. The lab maintainer is cetanibp; independent review has not been demonstrated.

## Planned request checks

1. Validate the user identity with supported middleware, including issuer, tenant, audience, signature and expiry. Resolve roles from trusted server-side policy; never accept prompt text or caller-supplied role/filter values as authority.
2. Check the current approved policy, selected corpus and source eligibility, including approval, freshness, removal and revocation.
3. Establish the workload's identity and scoped service permission separately.
4. Build the allowed-document restriction on the server from the intersection of user permissions and eligible selected sources. Apply it on every retrieval path before content reaches model context.
5. Apply the same check to cached answers, derived glossary definitions, snippets and citations. If current authorization cannot be established, deny instead of returning an old answer.
6. Record a sanitized decision with correlation and policy/corpus versions. Return a generic denial that does not reveal restricted document titles or URLs.

These checks are design requirements, not executable code. There must be no alternative API that accepts arbitrary security filters or exposes the workload's broader index access to clients.

## What this lab can prove

The source GitHub repository is public. A rule denying a document through our assistant cannot make that source private or prevent someone reading it directly on GitHub. Future tests can prove that the application follows its configured restrictions over synthetic fixtures. Demonstrating confidential-source isolation requires a separately protected synthetic fixture and deployment evidence; no real sensitive data is needed.

The current three documents share one classification and the same two allowed reader roles. They can test authenticated versus unassigned access but do not yet supply contrasting per-document reader permissions. A future synthetic fixture will be needed to test that boundary meaningfully.

The manifest and glossary are still drafts. Their content approval, real identity mappings, enforced retrieval filters and measured revocation behavior remain prerequisites for claiming runtime readiness. Evaluation design can proceed while those controls are being prepared.

## Freshness, revocation, audit and exceptions

The manifest's proposed 30-day source review remains in effect as a design value. Check source revisions before index builds and current eligibility for each answer. Application policy should deny a known revoked source or user before cleanup, then remove affected index and cache entries. Directory changes, token lifetime and change-detection delays must be measured; this document does not promise instant propagation from Entra.

Audit only the fields listed in the JSON. The proposed retention for sanitized access-decision records is 30 days, separate from the content review interval. Both numbers are lab choices pending review, not Microsoft requirements. Exclude tokens, credentials, source bodies, sensitive questions and denied-document metadata. Detailed retention and export implementation follows with #20/#45.

No exception is enabled. A future exception needs documented scope, approver, expiry and revocation verification outside the assistant. This step does not grant any access or authorize a recovery action.

## Evaluation seeds

The JSON includes eleven scenario specifications, covering an authorized reader, operator action denial, unknown identities, forged roles/filters, workload-only access, revoked cached access, ineligible sources, unavailable policy, injected source instructions, serving-workload writes and maintainer role separation. They are visible development examples, not held-out cases or executed security tests. Later deterministic assertions must verify denied content never appears in retrieved model context, answers, citations or sensitive logs.

## Learning resources

- [Microsoft: Managed identities overview](https://learn.microsoft.com/en-us/entra/identity/managed-identities-azure-resources/overview) — read “What are managed identities?” and watch the embedded overview video. Workload authentication still requires downstream authorization.
- [Microsoft: Security filters for Azure AI Search](https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search) — read “About the security filter pattern.” A filter string does not authenticate its principal; the application must supply trusted identity context. The article also points to built-in ACL support; implementation selection must verify support for our eventual source and service configuration.

Resources checked September 6, 2026. This is a proposed application policy, not a deployed Purview control, Entra configuration or final Azure architecture decision.

## Evidence and next step

Artifact checks validate JSON, policy-ID agreement with the manifest, matching corpus/document/classification scope, reader-role consistency, operation references, deny defaults, unique scenario IDs and documentation links. Those checks establish structural consistency, not effective authorization.

Review the matrix and explain why an application with index access must still check the person asking the question. Next walkthrough: design the initial evaluation questions and expected behavior before choosing or tuning retrieval. Approval and runtime readiness remain explicitly open.
