"""Behavior tests for a synthetic tool boundary, not live identity enforcement."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from threading import Event

from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from read_only_tools import (  # noqa: E402
    FixtureBackend, FixturePolicy, RateLimited, ReadGrant, ReadOnlyTools,
    RESPONSE, TrustedContext,
)


class ReadOnlyContractTests(unittest.TestCase):
    def setUp(self):
        self.rows = json.loads((ROOT / "fixtures/object-runs.json").read_text(encoding="utf-8"))
        self.context = TrustedContext(
            "10000000-0000-4000-8000-000000000001",
            "10000000-0000-4000-8000-000000000002",
            "10000000-0000-4000-8000-000000000003",
        )
        self.grant = ReadGrant("synthetic-policy-v1", frozenset({"development"}),
                               frozenset({"ingest-clinical-encounter"}))
        self.policy = FixturePolicy({self.context.requesting_user_id: self.grant},
                                    {self.context.workload_id: self.grant})
        self.backend = FixtureBackend(self.rows)
        self.audit = []
        self.now = 10.0
        self.tools = ReadOnlyTools(self.backend, self.policy, audit=self.audit,
                                  clock=lambda: self.now)
        self.args = {"environment": "development", "object_run_id": self.rows[0]["object_run_id"]}

    def call(self, arguments=None, **kwargs):
        response = self.tools.inspect_object_run(
            self.args if arguments is None else arguments,
            self.context, deadline=kwargs.pop("deadline", 15.0), **kwargs,
        )
        RESPONSE.validate(response)
        return response

    def assert_error(self, response, code, calls):
        self.assertEqual("error", response["status"])
        self.assertEqual(code, response["error"]["code"])
        self.assertNotIn("data", response)
        self.assertEqual(calls, self.backend.calls)
        self.assertEqual(code, self.audit[-1]["error_code"])

    def test_blocked_run_preserves_state_and_returns_release_evidence(self):
        response = self.call()
        self.assertEqual("PASS", response["data"]["quality_enforcement"])
        self.assertEqual(self.rows[0]["release_id"], response["data"]["record"]["release_id"])
        self.assertEqual([1, 2, 3], [row["rank"] for row in response["data"]["evidence"]])
        self.assertEqual("QUALITY_ENFORCEMENT", response["data"]["evidence"][0]["kind"])
        self.assertEqual(1, self.backend.calls)

    def test_each_unsafe_block_condition_is_a_breach(self):
        for field, value in (
            ("object_run_status", "SUCCEEDED"),
            ("object_run_status", "SUCCEEDED_WITH_WARNINGS"),
            ("watermark_candidate_status", "COMMITTED"),
            ("committed_object_run_id", self.rows[0]["object_run_id"]),
        ):
            with self.subTest(field=field, value=value):
                row = {**self.rows[0], field: value}
                self.tools.backend = FixtureBackend([row])
                self.assertEqual("BREACH", self.call()["data"]["quality_enforcement"])

    def test_warning_remains_accepted(self):
        row = {**self.rows[0], "quality_decision_status": "ACCEPTED_WITH_WARNING",
               "object_run_status": "SUCCEEDED_WITH_WARNINGS", "watermark_candidate_status": "COMMITTED"}
        self.tools.backend = FixtureBackend([row])
        self.assertEqual("NOT_APPLICABLE", self.call()["data"]["quality_enforcement"])

    def test_missing_quality_candidate_or_state_stays_unknown(self):
        for field in ("quality_decision_status", "watermark_candidate_status", "state_version"):
            with self.subTest(field=field):
                self.tools.backend = FixtureBackend([{**self.rows[0], field: None}])
                self.assertEqual("UNKNOWN", self.call()["data"]["quality_enforcement"])

    def test_positive_breach_is_retained_with_other_evidence_missing(self):
        row = {**self.rows[0], "watermark_candidate_status": "COMMITTED", "state_version": None}
        self.tools.backend = FixtureBackend([row])
        self.assertEqual("BREACH", self.call()["data"]["quality_enforcement"])

    def test_unknown_user_or_workload_denied_before_backend(self):
        for grants, identity in ((self.policy.users, self.context.requesting_user_id),
                                 (self.policy.workloads, self.context.workload_id)):
            with self.subTest(identity=identity):
                saved = grants.pop(identity)
                self.assert_error(self.call(), "ACCESS_DENIED", 0)
                grants[identity] = saved

    def test_environment_intersection_denies_workload_broader_access(self):
        self.policy.workloads[self.context.workload_id] = ReadGrant(
            "v1", frozenset({"development", "production"}), self.grant.ingestion_object_keys,
        )
        self.assert_error(self.call({**self.args, "environment": "production"}), "ACCESS_DENIED", 0)

    def test_workload_scope_also_limits_user(self):
        self.policy.workloads[self.context.workload_id] = ReadGrant(
            "v1", frozenset({"test"}), self.grant.ingestion_object_keys,
        )
        self.assert_error(self.call(), "ACCESS_DENIED", 0)

    def test_out_of_scope_object_matches_missing_run_without_leaking_row(self):
        self.backend = FixtureBackend([{**self.rows[0], "ingestion_object_key": "restricted-object"}])
        self.tools.backend = self.backend
        response = self.call()
        self.assert_error(response, "NOT_FOUND", 1)
        self.assertNotIn("restricted-object", json.dumps([response, self.audit]))

    def test_revoked_user_is_rechecked_on_next_call(self):
        self.assertEqual("ok", self.call()["status"])
        self.policy.users.pop(self.context.requesting_user_id)
        self.assert_error(self.call(), "ACCESS_DENIED", 1)

    def test_forged_identity_filter_sql_or_action_is_rejected(self):
        for field in ("role", "requesting_user_id", "workload_id", "filter", "sql", "action", "deadline"):
            with self.subTest(field=field):
                self.assert_error(self.call({**self.args, field: "untrusted"}), "INVALID_ARGUMENT", 0)

    def test_invalid_uuid_environment_or_non_object_rejected(self):
        for arguments in ({**self.args, "object_run_id": "'; DELETE FROM ops.ObjectRun; --"},
                          {**self.args, "environment": "Development"}, {}, None, []):
            with self.subTest(arguments=arguments):
                # Call directly here, because None in the helper means use valid arguments.
                response = self.tools.inspect_object_run(arguments, self.context, deadline=15)
                RESPONSE.validate(response)
                self.assert_error(response, "INVALID_ARGUMENT", 0)

    def test_untrusted_text_is_absent_from_response_and_audit(self):
        response = self.call()
        serialized = json.dumps([response, self.audit])
        self.assertNotIn(self.rows[0]["error_summary"], serialized)
        self.assertNotIn("error_summary", serialized)
        self.assertNotIn("input_boundary_hash", json.dumps(self.audit))

    def test_missing_run_returns_not_found_after_authorization(self):
        self.assert_error(self.call({**self.args, "object_run_id": "20000000-0000-4000-8000-000000000099"}),
                          "NOT_FOUND", 1)

    def test_deadline_cancellation_and_invalid_deadline_prevent_read(self):
        self.assert_error(self.call(deadline=10), "DEADLINE_EXCEEDED", 0)
        cancelled = Event()
        cancelled.set()
        self.assert_error(self.call(cancelled=cancelled), "CANCELLED", 0)
        for deadline in (float("nan"), float("inf"), 16.0, True, "15"):
            with self.subTest(deadline=deadline):
                self.assert_error(self.call(deadline=deadline), "INVALID_ARGUMENT", 0)

    def test_expiry_or_cancellation_during_read_discards_result(self):
        for outcome in ("expiry", "cancel"):
            with self.subTest(outcome=outcome):
                self.now = 10
                cancelled = Event()
                def read(*args, **kwargs):
                    if outcome == "expiry":
                        self.now = 15
                    else:
                        cancelled.set()
                    return copy.deepcopy(self.rows[0])
                self.tools.backend = type("LateBackend", (), {"read": staticmethod(read)})()
                response = self.call(cancelled=cancelled)
                self.assertEqual("DEADLINE_EXCEEDED" if outcome == "expiry" else "CANCELLED",
                                 response["error"]["code"])
                self.assertNotIn("data", response)
                self.assertEqual(1, self.audit[-1]["backend_calls"])

    def test_backend_errors_are_sanitized_and_never_retried(self):
        for exception, code, retryable in ((RateLimited("secret endpoint"), "RATE_LIMITED", True),
                                           (TimeoutError("secret endpoint"), "DEADLINE_EXCEEDED", False),
                                           (RuntimeError("secret endpoint"), "DEPENDENCY_UNAVAILABLE", True)):
            with self.subTest(code=code):
                calls = []
                def read(*args, **kwargs):
                    calls.append(1)
                    raise exception
                self.tools.backend = type("FailingBackend", (), {"read": staticmethod(read)})()
                response = self.call()
                self.assertEqual(code, response["error"]["code"])
                self.assertEqual(retryable, response["error"]["retryable"])
                self.assertEqual(1, len(calls))
                self.assertNotIn("secret endpoint", json.dumps([response, self.audit]))

    def test_policy_failure_denies_data_and_is_sanitized(self):
        def unavailable(_):
            raise RuntimeError("secret policy detail")
        self.tools.policy = unavailable
        response = self.call()
        self.assert_error(response, "DEPENDENCY_UNAVAILABLE", 0)
        self.assertNotIn("secret policy detail", json.dumps([response, self.audit]))

    def test_invalid_missing_or_conflicting_backend_evidence_is_rejected(self):
        rows = [{**self.rows[0], "state_version": -1},
                {**self.rows[0], "release_id": "invalid"},
                {**self.rows[0], "environment": "production"},
                {**self.rows[0], "object_run_id": self.rows[1]["object_run_id"]},
                {name: value for name, value in self.rows[0].items() if name != "input_boundary_hash"},
                []]
        for row in rows:
            with self.subTest(row=row):
                self.tools.backend = type("BadBackend", (), {"read": staticmethod(lambda *a, **k: row)})()
                response = self.call()
                self.assertEqual("INVALID_EVIDENCE", response["error"]["code"])
                self.assertNotIn("data", response)

    def test_adapter_does_not_mutate_fixture_and_returns_independent_copies(self):
        original = copy.deepcopy(self.rows)
        response = self.call()
        response["data"]["record"]["object_run_status"] = "SUCCEEDED"
        self.assertEqual("RECOVERY_REQUIRED", self.call()["data"]["record"]["object_run_status"])
        self.assertEqual(original, self.rows)

    def test_response_schema_rejects_leakage_invalid_id_and_unknown_error(self):
        good = self.call()
        bad = copy.deepcopy(good)
        bad["data"]["raw_payload"] = "secret"
        with self.assertRaises(ValidationError):
            RESPONSE.validate(bad)
        bad = copy.deepcopy(good)
        bad["correlation_id"] = "not-a-uuid"
        with self.assertRaises(ValidationError):
            RESPONSE.validate(bad)
        bad = {"contract_version": "1.0.0", "correlation_id": self.context.correlation_id,
               "status": "error", "error": {"code": "UNKNOWN_CODE", "retryable": False}}
        with self.assertRaises(ValidationError):
            RESPONSE.validate(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)
