"""Credential-free OPS-002 SLO and alert-routing contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from typing import Callable, Iterable


ACCEPTED_STATUSES = {"SUCCEEDED", "SUCCEEDED_WITH_WARNINGS"}
ACCEPTED_QUALITY = {"ACCEPTED", "ACCEPTED_WITH_WARNING"}


@dataclass(frozen=True)
class Attempt:
    occurrence_key: str
    attempt_number: int
    started_at_utc: datetime
    completed_at_utc: datetime | None
    object_run_status: str
    quality_decision_status: str | None = None
    quality_decided_at_utc: datetime | None = None
    quality_enforcement_safe: bool = True
    excluded: bool = False


@dataclass(frozen=True)
class Occurrence:
    occurrence_key: str
    first_started_at_utc: datetime
    completed_at_utc: datetime | None
    final_status: str
    quality_decision_status: str | None
    accepted_publication_at_utc: datetime | None
    quality_enforcement_safe: bool
    excluded: bool

    @property
    def duration_minutes(self) -> Decimal | None:
        if self.completed_at_utc is None:
            return None
        seconds = Decimal(
            str((self.completed_at_utc - self.first_started_at_utc).total_seconds())
        )
        return seconds / Decimal("60")


@dataclass(frozen=True)
class Evaluation:
    objective_key: str
    numerator_count: int
    denominator_count: int
    excluded_count: int
    observed_value: Decimal | None
    target_value: Decimal
    evaluation_status: str
    error_budget_consumption: Decimal | None


@dataclass(frozen=True)
class RoutingDecision:
    delivery_mode: str
    decision_status: str
    deduplication_key: str


def collapse_attempts(attempts: Iterable[Attempt]) -> list[Occurrence]:
    grouped: dict[str, list[Attempt]] = {}
    for attempt in attempts:
        grouped.setdefault(attempt.occurrence_key, []).append(attempt)

    occurrences: list[Occurrence] = []
    for occurrence_key, members in sorted(grouped.items()):
        ordered = sorted(
            members,
            key=lambda item: (item.attempt_number, item.started_at_utc),
        )
        final = ordered[-1]
        accepted_times = [
            item.quality_decided_at_utc
            for item in ordered
            if item.quality_decision_status in ACCEPTED_QUALITY
            and item.quality_decided_at_utc is not None
        ]
        occurrences.append(
            Occurrence(
                occurrence_key=occurrence_key,
                first_started_at_utc=min(item.started_at_utc for item in ordered),
                completed_at_utc=final.completed_at_utc,
                final_status=final.object_run_status,
                quality_decision_status=final.quality_decision_status,
                accepted_publication_at_utc=(
                    min(accepted_times) if accepted_times else None
                ),
                quality_enforcement_safe=final.quality_enforcement_safe,
                excluded=any(item.excluded for item in ordered),
            )
        )
    return occurrences


def _percent(numerator: int, denominator: int) -> Decimal | None:
    if denominator == 0:
        return None
    return (
        Decimal(numerator) * Decimal("100") / Decimal(denominator)
    ).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


def _evaluate(
    objective_key: str,
    occurrences: Iterable[Occurrence],
    target: Decimal,
    predicate: Callable[[Occurrence], bool],
) -> Evaluation:
    all_rows = list(occurrences)
    eligible = [row for row in all_rows if not row.excluded]
    numerator = sum(1 for row in eligible if predicate(row))
    denominator = len(eligible)
    observed = _percent(numerator, denominator)
    status = "NO_DATA" if observed is None else (
        "PASS" if observed >= target else "BREACH"
    )
    allowed_miss = Decimal("100") - target
    actual_miss = None if observed is None else Decimal("100") - observed
    budget = None
    if actual_miss is not None and allowed_miss > 0:
        budget = (actual_miss / allowed_miss).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )
    return Evaluation(
        objective_key=objective_key,
        numerator_count=numerator,
        denominator_count=denominator,
        excluded_count=len(all_rows) - denominator,
        observed_value=observed,
        target_value=target,
        evaluation_status=status,
        error_budget_consumption=budget,
    )


def evaluate_reliability(
    occurrences: Iterable[Occurrence], target: Decimal = Decimal("99.5")
) -> Evaluation:
    def reliable(row: Occurrence) -> bool:
        if row.final_status in ACCEPTED_STATUSES:
            return True
        return (
            row.quality_decision_status == "BLOCKED"
            and row.quality_enforcement_safe
        )

    return _evaluate("ingestion-reliability", occurrences, target, reliable)


def evaluate_quality_acceptance(
    occurrences: Iterable[Occurrence], target: Decimal = Decimal("99")
) -> Evaluation:
    return _evaluate(
        "quality-acceptance",
        occurrences,
        target,
        lambda row: row.quality_decision_status in ACCEPTED_QUALITY,
    )


def evaluate_quality_enforcement(
    occurrences: Iterable[Occurrence], target: Decimal = Decimal("100")
) -> Evaluation:
    blocked = [
        row for row in occurrences if row.quality_decision_status == "BLOCKED"
    ]
    return _evaluate(
        "quality-enforcement",
        blocked,
        target,
        lambda row: row.quality_enforcement_safe
        and row.final_status not in ACCEPTED_STATUSES,
    )


def evaluate_duration(
    occurrences: Iterable[Occurrence],
    duration_target_minutes: Decimal,
    target: Decimal = Decimal("95"),
) -> Evaluation:
    return _evaluate(
        "duration-compliance",
        occurrences,
        target,
        lambda row: row.duration_minutes is not None
        and row.duration_minutes <= duration_target_minutes,
    )


def evaluate_freshness(
    objective_key: str,
    occurrences: Iterable[Occurrence],
    deadline_by_occurrence: dict[str, datetime],
    target: Decimal = Decimal("99"),
) -> Evaluation:
    if objective_key not in {"critical-freshness", "standard-freshness"}:
        raise ValueError("Unsupported freshness objective")
    return _evaluate(
        objective_key,
        occurrences,
        target,
        lambda row: row.accepted_publication_at_utc is not None
        and row.occurrence_key in deadline_by_occurrence
        and row.accepted_publication_at_utc
        <= deadline_by_occurrence[row.occurrence_key],
    )


def route_alert(
    *,
    environment_code: str,
    ingestion_object_key: str | None,
    detection_category: str,
    severity: str,
    deduplication_scope: str,
    routing_alias: str | None,
    suppressed: bool = False,
) -> RoutingDecision:
    if severity == "P1" and suppressed:
        raise ValueError("P1 alert routing cannot be suppressed")
    if environment_code not in {"development", "test", "production"}:
        raise ValueError("Unsupported environment")

    delivery_mode = (
        "NOTIFICATION_REQUESTED"
        if environment_code == "production"
        else "SIMULATED"
    )
    decision_status = (
        "NO_ROUTE" if routing_alias is None
        else "SUPPRESSED" if suppressed
        else "ROUTED"
    )
    identity = "|".join(
        [
            environment_code,
            ingestion_object_key or "platform",
            detection_category,
            severity,
            deduplication_scope,
            routing_alias or "no-route",
        ]
    )
    return RoutingDecision(
        delivery_mode=delivery_mode,
        decision_status=decision_status,
        deduplication_key=sha256(identity.encode("utf-8")).hexdigest().upper(),
    )
