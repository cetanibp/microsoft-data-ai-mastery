"""One synthetic, read-only Northstar tool. No network or execution path."""

from __future__ import annotations

import copy
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Callable, Protocol
from uuid import UUID

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "contracts/inspect-object-run-v1.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
VERSION = "1.0.0"


def validator(definition: str) -> Draft202012Validator:
    return Draft202012Validator(
        {"$ref": f"#/$defs/{definition}", "$defs": SCHEMA["$defs"]},
        format_checker=FormatChecker(),
    )


REQUEST = validator("request")
RECORD = validator("record")
RESPONSE = validator("response")
RECORD_FIELDS = tuple(SCHEMA["$defs"]["record"]["required"])


@dataclass(frozen=True)
class TrustedContext:
    """Server-created context; never deserialize this from model arguments.

    Local tests inject synthetic IDs. A deployed adapter must create this only
    after validating the user's token and establishing its own workload identity.
    """

    requesting_user_id: str
    workload_id: str
    correlation_id: str

    def __post_init__(self) -> None:
        for name in ("requesting_user_id", "workload_id", "correlation_id"):
            if str(UUID(getattr(self, name))) != getattr(self, name):
                raise ValueError("Trusted identity IDs must be canonical UUIDs")


@dataclass(frozen=True)
class ReadGrant:
    """Trusted current policy: the intersection of user and workload scopes."""

    policy_version: str
    environments: frozenset[str]
    ingestion_object_keys: frozenset[str]


class FixturePolicy:
    """Synthetic server-owned grants, intersected for each user/workload call."""

    def __init__(self, users: dict[str, ReadGrant], workloads: dict[str, ReadGrant],
                 version: str = "synthetic-policy-v1"):
        self.users = dict(users)
        self.workloads = dict(workloads)
        self.version = version

    def __call__(self, context: TrustedContext) -> ReadGrant | None:
        user = self.users.get(context.requesting_user_id)
        workload = self.workloads.get(context.workload_id)
        if user is None or workload is None:
            return None
        return ReadGrant(self.version, user.environments & workload.environments,
                         user.ingestion_object_keys & workload.ingestion_object_keys)


class RateLimited(Exception):
    """The backend refused the read because of its rate limit."""


class ReadBackend(Protocol):
    def read(self, environment: str, object_run_id: str, *,
             allowed_object_keys: frozenset[str], timeout_seconds: float,
             cancelled: Event) -> dict | None:
        """One exact lookup; honor timeout and cancellation; no retry or writes."""
        ...


class FixtureBackend:
    """In-memory synthetic adapter. Copies inputs and outputs to prevent mutation."""

    def __init__(self, records: list[dict]):
        self._records = copy.deepcopy(records)
        self.calls = 0

    def read(self, environment: str, object_run_id: str, *,
             allowed_object_keys: frozenset[str], timeout_seconds: float,
             cancelled: Event) -> dict | None:
        self.calls += 1
        matches = [row for row in self._records
                   if row.get("environment") == environment
                   and row.get("object_run_id") == object_run_id
                   and row.get("ingestion_object_key") in allowed_object_keys]
        if len(matches) > 1:
            raise ValueError("Duplicate fixture identity")
        return copy.deepcopy(matches[0]) if matches else None


def quality_enforcement(record: dict) -> str:
    """Use the OPS-002 condition, while keeping incomplete evidence unknown."""
    quality = record["quality_decision_status"]
    if quality is None:
        return "UNKNOWN"
    if quality != "BLOCKED":
        return "NOT_APPLICABLE"
    if (record["object_run_status"] in {"SUCCEEDED", "SUCCEEDED_WITH_WARNINGS"}
            or record["watermark_candidate_status"] == "COMMITTED"
            or record["committed_object_run_id"] == record["object_run_id"]):
        return "BREACH"
    if record["watermark_candidate_status"] is None or record["state_version"] is None:
        return "UNKNOWN"
    return "PASS"


class ReadOnlyTools:
    def __init__(self, backend: ReadBackend,
                 policy: Callable[[TrustedContext], ReadGrant | None], *,
                 audit: list[dict], clock: Callable[[], float] = time.monotonic):
        self.backend = backend
        self.policy = policy
        self.audit = audit
        self.clock = clock

    def inspect_object_run(self, arguments: dict, context: TrustedContext, *,
                           deadline: float, cancelled: Event | None = None) -> dict:
        """Return one observation with at most one backend call and no retries.

        deadline is an absolute monotonic deadline set by the caller's server.
        Audit is a synthetic in-memory sink, not a durable production audit log.
        """
        cancelled = cancelled if cancelled is not None else Event()
        backend_calls = 0
        grant = None

        def finish(*, code: str | None = None, data: dict | None = None) -> dict:
            response = {"contract_version": VERSION,
                        "correlation_id": context.correlation_id,
                        "status": "error" if code else "ok"}
            if code:
                response["error"] = {
                    "code": code,
                    "retryable": code in {"RATE_LIMITED", "DEPENDENCY_UNAVAILABLE"},
                }
            else:
                response["data"] = data
            RESPONSE.validate(response)
            self.audit.append({
                "contract_version": VERSION,
                "correlation_id": context.correlation_id,
                "requesting_user_id": context.requesting_user_id,
                "workload_id": context.workload_id,
                "policy_version": grant.policy_version if grant else None,
                "status": response["status"],
                "error_code": code,
                "backend_calls": backend_calls,
            })
            return response

        def stopped() -> str | None:
            if cancelled.is_set():
                return "CANCELLED"
            if self.clock() >= deadline:
                return "DEADLINE_EXCEEDED"
            return None

        try:
            REQUEST.validate(arguments)
        except ValidationError:
            return finish(code="INVALID_ARGUMENT")
        if (not isinstance(deadline, (int, float)) or isinstance(deadline, bool)
                or not math.isfinite(deadline) or deadline - self.clock() > 5):
            return finish(code="INVALID_ARGUMENT")
        # Normalize UUIDs before lookup, so alternate casing cannot split identity.
        arguments = {**arguments, "object_run_id": str(UUID(arguments["object_run_id"]))}
        if code := stopped():
            return finish(code=code)
        try:
            grant = self.policy(context)  # Re-resolve on every call; no grant cache.
        except Exception:
            return finish(code="DEPENDENCY_UNAVAILABLE")
        if (grant is None or arguments["environment"] not in grant.environments
                or not grant.ingestion_object_keys):
            return finish(code="ACCESS_DENIED")
        if code := stopped():
            return finish(code=code)
        backend_calls = 1
        try:
            raw_record = self.backend.read(
                arguments["environment"], arguments["object_run_id"],
                allowed_object_keys=grant.ingestion_object_keys,
                timeout_seconds=deadline - self.clock(), cancelled=cancelled,
            )
        except RateLimited:
            return finish(code=stopped() or "RATE_LIMITED")
        except TimeoutError:
            return finish(code=stopped() or "DEADLINE_EXCEEDED")
        except Exception:
            return finish(code=stopped() or "DEPENDENCY_UNAVAILABLE")
        if code := stopped():
            return finish(code=code)
        if raw_record is None:
            return finish(code="NOT_FOUND")
        if not isinstance(raw_record, dict):
            return finish(code="INVALID_EVIDENCE")
        # Drop free-form errors, payloads, URLs and source instructions before
        # validation, response generation or logging. Never interpolate them.
        record = {name: raw_record[name] for name in RECORD_FIELDS if name in raw_record}
        try:
            RECORD.validate(record)
        except ValidationError:
            return finish(code="INVALID_EVIDENCE")
        if (record["environment"] != arguments["environment"]
                or record["object_run_id"] != arguments["object_run_id"]):
            return finish(code="INVALID_EVIDENCE")
        if record["ingestion_object_key"] not in grant.ingestion_object_keys:
            return finish(code="NOT_FOUND")
        integrity = quality_enforcement(record)
        evidence = [
            {"rank": 1, "kind": "QUALITY_ENFORCEMENT",
             "source": "ops.vw_OperationalOccurrence contract", "value": integrity},
            {"rank": 2, "kind": "RUN_STATE", "source": "ops.ObjectRun",
             "value": record["object_run_status"]},
            {"rank": 3, "kind": "QUALITY_DECISION", "source": "ops.QualityDecision",
             "value": record["quality_decision_status"] or "UNKNOWN"},
        ]
        return finish(data={
            "record": record, "quality_enforcement": integrity, "evidence": evidence,
            "observation_kind": "synthetic_fixture",
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        })


def demo() -> None:
    fixtures = json.loads((ROOT / "fixtures/object-runs.json").read_text(encoding="utf-8"))
    context = TrustedContext(
        "10000000-0000-4000-8000-000000000001",
        "10000000-0000-4000-8000-000000000002",
        "10000000-0000-4000-8000-000000000003",
    )
    grant = ReadGrant("synthetic-policy-v1", frozenset({"development"}),
                      frozenset({"ingest-clinical-encounter"}))
    audit: list[dict] = []
    policy = FixturePolicy({context.requesting_user_id: grant}, {context.workload_id: grant})
    tools = ReadOnlyTools(FixtureBackend(fixtures), policy, audit=audit)
    responses = [tools.inspect_object_run(
        {"environment": row["environment"], "object_run_id": row["object_run_id"]},
        context, deadline=time.monotonic() + 5,
    ) for row in fixtures]
    print(json.dumps({"responses": responses, "audit": audit}, indent=2))


if __name__ == "__main__":
    demo()
