# Northstar offline reference

Replay five saved development cases with Python 3.10 or later and its standard
library. No Azure access, credentials, model, dependencies, or original lab
directory are required.

Open the [ingestion reference](views/AI001-012-C1.md) or
[watermark reference](views/AI001-013-C1.md) in Markdown preview. Both retain
all five retrieved passages in their saved order. The other views contain
the [rerun clarification](views/AI001-012.md),
[watermark clarification](views/AI001-013.md), and
[force-commit refusal](views/AI001-025.md).

## Run from the repository root

```bash
python -X utf8 04-foundry-ai-engineering/AI-001/offline-reference/reference.py --case AI001-012-C1
python -X utf8 04-foundry-ai-engineering/AI-001/offline-reference/reference.py --case AI001-013-C1 --format json
python -m unittest discover -s 04-foundry-ai-engineering/AI-001/tests -p test_offline_reference.py -v
```

For portable replay, copy `reference.py` and the `inputs` directory together
to any directory, then run `python -X utf8 reference.py --case AI001-012-C1`.
The CLI resolves inputs relative to its own file. Unknown case IDs fail.
It verifies input hashes, case identity, development split, the five-passage
limit, path containment, and false runtime eligibility before rendering.
These checks detect accidental changes; they are not authentication or
serving-time authorization, and hashes stored beside inputs are not signatures.

## What this reference demonstrates

The two procedure cases display source evidence, not generated procedural
answers. The other three replay frozen clarification/refusal decisions. The
CLI does not classify new questions, retrieve fresh passages, or inspect live
state. Its refusal's historical wording, "This read-only application", does
not mean a serving application has been deployed.

Both procedure views preserve the two required evidence sections from their
saved contexts. The force-commit case still lacks Corrective state action in
its saved retrieval. That passage exists in other cases but is not inserted
into this one. A clear refusal does not satisfy its missing-evidence gate.

The [user feedback](../evidence/offline-reference-navigation-human-feedback.md)
supports retaining the navigation and wording. Interpretation, full reading
burden, semantic correctness, and application readiness are separate judgments.
The [historical agent review](review/prior-codex-review.json) is retained as an
archive; its `passed` labels are limited agent judgments, not human approval.

## Import provenance

This package derives from `offline-reference-v2-w609x6jv`. Its
[import manifest](import-manifest.json) records original and repository hashes
for every imported file and each transformation. Source files were checked
against the original inventory before import. The runtime script and all five
Markdown views are byte-identical to that package.

Original Azure chunk IDs encode storage addresses. In inputs and JSON views,
each is replaced by `sha256:` plus the SHA-256 of the original UTF-8 ID. The
input index hashes were recomputed for these explicitly sanitized copies.
Passage text, headings, order, document identities, pinned URLs, source commit,
saved questions, decisions, and false eligibility flags remain unchanged.
JSON preserves embedded source whitespace; Markdown uses normalized line endings.

The manifest is an import record, not a signature or a hash inventory for new
repository documentation. `.gitattributes` preserves LF bytes on checkout.

[Checkpoint 12](../evidence/azure-answer-reference-12.md) documents the later
span and selection failures that led to retaining every retrieved passage.
Full historical model callers, raw requests, and authentication artifacts
remain in the operator's lab. Their inference is not reproduced by this CLI.
