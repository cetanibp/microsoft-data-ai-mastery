from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


FAB002_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = FAB002_ROOT.parents[1]
SQL_ROOT = (
    REPO_ROOT
    / "01-fabric-platform-engineering"
    / "FAB-001"
    / "workspace"
    / "sqldb_northstar_control.SQLDatabase"
    / "ops"
    / "StoredProcedures"
)
NOTEBOOK_ROOT = (
    FAB002_ROOT / "workspace" / "NB_FAB002_IncrementalEncounter.Notebook"
)


class SqlRuntimeProcedureTests(unittest.TestCase):
    def test_required_procedures_are_present(self) -> None:
        expected = {
            "usp_ResolveWatermarkContext.sql",
            "usp_BeginWatermarkAttempt.sql",
            "usp_CompleteWatermarkAttempt.sql",
            "usp_FailWatermarkAttempt.sql",
        }
        self.assertTrue(expected.issubset({path.name for path in SQL_ROOT.glob("*.sql")}))

    def test_begin_claims_state_and_candidate_atomically(self) -> None:
        sql = (SQL_ROOT / "usp_BeginWatermarkAttempt.sql").read_text("utf-8")
        for required in (
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE",
            "WITH (UPDLOCK, HOLDLOCK)",
            "BEGIN TRANSACTION",
            "INSERT ops.ObjectRun",
            "INSERT ops.WatermarkCandidate",
            "'PROPOSED'",
            "COMMIT TRANSACTION",
        ):
            self.assertIn(required, sql)

    def test_commit_uses_compare_and_commit_predicate(self) -> None:
        sql = (SQL_ROOT / "usp_CompleteWatermarkAttempt.sql").read_text("utf-8")
        for required in (
            "AND committed_value = @from_value",
            "AND state_version = @observed_state_version",
            "IF @@ROWCOUNT = 0",
            "'RECOVERY_REQUIRED'",
            "'WATERMARK_COMMITTED'",
        ):
            self.assertIn(required, sql)

    def test_failure_abandons_candidate_without_updating_state(self) -> None:
        sql = (SQL_ROOT / "usp_FailWatermarkAttempt.sql").read_text("utf-8")
        self.assertIn("candidate_status = 'ABANDONED'", sql)
        self.assertNotIn("UPDATE ops.WatermarkState", sql)
        self.assertIn("'WATERMARK_ABANDONED'", sql)
        self.assertIn("@accepted_row_count + @rejected_row_count", sql)
        self.assertIn("THROW 51033", sql)

    def test_procedures_do_not_contain_secret_assignments(self) -> None:
        secret_assignment = re.compile(
            r"(?i)(password|secret|token|connection_string)\s*[:=]\s*['\"]"
        )
        for path in SQL_ROOT.glob("*.sql"):
            self.assertIsNone(secret_assignment.search(path.read_text("utf-8")))


class NotebookArtifactTests(unittest.TestCase):
    def test_platform_metadata_is_valid_and_has_no_physical_binding(self) -> None:
        platform = json.loads((NOTEBOOK_ROOT / ".platform").read_text("utf-8"))
        self.assertEqual("Notebook", platform["metadata"]["type"])
        self.assertEqual(
            "NB_FAB002_IncrementalEncounter", platform["metadata"]["displayName"]
        )
        self.assertNotIn("workspace", json.dumps(platform).lower())
        self.assertNotIn("lakehouse", json.dumps(platform).lower())

    def test_notebook_enforces_window_deduplication_and_delta_merge(self) -> None:
        notebook = (NOTEBOOK_ROOT / "notebook-content.py").read_text("utf-8")
        for required in (
            'F.col("updated_at_utc") >',
            'F.col("updated_at_utc") <=',
            'Window.partitionBy("encounter_id")',
            '.merge(accepted.alias("source")',
            ".whenMatchedUpdateAll()",
            ".whenNotMatchedInsertAll()",
        ):
            self.assertIn(required, notebook)

    def test_notebook_routes_additive_and_blocks_breaking_drift(self) -> None:
        notebook = (NOTEBOOK_ROOT / "notebook-content.py").read_text("utf-8")
        self.assertIn('scenario == "additive_drift"', notebook)
        self.assertIn('scenario == "breaking_drift"', notebook)
        self.assertIn("BREAKING_SCHEMA_DRIFT", notebook)
        self.assertIn("column_names_json", notebook)
        self.assertNotIn("rejected_payload", notebook)

    def test_additive_drift_evidence_is_idempotent_by_object_run(self) -> None:
        notebook = (NOTEBOOK_ROOT / "notebook-content.py").read_text("utf-8")
        self.assertIn("drift_event_frame", notebook)
        self.assertIn(
            '"target.object_run_id = source.object_run_id"', notebook
        )
        self.assertIn('drift_target.alias("target")', notebook)
        self.assertNotIn('mode(\n        "append"\n    ).saveAsTable(drift_table)', notebook)

    def test_notebook_has_required_parameter_and_exit_contract(self) -> None:
        notebook = (NOTEBOOK_ROOT / "notebook-content.py").read_text("utf-8")
        self.assertIn("# PARAMETERS CELL", notebook)
        for name in (
            "release_id",
            "run_id",
            "object_run_id",
            "correlation_id",
            "lower_bound",
            "upper_bound",
        ):
            self.assertRegex(notebook, rf"(?m)^{name} = ")
        self.assertIn("notebookutils.notebook.exit(result_json)", notebook)


if __name__ == "__main__":
    unittest.main()
