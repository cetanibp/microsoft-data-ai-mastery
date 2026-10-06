# AGENT-001 — Safe operational tool contracts

Current focus as of October 6, 2026. First increment: a versioned
`inspect_object_run` contract and a runnable direct function adapter over
synthetic fixtures. [Issue #14](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/14)
remains open; authenticated MCP and live backend evidence follow separately.

## Run the first checkpoint

From the repository root, use the existing virtual environment:

```powershell
& .\.venv\Scripts\python.exe -B -m pip install -r 05-agent-engineering/AGENT-001/requirements.txt
& .\.venv\Scripts\python.exe -B 05-agent-engineering/AGENT-001/runtime/read_only_tools.py
& .\.venv\Scripts\python.exe -B 05-agent-engineering/AGENT-001/tests/run_contract_tests.py --output 05-agent-engineering/AGENT-001/evidence/local-contract-test-results.json
```

Installation needs package access. Once installed, the demo and tests need
no credentials, endpoint, model, Fabric workspace or network.

The demo inspects two synthetic attempts. Both have a `BLOCKED` quality
decision. The first returns quality-enforcement `PASS`: its candidate was
abandoned and another attempt remains the last committing run. The second
returns `BREACH`: its candidate committed despite the block. `PASS` describes
preservation of the quality boundary; it does not authorize recovery.

The useful learning question is why the same quality decision leads to
different integrity results. Inspect the candidate status and the last
committing object-run ID, then compare the result with
[OPS-002 triage](../../02-dataops-devops/OPS-002/runbooks/triage.md).

## What is implemented

- [Draft 2020-12 schema](contracts/inspect-object-run-v1.schema.json) for inputs,
  the projected record, ranked evidence and success/error responses.
- [Direct adapter](runtime/read_only_tools.py) with a single exact lookup,
  current synthetic user/workload scope intersection, sanitized audit events,
  deadlines, cancellation checks and structured failures.
- [Behavior tests](tests/test_read_only_tools.py) for preservation/breach,
  incomplete evidence, denial, revocation between calls, injected arguments
  and output, malformed evidence, dependency errors and bounded reads.
- [Contract and identity matrix](tool-contract.md),
  [threat model and approval requirements](threat-model.md), and
  [local evidence](evidence/local-contract-test-results.json).

Evidence ranks express a fixed inspection priority: quality integrity, run
state, then quality decision. They are not model confidence or a learned
root-cause ranking. Missing quality/candidate/state evidence stays `UNKNOWN`
unless an observed condition already establishes a breach. The observation
retains the run's recorded release and fixed input-boundary hash.

## Next increment and stopping point

Wrap this same contract with an authenticated MCP adapter and compare its
authorization, failure behavior and measured latency with the direct path.
Verify current protocol/SDK support at that implementation checkpoint.
Then supply AGENT-002 with the bounded inspection interface and add owner,
lineage and correlated telemetry tools as separate contracts.

This first increment ends at runnable local contract evidence. Real token
validation, downstream SQL permissions, coherent live reads, durable audit,
authenticated MCP, workflow-wide budgets and actual producer telemetry are
open. The fixture policy is an executable example, not deployed Entra
authorization. No consequential operation is exposed.

## Retrieval handoff

The user directed a move out of retrieval tuning on October 6, 2026.
[AI-001 checkpoint 15](../../04-foundry-ai-engineering/AI-001/evidence/azure-development-query-expansion-15.md)
remains the last executed comparison: original 3/5, expanded 4/5 and fused
3/5 complete contexts. The force-commit gap and semantic reviewer failures
remain unresolved. Comparison 03 remains a draft pending independent review;
it is deferred while this track proceeds. AI-001 completion is not claimed.
