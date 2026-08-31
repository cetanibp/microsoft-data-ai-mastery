#!/usr/bin/env python3
"""Run FAB-003 contract tests and emit sanitized machine-readable evidence."""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


TEST_ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    sys.path.insert(0, str(TEST_ROOT.parent / "runtime"))
    sys.path.insert(0, str(TEST_ROOT))
    suite = unittest.defaultTestLoader.discover(
        str(TEST_ROOT), pattern="test_*.py", top_level_dir=str(TEST_ROOT)
    )
    captured = io.StringIO()
    result = unittest.TextTestRunner(stream=captured, verbosity=2).run(suite)
    output = captured.getvalue()
    print(output, end="")
    report = {
        "contract": "FAB-003",
        "contract_version": "0.1.0",
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "commit_sha": os.getenv("GITHUB_SHA", "local"),
        "workflow_run_id": os.getenv("GITHUB_RUN_ID", "local"),
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "failure_details": [
            {"test": str(test), "detail": detail[-2000:]}
            for test, detail in result.failures + result.errors
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
