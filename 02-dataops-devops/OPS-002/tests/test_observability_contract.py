from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from observability import (
    Attempt,
    collapse_attempts,
    evaluate_duration,
    evaluate_freshness,
    evaluate_quality_acceptance,
    evaluate_quality_enforcement,
    evaluate_reliability,
    route_alert,
)


UTC = timezone.utc
START = datetime(2026, 9, 2, 1, 0, tzinfo=UTC)


def attempt(
    key: str,
    *,
    number: int = 1,
    minutes: int = 5,
    status: str = "SUCCEEDED",
    quality: str | None = "ACCEPTED",
    safe: bool = True,
    excluded: bool = False,
) -> Attempt:
    return Attempt(
        occurrence_key=key,
        attempt_number=number,
        started_at_utc=START,
        completed_at_utc=START + timedelta(minutes=minutes),
        object_run_status=status,
        quality_decision_status=quality,
        quality_decided_at_utc=(START + timedelta(minutes=minutes)),
        quality_enforcement_safe=safe,
        excluded=excluded,
    )


class EvaluationTests(unittest.TestCase):
    def test_attempts_collapse_to_one_logical_occurrence(self):
        rows = collapse_attempts(
            [
                attempt("a", number=1, status="FAILED", quality=None),
                attempt("a", number=2, minutes=8, status="SUCCEEDED"),
            ]
        )
        self.assertEqual(1, len(rows))
        self.assertEqual("SUCCEEDED", rows[0].final_status)
        self.assertEqual(Decimal("8"), rows[0].duration_minutes)

    def test_warning_is_reliable_and_quality_accepted(self):
        rows = collapse_attempts(
            [attempt("a", status="SUCCEEDED_WITH_WARNINGS", quality="ACCEPTED_WITH_WARNING")]
        )
        self.assertEqual("PASS", evaluate_reliability(rows).evaluation_status)
        self.assertEqual("PASS", evaluate_quality_acceptance(rows).evaluation_status)

    def test_safe_quality_block_is_not_platform_failure(self):
        rows = collapse_attempts(
            [attempt("a", status="RECOVERY_REQUIRED", quality="BLOCKED", safe=True)]
        )
        self.assertEqual("PASS", evaluate_reliability(rows).evaluation_status)
        self.assertEqual("BREACH", evaluate_quality_acceptance(rows).evaluation_status)
        self.assertEqual("PASS", evaluate_quality_enforcement(rows).evaluation_status)

    def test_unsafe_quality_block_is_zero_tolerance_breach(self):
        rows = collapse_attempts(
            [attempt("a", status="SUCCEEDED", quality="BLOCKED", safe=False)]
        )
        result = evaluate_quality_enforcement(rows)
        self.assertEqual("BREACH", result.evaluation_status)
        self.assertIsNone(result.error_budget_consumption)

    def test_duration_counts_end_to_end_retry_time(self):
        rows = collapse_attempts(
            [
                attempt("a", number=1, minutes=10, status="FAILED", quality=None),
                Attempt(
                    occurrence_key="a",
                    attempt_number=2,
                    started_at_utc=START + timedelta(minutes=10),
                    completed_at_utc=START + timedelta(minutes=35),
                    object_run_status="SUCCEEDED",
                    quality_decision_status="ACCEPTED",
                    quality_decided_at_utc=START + timedelta(minutes=35),
                ),
            ]
        )
        result = evaluate_duration(rows, Decimal("30"))
        self.assertEqual("BREACH", result.evaluation_status)

    def test_freshness_uses_accepted_publication_time(self):
        rows = collapse_attempts([attempt("a", minutes=14)])
        result = evaluate_freshness(
            "critical-freshness", rows, {"a": START + timedelta(minutes=15)}
        )
        self.assertEqual("PASS", result.evaluation_status)

    def test_preapproved_exclusion_is_visible(self):
        rows = collapse_attempts(
            [attempt("a"), attempt("b", status="FAILED", quality=None, excluded=True)]
        )
        result = evaluate_reliability(rows)
        self.assertEqual(1, result.denominator_count)
        self.assertEqual(1, result.excluded_count)

    def test_empty_window_is_no_data(self):
        result = evaluate_reliability([])
        self.assertEqual("NO_DATA", result.evaluation_status)
        self.assertIsNone(result.observed_value)

    def test_error_budget_consumption_is_calculated(self):
        rows = collapse_attempts(
            [attempt(str(index)) for index in range(99)]
            + [attempt("failed", status="FAILED", quality=None)]
        )
        result = evaluate_quality_acceptance(rows)
        self.assertEqual(Decimal("1.000000"), result.error_budget_consumption)


class RoutingTests(unittest.TestCase):
    def test_development_routes_are_simulated(self):
        result = route_alert(
            environment_code="development",
            ingestion_object_key="ingest-clinical-encounter",
            detection_category="QUALITY",
            severity="P2",
            deduplication_scope="window-1",
            routing_alias="route-data-operations",
        )
        self.assertEqual("SIMULATED", result.delivery_mode)

    def test_production_requests_notification(self):
        result = route_alert(
            environment_code="production",
            ingestion_object_key="ingest-clinical-encounter",
            detection_category="QUALITY",
            severity="P2",
            deduplication_scope="window-1",
            routing_alias="route-data-operations",
        )
        self.assertEqual("NOTIFICATION_REQUESTED", result.delivery_mode)

    def test_missing_route_is_durable_decision(self):
        result = route_alert(
            environment_code="test",
            ingestion_object_key=None,
            detection_category="TELEMETRY",
            severity="P1",
            deduplication_scope="window-1",
            routing_alias=None,
        )
        self.assertEqual("NO_ROUTE", result.decision_status)

    def test_p1_cannot_be_suppressed(self):
        with self.assertRaisesRegex(ValueError, "cannot be suppressed"):
            route_alert(
                environment_code="production",
                ingestion_object_key="ingest-clinical-encounter",
                detection_category="QUALITY_ENFORCEMENT",
                severity="P1",
                deduplication_scope="window-1",
                routing_alias="route-data-operations",
                suppressed=True,
            )

    def test_deduplication_is_stable(self):
        arguments = dict(
            environment_code="development",
            ingestion_object_key="ingest-clinical-encounter",
            detection_category="DURATION",
            severity="P3",
            deduplication_scope="window-1",
            routing_alias="route-data-operations",
        )
        self.assertEqual(
            route_alert(**arguments).deduplication_key,
            route_alert(**arguments).deduplication_key,
        )


if __name__ == "__main__":
    unittest.main()
