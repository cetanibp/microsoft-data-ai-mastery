#!/usr/bin/env python3
"""Run RTI-001 repository contract tests and optionally emit JSON evidence."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    suite = unittest.defaultTestLoader.discover(
        str(Path(__file__).parent), pattern="test_*.py"
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    payload = {
        "tracking_id": "RTI-001",
        "contract_version": "1.0.0",
        "status": "PASS" if result.wasSuccessful() else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())

