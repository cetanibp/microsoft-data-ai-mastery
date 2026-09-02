from __future__ import annotations

import unittest
from pathlib import Path


RUNBOOK_ROOT = Path(__file__).resolve().parents[1] / "runbooks"


class RunbookContractTests(unittest.TestCase):
    def test_required_runbooks_exist(self):
        for name in (
            "README.md",
            "triage.md",
            "replay.md",
            "escalation.md",
            "recovery.md",
            "incident-record-template.md",
            "queries.sql",
        ):
            self.assertTrue((RUNBOOK_ROOT / name).is_file(), name)

    def test_replay_preserves_quality_and_state_boundaries(self):
        text = (RUNBOOK_ROOT / "replay.md").read_text()
        for token in (
            "Do not update `WatermarkState` directly",
            "original object-run identity and boundary",
            "quality-accepted wrapper",
            "idempotent",
            "input_boundary_hash",
        ):
            self.assertIn(token, text)

    def test_p1_is_unsuppressible_and_requires_containment(self):
        escalation = (RUNBOOK_ROOT / "escalation.md").read_text()
        triage = (RUNBOOK_ROOT / "triage.md").read_text()
        self.assertIn("Suppression is prohibited", escalation)
        self.assertIn("two-person review", escalation)
        self.assertIn("Stop and escalate as P1", triage)

    def test_quality_block_cannot_be_bypassed(self):
        combined = "\n".join(
            (RUNBOOK_ROOT / name).read_text()
            for name in ("README.md", "replay.md", "recovery.md")
        )
        self.assertIn("Do not disable a BLOCK rule", combined)
        self.assertIn("Bypass, downgrade, or delete the block", combined)

    def test_query_pack_is_read_only_and_correlated(self):
        text = (RUNBOOK_ROOT / "queries.sql").read_text()
        for token in (
            "vw_OpenSloBreach",
            "vw_OperationsDashboard",
            "vw_QualityEnforcementIntegrity",
            "input_boundary_hash",
            "AlertRoutingDecision",
        ):
            self.assertIn(token, text)
        lowered = text.lower()
        for forbidden in ("insert ", "update ", "delete ", "merge ", "exec "):
            self.assertNotIn(forbidden, lowered)

    def test_incident_record_prohibits_sensitive_evidence(self):
        text = (RUNBOOK_ROOT / "incident-record-template.md").read_text()
        for token in (
            "Do not include payloads",
            "credentials",
            "patient data",
            "workspace/item identifiers",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
