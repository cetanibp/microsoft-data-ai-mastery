# Clarification retrieval checkpoint 10

[Structured results](azure-clarification-retrieval-10.json). User-supplied lab run at 2026-09-10T23:41:07.886176+00:00; no Azure configuration changes.

| Case | Original required ranks | Clarified required ranks |
|---|---|---|
| Rerun: Procedure / Select a pattern | missing / 2 | 5 / 1 |
| Watermark: Procedure / Recovery verification | missing / 5 | 2 / 1 |
| Force commit: Corrective state action | missing | unchanged control: missing |

Both synthetic clarification variants contain all required passages; original gaps reproduce. Rerun Procedure remains at the top-five boundary. Watermark variant asks for verification steps, not a live value. Added context and changed intent are explicit experimental inputs, not model-generated clarification.

The runner initially returned invalid JSON. Stripping CR from Git Bash job IDs resolved the user run; Windows CRLF handling was the suspected cause. The repository runner now strips CR defensively and writes the jobs file with explicit LF. No raw failing HTTP body was captured to prove causality.

Next: [answer evaluation 01](../evaluation/answer-evaluation-01.md). Retrieval is frozen for this slice; model/deployment discovery is needed before constructing a provider-specific caller. No generated answer, reserved evaluation, authorization proof, issue closure or score change is claimed.
