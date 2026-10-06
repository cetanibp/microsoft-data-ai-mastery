"""Run local AGENT-001 tests and emit versioned, hashed synthetic evidence."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
import sys
import unittest
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    print(stream.getvalue(), end="")
    artifacts = [
        "requirements.txt", "contracts/inspect-object-run-v1.schema.json",
        "runtime/read_only_tools.py", "fixtures/object-runs.json",
        "tests/test_read_only_tools.py", "tests/run_contract_tests.py",
        "README.md", "tool-contract.md", "threat-model.md", "RETRO.md",
    ]
    report = {
        "contract": "AGENT-001.inspect_object_run",
        "contract_version": "1.0.0",
        "evidence_class": "local_synthetic_behavior",
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped),
        "python_version": platform.python_version(),
        "dependencies": {name: version(name) for name in
                         ("jsonschema", "attrs", "referencing", "jsonschema-specifications", "rpds-py")},
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                            for name in artifacts},
        "execution": {"network_requests": 0, "model_calls": 0,
                      "live_backend_reads": 0, "operational_writes": 0},
        "limitations": ["synthetic policy and data only", "no authenticated MCP adapter",
                        "no live token or SQL authorization", "in-memory audit only"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
