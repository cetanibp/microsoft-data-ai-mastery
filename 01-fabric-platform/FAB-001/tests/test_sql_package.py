from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


FAB_ROOT = Path(__file__).resolve().parents[1]
SQL_ROOT = FAB_ROOT / "sql"
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "northstar_release.json"


def sql_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(SQL_ROOT.glob("*.sql"))
    )


class SqlPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = sql_text()
        cls.seed = (SQL_ROOT / "100_seed_northstar.sql").read_text(encoding="utf-8")
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_expected_execution_files_exist(self) -> None:
        self.assertEqual(
            [
                "001_create_schemas.sql",
                "010_create_definition_tables.sql",
                "020_create_runtime_tables.sql",
                "030_create_views.sql",
                "100_seed_northstar.sql",
            ],
            [path.name for path in sorted(SQL_ROOT.glob("*.sql"))],
        )

    def test_all_foreign_key_targets_are_created(self) -> None:
        tables = set(
            re.findall(r"CREATE TABLE\s+([A-Za-z0-9_.]+)", self.text, re.I)
        )
        references = set(
            re.findall(r"REFERENCES\s+([A-Za-z0-9_.]+)", self.text, re.I)
        )
        self.assertEqual(set(), references - tables)
        self.assertEqual(28, len(tables))

    def test_named_constraints_are_unique(self) -> None:
        names = re.findall(r"CONSTRAINT\s+([A-Za-z0-9_]+)", self.text, re.I)
        duplicates = {name for name in names if names.count(name) > 1}
        self.assertEqual(set(), duplicates)
        self.assertGreaterEqual(len(names), 170)

    def test_runtime_contract_contains_concurrency_token(self) -> None:
        self.assertRegex(self.text, r"row_version\s+rowversion\s+NOT NULL")
        self.assertIn("observed_state_version", self.text)
        self.assertIn("WATERMARK_ABANDONED", self.text)
        self.assertIn("WATERMARK_COMMITTED", self.text)

    def test_resolution_and_validation_views_exist(self) -> None:
        self.assertIn(
            "CREATE OR ALTER VIEW ctrl.vw_ActiveIngestionConfiguration", self.text
        )
        self.assertIn(
            "CREATE OR ALTER VIEW ctrl.vw_MetadataValidationIssue", self.text
        )

    def test_seed_uses_transaction_and_immutable_bundle_guard(self) -> None:
        self.assertIn("BEGIN TRANSACTION", self.seed)
        self.assertIn("COMMIT TRANSACTION", self.seed)
        self.assertIn("WHERE release_version = '1.0.0'", self.seed)
        self.assertNotRegex(self.seed, r"(?im)^\s*(UPDATE|DELETE|MERGE)\s+ctrl\.")

    def test_fixture_object_keys_match_seed(self) -> None:
        keys = {
            obj["key"] for obj in self.fixture["ingestion_objects"]
        }
        for key in keys:
            self.assertIn(f"'{key}'", self.seed)

    def test_fixture_and_seed_cover_all_load_strategies(self) -> None:
        strategies = {
            policy["strategy"] for policy in self.fixture["load_policies"]
        }
        self.assertEqual({"FULL", "WATERMARK", "APPEND", "SNAPSHOT"}, strategies)
        for strategy in strategies:
            self.assertIn(f"'{strategy}'", self.seed)

    def test_seed_contains_only_logical_connection_values(self) -> None:
        forbidden = (
            "https://",
            "http://",
            "password=",
            "secret=",
            "token=",
            "accountkey=",
            "sharedaccesssignature=",
        )
        lowered = self.seed.casefold()
        for marker in forbidden:
            self.assertNotIn(marker, lowered)

    def test_seed_has_expected_environment_resolution_shape(self) -> None:
        production_event_config = next(
            obj
            for obj in self.fixture["ingestion_objects"]
            if obj["key"] == "ingest-facility-status-event"
        )["environment_config"]["production"]
        self.assertFalse(production_event_config["enabled"])
        self.assertEqual(5, len(self.fixture["ingestion_objects"]))
        self.assertEqual(3, len(self.fixture["environments"]))


if __name__ == "__main__":
    unittest.main()
