# OPS-002 retrospective

## Outcome

OPS-002 turned correlated ingestion and quality evidence into measurable SLO evaluations, operational projections, deterministic alert-routing decisions, and executable incident-response procedures. Live Development validation covered deployment, SLO replay safety, a reliability breach, simulated routing, and recovery of an orphaned watermark candidate.

## What worked

- Existing run, object-run, quality, watermark, ownership, and SLO identities supported observability without creating a competing execution model.
- Logical-occurrence projection prevented retries and replays from inflating reliability counts.
- Separate reliability, quality-acceptance, and quality-enforcement indicators preserved the distinction between platform failure and a correctly enforced quality block.
- Source-evidence hashes and deduplication keys made evaluation and routing persistence idempotent.
- Development routing produced durable evidence without contacting a real notification destination.
- The stale-candidate exercise demonstrated a safe recovery choice: preserve the later committed winner, abandon the obsolete attempt, and avoid an unnecessary replay.

## Problems found and corrected

### Routing deduplication

The initial candidate view and persistence procedure derived different deduplication keys. Live validation exposed the mismatch before notification persistence. The derivation was unified and automated tests now protect the contract.

### Open-breach projection

The first routing verification query expected `evaluation_status` from `ops.vw_OpenSloBreach`, but the view did not expose it. SQL compilation failed before any write. The view now projects the explicit `BREACH` status and the suite checks that surface.

### Exercise choice

The planned exercise assumed a newly injected failure. Precheck found a genuine orphaned proposed candidate from an older state version. Using that candidate produced stronger operational evidence and avoided adding artificial control-plane state.

## Current limitations

- Delivery is simulated in Development; no external paging provider or delivery acknowledgement was exercised.
- Evaluations are invoked by an operator/test batch rather than a production scheduler.
- The dashboard is a SQL projection and query pack rather than a rendered monitoring product.
- The exercise covered an object-level stale candidate, not capacity failure, regional outage, or database restore.
- Alert policy thresholds and aliases are validated for the current Northstar scenario, not benchmarked across multiple operating models.

## Improvements

1. Schedule SLO evaluation and routing with a governed Fabric orchestration identity.
2. Add delivery-provider acknowledgement and dead-letter evidence for Test or a dedicated integration environment.
3. Publish the operations projection through a governed semantic model and dashboard.
4. Measure detection, acknowledgement, and recovery latency automatically from audit events.
5. Exercise capacity exhaustion and control-store restoration as part of broader continuity testing.
6. Apply the FAB-004 F256 `PAR4` performance and capacity baselines to [#11 — RTI-001](https://github.com/cetanibp/microsoft-data-ai-mastery/issues/11) monitoring thresholds; keep SLO and routing thresholds scenario-specific until analytics, real-time, AI, and controlled companion-workload evidence is available.

## Skill result

The implementation meets the Level 3 threshold for observability, SLOs, and incident response: the solution was designed, built, contract-tested, live-validated, deliberately exercised through a real failure state, troubleshot, recovered, and documented. Level 4 still requires cross-scenario optimization, production delivery integration, and broader operational governance evidence.
