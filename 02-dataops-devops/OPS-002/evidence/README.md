# OPS-002 evidence

## Current evidence

- `local-contract-test-results.json` — sanitized local execution report.
- [Live Development checkpoint](live-development-checkpoint.md) — deployment, projection, SLO, and simulated routing results.
- [Failure-recovery exercise](failure-recovery-exercise.md) — stale-candidate detection, triage, terminal handling, and state-safe recovery.
- GitHub Actions will publish `ci-contract-test-results.json` as the `ops-002-contract-evidence` artifact.

## Evidence boundaries

The failure exercise used a real orphaned candidate discovered during precheck. Replay was intentionally unnecessary because a later accepted boundary already covered the stale candidate's range.

Evidence must not include workspace or item identifiers, endpoints, credentials, tenant information, personal routing addresses, patient data, proprietary metadata, or source payloads.
