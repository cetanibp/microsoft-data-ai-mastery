# Working Agreement

## Issue lifecycle

`Backlog` → `This Quarter` → `This Month` → `This Week` → `In Progress` → `Review / Improve` → `Mastered`

- Limit work in progress to two items.
- Link each work item to one epic and one milestone.
- Split items that cannot produce reviewable evidence within two weeks.
- Keep learning notes inside the implementation or architecture context they support.

## Definition of done

- Acceptance criteria are checked.
- Implementation is reproducible.
- Happy-path and failure-path tests exist.
- Architecture and tradeoffs are documented.
- Security, operations, and cost implications are considered.
- Evidence is linked from the issue.
- A short retrospective names what changed and what should improve next.

## Repository conventions

- Use architecture decision records for consequential choices. Copy `09-enterprise-architecture/decisions/ADR-000-template.md` and number sequentially.
- Inside each track folder, keep evidence for a work item in a subfolder named after its planning ID (for example `01-fabric-platform-engineering/FAB-002/`) containing source, tests, docs or diagrams, and a short `RETRO.md`.
- Never commit secrets, credentials, patient data, or proprietary production data.
- Use synthetic or approved public datasets.
- Prefer diagrams-as-code or source-editable diagrams.
- Make demos repeatable from documented prerequisites.


## Learning-depth and dependency rules

- Specify prerequisite **increments** when the full upstream issue is not needed. The #19/#20 corpus/access slice enables #13; full governance follows later.
- Define AI datasets, expected behavior, held-out cases, thresholds, and version capture before implementation tuning. Add agent-specific evaluation as the workflow becomes executable.
- Separate core epic exit gates from optional advanced extensions. Optional issues may remain open after core delivery; milestone closure still requires its assigned issues to be completed or explicitly replanned.
- Link retrospective follow-ups to owned issues and point historical documents to current tracking without rewriting original results.
- Label evidence as planned, artifact-only validation, lab behavior, simulation, or independently reviewed as appropriate. Do not substitute one for another.
- Preserve skill scores during planning updates. Level 4 needs a second scenario, independent troubleshooting, and quantified tradeoffs; level 5 also needs standards, mentoring/handoff, and defended decisions with feedback.
- Record product/SDK versions and current support limitations when choosing implementation details. Use synthetic or approved public data throughout.

See [the September review](tracking/LEARNING_GAP_REVIEW_2026-09.md) for the current expanded backlog.
