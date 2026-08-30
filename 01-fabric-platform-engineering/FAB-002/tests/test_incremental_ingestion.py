from __future__ import annotations

import unittest

from incremental_ingestion import (
    InMemoryControlPlane,
    InMemoryTarget,
    IncrementalIngestionRuntime,
    IngestionConfig,
    StaleWatermarkCandidate,
)


class IncrementalIngestionContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = IngestionConfig(
            environment_id="development",
            release_id="1.0.0",
            ingestion_object_key="ingest-clinical-encounter",
            business_key="encounter_id",
            watermark_column="modified_sequence",
            expected_columns=frozenset(
                {"encounter_id", "modified_sequence", "encounter_status"}
            ),
        )
        self.control = InMemoryControlPlane(initial_watermark=100)
        self.target = InMemoryTarget(self.config.business_key)
        self.runtime = IncrementalIngestionRuntime(
            self.config, self.control, self.target
        )

    @staticmethod
    def rows() -> list[dict[str, object]]:
        return [
            {
                "encounter_id": "enc-001",
                "modified_sequence": 100,
                "encounter_status": "complete",
            },
            {
                "encounter_id": "enc-002",
                "modified_sequence": 101,
                "encounter_status": "arrived",
            },
            {
                "encounter_id": "enc-003",
                "modified_sequence": 105,
                "encounter_status": "complete",
            },
            {
                "encounter_id": "enc-004",
                "modified_sequence": 106,
                "encounter_status": "future-window",
            },
        ]

    def test_success_uses_lower_exclusive_upper_inclusive_window(self) -> None:
        result = self.runtime.execute(self.rows(), upper_bound=105)

        self.assertEqual("SUCCEEDED", result.evidence.status)
        self.assertEqual(2, result.evidence.extracted_row_count)
        self.assertEqual(2, result.evidence.accepted_row_count)
        self.assertEqual(2, result.evidence.inserted_row_count)
        self.assertEqual(105, result.committed_watermark)
        self.assertEqual(1, result.state_version)
        self.assertEqual({"enc-002", "enc-003"}, set(self.target.rows))

    def test_unchanged_empty_window_is_a_state_no_op(self) -> None:
        result = self.runtime.execute(self.rows(), upper_bound=100)

        self.assertEqual("SUCCEEDED", result.evidence.status)
        self.assertEqual(0, result.evidence.extracted_row_count)
        self.assertEqual(100, result.committed_watermark)
        self.assertEqual(0, result.state_version)
        self.assertEqual({}, self.control.candidates)
        self.assertEqual({}, self.target.rows)

    def test_in_window_duplicates_keep_greatest_watermark(self) -> None:
        rows = [
            {
                "encounter_id": "enc-002",
                "modified_sequence": 101,
                "encounter_status": "arrived",
            },
            {
                "encounter_id": "enc-002",
                "modified_sequence": 104,
                "encounter_status": "complete",
            },
        ]

        result = self.runtime.execute(rows, upper_bound=105)

        self.assertEqual("SUCCEEDED", result.evidence.status)
        self.assertEqual(2, result.evidence.extracted_row_count)
        self.assertEqual(1, result.evidence.accepted_row_count)
        self.assertEqual(1, result.evidence.duplicate_row_count)
        self.assertEqual(104, self.target.rows["enc-002"]["modified_sequence"])

    def test_failure_after_target_write_preserves_watermark(self) -> None:
        result = self.runtime.execute(
            self.rows(), upper_bound=105, failure_stage="AFTER_TARGET_WRITE"
        )

        self.assertEqual("FAILED", result.evidence.status)
        self.assertEqual("INJECTED_FAILURE", result.evidence.error_classification)
        self.assertEqual(100, result.committed_watermark)
        self.assertEqual(0, result.state_version)
        self.assertEqual(2, len(self.target.rows))
        candidate = next(iter(self.control.candidates.values()))
        self.assertEqual("ABANDONED", candidate.status)

    def test_replay_after_post_write_failure_is_idempotent(self) -> None:
        failed = self.runtime.execute(
            self.rows(), upper_bound=105, failure_stage="AFTER_TARGET_WRITE"
        )
        recovered = self.runtime.execute(
            self.rows(), upper_bound=105, attempt_number=2
        )

        self.assertEqual("FAILED", failed.evidence.status)
        self.assertEqual("SUCCEEDED", recovered.evidence.status)
        self.assertEqual(0, recovered.evidence.inserted_row_count)
        self.assertEqual(0, recovered.evidence.updated_row_count)
        self.assertEqual(2, len(self.target.rows))
        self.assertEqual(105, recovered.committed_watermark)
        self.assertEqual(1, recovered.state_version)

    def test_already_committed_rows_are_not_reprocessed(self) -> None:
        first = self.runtime.execute(self.rows(), upper_bound=105)
        second = self.runtime.execute(self.rows(), upper_bound=105, attempt_number=2)

        self.assertEqual("SUCCEEDED", first.evidence.status)
        self.assertEqual("SUCCEEDED", second.evidence.status)
        self.assertEqual(0, second.evidence.extracted_row_count)
        self.assertEqual(2, len(self.target.rows))

    def test_stale_candidate_is_rejected_without_overwrite(self) -> None:
        first = self.control.propose("object-run-1", upper_bound=105)
        stale = self.control.propose("object-run-2", upper_bound=110)
        self.control.commit(first)

        with self.assertRaises(StaleWatermarkCandidate):
            self.control.commit(stale)

        self.assertEqual(105, self.control.state.value)
        self.assertEqual(1, self.control.state.version)
        self.assertEqual("ABANDONED", stale.status)
        self.assertEqual("STALE_STATE_VERSION", stale.reason)

    def test_evidence_preserves_identity_counts_status_and_boundary_hash(self) -> None:
        result = self.runtime.execute(
            self.rows(), upper_bound=105, correlation_id="fab002-contract-001"
        )
        evidence = result.evidence

        self.assertEqual("fab002-contract-001", evidence.correlation_id)
        self.assertEqual("development", evidence.environment_id)
        self.assertEqual("1.0.0", evidence.release_id)
        self.assertEqual("ingest-clinical-encounter", evidence.ingestion_object_key)
        self.assertEqual(64, len(evidence.input_boundary_hash))
        self.assertEqual("SUCCEEDED", evidence.status)
        self.assertGreaterEqual(evidence.duration_ms, 0)
        self.assertEqual(2, evidence.extracted_row_count)
        self.assertEqual(2, evidence.accepted_row_count)

    def test_conflicting_same_watermark_duplicate_fails_deterministically(self) -> None:
        rows = [
            {
                "encounter_id": "enc-002",
                "modified_sequence": 101,
                "encounter_status": "arrived",
            },
            {
                "encounter_id": "enc-002",
                "modified_sequence": 101,
                "encounter_status": "complete",
            },
        ]

        result = self.runtime.execute(rows, upper_bound=105)

        self.assertEqual("FAILED", result.evidence.status)
        self.assertEqual("DUPLICATE_CONFLICT", result.evidence.error_classification)
        self.assertEqual(100, result.committed_watermark)
        self.assertEqual(0, result.state_version)
        self.assertEqual({}, self.target.rows)

    def test_missing_required_column_fails_without_payload_in_error(self) -> None:
        rows = [
            {
                "encounter_id": "enc-sensitive-value",
                "modified_sequence": 101,
            }
        ]

        result = self.runtime.execute(rows, upper_bound=105)

        self.assertEqual("FAILED", result.evidence.status)
        self.assertEqual(
            "SOURCE_CONTRACT_VIOLATION",
            result.evidence.error_classification,
        )
        self.assertEqual(100, result.committed_watermark)
        self.assertNotIn("enc-sensitive-value", result.evidence.error_classification)


if __name__ == "__main__":
    unittest.main()
