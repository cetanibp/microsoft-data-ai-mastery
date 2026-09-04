# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# PARAMETERS CELL ********************

environment_name = "development"
benchmark_run_group_id = "unconfigured"
scenario_id = "SMOKE"
alternative_id = "SEQ1"
scale_tier = "smoke"
repetition = 0
object_count = 1
rows_per_object = 10000
seed = 20260902
worker_notebook = "NB_FAB004_BenchmarkWorker"
target_prefix = "fab004_benchmark"
reset_targets = True

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import re
import time
from datetime import datetime, timezone


ALLOWED_ENVIRONMENTS = {"development"}
ALLOWED_SCENARIOS = {"SMOKE", "STEADY", "PEAK", "REPLAY"}
ALLOWED_ALTERNATIVES = {"SEQ1": 1, "PAR4": 4}
TIER_CONTRACTS = {
    "smoke": (1, 10_000),
    "standard": (4, 1_000_000),
    "large": (8, 10_000_000),
}
SAFE_NAME = re.compile(r"^[A-Za-z0-9_]+$")

assert environment_name in ALLOWED_ENVIRONMENTS
assert benchmark_run_group_id != "unconfigured"
assert scenario_id in ALLOWED_SCENARIOS
assert alternative_id in ALLOWED_ALTERNATIVES
assert scale_tier in TIER_CONTRACTS
assert (object_count, rows_per_object) == TIER_CONTRACTS[scale_tier]
assert isinstance(repetition, int) and 0 <= repetition <= 3
assert isinstance(seed, int) and seed > 0
assert SAFE_NAME.fullmatch(worker_notebook)
assert target_prefix == "fab004_benchmark"
assert isinstance(reset_targets, bool)
if scenario_id == "SMOKE":
    assert scale_tier == "smoke" and alternative_id == "SEQ1" and repetition == 0
elif scenario_id == "PEAK":
    assert scale_tier == "large" and 1 <= repetition <= 3
else:
    assert scale_tier == "standard" and 1 <= repetition <= 3

max_parallelism = ALLOWED_ALTERNATIVES[alternative_id]
targets = [
    (
        f"{target_prefix}_{scenario_id.lower()}_{alternative_id.lower()}_"
        f"r{repetition:02d}_o{index:03d}"
    )
    for index in range(object_count)
]

if reset_targets:
    for target in targets:
        spark.sql(f"DROP TABLE IF EXISTS `{target}`")


def exit_value(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("exitVal", "exit_value", "result"):
            if isinstance(value.get(key), str):
                return value[key]
    candidate = getattr(value, "exitVal", None)
    if isinstance(candidate, str):
        return candidate
    raise ValueError("Worker result did not contain a parseable exit value.")


def run_phase(replay):
    submitted_at = datetime.now(timezone.utc)
    activities = []
    for index, target in enumerate(targets):
        activities.append(
            {
                "name": f"object_{index:03d}",
                "path": worker_notebook,
                "timeoutPerCellInSeconds": 1800,
                "args": {
                    "environment_name": environment_name,
                    "benchmark_run_group_id": benchmark_run_group_id,
                    "scenario_id": scenario_id,
                    "alternative_id": alternative_id,
                    "scale_tier": scale_tier,
                    "repetition": repetition,
                    "object_index": index,
                    "rows_per_object": rows_per_object,
                    "seed": seed,
                    "target_table": target,
                    "replay": replay,
                    "submitted_at_utc": submitted_at.isoformat(),
                },
            }
        )
    dag = {
        "activities": activities,
        "timeoutInSeconds": 7200,
        "concurrency": max_parallelism,
    }
    raw_results = notebookutils.notebook.runMultiple(
        dag, {"displayDAGViaGraphviz": False}
    )
    return [json.loads(exit_value(raw_results[item["name"]])) for item in activities]


if scenario_id == "REPLAY":
    seed_results = run_phase(replay=False)
    assert all(item["correctness_status"] == "PASS" for item in seed_results)

orchestrator_started_at = datetime.now(timezone.utc)
orchestrator_started = time.perf_counter()
worker_results = run_phase(replay=scenario_id == "REPLAY")
elapsed_seconds = time.perf_counter() - orchestrator_started

accepted_row_count = sum(item["accepted_row_count"] for item in worker_results)
expected_row_count = object_count * rows_per_object
correctness_status = (
    "PASS"
    if accepted_row_count == expected_row_count
    and all(item["correctness_status"] == "PASS" for item in worker_results)
    else "FAIL"
)
completed_at = datetime.now(timezone.utc)
result = {
    "contract_version": "1.0.0",
    "status": "SUCCEEDED" if correctness_status == "PASS" else "FAILED",
    "correctness_status": correctness_status,
    "environment": environment_name,
    "capacity_sku": "F256",
    "benchmark_run_group_id": benchmark_run_group_id,
    "scenario_id": scenario_id,
    "alternative_id": alternative_id,
    "max_parallelism": max_parallelism,
    "scale_tier": scale_tier,
    "repetition": repetition,
    "object_count": object_count,
    "rows_per_object": rows_per_object,
    "expected_row_count": expected_row_count,
    "accepted_row_count": accepted_row_count,
    "rejected_row_count": sum(item["rejected_row_count"] for item in worker_results),
    "duplicate_row_count": sum(item["duplicate_row_count"] for item in worker_results),
    "elapsed_seconds": round(elapsed_seconds, 6),
    "throughput_rows_per_second": round(accepted_row_count / elapsed_seconds, 3),
    "maximum_worker_queue_seconds": max(item["queue_seconds"] for item in worker_results),
    "worker_results": worker_results,
    "started_at_utc": orchestrator_started_at.isoformat(),
    "completed_at_utc": completed_at.isoformat(),
}
result_json = json.dumps(result, sort_keys=True)
print(result_json)
notebookutils.notebook.exit(result_json)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
