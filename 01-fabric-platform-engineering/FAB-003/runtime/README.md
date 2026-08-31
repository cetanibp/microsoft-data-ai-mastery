# FAB-003 reference runtime

This folder will contain a credential-free executable quality-gate contract using only synthetic Northstar data.

The first increment will provide:

- typed allowlisted policy definitions;
- count and aggregate observations;
- deterministic `BLOCK` and `WARN` decisions;
- idempotent quality-result and quarantine identities;
- an explicit watermark-commit eligibility result.

The reference runtime proves semantics and is not the production Fabric execution engine.
