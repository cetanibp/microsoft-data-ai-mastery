from __future__ import annotations

import json
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
FAB003_ROOT = REPO_ROOT / "01-fabric-platform-engineering" / "FAB-003"


class SqlArtifactTests(unittest.TestCase):
    def test_runtime_tables_and_operational_view_exist(self):
        expected = [
            CONTROL_ROOT / "ops" / "Tables" / "QualityCheckResult.sql",
            CONTROL_ROOT / "ops" / "Tables" / "QualityDecision.sql",
            CONTROL_ROOT / "ops" / "Tables" / "QuarantineEvidence.sql",
            CONTROL_ROOT / "ops" / "Views" / "vw_QualityResultOperational.sql",
        ]
        for path in expected:
            self.assertTrue(path.is_file(), path)

    def test_quality_results_are_correlated_and_constrained(self):
        text = (
            CONTROL_ROOT / "ops" / "Tables" / "QualityCheckResult.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("FK_ops_QualityCheckResult_object_run", text)
        self.assertIn("FK_ops_QualityCheckResult_policy", text)
        self.assertIn("UQ_ops_QualityCheckResult_rule", text)
        for token in ("'PASS'", "'WARN'", "'FAIL'", "'ERROR'", "'BLOCK'"):
            self.assertIn(token, text)

    def test_result_and_quarantine_writes_are_idempotent(self):
        result_proc = (
            CONTROL_ROOT
            / "ops"
            / "StoredProcedures"
            / "usp_RecordQualityCheckResult.sql"
        ).read_text(encoding="utf-8")
        quarantine_proc = (
            CONTROL_ROOT
            / "ops"
            / "StoredProcedures"
            / "usp_RecordQuarantineEvidence.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("Quality result identity changed", result_proc)
        self.assertIn("WITH (UPDLOCK, HOLDLOCK)", result_proc)
        self.assertIn("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE", quarantine_proc)
        self.assertIn("BEGIN TRANSACTION", quarantine_proc)
        self.assertIn("COMMIT TRANSACTION", quarantine_proc)

    def test_quarantine_stores_hashes_not_payloads(self):
        text = (
            CONTROL_ROOT / "ops" / "Tables" / "QuarantineEvidence.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("source_record_identity_hash", text)
        self.assertIn("input_boundary_hash", text)
        self.assertNotIn("payload", text.lower())
        self.assertNotIn("source_value", text.lower())

    def test_finalization_blocks_and_abandons_candidate(self):
        text = (
            CONTROL_ROOT
            / "ops"
            / "StoredProcedures"
            / "usp_FinalizeQualityDecision.sql"
        ).read_text(encoding="utf-8")
        for token in (
            "QUALITY_GATE_BLOCKED",
            "candidate_status = 'ABANDONED'",
            "watermark_commit_eligible",
            "Required quality results are missing or duplicated",
        ):
            self.assertIn(token, text)

    def test_completion_wrapper_requires_accepted_decision(self):
        text = (
            CONTROL_ROOT
            / "ops"
            / "StoredProcedures"
            / "usp_CompleteQualityAcceptedWatermarkAttempt.sql"
        ).read_text(encoding="utf-8")
        eligibility_position = text.index("watermark_commit_eligible = 1")
        completion_position = text.index("EXEC ops.usp_CompleteWatermarkAttempt")
        self.assertLess(eligibility_position, completion_position)
        self.assertIn("WITH (UPDLOCK, HOLDLOCK)", text)

    def test_policy_resolution_reuses_fab001_contract(self):
        text = (
            CONTROL_ROOT
            / "ops"
            / "StoredProcedures"
            / "usp_ResolveQualityPolicy.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("ctrl.ObjectQualityPolicy", text)
        self.assertIn("ctrl.QualityPolicy", text)
        self.assertIn("contract_reference", text)


class NotebookArtifactTests(unittest.TestCase):
    def setUp(self):
        self.notebook_path = (
            FAB003_ROOT
            / "workspace"
            / "NB_FAB003_QualityGate.Notebook"
            / "notebook-content.py"
        )
        self.source = self.notebook_path.read_text(encoding="utf-8")

    def test_notebook_is_a_deployable_fabric_item(self):
        platform_path = self.notebook_path.parent / ".platform"
        platform = json.loads(platform_path.read_text(encoding="utf-8"))
        self.assertEqual("Notebook", platform["metadata"]["type"])
        self.assertEqual("NB_FAB003_QualityGate", platform["metadata"]["displayName"])
        self.assertIn("# PARAMETERS CELL", self.source)
        self.assertIn('"name": "synapse_pyspark"', self.source)

    def test_notebook_uses_allowlisted_contracts_without_executable_metadata(self):
        for token in (
            "CONTRACTS =",
            "ALLOWED_CHECK_TYPES",
            "ALLOWED_OPERATORS",
            "ALLOWED_FIELDS",
            "UNSUPPORTED_QUALITY_CONTRACT",
        ):
            self.assertIn(token, self.source)
        self.assertNotIn("eval(", self.source)
        self.assertNotIn("exec(", self.source)
        self.assertNotIn("spark.sql(", self.source)

    def test_notebook_persists_and_returns_quality_evidence(self):
        for token in (
            "quality_results_table",
            "quarantine_table",
            ".whenMatchedUpdateAll()",
            '"quality_results": results',
            '"quarantine_records": quarantine_records',
            '"watermark_commit_eligible"',
            '"result_set_hash"',
        ):
            self.assertIn(token, self.source)

    def test_failure_injection_is_development_only(self):
        self.assertIn('environment_name == "development"', self.source)
        self.assertIn('"BLOCK_TARGET_COUNT"', self.source)
        self.assertIn('"REQUIRED_ERROR"', self.source)

    def test_no_physical_or_secret_values_are_committed(self):
        lowered = self.source.lower()
        for forbidden in (
            "password=",
            "client_secret",
            "access_token",
            "jdbc:",
            "https://onelake",
            "workspace_id",
            "tenant_id",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_fab002_emits_only_hashed_duplicate_identities_when_available(self):
        upstream = (
            REPO_ROOT
            / "01-fabric-platform-engineering"
            / "FAB-002"
            / "workspace"
            / "NB_FAB002_IncrementalEncounter.Notebook"
            / "notebook-content.py"
        )
        if upstream.exists():
            text = upstream.read_text(encoding="utf-8")
            self.assertIn("duplicate_identity_hashes", text)
            self.assertIn("F.sha2", text)
            self.assertIn('"duplicate_identity_hashes"', text)


if __name__ == "__main__":
    unittest.main()
