"""Credential-free FAB-001 metadata contract validation.

The validator intentionally models only the control-plane contract. It does
not connect to Fabric, resolve a managed connection, or execute source SQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


SECRET_MARKERS = (
    "password=",
    "secret=",
    "token=",
    "accountkey=",
    "sharedaccesssignature=",
    "://",
)

REQUIRED_PRODUCTION_ROLES = {
    "ENGINEERING",
    "SOURCE_STEWARD",
    "OPERATIONS",
}

LOAD_STRATEGIES = {"FULL", "WATERMARK", "APPEND", "SNAPSHOT"}


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    entity: str
    message: str


class ConcurrencyConflict(RuntimeError):
    """Raised when a watermark candidate observed an obsolete state version."""


@dataclass
class WatermarkCandidate:
    run_id: str
    from_value: str
    to_value: str
    observed_state_version: int
    status: str = "PROPOSED"
    resolution_reason: str | None = None


class WatermarkTracker:
    """Small in-memory model of the proposed watermark transaction contract."""

    def __init__(self, committed_value: str, state_version: int = 0) -> None:
        if state_version < 0:
            raise ValueError("state_version cannot be negative")
        self.committed_value = committed_value
        self.state_version = state_version
        self.committed_run_id: str | None = None

    def propose(self, run_id: str, to_value: str) -> WatermarkCandidate:
        return WatermarkCandidate(
            run_id=run_id,
            from_value=self.committed_value,
            to_value=to_value,
            observed_state_version=self.state_version,
        )

    def commit(self, candidate: WatermarkCandidate) -> None:
        if candidate.status != "PROPOSED":
            raise ValueError("only a proposed candidate can commit")
        if candidate.observed_state_version != self.state_version:
            raise ConcurrencyConflict(
                "watermark state changed after the candidate was proposed"
            )
        self.committed_value = candidate.to_value
        self.state_version += 1
        self.committed_run_id = candidate.run_id
        candidate.status = "COMMITTED"
        candidate.resolution_reason = "accepted data and matching state version"

    def abandon(self, candidate: WatermarkCandidate, reason: str) -> None:
        if candidate.status != "PROPOSED":
            raise ValueError("only a proposed candidate can be abandoned")
        if not reason.strip():
            raise ValueError("an abandonment reason is required")
        candidate.status = "ABANDONED"
        candidate.resolution_reason = reason


def _index(
    values: Iterable[dict[str, Any]],
    key_name: str,
    entity_name: str,
    issues: list[ValidationIssue],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for value in values:
        key = value.get(key_name)
        if not isinstance(key, str) or not key:
            issues.append(
                ValidationIssue(
                    "STABLE_KEY_MISSING",
                    entity_name,
                    f"{key_name} must be a non-empty string",
                )
            )
            continue
        if key in result:
            issues.append(
                ValidationIssue(
                    "DUPLICATE_STABLE_KEY",
                    f"{entity_name}:{key}",
                    f"duplicate {key_name}",
                )
            )
            continue
        result[key] = value
    return result


def _contains_secret_like_literal(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.casefold()
    return any(marker in lowered for marker in SECRET_MARKERS)


def _validate_dependencies(
    objects: dict[str, dict[str, Any]],
    dependencies: list[dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    adjacency = {key: [] for key in objects}

    for dependency in dependencies:
        predecessor = dependency.get("predecessor")
        successor = dependency.get("successor")
        entity = f"dependency:{predecessor}->{successor}"

        if predecessor not in objects:
            issues.append(
                ValidationIssue(
                    "DEPENDENCY_PREDECESSOR_MISSING",
                    entity,
                    "predecessor object does not exist",
                )
            )
            continue
        if successor not in objects:
            issues.append(
                ValidationIssue(
                    "DEPENDENCY_SUCCESSOR_MISSING",
                    entity,
                    "successor object does not exist",
                )
            )
            continue
        if predecessor == successor:
            issues.append(
                ValidationIssue(
                    "DEPENDENCY_SELF_REFERENCE",
                    entity,
                    "an object cannot depend on itself",
                )
            )
            continue

        adjacency[predecessor].append(successor)

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, path: list[str]) -> None:
        if node in visiting:
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            issues.append(
                ValidationIssue(
                    "DEPENDENCY_CYCLE",
                    "dependency-graph",
                    " -> ".join(cycle),
                )
            )
            return
        if node in visited:
            return

        visiting.add(node)
        path.append(node)
        for successor in adjacency[node]:
            visit(successor, path)
        path.pop()
        visiting.remove(node)
        visited.add(node)

    for object_key in adjacency:
        visit(object_key, [])


def validate_release(metadata: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    release = metadata.get("release", {})
    if release.get("status") not in {"APPROVED", "ACTIVE"}:
        issues.append(
            ValidationIssue(
                "RELEASE_NOT_APPROVABLE",
                f"release:{release.get('version', '<unknown>')}",
                "runtime resolution requires an approved or active release",
            )
        )

    environments = _index(
        metadata.get("environments", []), "code", "environment", issues
    )
    sources = _index(metadata.get("sources", []), "key", "source", issues)
    source_objects = _index(
        metadata.get("source_objects", []), "key", "source-object", issues
    )
    target_objects = _index(
        metadata.get("target_objects", []), "key", "target-object", issues
    )
    load_policies = _index(
        metadata.get("load_policies", []), "key", "load-policy", issues
    )
    watermark_policies = _index(
        metadata.get("watermark_policies", []),
        "key",
        "watermark-policy",
        issues,
    )
    execution_policies = _index(
        metadata.get("execution_policies", []),
        "key",
        "execution-policy",
        issues,
    )
    schedules = _index(metadata.get("schedules", []), "key", "schedule", issues)
    slos = _index(metadata.get("slos", []), "key", "slo", issues)
    quality_policies = _index(
        metadata.get("quality_policies", []), "key", "quality-policy", issues
    )
    owner_groups = _index(
        metadata.get("owner_groups", []), "key", "owner-group", issues
    )
    objects = _index(
        metadata.get("ingestion_objects", []), "key", "ingestion-object", issues
    )

    parameter_definitions = metadata.get("strategy_parameter_definitions", {})

    for source_key, source in sources.items():
        environment_config = source.get("environment_config", {})
        for environment_code, environment in environments.items():
            config = environment_config.get(environment_code)
            if not config:
                issues.append(
                    ValidationIssue(
                        "SOURCE_ENVIRONMENT_CONFIG_MISSING",
                        f"source:{source_key}/{environment_code}",
                        "source has no environment configuration",
                    )
                )
                continue
            for field in ("connection_reference", "landing_zone"):
                if _contains_secret_like_literal(config.get(field)):
                    issues.append(
                        ValidationIssue(
                            "UNSAFE_CONFIGURATION_LITERAL",
                            f"source:{source_key}/{environment_code}/{field}",
                            "configuration must contain a safe logical key only",
                        )
                    )
            if environment.get("production") and config.get("enabled") is not True:
                # Disabled production sources are permitted, but any object that uses
                # one will be rejected below.
                continue

    for source_object_key, source_object in source_objects.items():
        if source_object.get("source") not in sources:
            issues.append(
                ValidationIssue(
                    "SOURCE_REFERENCE_MISSING",
                    f"source-object:{source_object_key}",
                    "referenced source does not exist",
                )
            )

    for policy_key, policy in load_policies.items():
        strategy = policy.get("strategy")
        watermark_key = policy.get("watermark_policy")
        entity = f"load-policy:{policy_key}"

        if strategy not in LOAD_STRATEGIES:
            issues.append(
                ValidationIssue(
                    "LOAD_STRATEGY_UNSUPPORTED",
                    entity,
                    f"unsupported strategy: {strategy}",
                )
            )
            continue
        if strategy == "WATERMARK" and watermark_key not in watermark_policies:
            issues.append(
                ValidationIssue(
                    "WATERMARK_POLICY_MISSING",
                    entity,
                    "WATERMARK strategy requires a valid watermark policy",
                )
            )
        if strategy != "WATERMARK" and watermark_key is not None:
            issues.append(
                ValidationIssue(
                    "WATERMARK_POLICY_NOT_ALLOWED",
                    entity,
                    "only WATERMARK strategy may reference a watermark policy",
                )
            )

        definitions = parameter_definitions.get(strategy, {})
        values = policy.get("parameters", {})
        for parameter_key, definition in definitions.items():
            if definition.get("required") and parameter_key not in values:
                issues.append(
                    ValidationIssue(
                        "REQUIRED_PARAMETER_MISSING",
                        entity,
                        f"required parameter is missing: {parameter_key}",
                    )
                )
        for parameter_key, value in values.items():
            definition = definitions.get(parameter_key)
            if not definition:
                issues.append(
                    ValidationIssue(
                        "PARAMETER_NOT_ALLOWLISTED",
                        entity,
                        f"parameter is not allowlisted: {parameter_key}",
                    )
                )
                continue
            expected_type = definition.get("type")
            actual_type = (
                "BOOLEAN"
                if isinstance(value, bool)
                else "INTEGER"
                if isinstance(value, int)
                else "DECIMAL"
                if isinstance(value, float)
                else "STRING"
                if isinstance(value, str)
                else "UNKNOWN"
            )
            if actual_type != expected_type:
                issues.append(
                    ValidationIssue(
                        "PARAMETER_TYPE_MISMATCH",
                        entity,
                        f"{parameter_key} expected {expected_type}, got {actual_type}",
                    )
                )
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                minimum = definition.get("minimum")
                maximum = definition.get("maximum")
                if minimum is not None and value < minimum:
                    issues.append(
                        ValidationIssue(
                            "PARAMETER_OUT_OF_RANGE",
                            entity,
                            f"{parameter_key} is below minimum {minimum}",
                        )
                    )
                if maximum is not None and value > maximum:
                    issues.append(
                        ValidationIssue(
                            "PARAMETER_OUT_OF_RANGE",
                            entity,
                            f"{parameter_key} is above maximum {maximum}",
                        )
                    )
            allowed_values = definition.get("allowed_values")
            if allowed_values is not None and value not in allowed_values:
                issues.append(
                    ValidationIssue(
                        "PARAMETER_VALUE_NOT_ALLOWED",
                        entity,
                        f"{parameter_key} is not in the allowlist",
                    )
                )
            if _contains_secret_like_literal(value):
                issues.append(
                    ValidationIssue(
                        "UNSAFE_PARAMETER_LITERAL",
                        entity,
                        f"unsafe parameter literal: {parameter_key}",
                    )
                )

    for object_key, obj in objects.items():
        entity = f"ingestion-object:{object_key}"
        source_object = source_objects.get(obj.get("source_object"))

        if source_object is None:
            issues.append(
                ValidationIssue(
                    "SOURCE_OBJECT_REFERENCE_MISSING",
                    entity,
                    "referenced source object does not exist",
                )
            )
        if obj.get("target_object") not in target_objects:
            issues.append(
                ValidationIssue(
                    "TARGET_OBJECT_REFERENCE_MISSING",
                    entity,
                    "referenced target object does not exist",
                )
            )
        if obj.get("load_policy") not in load_policies:
            issues.append(
                ValidationIssue(
                    "LOAD_POLICY_REFERENCE_MISSING",
                    entity,
                    "referenced load policy does not exist",
                )
            )
        if obj.get("execution_policy") not in execution_policies:
            issues.append(
                ValidationIssue(
                    "EXECUTION_POLICY_REFERENCE_MISSING",
                    entity,
                    "referenced execution policy does not exist",
                )
            )

        for schedule_key in obj.get("schedules", []):
            if schedule_key not in schedules:
                issues.append(
                    ValidationIssue(
                        "SCHEDULE_REFERENCE_MISSING",
                        entity,
                        f"schedule does not exist: {schedule_key}",
                    )
                )
        if not obj.get("schedules"):
            issues.append(
                ValidationIssue(
                    "SCHEDULE_MISSING", entity, "object has no schedule"
                )
            )
        for slo_key in obj.get("slos", []):
            if slo_key not in slos:
                issues.append(
                    ValidationIssue(
                        "SLO_REFERENCE_MISSING",
                        entity,
                        f"SLO does not exist: {slo_key}",
                    )
                )
        for quality_key in obj.get("quality_policies", []):
            if quality_key not in quality_policies:
                issues.append(
                    ValidationIssue(
                        "QUALITY_POLICY_REFERENCE_MISSING",
                        entity,
                        f"quality policy does not exist: {quality_key}",
                    )
                )

        ownership_roles: set[str] = set()
        for ownership in obj.get("ownership", []):
            owner_key = ownership.get("owner")
            role = ownership.get("role")
            if owner_key not in owner_groups:
                issues.append(
                    ValidationIssue(
                        "OWNER_REFERENCE_MISSING",
                        entity,
                        f"owner group does not exist: {owner_key}",
                    )
                )
            if isinstance(role, str):
                ownership_roles.add(role)

        environment_config = obj.get("environment_config", {})
        for environment_code, environment in environments.items():
            config = environment_config.get(environment_code)
            if not config:
                issues.append(
                    ValidationIssue(
                        "OBJECT_ENVIRONMENT_CONFIG_MISSING",
                        f"{entity}/{environment_code}",
                        "object has no environment configuration",
                    )
                )
                continue
            if _contains_secret_like_literal(config.get("routing_alias")):
                issues.append(
                    ValidationIssue(
                        "UNSAFE_CONFIGURATION_LITERAL",
                        f"{entity}/{environment_code}/routing_alias",
                        "routing alias must be a safe logical key",
                    )
                )
            if not config.get("enabled"):
                continue

            if source_object:
                source = sources.get(source_object.get("source"))
                source_config = (
                    source.get("environment_config", {}).get(environment_code)
                    if source
                    else None
                )
                if not source_config or not source_config.get("enabled"):
                    issues.append(
                        ValidationIssue(
                            "ENABLED_OBJECT_SOURCE_DISABLED",
                            f"{entity}/{environment_code}",
                            "enabled object requires an enabled source configuration",
                        )
                    )

            if environment.get("production"):
                if not obj.get("slos"):
                    issues.append(
                        ValidationIssue(
                            "PRODUCTION_SLO_MISSING",
                            entity,
                            "production-enabled object requires an SLO",
                        )
                    )
                missing_roles = REQUIRED_PRODUCTION_ROLES - ownership_roles
                for role in sorted(missing_roles):
                    issues.append(
                        ValidationIssue(
                            "PRODUCTION_OWNERSHIP_MISSING",
                            entity,
                            f"required role is missing: {role}",
                        )
                    )

    _validate_dependencies(objects, metadata.get("dependencies", []), issues)
    return issues


def resolve_environment(
    metadata: dict[str, Any], environment_code: str
) -> list[dict[str, Any]]:
    issues = validate_release(metadata)
    if issues:
        codes = ", ".join(sorted({issue.code for issue in issues}))
        raise ValueError(f"metadata release is invalid: {codes}")

    environments = {item["code"]: item for item in metadata["environments"]}
    if environment_code not in environments:
        raise KeyError(f"unknown environment: {environment_code}")

    source_objects = {item["key"]: item for item in metadata["source_objects"]}
    sources = {item["key"]: item for item in metadata["sources"]}
    load_policies = {item["key"]: item for item in metadata["load_policies"]}
    execution_policies = {
        item["key"]: item for item in metadata["execution_policies"]
    }
    result: list[dict[str, Any]] = []

    for obj in metadata["ingestion_objects"]:
        object_config = obj["environment_config"][environment_code]
        if not object_config["enabled"]:
            continue
        source_object = source_objects[obj["source_object"]]
        source = sources[source_object["source"]]
        source_config = source["environment_config"][environment_code]
        result.append(
            {
                "environment": environment_code,
                "release_version": metadata["release"]["version"],
                "object_key": obj["key"],
                "source_object": source_object["key"],
                "connection_reference": source_config["connection_reference"],
                "landing_zone": source_config["landing_zone"],
                "routing_alias": object_config["routing_alias"],
                "priority": object_config.get("priority")
                or execution_policies[obj["execution_policy"]]["default_priority"],
                "strategy": load_policies[obj["load_policy"]]["strategy"],
            }
        )

    return sorted(result, key=lambda item: (-item["priority"], item["object_key"]))
