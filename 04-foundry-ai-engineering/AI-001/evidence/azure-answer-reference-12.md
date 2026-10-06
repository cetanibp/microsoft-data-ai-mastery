# Checkpoint 12: source spans, selection failures, and portable reference

Recorded September 21, 2026 for AI-001 [#13](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/13)
and evaluation work [#16](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/16).
This follows [checkpoint 11](azure-answer-guards-11.md). Historical experiments
ran September 12 Pacific time (September 12–13 UTC); this increment imports
their selected evidence and the later offline reference. No new inference,
retrieval, or cloud configuration was performed.

**Decision: retain the offline evidence reference; do not adopt the model
selector or same-model reviewer as an application release gate.**

## What happened after checkpoint 11

| Experiment | Observed result | Interpretation |
|---|---|---|
| First source-span v4 batch | Nine requests attempted; none succeeded because MFA authentication expired. Twelve local tests and 95 source spans verified. | No model-quality conclusion; API usage was unavailable, not measured as zero. |
| V4 authentication recovery | Same frozen script, prompts, schemas, cases and nine planned requests; two conditional answer reviews produced eleven successful model calls. All 29 assembled quotes were exact. Automated routes matched 5/5 and the reviewer accepted 2/2 procedure answers. | Source copying improved, but agent inspection rejected the ingestion answer for an unsupported relationship and an omitted integrity check. No full answer-quality pass. |
| Extractive v5 | Two selection calls and eight independent full-claim reviews. All four selected passages were exact; complete required evidence fell from 2/2 saved contexts to 0/2 selected views. | Exact extraction does not guarantee complete selection. |
| Offline reference and navigation revision | All retrieved passages retained in each procedure view; navigation links and source links grouped without dropping evidence. | A reproducible saved-case reference, not a classifier or synthesized answer. |

V4's ingestion claim used accountable-owner metadata to determine whether an
execution attempt owns a boundary. The cited source supports identifying the
accountable person, not that additional relationship. The model reviewer
accepted a supported prefix and missed the unsupported purpose clause. The
answer also omitted the explicit quality-enforcement-integrity check before
recovery. Watermark answer atomicity and full checklist completeness were
not established by the saved review.

The reviewer matched 6/7 v4 diagnostics but accepted D07's broad prohibition
based on condition-specific evidence. V5 matched 6/8, accepting both supported
controls and rejecting four of six unsupported cases; D07 and the added
owner/attempt negative control D08 remained false acceptances. These are
known development controls, not independent generalization evidence.

V5 selected three ingestion passages (1,809 characters) and one watermark
passage (977 characters). Each selection retained only one of two required
passages: ingestion omitted Select a pattern; watermark omitted Triage
Procedure. The all-five comparison retained 3,386 and 4,257 characters and
both required passages per case. This comparison was generated offline after
the fixed batch; it does not repair the recorded selection failures.

## Historical execution evidence

The [selected JSON export](azure-answer-reference-12.json) preserves final
reviews, allowlisted execution metadata, original file hashes, and historical
offline validation records. Imported source files were checked against their
local final hash inventories. This checks archival consistency, not an
independent reconstruction of cloud execution.

V4 recovery used 25,660 input and 1,847 output tokens across eleven calls.
V5 used 9,961 input and 647 output tokens across ten calls. The existing
deployment alias was `northstar-answer-dev`; the underlying
`gpt-4.1-mini 2025-04-14` version was carried from prior evidence, not freshly
verified here. Historical reports record `store=false` and bounded output
tokens. Timings include CLI overhead; no currency cost or production latency
claim follows. The unsuccessful authentication batch has unknown usage.

The full raw requests, responses, live callers and authentication artifacts
remain in `NorthstarLab`. The repository export is selected historical
evidence; it does not make those inference experiments independently runnable.

## Portable artifact and fresh validation

The [offline reference](../offline-reference/README.md) now contains the
unchanged renderer, five saved development inputs, expected JSON/Markdown
views, and the historical agent review. Only the script and inputs are needed
for replay. It reads no repository dataset and makes no network or model calls.

Azure-derived chunk IDs encode storage addresses. Each was replaced by a
stable SHA-256 ID in the repository inputs and JSON views. The
[import manifest](../offline-reference/import-manifest.json) records source
and destination hashes and transformations. All source text, headings, order,
questions, routes, pinned URLs and false eligibility flags were preserved.
All five Markdown views and the renderer are byte-identical to the local
navigation revision. The original lab packages were not modified.

Eight fresh [contract tests](../tests/test_offline_reference.py) passed on
September 21 using Python 3.14.2 from the repository's existing virtual
environment. The JSON export records the command, test-file hash and result.
They verify imported hashes, expected outputs, passage and link
preservation, declared required-section coverage and the unresolved control
gap, unknown-case rejection, input tampering, path escape, and saved-scope
guards. A relocation test copied only the renderer and inputs to a temporary
directory and ran all five cases in both output formats from another working
directory with Python isolated mode. These checks validate local replay, not
semantic correctness or serving-time access enforcement.

Reproduce from the repository root:

```bash
python -m unittest discover -s 04-foundry-ai-engineering/AI-001/tests -p test_offline_reference.py -v
```

## User review and next increment

[Recorded user feedback](offline-reference-navigation-human-feedback.md)
found both procedure views easy to navigate and both clarification responses
and the refusal clear. Retain the current presentation. This focused feedback
does not fill every field in the historical human-review template or establish
an independently authored evaluation. Historical agent pass labels remain
separate from this user feedback.

Next, expand independently reviewed development cases around complete
relations and purpose clauses, and investigate the force-commit retrieval gap
with a declared comparison before changing retrieval. Corrective state action
still is not present in that case's saved context; its presence in other cases
does not supply it to this one. Keep source evidence separate from generated
advice and report completeness and supported-claim failures independently.

Reserved cases remain unused. No application deployment, issue closure,
source approval, eligibility change, ADR acceptance, or competency-score change
is established by this checkpoint. Access/freshness/injection controls,
changed-source heading fixtures, vector/hybrid comparison, full rubric and
supported-answer latency/cost remain open.
