"""Credential-free executable contract for FAB-002 incremental ingestion.

This module models safety behavior, not Fabric connectivity. Production adapters
must preserve these state, replay, identity, and evidence invariants.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable


class IngestionError(RuntimeError):
    """Base class for sanitized runtime failures."""


class InjectedFailure(IngestionError):
    """A deterministic failure used to prove recovery behavior."""


class StaleWatermarkCandidate(IngestionError):
    """The committed state changed after a candidate observed it."""


class DuplicateConflict(IngestionError):
    """One business key has conflicting rows at the same watermark."""


@dataclass(frozen=True)
class IngestionConfig:
    environment_id: str
    release_id: str
    ingestion_object_key: str
    business_key: str
    watermark_column: str
    expected_columns: frozenset[str]
    correlation_prefix: str = "fab002"


@dataclass
class WatermarkState:
    value: int
    version: int = 0
    committed_object_run_id: str | None = None


@dataclass
class WatermarkCandidate:
    candidate_id: str
    object_run_id: str
    from_value: int
    to_value: int
    observed_state_version: int
    status: str = "PROPOSED"
    reason: str | None = None


@dataclass
class ObjectRunEvidence:
    object_run_id: str
    run_id: str
    correlation_id: str
    environment_id: str
    release_id: str
    ingestion_object_key: str
    attempt_number: int
    input_boundary_hash: str
    status: str = "RUNNING"
    extracted_row_count: int = 0
    accepted_row_count: int = 0
    rejected_row_count: int = 0
    inserted_row_count: int = 0
    updated_row_count: int = 0
    duplicate_row_count: int = 0
    duration_ms: int = 0
    error_classification: str | None = None


@dataclass(frozen=True)
class RunResult:
    evidence: ObjectRunEvidence
    committed_watermark: int
    state_version: int


def _stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _error_code(error: IngestionError) -> str:
    if isinstance(error, InjectedFailure):
        return "INJECTED_FAILURE"
    if isinstance(error, DuplicateConflict):
        return "DUPLICATE_CONFLICT"
    if isinstance(error, StaleWatermarkCandidate):
        return "STALE_WATERMARK_CANDIDATE"
    return "SOURCE_CONTRACT_VIOLATION"


class InMemoryControlPlane:
    """Small adapter that enforces FAB-001 compare-and-commit semantics."""

    def __init__(self, initial_watermark: int = 0) -> None:
        self.state = WatermarkState(initial_watermark)
        self.candidates: dict[str, WatermarkCandidate] = {}
        self.events: list[dict[str, Any]] = []

    def propose(self, object_run_id: str, upper_bound: int) -> WatermarkCandidate:
        candidate = WatermarkCandidate(
            candidate_id=str(uuid.uuid4()),
            object_run_id=object_run_id,
            from_value=self.state.value,
            to_value=upper_bound,
            observed_state_version=self.state.version,
        )
        self.candidates[candidate.candidate_id] = candidate
        self.events.append(
            {
                "event_type": "WATERMARK_PROPOSED",
                "object_run_id": object_run_id,
                "candidate_id": candidate.candidate_id,
            }
        )
        return candidate

    def abandon(self, candidate: WatermarkCandidate, reason: str) -> None:
        if candidate.status != "PROPOSED":
            return
        candidate.status = "ABANDONED"
        candidate.reason = reason
        self.events.append(
            {
                "event_type": "WATERMARK_ABANDONED",
                "object_run_id": candidate.object_run_id,
                "candidate_id": candidate.candidate_id,
                "reason": reason,
            }
        )

    def commit(self, candidate: WatermarkCandidate) -> None:
        if candidate.status != "PROPOSED":
            raise IngestionError("candidate is not eligible for commit")
        if candidate.observed_state_version != self.state.version:
            candidate.status = "ABANDONED"
            candidate.reason = "STALE_STATE_VERSION"
            self.events.append(
                {
                    "event_type": "WATERMARK_ABANDONED",
                    "object_run_id": candidate.object_run_id,
                    "candidate_id": candidate.candidate_id,
                    "reason": candidate.reason,
                }
            )
            raise StaleWatermarkCandidate("watermark state changed before commit")
        if candidate.from_value != self.state.value:
            raise StaleWatermarkCandidate("watermark value changed before commit")
        self.state.value = candidate.to_value
        self.state.version += 1
        self.state.committed_object_run_id = candidate.object_run_id
        candidate.status = "COMMITTED"
        candidate.reason = "TARGET_ACCEPTED"
        self.events.append(
            {
                "event_type": "WATERMARK_COMMITTED",
                "object_run_id": candidate.object_run_id,
                "candidate_id": candidate.candidate_id,
            }
        )


class InMemoryTarget:
    """Bronze-like target with business-key upsert semantics."""

    def __init__(self, business_key: str) -> None:
        self.business_key = business_key
        self.rows: dict[Any, dict[str, Any]] = {}

    def upsert(self, rows: Iterable[dict[str, Any]]) -> tuple[int, int]:
        inserted = 0
        updated = 0
        for row in rows:
            key = row[self.business_key]
            if key in self.rows:
                if self.rows[key] != row:
                    self.rows[key] = dict(row)
                    updated += 1
            else:
                self.rows[key] = dict(row)
                inserted += 1
        return inserted, updated


def _deduplicate(
    rows: Iterable[dict[str, Any]], business_key: str, watermark_column: str
) -> tuple[list[dict[str, Any]], int]:
    selected: dict[Any, dict[str, Any]] = {}
    duplicates = 0
    for row in rows:
        key = row[business_key]
        current = selected.get(key)
        if current is None:
            selected[key] = dict(row)
            continue
        duplicates += 1
        current_watermark = current[watermark_column]
        incoming_watermark = row[watermark_column]
        if incoming_watermark > current_watermark:
            selected[key] = dict(row)
        elif incoming_watermark == current_watermark and current != row:
            raise DuplicateConflict(
                "conflicting rows share a business key and watermark"
            )
    return list(selected.values()), duplicates


class IncrementalIngestionRuntime:
    """Reference orchestrator for one fixed watermark window."""

    FAILURE_STAGES = {"AFTER_EXTRACT", "AFTER_TARGET_WRITE", "BEFORE_COMMIT"}

    def __init__(
        self,
        config: IngestionConfig,
        control_plane: InMemoryControlPlane,
        target: InMemoryTarget,
    ) -> None:
        self.config = config
        self.control_plane = control_plane
        self.target = target

    def execute(
        self,
        source_rows: Iterable[dict[str, Any]],
        upper_bound: int,
        *,
        attempt_number: int = 1,
        correlation_id: str | None = None,
        failure_stage: str | None = None,
    ) -> RunResult:
        if failure_stage is not None and failure_stage not in self.FAILURE_STAGES:
            raise ValueError(f"unsupported failure stage: {failure_stage}")
        if upper_bound < self.control_plane.state.value:
            raise ValueError("upper bound cannot precede committed watermark")

        started = time.perf_counter()
        run_id = str(uuid.uuid4())
        object_run_id = str(uuid.uuid4())
        correlation_id = correlation_id or f"{self.config.correlation_prefix}-{run_id}"
        lower_bound = self.control_plane.state.value
        boundary = {
            "environment_id": self.config.environment_id,
            "release_id": self.config.release_id,
            "ingestion_object_key": self.config.ingestion_object_key,
            "lower_exclusive": lower_bound,
            "upper_inclusive": upper_bound,
        }
        evidence = ObjectRunEvidence(
            object_run_id=object_run_id,
            run_id=run_id,
            correlation_id=correlation_id,
            environment_id=self.config.environment_id,
            release_id=self.config.release_id,
            ingestion_object_key=self.config.ingestion_object_key,
            attempt_number=attempt_number,
            input_boundary_hash=_stable_hash(boundary),
        )
        candidate: WatermarkCandidate | None = None

        try:
            materialized = [dict(row) for row in source_rows]
            for row in materialized:
                missing = self.config.expected_columns.difference(row)
                if missing:
                    raise IngestionError("source row is missing required columns")
            extracted = [
                row
                for row in materialized
                if lower_bound < row[self.config.watermark_column] <= upper_bound
            ]
            evidence.extracted_row_count = len(extracted)
            if failure_stage == "AFTER_EXTRACT":
                raise InjectedFailure("intentional failure after extraction")

            accepted, duplicate_count = _deduplicate(
                extracted, self.config.business_key, self.config.watermark_column
            )
            evidence.accepted_row_count = len(accepted)
            evidence.duplicate_row_count = duplicate_count
            if upper_bound == lower_bound and not accepted:
                evidence.status = "SUCCEEDED"
            else:
                candidate = self.control_plane.propose(object_run_id, upper_bound)
                inserted, updated = self.target.upsert(accepted)
                evidence.inserted_row_count = inserted
                evidence.updated_row_count = updated
                if failure_stage == "AFTER_TARGET_WRITE":
                    raise InjectedFailure("intentional failure after target write")
                if failure_stage == "BEFORE_COMMIT":
                    raise InjectedFailure(
                        "intentional failure before watermark commit"
                    )

                self.control_plane.commit(candidate)
                evidence.status = "SUCCEEDED"
        except StaleWatermarkCandidate:
            evidence.status = "RECOVERY_REQUIRED"
            evidence.error_classification = "STALE_WATERMARK_CANDIDATE"
        except IngestionError as error:
            if candidate is not None:
                self.control_plane.abandon(candidate, _error_code(error))
            evidence.status = "FAILED"
            evidence.error_classification = _error_code(error)
        finally:
            evidence.duration_ms = max(0, int((time.perf_counter() - started) * 1000))

        return RunResult(
            evidence=evidence,
            committed_watermark=self.control_plane.state.value,
            state_version=self.control_plane.state.version,
        )
