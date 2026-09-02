# FAB-003 reference runtime

This folder contains a credential-free executable quality-gate contract using only synthetic Northstar data.

The first increment provides:

- typed allowlisted policy definitions;
- absolute and percentage count reconciliation plus aggregate observations;
- deterministic `BLOCK` and `WARN` decisions;
- idempotent quality-result and quarantine identities;
- an explicit watermark-commit eligibility result.

The reference runtime proves semantics and is not the production Fabric execution engine.

See [quality_gates.py](quality_gates.py).
