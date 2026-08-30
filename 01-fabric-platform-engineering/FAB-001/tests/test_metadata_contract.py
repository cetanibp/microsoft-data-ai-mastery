from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from metadata_contract import (
    ConcurrencyConflict,
    WatermarkTracker,
    resolve_environment,
    validate_release,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "northstar_release.json"


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def issue_codes(metadata: dict) -> set[str]:
    return {issue.code for issue in validate_release(metadata)}


class MetadataContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = load_fixture()

    def test_representative_release_is_valid(self) -> None:
        self.assertEqual([], validate_release(self.metadata))

    def test_draft_release_cannot_resolve(self) -> None:
        self.metadata["release"]["status"] = "DRAFT"
        self.assertIn("RELEASE_NOT_APPROVABLE", issue_codes(self.metadata))

    def test_environment_resolution_changes_configuration_not_code(self) -> None:
        development = resolve_environment(self.metadata, "development")
        production = resolve_environment(self.metadata, "production")

        self.assertEqual(5, len(development))
        self.assertEqual(4, len(production))
        self.assertEqual(
            "connection-ehr-reader-development",
            next(
                row["connection_reference"]
                for row in development
                if row["object_key"] == "ingest-clinical-encounter"
            ),
        )
        self.assertEqual(
            "connection-ehr-reader-production",
            next(
                row["connection_reference"]
                for row in production
                if row["object_key"] == "ingest-clinical-encounter"
            ),
        )
        self.assertNotIn(
            "ingest-facility-status-event",
            {row["object_key"] for row in production},
        )

    def test_unknown_environment_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            resolve_environment(self.metadata, "disaster-recovery")

    def test_duplicate_stable_key_is_rejected(self) -> None:
        self.metadata["ingestion_objects"].append(
            copy.deepcopy(self.metadata["ingestion_objects"][0])
        )
        self.assertIn("DUPLICATE_STABLE_KEY", issue_codes(self.metadata))

    def test_missing_source_reference_is_rejected(self) -> None:
        self.metadata["source_objects"][0]["source"] = "missing-source"
        self.assertIn("SOURCE_REFERENCE_MISSING", issue_codes(self.metadata))

    def test_missing_target_reference_is_rejected(self) -> None:
        self.metadata["ingestion_objects"][0]["target_object"] = "missing-target"
        self.assertIn("TARGET_OBJECT_REFERENCE_MISSING", issue_codes(self.metadata))

    def test_missing_source_environment_configuration_is_rejected(self) -> None:
        del self.metadata["sources"][0]["environment_config"]["test"]
        self.assertIn(
            "SOURCE_ENVIRONMENT_CONFIG_MISSING", issue_codes(self.metadata)
        )

    def test_enabled_object_cannot_use_disabled_source(self) -> None:
        self.metadata["sources"][0]["environment_config"]["production"][
            "enabled"
        ] = False
        self.assertIn("ENABLED_OBJECT_SOURCE_DISABLED", issue_codes(self.metadata))

    def test_secret_like_connection_literal_is_rejected(self) -> None:
        self.metadata["sources"][0]["environment_config"]["development"][
            "connection_reference"
        ] = "https://example.invalid?token=unsafe"
        self.assertIn("UNSAFE_CONFIGURATION_LITERAL", issue_codes(self.metadata))

    def test_secret_like_routing_literal_is_rejected(self) -> None:
        self.metadata["ingestion_objects"][0]["environment_config"][
            "development"
        ]["routing_alias"] = "token=unsafe"
        self.assertIn("UNSAFE_CONFIGURATION_LITERAL", issue_codes(self.metadata))

    def test_watermark_strategy_requires_watermark_policy(self) -> None:
        self.metadata["load_policies"][1]["watermark_policy"] = None
        self.assertIn("WATERMARK_POLICY_MISSING", issue_codes(self.metadata))

    def test_non_watermark_strategy_rejects_watermark_policy(self) -> None:
        self.metadata["load_policies"][0][
            "watermark_policy"
        ] = "wm-updated-at-5m-overlap"
        self.assertIn("WATERMARK_POLICY_NOT_ALLOWED", issue_codes(self.metadata))

    def test_unallowlisted_parameter_is_rejected(self) -> None:
        self.metadata["load_policies"][0]["parameters"]["source_sql"] = (
            "select * from source"
        )
        self.assertIn("PARAMETER_NOT_ALLOWLISTED", issue_codes(self.metadata))

    def test_parameter_type_mismatch_is_rejected(self) -> None:
        self.metadata["load_policies"][0]["parameters"]["batch_size"] = "100000"
        self.assertIn("PARAMETER_TYPE_MISMATCH", issue_codes(self.metadata))

    def test_parameter_out_of_range_is_rejected(self) -> None:
        self.metadata["load_policies"][0]["parameters"]["batch_size"] = 0
        self.assertIn("PARAMETER_OUT_OF_RANGE", issue_codes(self.metadata))

    def test_production_object_requires_slo(self) -> None:
        self.metadata["ingestion_objects"][0]["slos"] = []
        self.assertIn("PRODUCTION_SLO_MISSING", issue_codes(self.metadata))

    def test_production_object_requires_operational_owner(self) -> None:
        obj = self.metadata["ingestion_objects"][0]
        obj["ownership"] = [
            ownership
            for ownership in obj["ownership"]
            if ownership["role"] != "OPERATIONS"
        ]
        self.assertIn("PRODUCTION_OWNERSHIP_MISSING", issue_codes(self.metadata))

    def test_dependency_self_reference_is_rejected(self) -> None:
        self.metadata["dependencies"].append(
            {
                "predecessor": "ingest-pharmacy-order",
                "successor": "ingest-pharmacy-order",
                "condition": "SUCCESS",
            }
        )
        self.assertIn("DEPENDENCY_SELF_REFERENCE", issue_codes(self.metadata))

    def test_dependency_cycle_is_rejected(self) -> None:
        self.metadata["dependencies"].append(
            {
                "predecessor": "ingest-pharmacy-order",
                "successor": "ingest-facility-reference",
                "condition": "SUCCESS",
            }
        )
        issues = validate_release(self.metadata)
        cycles = [issue for issue in issues if issue.code == "DEPENDENCY_CYCLE"]
        self.assertEqual(1, len(cycles))
        self.assertIn("ingest-facility-reference", cycles[0].message)


class WatermarkContractTests(unittest.TestCase):
    def test_abandoned_candidate_does_not_advance_state(self) -> None:
        tracker = WatermarkTracker("2026-08-01T00:00:00Z", state_version=7)
        candidate = tracker.propose("run-failed", "2026-08-01T01:00:00Z")

        tracker.abandon(candidate, "controlled extraction failure")

        self.assertEqual("ABANDONED", candidate.status)
        self.assertEqual("2026-08-01T00:00:00Z", tracker.committed_value)
        self.assertEqual(7, tracker.state_version)
        self.assertIsNone(tracker.committed_run_id)

    def test_successful_candidate_advances_state_once(self) -> None:
        tracker = WatermarkTracker("100", state_version=2)
        candidate = tracker.propose("run-success", "200")

        tracker.commit(candidate)

        self.assertEqual("COMMITTED", candidate.status)
        self.assertEqual("200", tracker.committed_value)
        self.assertEqual(3, tracker.state_version)
        self.assertEqual("run-success", tracker.committed_run_id)
        with self.assertRaises(ValueError):
            tracker.commit(candidate)

    def test_stale_candidate_cannot_overwrite_newer_commit(self) -> None:
        tracker = WatermarkTracker("100", state_version=4)
        first = tracker.propose("run-first", "200")
        stale = tracker.propose("run-stale", "300")

        tracker.commit(first)

        with self.assertRaises(ConcurrencyConflict):
            tracker.commit(stale)
        self.assertEqual("200", tracker.committed_value)
        self.assertEqual(5, tracker.state_version)


if __name__ == "__main__":
    unittest.main()
