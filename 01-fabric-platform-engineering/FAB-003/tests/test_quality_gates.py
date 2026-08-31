from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))

from quality_gates import (  # noqa: E402
    EvaluationContext,
    InMemoryQualityEvidence,
    InMemoryWatermarkState,
    InvalidRecord,
    QualityContractError,
    QualityGateRuntime,
    QualityPolicy,
)


def context(**overrides):
    values = {
        "environment_id": "development",
        "release_id": "release-1",
        "run_id": "run-1",
        "object_run_id": "object-run-1",
        "ingestion_object_key": "ingest-clinical-encounter",
        "attempt_number": 1,
        "input_boundary_hash": "boundary-hash",
        "extracted_count": 2,
        "accepted_count": 2,
        "rejected_count": 0,
        "duplicate_count": 0,
    }
    values.update(overrides)
    return EvaluationContext(**values)


def policy(
    key="row-count-balance",
    check="ROW_COUNT_BALANCE",
    enforcement="BLOCK",
    operator="EQ",
    threshold=0,
    ordinal=1,
    field_name=None,
    measurement_mode="ABSOLUTE",
    required=True,
    quarantine_expected=False,
):
    return QualityPolicy(
        policy_key=key,
        policy_version="1.0.0",
        check_type=check,
        enforcement_mode=enforcement,
        operator=operator,
        threshold=threshold,
        ordinal=ordinal,
        field_name=field_name,
        measurement_mode=measurement_mode,
        required=required,
        quarantine_expected=quarantine_expected,
    )


ROWS = (
    {"encounter_id": "e-1", "amount": 10, "status": "closed"},
    {"encounter_id": "e-2", "amount": 20, "status": "open"},
)


class PolicyContractTests(unittest.TestCase):
    def test_rejects_unallowlisted_check_type(self):
        with self.assertRaises(QualityContractError):
            policy(check="EXECUTE_SQL")

    def test_rejects_invalid_operator_and_field(self):
        with self.assertRaises(QualityContractError):
            policy(operator="LIKE")
        with self.assertRaises(QualityContractError):
            policy(check="SUM_VALUE", field_name="amount; DROP TABLE x")

    def test_rejects_nonfinite_threshold(self):
        with self.assertRaises(QualityContractError):
            policy(threshold="NaN")

    def test_runtime_rejects_field_outside_allowlist(self):
        runtime = QualityGateRuntime({"encounter_id"})
        with self.assertRaises(QualityContractError):
            runtime.evaluate(
                context(),
                [policy(check="SUM_VALUE", field_name="amount")],
                target_rows=ROWS,
            )


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.evidence = InMemoryQualityEvidence()
        self.runtime = QualityGateRuntime(
            {"encounter_id", "amount", "status"}, self.evidence
        )

    def test_balanced_counts_and_target_count_are_accepted(self):
        decision = self.runtime.evaluate(
            context(),
            [
                policy(),
                policy(
                    key="target-count",
                    check="TARGET_COUNT",
                    operator="EQ",
                    threshold=0,
                    ordinal=2,
                ),
            ],
            target_rows=ROWS,
        )
        self.assertEqual("ACCEPTED", decision.status)
        self.assertTrue(decision.watermark_commit_eligible)
        self.assertEqual(["PASS", "PASS"], [r.status for r in decision.results])

    def test_warning_variance_remains_commit_eligible(self):
        decision = self.runtime.evaluate(
            context(accepted_count=3),
            [
                policy(
                    key="target-count-warning",
                    check="TARGET_COUNT",
                    enforcement="WARN",
                    operator="LE",
                    threshold=0,
                )
            ],
            target_rows=ROWS,
        )
        self.assertEqual("ACCEPTED_WITH_WARNING", decision.status)
        self.assertTrue(decision.watermark_commit_eligible)
        self.assertEqual("WARN", decision.results[0].status)

    def test_percentage_count_variance_uses_expected_count(self):
        decision = self.runtime.evaluate(
            context(accepted_count=4),
            [
                policy(
                    key="target-count-percentage",
                    check="TARGET_COUNT",
                    operator="LE",
                    threshold=50,
                    measurement_mode="PERCENTAGE",
                )
            ],
            target_rows=ROWS,
        )
        self.assertEqual(Decimal("50"), decision.results[0].observed_value)
        self.assertEqual("ACCEPTED", decision.status)

    def test_blocking_count_variance_prevents_commit(self):
        decision = self.runtime.evaluate(
            context(extracted_count=3), [policy()], target_rows=ROWS
        )
        state = InMemoryWatermarkState(value=100, version=4)
        committed = state.commit_if_eligible(decision, 200, context().object_run_id)
        self.assertEqual("BLOCKED", decision.status)
        self.assertFalse(committed)
        self.assertEqual((100, 4, None), (state.value, state.version, state.committed_object_run_id))

    def test_warning_can_commit_watermark(self):
        decision = self.runtime.evaluate(
            context(accepted_count=3),
            [
                policy(
                    key="target-count-warning",
                    check="TARGET_COUNT",
                    enforcement="WARN",
                    operator="EQ",
                    threshold=0,
                )
            ],
            target_rows=ROWS,
        )
        state = InMemoryWatermarkState(value=100)
        self.assertTrue(state.commit_if_eligible(decision, 200, context().object_run_id))
        self.assertEqual((200, 1, "object-run-1"), (state.value, state.version, state.committed_object_run_id))

    def test_required_observation_error_blocks(self):
        decision = self.runtime.evaluate(
            context(),
            [policy(check="SUM_VALUE", field_name="amount")],
            target_rows=({"encounter_id": "e-1"},),
        )
        self.assertEqual("BLOCKED", decision.status)
        self.assertEqual("ERROR", decision.results[0].status)
        self.assertEqual(
            "REQUIRED_OBSERVATION_UNAVAILABLE",
            decision.results[0].error_classification,
        )

    def test_optional_warning_observation_error_warns(self):
        decision = self.runtime.evaluate(
            context(),
            [
                policy(
                    key="optional-amount",
                    check="SUM_VALUE",
                    enforcement="WARN",
                    field_name="amount",
                    required=False,
                )
            ],
            target_rows=({"encounter_id": "e-1"},),
        )
        self.assertEqual("ACCEPTED_WITH_WARNING", decision.status)
        self.assertEqual("WARN", decision.results[0].status)

    def test_aggregate_checks_use_decimal_boundaries(self):
        decision = self.runtime.evaluate(
            context(),
            [
                policy(
                    key="amount-sum",
                    check="SUM_VALUE",
                    operator="EQ",
                    threshold="30.0",
                    field_name="amount",
                )
            ],
            target_rows=ROWS,
        )
        self.assertEqual(Decimal("30"), decision.results[0].observed_value)
        self.assertEqual("ACCEPTED", decision.status)

    def test_null_rate_threshold_boundary_passes(self):
        rows = ({"encounter_id": "e-1", "status": None}, {"encounter_id": "e-2", "status": "open"})
        decision = self.runtime.evaluate(
            context(),
            [
                policy(
                    key="status-null-rate",
                    check="NULL_RATE",
                    operator="LE",
                    threshold=50,
                    field_name="status",
                )
            ],
            target_rows=rows,
        )
        self.assertEqual(Decimal("50"), decision.results[0].observed_value)
        self.assertEqual("PASS", decision.results[0].status)

    def test_duplicate_key_check_blocks(self):
        rows = (
            {"encounter_id": "e-1", "amount": 10},
            {"encounter_id": "e-1", "amount": 11},
        )
        decision = self.runtime.evaluate(
            context(),
            [
                policy(
                    key="encounter-key-unique",
                    check="DISTINCT_KEY",
                    operator="EQ",
                    threshold=0,
                    field_name="encounter_id",
                )
            ],
            target_rows=rows,
        )
        self.assertEqual("BLOCKED", decision.status)

    def test_quarantine_identity_is_deterministic_and_idempotent(self):
        quarantine_policy = policy(
            key="encounter-key-unique",
            check="DISTINCT_KEY",
            operator="GE",
            threshold=0,
            field_name="encounter_id",
            quarantine_expected=True,
        )
        invalid = InvalidRecord(
            record_identity="encounter:e-1:source-row-2",
            reason_code="DUPLICATE_BUSINESS_KEY",
            policy_key=quarantine_policy.policy_key,
        )
        first = self.runtime.evaluate(
            context(), [quarantine_policy], target_rows=ROWS, invalid_records=[invalid]
        )
        second = self.runtime.evaluate(
            context(), [quarantine_policy], target_rows=ROWS, invalid_records=[invalid]
        )
        self.assertEqual(
            first.quarantine_records[0].quarantine_id,
            second.quarantine_records[0].quarantine_id,
        )
        self.assertEqual(1, len(self.evidence.quarantine))
        self.assertNotIn("e-1", first.quarantine_records[0].source_record_identity_hash)

    def test_replay_does_not_duplicate_check_results(self):
        policies = [policy()]
        first = self.runtime.evaluate(context(), policies, target_rows=ROWS)
        second = self.runtime.evaluate(context(), policies, target_rows=ROWS)
        self.assertEqual(first.results[0].result_id, second.results[0].result_id)
        self.assertEqual(1, len(self.evidence.results))

    def test_result_identity_changes_for_new_object_run(self):
        first = self.runtime.evaluate(context(), [policy()], target_rows=ROWS)
        second = self.runtime.evaluate(
            context(object_run_id="object-run-2"), [policy()], target_rows=ROWS
        )
        self.assertNotEqual(first.results[0].result_id, second.results[0].result_id)
        self.assertEqual(2, len(self.evidence.results))


if __name__ == "__main__":
    unittest.main()
