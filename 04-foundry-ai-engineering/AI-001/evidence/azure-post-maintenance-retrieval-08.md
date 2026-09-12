# Post-maintenance retrieval — checkpoint 08

Evidence: user-executed Azure lab responses, manually reviewed. [Structured observations](azure-post-maintenance-retrieval-08.json).

## Purpose and outcome

[Checkpoint 07](azure-heading-maintenance-07.md) established automatic population of missing target heading values. This checkpoint asks whether retrieval quality reproduces after that maintenance.

The five-query batch recorded at 2026-09-10T20:11:39.715280+00:00 reproduced four of five primary ranks:

| Case | Before maintenance | After maintenance |
|---|---:|---:|
| Target-write failure | 1 | 1 |
| Recovery completion | 1 | 1 |
| Triage identifiers | 1 | 2 |
| Routing failure | 1 | 1 |
| Stale candidate | 2 | 2 |

All five primary evidence passages remained in top five. Completion's checklist remained second and stale candidate's checklist fourth. All returned lab flags were false. The identifier passage retains at least one, the full option list, and the sensitive-information restriction.

## Diagnostic controls

The identifiers query was repeated three times with exactly the same request. The original batch plus three repeats had identical top-five ordering and scores. Completion criteria scored 6.5382185 and Required starting evidence 6.2656846; this was not an equal-score tie.

A further paired query at 2026-09-10T20:55:36.897690+00:00 changed only scoringStatistics from omitted/default to global. Both returned seven matches, the required passage second, and identical top-five scores/order. No Azure configuration changed.

This provides no observed benefit from global scoring for this case. It neither establishes why the historical ranking changed nor proves all shard/replica behavior irrelevant. No feature weights, synonyms, session IDs or semantic/vector ranking were introduced.

## Decision and next increment

Retain separate headings with default scoring as a provisional development baseline, now with primary ranks 1,1,2,1,2. Preserve the regression in the record. Automatic heading population passed; complete rank parity did not.

Move to the [broader development retrieval batch](../evaluation/development-retrieval-batch-02.json), selected from existing development cases with no runtime fixture overrides. Expected evidence and future answer behavior are declared before execution. Required nested State evidence is evaluated inside the managed Recovery verification chunk.

This is retrieval inspection, not a test of generated clarification, refusal, live diagnosis, access control or full rubric success. Reserved cases remain unused. Changed-source and absent-source-heading lifecycle fixtures remain separate pending work.

Local responses are user-owned evidence; pasted formatting is not a byte-exact archive. No issue closure or skill-score change.
