# Northstar operational glossary

Step 3 of the AI-001 prerequisite walkthrough. **Draft; source-informed definitions and proposed clarification behavior only.** No retrieval or semantic evaluation has run.

The [machine-readable glossary](operational-glossary.json) connects stable term IDs, domain-specific meanings, conservative aliases, common confusions and revision-pinned source sections. It supports [DATA-001 #19](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/19) and [AI-001 #13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13).

## Why a glossary matters

The manifest answers which documents we may use. The glossary answers what important words mean in Northstar. For example, a target write can succeed before a later failure; that does not establish quality acceptance or permission to advance committed state. A fluent answer that merges these concepts can recommend an incorrect action.

Definitions are source-informed paraphrases for review, not replacements for the original contracts. The initial corpus does not define every SQL field, interval predicate, identifier cardinality or recovery step. Ask for more evidence when those details matter.

## Terms and source evidence

### Quality block

A quality outcome that prevents acceptance when a required blocking check fails.

**Operational meaning:** Do not bypass, downgrade or delete the block. Correct data or contract implementation and use the documented recovery procedure; watermark commit requires acceptance.

**Aliases:** blocking quality failure. **Do not equate with:** quality warning; every execution failure.

**Sources:** [northstar-quality-gates](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/01-fabric-platform-engineering/FAB-003/README.md) — Initial vertical slice; [northstar-recovery](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/recovery.md) — Select a pattern, State.

### Quality warning

A warning-level quality result, distinguished from a blocking quality failure by the activated policy.

**Operational meaning:** A warning is not itself proof of an accepted run. Inspect the full quality and acceptance evidence; do not convert a blocking rule to WARN to bypass recovery requirements.

**Aliases:** warning-level quality result. **Do not equate with:** quality block; proof that all acceptance requirements passed.

**Sources:** [northstar-quality-gates](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/01-fabric-platform-engineering/FAB-003/README.md) — Initial vertical slice, Issue acceptance criteria; [northstar-recovery](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/recovery.md) — Select a pattern.

### Committed watermark

The accepted progress state tracked by the watermark protocol; this glossary uses the term for committed state rather than a proposed candidate.

**Operational meaning:** Verify the committed version and committing object run. A candidate commits only after acceptance; normal replay must follow the compare-and-commit protocol.

**Aliases:** committed ingestion watermark. **Do not equate with:** proposed watermark candidate; latest source timestamp; target write completion.

**Sources:** [northstar-quality-gates](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/01-fabric-platform-engineering/FAB-003/README.md) — Binding upstream contracts; [northstar-recovery](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/recovery.md) — State, Corrective state action.

### Fixed input boundary

The identified input scope retained for an ingestion attempt and its recovery replay.

**Operational meaning:** After a durable target write followed by failure, the recovery runbook specifies replaying the same boundary rather than creating a new one. Exact interval endpoints and predicates are outside this initial corpus.

**Aliases:** fixed ingestion input boundary. **Do not equate with:** new input scope; unbounded latest data.

**Sources:** [northstar-triage](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/triage.md) — Procedure; [northstar-recovery](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/recovery.md) — Select a pattern.

### Replay

Reprocessing under the documented recovery pattern; data replay after a durable target write uses the same fixed boundary and an idempotent merge.

**Operational meaning:** Establish run state and ownership first. Do not replay an active ingestion occurrence. Telemetry-only recovery may require replaying the evaluator/router rather than ingestion.

**Aliases:** recovery replay. **Do not equate with:** blind rerun; full reload; manual watermark advancement.

**Sources:** [northstar-triage](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/triage.md) — Procedure, Stop conditions; [northstar-recovery](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/recovery.md) — Select a pattern.

### Idempotency

For the documented data replay, repeating the operation preserves the intended target result without accumulating duplicate effects.

**Operational meaning:** Verify the target result, deduplicated quarantine evidence and at-most-once watermark advancement. A repeat-safe target merge does not by itself prove repeat-safe notifications or every other system effect.

**Aliases:** repeat-safe target result. **Do not equate with:** exactly one execution; all external side effects are repeat-safe.

**Sources:** [northstar-recovery](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/recovery.md) — Select a pattern, Data and quality, State, Observability.

### Object run

The identified execution occurrence for an ingested object, used to connect quality, state and operational evidence.

**Operational meaning:** Keep the occurrence identity when selecting evidence and verify that the committing object run matches the accepted occurrence. Do not infer cardinality or identifier equality from this glossary.

**Aliases:** object execution occurrence. **Do not equate with:** object name; correlation ID; pipeline run ID.

**Sources:** [northstar-quality-gates](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/01-fabric-platform-engineering/FAB-003/README.md) — Objective, Binding upstream contracts; [northstar-recovery](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/recovery.md) — State.

### Correlation ID

An identifier usable as a starting point to locate related operational evidence during triage.

**Operational meaning:** Use it to find evidence, then establish environment, release, occurrence and fixed boundary. Possessing an identifier does not grant access to that evidence.

**Aliases:** correlation identifier. **Do not equate with:** authorization credential; guaranteed unique object-run ID.

**Sources:** [northstar-triage](https://github.com/cetanibp/microsoft-data-ai-mastery/blob/746199302b9a0275e7dba8e1e3c8ca5586043c89/02-dataops-devops/OPS-002/runbooks/triage.md) — Required starting evidence, Procedure, Completion criteria.

## How to read the JSON

| Field | Purpose |
|---|---|
| domain | Limits these definitions to Northstar lab data operations. |
| term_id / preferred_name | Stable machine identity and readable canonical name. |
| definition | Proposed shared meaning. |
| aliases | Alternative wording that can help future retrieval in this domain. |
| not_equivalent_to | Related but distinct concepts that must not be merged. |
| operational_implication | Why the distinction affects interpretation or recovery. |
| sources | Document identity, pinned revision, file hash and supporting section names. |
| clarification_cases | Example questions and expected behavior for later evaluation. |

## Ambiguity review cases

These five cases are evaluation seeds for #16, not executed tests and not the full 30-question AI-001 dataset. Because they are visible development examples, do not later claim they are held-out cases.

| Question | Expected behavior |
|---|---|
| The quality check failed. Is the load blocked? | Clarify enforcement level and inspect the complete decision; do not equate every failed check with BLOCK. |
| The target write finished. Can we move the watermark? | Require acceptance and the normal compare-and-commit protocol; target write completion is insufficient. |
| Can I rerun it? | Clarify the occurrence and failure category, check active ownership, and distinguish ingestion replay from evaluator/router replay. |
| Does idempotent mean it only ran once? | Explain that repeated execution can preserve the intended result; execution count and effect count differ. |
| I have the correlation ID; is that the object-run ID? | Treat them as different identifier concepts and inspect the evidence mapping rather than assuming equality. |

## Scope, access and maintenance

The three-source corpus manifest stays at version 0.1.0. This glossary has its own version and is a supporting draft metadata artifact; it is not automatically indexed as a fourth approved document. A future consumer must record both versions. Approving glossary use in model context or retrieval requires an explicit integration step and the same source access/freshness checks; paraphrasing restricted content must never bypass its restrictions.

A source change triggers definition review. Update affected definitions and cases through a reviewed commit, bump glossary_version, and preserve the old version for permitted reproducibility. Conflicting definitions must be flagged for the owner rather than resolved by selecting the newest text automatically. No glossary entry grants permission to execute a recovery action.

## Learning and checkpoint

Read [Microsoft Purview: Glossary terms in Unified Catalog](https://learn.microsoft.com/en-us/purview/unified-catalog-glossary-terms), especially “What is a glossary term?” It explains shared definitions, domain context and links to data assets. This repository exercise teaches those concepts; it does not deploy or demonstrate Purview. Resource checked September 5, 2026.

For this step, compare Quality block with Quality warning, and read Replay and Idempotency. Try explaining why a repeat-safe operation can execute more than once. Step 4 now provides the [draft identity/access matrix](../../07-governance-security/GOV-001/README.md), including authorization of derived glossary content. Next: initial evaluation design.

## Artifact verification

JSON parsing, unique term/case IDs, case-to-term references, source revision/hash references and supporting section headings are checked. This validates artifact structure and traceability only. Meaning, synonym resolution, ambiguity handling, permission behavior and answer quality still need review and runtime evaluation.
