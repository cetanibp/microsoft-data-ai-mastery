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
PIPELINE_ROOT = (
    FAB002_ROOT / "workspace" / "PL_FAB002_IncrementalEncounter.DataPipeline"
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


class PipelineArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.platform = json.loads((PIPELINE_ROOT / ".platform").read_text("utf-8"))
        self.pipeline = json.loads(
            (PIPELINE_ROOT / "pipeline-content.json").read_text("utf-8")
        )
        self.activities = {
            activity["name"]: activity
            for activity in self.pipeline["properties"]["activities"]
        }

    def test_platform_metadata_and_required_activity_graph(self) -> None:
        self.assertEqual("DataPipeline", self.platform["metadata"]["type"])
        self.assertEqual(
            "PL_FAB002_IncrementalEncounter",
            self.platform["metadata"]["displayName"],
        )
        self.assertEqual(
            {
                "Resolve_Context",
                "Set_ObjectRunId",
                "Set_CandidateId",
                "Compute_BoundaryHash",
                "Begin_Attempt",
                "Run_IncrementalNotebook",
                "Complete_Attempt",
                "Fail_Attempt",
            },
            set(self.activities),
        )
        self.assertEqual(
            ["Succeeded"],
            self.activities["Complete_Attempt"]["dependsOn"][0][
                "dependencyConditions"
            ],
        )
        self.assertEqual(
            ["Failed"],
            self.activities["Fail_Attempt"]["dependsOn"][0][
                "dependencyConditions"
            ],
        )

    def test_pipeline_uses_unique_run_identity_on_all_sql_paths(self) -> None:
        for activity_name in ("Begin_Attempt", "Complete_Attempt", "Fail_Attempt"):
            parameters = self.activities[activity_name]["typeProperties"][
                "storedProcedureParameters"
            ]
            correlation = parameters["correlation_id"]["value"]
            self.assertEqual("Expression", correlation["type"])
            self.assertEqual("@pipeline().RunId", correlation["value"])

        begin_parameters = self.activities["Begin_Attempt"]["typeProperties"][
            "storedProcedureParameters"
        ]
        self.assertEqual(
            "@pipeline().PipelineName",
            begin_parameters["trigger_reference"]["value"]["value"],
        )
        fail_parameters = self.activities["Fail_Attempt"]["typeProperties"][
            "storedProcedureParameters"
        ]
        self.assertEqual(
            "Expression", fail_parameters["actor_identity"]["value"]["type"]
        )

    def test_pipeline_pins_boundaries_and_parses_notebook_counts(self) -> None:
        notebook = self.activities["Run_IncrementalNotebook"]
        self.assertEqual(3, notebook["policy"]["retry"])
        self.assertEqual(120, notebook["policy"]["retryIntervalInSeconds"])
        notebook_parameters = notebook["typeProperties"]["parameters"]
        self.assertEqual(
            "@activity('Resolve_Context').output.firstRow.committed_value",
            notebook_parameters["lower_bound"]["value"]["value"],
        )
        self.assertEqual(
            "@pipeline().parameters.upper_bound",
            notebook_parameters["upper_bound"]["value"]["value"],
        )
        complete_parameters = self.activities["Complete_Attempt"]["typeProperties"][
            "storedProcedureParameters"
        ]
        for count_name in (
            "extracted_row_count",
            "accepted_row_count",
            "rejected_row_count",
        ):
            self.assertIn(
                ".output.result.exitValue",
                complete_parameters[count_name]["value"]["value"],
            )


if __name__ == "__main__":
    unittest.main()
