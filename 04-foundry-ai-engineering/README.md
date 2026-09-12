# Foundry AI Engineering

Store grounded AI applications, model evaluations, retrieval experiments, deployment designs, and safety evidence here.

## Planned work — September 5, 2026

Start AI-001 after the minimum #19/#20 corpus/access-policy slice, with #16 dataset/rubric design before retrieval tuning. AI-002 supplies reproducible application deployment, identity/network validation, release gates and rollback.

| Issue | Outcome | Scope |
|---|---|---|
| [#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13) | AI-001 — Build a grounded retrieval baseline | Required planned work |
| [#45](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/45) | AI-002 — Deploy the AI application with reproducible Azure infrastructure | Required planned work |

Implementation evidence will be added under each planning ID as work is completed. These links represent backlog scope, not completed capability. See the [learning-gap review](../tracking/LEARNING_GAP_REVIEW_2026-09.md) for dependencies and evidence expectations.

## Current prerequisite increment

The [DATA-001 corpus walkthrough](../06-ai-ready-data/DATA-001/README.md) now provides a draft manifest for three Northstar operational documents. The source-linked glossary and [draft identity/access matrix](../07-governance-security/GOV-001/README.md) are also available. [AI-001 evaluation design](AI-001/evaluation/README.md) now supplies 30 questions and proposed targets before tuning. [Local corpus preparation](AI-001/runtime/README.md) now verifies three source hashes and builds two chunking alternatives, with 13 passing local tests. [Three-way Azure keyword retrieval evidence](AI-001/evidence/azure-markdown-h2-comparison-03.md) now records five development questions and 24/15/18 chunks. Azure h2 preserves complete required context within the top five for all five; ranking is mixed. [Live configuration and aligned-API checks](AI-001/evidence/azure-aligned-api-comparison-04.md) now confirm all 15 required-passage ranks reproduced. [Heading-search checkpoint 05](AI-001/evidence/azure-heading-search-05.md) now records two improvements and no regressions across five development queries, with the original records preserved. [Separate-heading checkpoint 06](AI-001/evidence/azure-separate-headings-06.md) supersedes the combined preference: one primary improvement, four unchanged, and a secondary checklist regression. [Maintenance checkpoint 07](AI-001/evidence/azure-heading-maintenance-07.md) now demonstrates automatic restoration of missing heading copies with all 18 records preserved. Next: batched retrieval repeat and changed-source fixtures; approval, serving-time enforcement and the #19/#20 runtime readiness gate remain open.

## Historical checkpoint 08

[Post-maintenance retrieval and scoring diagnostic](AI-001/evidence/azure-post-maintenance-retrieval-08.md) records primary ranks 1,1,2,1,2: identifiers regressed to second; four other primary ranks reproduced. Four repeated samples and a default/global scoring pair produced identical identifier ordering and scores. Cause remains unconfirmed. Keep separate headings/default scoring provisionally; automatic population is verified but rank parity is not. Next: the prepared broader development retrieval batch (AI001-001, 011, 012, 013, 025). No model or reserved evaluation is claimed.

## Current checkpoint 11 — bounded model and guard experiments

[AI-001 results](AI-001/evidence/azure-answer-guards-11.md) now include saved-context answer evaluation, knowledge-base diagnostics, automatic reformulation and three local guard iterations. Schema-constrained output works for the tested requests, but quote fidelity, assertion splitting and compound-claim support remain blockers. No serving candidate is ready; reserved evaluation, approval/access/freshness controls and deployment remain open. Skill scores and issue status are unchanged.
