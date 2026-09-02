from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
CONTROL_ROOT = (
    REPO_ROOT
    / "01-fabric-platform-engineering"
    / "FAB-001"
    / "workspace"
    / "sqldb_northstar_control.SQLDatabase"
)


class SqlArtifactTests(unittest.TestCase):
    def test_operational_tables_exist(self):
        for name in ("TelemetryExclusion", "SloEvaluation", "AlertRoutingDecision"):
            self.assertTrue((CONTROL_ROOT / "ops" / "Tables" / f"{name}.sql").is_file())

    def test_operational_views_exist(self):
        names = (
            "vw_OperationalOccurrence",
            "vw_QualityEnforcementIntegrity",
            "vw_SloEvaluationLatest",
            "vw_OpenSloBreach",
            "vw_AlertRoutingCandidate",
            "vw_OperationsDashboard",
        )
        for name in names:
            self.assertTrue((CONTROL_ROOT / "ops" / "Views" / f"{name}.sql").is_file())

    def test_evaluations_are_versioned_and_evidence_hashed(self):
        text = (CONTROL_ROOT / "ops" / "Tables" / "SloEvaluation.sql").read_text()
        for token in (
            "evaluator_version",
            "source_evidence_hash",
            "UQ_ops_SloEvaluation_identity",
            "quality-enforcement",
            "critical-alert-latency",
        ):
            self.assertIn(token, text)

    def test_exclusions_require_prior_approval(self):
        table = (CONTROL_ROOT / "ops" / "Tables" / "TelemetryExclusion.sql").read_text()
        procedure = (
            CONTROL_ROOT / "ops" / "StoredProcedures" / "usp_RecordTelemetryExclusion.sql"
        ).read_text()
        self.assertIn("approved_at_utc] <= [effective_start_utc", table)
        self.assertIn("approved and recorded before it begins", procedure)
        self.assertIn("WITH (UPDLOCK, HOLDLOCK)", procedure)

    def test_slo_persistence_rejects_identity_changes(self):
        text = (
            CONTROL_ROOT / "ops" / "StoredProcedures" / "usp_RecordSloEvaluation.sql"
        ).read_text()
        for token in (
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE",
            "WITH (UPDLOCK, HOLDLOCK)",
            "SLO evaluation identity changed",
            "@evaluation_status",
        ):
            self.assertIn(token, text)

    def test_routing_is_environment_aware_and_p1_is_unsuppressible(self):
        text = (
            CONTROL_ROOT
            / "ops"
            / "StoredProcedures"
            / "usp_RecordAlertRoutingDecision.sql"
        ).read_text()
        self.assertIn("WHEN @is_production = 1", text)
        self.assertIn("P1 alert routing cannot be suppressed", text)
        self.assertIn("HASHBYTES('SHA2_256'", text)
        self.assertNotIn("https://", text)
        self.assertNotIn("@northstar", text.lower())

    def test_quality_integrity_checks_state_and_accepted_status(self):
        occurrence = (
            CONTROL_ROOT / "ops" / "Views" / "vw_OperationalOccurrence.sql"
        ).read_text()
        for token in (
            "candidate.candidate_status = 'COMMITTED'",
            "watermark.committed_object_run_id = attempt.object_run_id",
            "SUCCEEDED_WITH_WARNINGS",
            "quality_enforcement_status",
        ):
            self.assertIn(token, occurrence)

    def test_development_and_test_routes_cannot_embed_destinations(self):
        table = (
            CONTROL_ROOT / "ops" / "Tables" / "AlertRoutingDecision.sql"
        ).read_text()
        for token in ("NOT LIKE '%@%'", "NOT LIKE '%://%'", "NOT LIKE '%=%'"):
            self.assertIn(token, table)


if __name__ == "__main__":
    unittest.main()
