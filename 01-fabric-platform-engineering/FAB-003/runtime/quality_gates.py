"""Credential-free executable contract for FAB-003 quality gates.

The module models policy validation, reconciliation, quarantine identity, and
publication decisions. Production Fabric adapters must preserve these semantics.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable


CHECK_TYPES = frozenset(
    {
        "ROW_COUNT_BALANCE",
        "TARGET_COUNT",
        "NULL_RATE",
        "DISTINCT_KEY",
        "MIN_VALUE",
        "MAX_VALUE",
        "SUM_VALUE",
    }
)
ENFORCEMENT_MODES = frozenset({"BLOCK", "WARN"})
OPERATORS = frozenset({"EQ", "NE", "LT", "LE", "GT", "GE"})
MEASUREMENT_MODES = frozenset({"ABSOLUTE", "PERCENTAGE"})
FIELD_CHECK_TYPES = frozenset(
    {"NULL_RATE", "DISTINCT_KEY", "MIN_VALUE", "MAX_VALUE", "SUM_VALUE"}
)
_SAFE_KEY = re.compile(r"^[a-z][a-z0-9-]{2,79}$")
_SAFE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


class QualityContractError(ValueError):
    """A sanitized policy or observation contract failure."""


def _stable_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _decimal(value: Any) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise QualityContractError("numeric value is required")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise QualityContractError("numeric value is invalid") from error
    if not parsed.is_finite():
        raise QualityContractError("numeric value must be finite")
    return parsed


@dataclass(frozen=True)
class QualityPolicy:
    policy_key: str
    policy_version: str
    check_type: str
    enforcement_mode: str
    operator: str
    threshold: Decimal | int | float | str
    ordinal: int
    field_name: str | None = None
    measurement_mode: str = "ABSOLUTE"
    required: bool = True
    quarantine_expected: bool = False

    def __post_init__(self) -> None:
        if not _SAFE_KEY.fullmatch(self.policy_key):
            raise QualityContractError("policy key is not an approved logical key")
        if not _SAFE_VERSION.fullmatch(self.policy_version):
            raise QualityContractError("policy version must use semantic versioning")
        if self.check_type not in CHECK_TYPES:
            raise QualityContractError("check type is not allowlisted")
        if self.enforcement_mode not in ENFORCEMENT_MODES:
            raise QualityContractError("enforcement mode is not allowlisted")
        if self.operator not in OPERATORS:
            raise QualityContractError("comparison operator is not allowlisted")
        if self.measurement_mode not in MEASUREMENT_MODES:
            raise QualityContractError("measurement mode is not allowlisted")
        if not isinstance(self.ordinal, int) or self.ordinal < 1:
            raise QualityContractError("policy ordinal must be a positive integer")
        if self.check_type in FIELD_CHECK_TYPES and not self.field_name:
            raise QualityContractError("field check requires an allowlisted field")
        if self.check_type not in FIELD_CHECK_TYPES and self.field_name is not None:
            raise QualityContractError("count reconciliation cannot declare a field")
        if self.check_type in FIELD_CHECK_TYPES and self.measurement_mode != "ABSOLUTE":
            raise QualityContractError("field checks use absolute observations")
        if self.field_name is not None and not self.field_name.isidentifier():
            raise QualityContractError("field name is not a logical identifier")
        object.__setattr__(self, "threshold", _decimal(self.threshold))


@dataclass(frozen=True)
class EvaluationContext:
    environment_id: str
    release_id: str
    run_id: str
    object_run_id: str
    ingestion_object_key: str
    attempt_number: int
    input_boundary_hash: str
    extracted_count: int
    accepted_count: int
    rejected_count: int
    duplicate_count: int

    def __post_init__(self) -> None:
        counts = (
            self.extracted_count,
            self.accepted_count,
            self.rejected_count,
            self.duplicate_count,
        )
        if any(not isinstance(value, int) or value < 0 for value in counts):
            raise QualityContractError("row counts must be nonnegative integers")
        if not isinstance(self.attempt_number, int) or self.attempt_number < 1:
            raise QualityContractError("attempt number must be positive")


@dataclass(frozen=True)
class InvalidRecord:
    record_identity: str
    reason_code: str
    policy_key: str

    def __post_init__(self) -> None:
        if not self.record_identity:
            raise QualityContractError("invalid record requires a stable identity")
        if not re.fullmatch(r"[A-Z][A-Z0-9_]{2,63}", self.reason_code):
            raise QualityContractError("quarantine reason code is invalid")


@dataclass(frozen=True)
class QualityCheckResult:
    result_id: str
    policy_key: str
    policy_version: str
    check_type: str
    enforcement_mode: str
    observed_value: Decimal | None
    operator: str
    threshold: Decimal
    status: str
    error_classification: str | None
    duration_ms: int


@dataclass(frozen=True)
class QuarantineRecord:
    quarantine_id: str
    object_run_id: str
    boundary_hash: str
    policy_key: str
    reason_code: str
    source_record_identity_hash: str


@dataclass(frozen=True)
class QualityDecision:
    status: str
    watermark_commit_eligible: bool
    results: tuple[QualityCheckResult, ...]
    quarantine_records: tuple[QuarantineRecord, ...]


@dataclass
class InMemoryQualityEvidence:
    """Idempotent evidence adapter keyed by deterministic identities."""

    results: dict[str, QualityCheckResult] = field(default_factory=dict)
    quarantine: dict[str, QuarantineRecord] = field(default_factory=dict)

    def write_result(self, result: QualityCheckResult) -> None:
        self.results[result.result_id] = result

    def write_quarantine(self, record: QuarantineRecord) -> None:
        self.quarantine[record.quarantine_id] = record


@dataclass
class InMemoryWatermarkState:
    """Minimal acceptance boundary proving blocked checks preserve state."""

    value: int
    version: int = 0
    committed_object_run_id: str | None = None

    def commit_if_eligible(
        self, decision: QualityDecision, upper_bound: int, object_run_id: str
    ) -> bool:
        if not decision.watermark_commit_eligible:
            return False
        self.value = upper_bound
        self.version += 1
        self.committed_object_run_id = object_run_id
        return True


def _compare(observed: Decimal, operator: str, threshold: Decimal) -> bool:
    return {
        "EQ": observed == threshold,
        "NE": observed != threshold,
        "LT": observed < threshold,
        "LE": observed <= threshold,
        "GT": observed > threshold,
        "GE": observed >= threshold,
    }[operator]


class QualityGateRuntime:
    """Evaluate ordered policies and derive one publication decision."""

    def __init__(
        self, allowed_fields: Iterable[str], evidence: InMemoryQualityEvidence | None = None
    ) -> None:
        self.allowed_fields = frozenset(allowed_fields)
        if any(not field_name.isidentifier() for field_name in self.allowed_fields):
            raise QualityContractError("allowed fields must be logical identifiers")
        self.evidence = evidence or InMemoryQualityEvidence()

    def evaluate(
        self,
        context: EvaluationContext,
        policies: Iterable[QualityPolicy],
        *,
        target_rows: Iterable[dict[str, Any]],
        invalid_records: Iterable[InvalidRecord] = (),
    ) -> QualityDecision:
        rows = tuple(dict(row) for row in target_rows)
        ordered = sorted(tuple(policies), key=lambda policy: policy.ordinal)
        if not ordered:
            raise QualityContractError("at least one quality policy is required")
        if len({policy.ordinal for policy in ordered}) != len(ordered):
            raise QualityContractError("policy ordinals must be unique")
        for policy in ordered:
            if policy.field_name and policy.field_name not in self.allowed_fields:
                raise QualityContractError("policy field is not allowlisted")

        results = tuple(self._evaluate_policy(context, policy, rows) for policy in ordered)
        for result in results:
            self.evidence.write_result(result)

        policy_by_key = {policy.policy_key: policy for policy in ordered}
        quarantined: list[QuarantineRecord] = []
        for invalid in invalid_records:
            policy = policy_by_key.get(invalid.policy_key)
            if policy is None or not policy.quarantine_expected:
                raise QualityContractError(
                    "quarantine record must reference an active quarantine policy"
                )
            record_hash = _stable_hash(invalid.record_identity)
            identity = {
                "object_run_id": context.object_run_id,
                "boundary_hash": context.input_boundary_hash,
                "policy_key": invalid.policy_key,
                "reason_code": invalid.reason_code,
                "record_hash": record_hash,
            }
            record = QuarantineRecord(
                quarantine_id=_stable_hash(identity),
                object_run_id=context.object_run_id,
                boundary_hash=context.input_boundary_hash,
                policy_key=invalid.policy_key,
                reason_code=invalid.reason_code,
                source_record_identity_hash=record_hash,
            )
            self.evidence.write_quarantine(record)
            quarantined.append(record)

        blocked = any(result.status in {"FAIL", "ERROR"} for result in results)
        warned = any(result.status == "WARN" for result in results)
        status = "BLOCKED" if blocked else (
            "ACCEPTED_WITH_WARNING" if warned else "ACCEPTED"
        )
        return QualityDecision(
            status=status,
            watermark_commit_eligible=not blocked,
            results=results,
            quarantine_records=tuple(quarantined),
        )

    def _evaluate_policy(
        self,
        context: EvaluationContext,
        policy: QualityPolicy,
        rows: tuple[dict[str, Any], ...],
    ) -> QualityCheckResult:
        started = time.perf_counter()
        observed: Decimal | None = None
        error_classification: str | None = None
        try:
            observed = self._observe(context, policy, rows)
            passed = _compare(observed, policy.operator, policy.threshold)
            status = "PASS" if passed else (
                "FAIL" if policy.enforcement_mode == "BLOCK" else "WARN"
            )
        except (QualityContractError, KeyError, TypeError, ValueError, ArithmeticError):
            error_classification = "REQUIRED_OBSERVATION_UNAVAILABLE"
            status = (
                "ERROR"
                if policy.required or policy.enforcement_mode == "BLOCK"
                else "WARN"
            )

        identity = {
            "environment_id": context.environment_id,
            "release_id": context.release_id,
            "object_run_id": context.object_run_id,
            "boundary_hash": context.input_boundary_hash,
            "policy_key": policy.policy_key,
            "policy_version": policy.policy_version,
        }
        return QualityCheckResult(
            result_id=_stable_hash(identity),
            policy_key=policy.policy_key,
            policy_version=policy.policy_version,
            check_type=policy.check_type,
            enforcement_mode=policy.enforcement_mode,
            observed_value=observed,
            operator=policy.operator,
            threshold=policy.threshold,
            status=status,
            error_classification=error_classification,
            duration_ms=max(0, math.floor((time.perf_counter() - started) * 1000)),
        )

    @staticmethod
    def _observe(
        context: EvaluationContext,
        policy: QualityPolicy,
        rows: tuple[dict[str, Any], ...],
    ) -> Decimal:
        if policy.check_type == "ROW_COUNT_BALANCE":
            accounted = (
                context.accepted_count
                + context.rejected_count
                + context.duplicate_count
            )
            variance = Decimal(abs(context.extracted_count - accounted))
            return QualityGateRuntime._count_observation(
                variance, context.extracted_count, policy.measurement_mode
            )
        if policy.check_type == "TARGET_COUNT":
            variance = Decimal(abs(context.accepted_count - len(rows)))
            return QualityGateRuntime._count_observation(
                variance, context.accepted_count, policy.measurement_mode
            )

        field_name = policy.field_name
        if field_name is None:
            raise QualityContractError("field observation is not configured")
        if any(field_name not in row for row in rows):
            raise QualityContractError("required field observation is unavailable")

        values = [row[field_name] for row in rows]
        if policy.check_type == "NULL_RATE":
            if not values:
                return Decimal(0)
            null_count = sum(value is None for value in values)
            return Decimal(null_count) * Decimal(100) / Decimal(len(values))
        if policy.check_type == "DISTINCT_KEY":
            comparable = [json.dumps(value, sort_keys=True, default=str) for value in values]
            return Decimal(len(values) - len(set(comparable)))

        numeric = [_decimal(value) for value in values]
        if not numeric:
            raise QualityContractError("aggregate requires at least one value")
        if policy.check_type == "MIN_VALUE":
            return min(numeric)
        if policy.check_type == "MAX_VALUE":
            return max(numeric)
        if policy.check_type == "SUM_VALUE":
            return sum(numeric, Decimal(0))
        raise QualityContractError("unsupported check type")

    @staticmethod
    def _count_observation(
        absolute_variance: Decimal, expected_count: int, measurement_mode: str
    ) -> Decimal:
        if measurement_mode == "ABSOLUTE":
            return absolute_variance
        if expected_count == 0:
            return Decimal(0) if absolute_variance == 0 else Decimal(100)
        return absolute_variance * Decimal(100) / Decimal(expected_count)
