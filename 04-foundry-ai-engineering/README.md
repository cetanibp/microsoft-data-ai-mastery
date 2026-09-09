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

The [DATA-001 corpus walkthrough](../06-ai-ready-data/DATA-001/README.md) now provides a draft manifest for three Northstar operational documents. The source-linked glossary and [draft identity/access matrix](../07-governance-security/GOV-001/README.md) are also available. [AI-001 evaluation design](AI-001/evaluation/README.md) now supplies 30 questions and proposed targets before tuning. [Local corpus preparation](AI-001/runtime/README.md) now verifies three source hashes and builds two chunking alternatives, with 13 passing local tests. [Three-way Azure keyword retrieval evidence](AI-001/evidence/azure-markdown-h2-comparison-03.md) now records five development questions and 24/15/18 chunks. Azure h2 preserves complete required context within the top five for all five; ranking is mixed. Next: capture sanitized configuration and align comparison controls; approval, serving-time enforcement and the #19/#20 runtime readiness gate remain open.
