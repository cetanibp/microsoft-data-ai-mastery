# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

import json
from datetime import datetime, timezone

library = notebookutils.variableLibrary.getLibrary(
    "vl_northstar_environment"
)

environment_name = library.environment_name
release_ring = library.release_ring
minimum_quality_pct = int(library.minimum_quality_pct)
allow_destructive_tests = library.allow_destructive_tests
validation_contract_version = library.validation_contract_version

expected_release_rings = {
    "development": "development",
    "test": "validation",
    "production": "stable",
}

expected_quality_thresholds = {
    "development": 90,
    "test": 95,
    "production": 99,
}

assert environment_name in expected_release_rings, (
    f"Invalid or unconfigured environment: {environment_name}"
)

assert release_ring == expected_release_rings[environment_name], (
    f"Release ring '{release_ring}' is invalid for "
    f"environment '{environment_name}'."
)

assert minimum_quality_pct == expected_quality_thresholds[environment_name], (
    f"Quality threshold {minimum_quality_pct} is invalid for "
    f"environment '{environment_name}'."
)

assert not (
    environment_name != "development" and allow_destructive_tests
), "Destructive tests must be disabled outside Development."

assert validation_contract_version == "1.0.0", (
    f"Unsupported validation contract: {validation_contract_version}"
)

result = {
    "status": "PASS",
    "environment": environment_name,
    "release_ring": release_ring,
    "minimum_quality_pct": minimum_quality_pct,
    "allow_destructive_tests": allow_destructive_tests,
    "validated_at_utc": datetime.now(timezone.utc).isoformat(),
    "validation_contract_version": validation_contract_version,
}

result_json = json.dumps(result, indent=2)
print(result_json)

notebookutils.notebook.exit(result_json)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
