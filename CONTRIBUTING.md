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

