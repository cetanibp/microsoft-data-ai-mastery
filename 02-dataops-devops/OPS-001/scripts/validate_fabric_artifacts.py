#!/usr/bin/env python3
"""Validate the OPS-001 Fabric Git definitions without requiring Fabric credentials."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
LIBRARY = WORKSPACE / "vl_northstar_environment.VariableLibrary"
NOTEBOOK = (
    WORKSPACE
    / "NB_OPS001_EnvironmentValidation.Notebook"
    / "notebook-content.py"
)

EXPECTED_TYPES = {
    "environment_name": "String",
    "release_ring": "String",
    "minimum_quality_pct": "Integer",
    "allow_destructive_tests": "Boolean",
    "validation_contract_version": "String",
}

EXPECTED_VALUE_SETS = {
    "development": {
        "environment_name": "development",
        "release_ring": "development",
        "minimum_quality_pct": 90,
        "allow_destructive_tests": True,
        "validation_contract_version": "1.1.0",
    },
    "test": {
        "environment_name": "test",
        "release_ring": "validation",
        "minimum_quality_pct": 95,
        "allow_destructive_tests": False,
        "validation_contract_version": "1.1.0",
    },
    "production": {
        "environment_name": "production",
        "release_ring": "stable",
        "minimum_quality_pct": 99,
        "allow_destructive_tests": False,
        "validation_contract_version": "1.1.0",
    },
}

SENSITIVE_KEY = re.compile(
    r"(^|_)(password|client_secret|clientsecret|token|api_key|apikey|secret)($|_)",
    re.IGNORECASE,
)
SENSITIVE_TEXT = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"AccountKey\s*=", re.IGNORECASE),
]


class ValidationError(RuntimeError):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"Invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc


def assert_equal(actual: Any, expected: Any, message: str) -> None:
    if actual != expected:
        raise ValidationError(f"{message}; expected {expected!r}, found {actual!r}")


def scan_json_keys(value: Any, path: str = "$") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if SENSITIVE_KEY.search(str(key)) and child not in ("", None, [], {}):
                findings.append(child_path)
            findings.extend(scan_json_keys(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(scan_json_keys(child, f"{path}[{index}]"))
    return findings


def validate() -> list[str]:
    checks: list[str] = []

    required_paths = [
        LIBRARY / ".platform",
        LIBRARY / "settings.json",
        LIBRARY / "variables.json",
        NOTEBOOK.parent / ".platform",
        NOTEBOOK,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.is_file()]
    if missing:
        raise ValidationError(f"Missing required Fabric files: {', '.join(missing)}")
    checks.append("Required Fabric item files exist")

    json_paths = sorted(WORKSPACE.rglob("*.json")) + sorted(WORKSPACE.rglob(".platform"))
    for path in json_paths:
        load_json(path)
    checks.append(f"Parsed {len(json_paths)} Fabric JSON metadata files")

    variables_doc = load_json(LIBRARY / "variables.json")
    variables = {item["name"]: item for item in variables_doc.get("variables", [])}
    assert_equal(set(variables), set(EXPECTED_TYPES), "Variable names do not match contract")
    for name, expected_type in EXPECTED_TYPES.items():
        assert_equal(variables[name].get("type"), expected_type, f"Type mismatch for {name}")

    assert_equal(variables["environment_name"].get("value"), "unconfigured", "Unsafe environment default")
    assert_equal(variables["release_ring"].get("value"), "unconfigured", "Unsafe release-ring default")
    assert_equal(
        variables["validation_contract_version"].get("value"),
        "unconfigured",
        "Unsafe contract-version default",
    )
    assert_equal(variables["allow_destructive_tests"].get("value"), False, "Unsafe destructive-test default")
    checks.append("Variable names, types, and safe defaults match contract")

    settings = load_json(LIBRARY / "settings.json")
    assert_equal(
        set(settings.get("valueSetsOrder", [])),
        set(EXPECTED_VALUE_SETS),
        "Value-set names do not match environments",
    )

    for environment, expected in EXPECTED_VALUE_SETS.items():
        value_set = load_json(LIBRARY / "valueSets" / f"{environment}.json")
        assert_equal(value_set.get("name"), environment, f"Value-set name mismatch for {environment}")
        overrides = {
            item["name"]: item.get("value")
            for item in value_set.get("variableOverrides", [])
        }
        assert_equal(overrides, expected, f"Invalid values for {environment}")
    checks.append("Development, Test, and Production values match policy")

    notebook_source = NOTEBOOK.read_text(encoding="utf-8-sig")
    compile(notebook_source, str(NOTEBOOK), "exec")
    required_notebook_tokens = [
        'getLibrary(',
        '"vl_northstar_environment"',
        "validation_contract_version",
        'validation_contract_version == "1.1.0"',
        "notebookutils.notebook.exit",
    ]
    absent = [token for token in required_notebook_tokens if token not in notebook_source]
    if absent:
        raise ValidationError(f"Notebook is missing contract tokens: {', '.join(absent)}")
    checks.append("Notebook syntax and configuration contract are valid")

    findings: list[str] = []
    for path in json_paths:
        document = load_json(path)
        findings.extend(
            f"{path.relative_to(ROOT)}:{finding}"
            for finding in scan_json_keys(document)
        )
    for path in WORKSPACE.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8-sig")
            for pattern in SENSITIVE_TEXT:
                if pattern.search(text):
                    findings.append(f"{path.relative_to(ROOT)}:{pattern.pattern}")
    if findings:
        raise ValidationError(f"Potential committed secret material: {', '.join(findings)}")
    checks.append("No obvious secret material detected")

    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        default=str(ROOT / "evidence" / "ci-validation-report.json"),
    )
    args = parser.parse_args()
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL",
        "checks": [],
    }

    try:
        report["checks"] = validate()
        report["status"] = "PASS"
        print("OPS-001 Fabric artifact validation: PASS")
        for check in report["checks"]:
            print(f"  - {check}")
        return_code = 0
    except (ValidationError, SyntaxError, KeyError, TypeError) as exc:
        report["error"] = str(exc)
        print(f"OPS-001 Fabric artifact validation: FAIL\n  - {exc}", file=sys.stderr)
        return_code = 1

    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
