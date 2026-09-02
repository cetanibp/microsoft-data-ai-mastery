"""Dependency-free validation helpers for the FAB-004 benchmark manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_METRICS = {
    "elapsed_seconds",
    "queue_seconds",
    "throughput_rows_per_second",
    "cu_seconds",
    "cu_seconds_per_million_rows",
    "peak_utilization_pct",
    "throttling_count",
    "correctness_status",
}


def load_manifest(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def tier_total_rows(manifest: dict[str, Any], tier_name: str) -> int:
    tier = manifest["scale_tiers"][tier_name]
    return int(tier["object_count"]) * int(tier["rows_per_object"])


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if manifest.get("tracking_id") != "FAB-004":
        errors.append("tracking_id must be FAB-004")
    if manifest.get("data_classification") != "synthetic":
        errors.append("only synthetic benchmark data is permitted")

    capacity = manifest.get("capacity", {})
    if capacity.get("sku") != "F256" or capacity.get("capacity_units") != 256:
        errors.append("capacity must declare F256 and 256 capacity units")
    if capacity.get("hourly_price_usd") is not None:
        errors.append("hourly_price_usd must remain an uncommitted environment input")

    alternatives = manifest.get("alternatives", [])
    parallelism = {
        item.get("alternative_id"): item.get("max_parallelism")
        for item in alternatives
    }
    if parallelism != {"SEQ1": 1, "PAR4": 4}:
        errors.append("alternatives must compare SEQ1=1 with PAR4=4")

    tiers = manifest.get("scale_tiers", {})
    expected_tiers = {
        "smoke": (1, 10_000),
        "standard": (4, 1_000_000),
        "large": (8, 10_000_000),
    }
    for name, (objects, rows) in expected_tiers.items():
        tier = tiers.get(name, {})
        if (tier.get("object_count"), tier.get("rows_per_object")) != (objects, rows):
            errors.append(f"scale tier {name} does not match the approved contract")

    scenario_ids: set[str] = set()
    for scenario in manifest.get("scenarios", []):
        scenario_id = scenario.get("scenario_id")
        if not scenario_id or scenario_id in scenario_ids:
            errors.append("scenario IDs must be present and unique")
        scenario_ids.add(scenario_id)
        tier_name = scenario.get("scale_tier")
        if tier_name not in tiers:
            errors.append(f"scenario {scenario_id} references an unknown scale tier")
        if scenario.get("comparison_included"):
            if scenario.get("alternatives") != ["SEQ1", "PAR4"]:
                errors.append(f"scenario {scenario_id} must compare SEQ1 and PAR4")
            if scenario.get("measured_repetitions") != 3:
                errors.append(f"scenario {scenario_id} must have three measured repetitions")

    if scenario_ids != {"SMOKE", "STEADY", "PEAK", "REPLAY"}:
        errors.append("scenario set must be SMOKE, STEADY, PEAK, and REPLAY")

    pair_order = manifest.get("pair_order")
    if pair_order != [
        ["SEQ1", "PAR4"],
        ["PAR4", "SEQ1"],
        ["SEQ1", "PAR4"],
    ]:
        errors.append("pair_order must alternate across three repetitions")

    metrics = set(manifest.get("required_metrics", []))
    missing_metrics = sorted(REQUIRED_METRICS - metrics)
    if missing_metrics:
        errors.append(f"required metrics missing: {', '.join(missing_metrics)}")

    thresholds = manifest.get("decision_thresholds", {})
    expected_thresholds = {
        "minimum_elapsed_improvement_pct": 15,
        "maximum_normalized_cu_increase_pct": 25,
        "capacity_review_utilization_pct": 80,
        "capacity_review_consecutive_samples": 3,
        "critical_workload_max_degradation_pct": 20,
    }
    for name, expected in expected_thresholds.items():
        if thresholds.get(name) != expected:
            errors.append(f"decision threshold {name} must equal {expected}")

    return errors


def allocated_cost_usd(cu_seconds: float, hourly_price_usd: float) -> float:
    if cu_seconds < 0 or hourly_price_usd < 0:
        raise ValueError("cost inputs cannot be negative")
    return cu_seconds / (256 * 3600) * hourly_price_usd
