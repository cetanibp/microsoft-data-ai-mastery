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
object_index = 0
rows_per_object = 10000
seed = 20260902
target_table = "fab004_benchmark_smoke_seq1_r00_o000"
replay = False
submitted_at_utc = "2026-09-02T00:00:00+00:00"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import math
import re
import time
from datetime import datetime, timezone

from delta.tables import DeltaTable
from pyspark import StorageLevel
from pyspark.sql import functions as F


ALLOWED_ENVIRONMENTS = {"development"}
ALLOWED_SCENARIOS = {"SMOKE", "STEADY", "PEAK", "REPLAY"}
ALLOWED_ALTERNATIVES = {"SEQ1", "PAR4"}
ALLOWED_TIERS = {"smoke", "standard", "large"}
SAFE_TABLE = re.compile(r"^fab004_benchmark_[a-z0-9_]+$")

assert environment_name in ALLOWED_ENVIRONMENTS
assert benchmark_run_group_id != "unconfigured"
assert scenario_id in ALLOWED_SCENARIOS
assert alternative_id in ALLOWED_ALTERNATIVES
assert scale_tier in ALLOWED_TIERS
assert isinstance(repetition, int) and 0 <= repetition <= 3
assert isinstance(object_index, int) and 0 <= object_index < 8
assert isinstance(rows_per_object, int) and 1 <= rows_per_object <= 10_000_000
assert isinstance(seed, int) and seed > 0
assert isinstance(replay, bool)
assert SAFE_TABLE.fullmatch(target_table), "Unsafe benchmark target name."

submitted_at = datetime.fromisoformat(submitted_at_utc.replace("Z", "+00:00"))
if submitted_at.tzinfo is None:
    submitted_at = submitted_at.replace(tzinfo=timezone.utc)
worker_started_at = datetime.now(timezone.utc)
queue_seconds = max(0.0, (worker_started_at - submitted_at).total_seconds())
worker_started = time.perf_counter()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

partition_count = max(1, min(32, math.ceil(rows_per_object / 250_000)))
base_epoch_seconds = 1_767_225_600 + ((seed % 10_000) * 86_400)

source = (
    spark.range(0, rows_per_object, 1, partition_count)
    .select(
        F.concat(
            F.lit(f"enc-{object_index:03d}-"),
            F.lpad(F.col("id").cast("string"), 12, "0"),
        ).alias("encounter_id"),
        F.concat(F.lit("fac-"), F.lpad(F.pmod(F.col("id"), F.lit(128)), 3, "0")).alias(
            "facility_id"
        ),
        F.when(F.pmod(F.col("id"), F.lit(5)) == 0, F.lit("arrived"))
        .otherwise(F.lit("complete"))
        .alias("encounter_status"),
        F.to_timestamp(F.from_unixtime(F.lit(base_epoch_seconds) + F.col("id"))).alias(
            "updated_at_utc"
        ),
        (F.col("id") + F.lit(seed)).cast("long").alias("source_sequence"),
    )
    .withColumn("_fab004_run_group_id", F.lit(benchmark_run_group_id))
    .withColumn("_fab004_scenario_id", F.lit(scenario_id))
    .withColumn("_fab004_alternative_id", F.lit(alternative_id))
    .withColumn("_fab004_repetition", F.lit(repetition))
    .withColumn("_fab004_object_index", F.lit(object_index))
    .persist(StorageLevel.MEMORY_AND_DISK)
)

accepted_row_count = source.count()
assert accepted_row_count == rows_per_object

target_existed = spark.catalog.tableExists(target_table)
if replay:
    assert target_existed, "Replay requires a seeded target."

if target_existed:
    target = DeltaTable.forName(spark, target_table)
    (
        target.alias("target")
        .merge(source.alias("source"), "target.encounter_id = source.encounter_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
    operation_metrics = target.history(1).select("operationMetrics").first()[0]
    inserted_row_count = int(operation_metrics.get("numTargetRowsInserted", "0"))
    updated_row_count = int(operation_metrics.get("numTargetRowsUpdated", "0"))
else:
    source.write.format("delta").mode("errorifexists").saveAsTable(target_table)
    inserted_row_count = accepted_row_count
    updated_row_count = 0

source.unpersist()

if replay:
    correctness_status = (
        "PASS"
        if inserted_row_count == 0 and updated_row_count == accepted_row_count
        else "FAIL"
    )
else:
    correctness_status = (
        "PASS"
        if inserted_row_count == accepted_row_count and updated_row_count == 0
        else "FAIL"
    )

completed_at = datetime.now(timezone.utc)
result = {
    "status": "SUCCEEDED" if correctness_status == "PASS" else "FAILED",
    "correctness_status": correctness_status,
    "environment": environment_name,
    "benchmark_run_group_id": benchmark_run_group_id,
    "scenario_id": scenario_id,
    "alternative_id": alternative_id,
    "scale_tier": scale_tier,
    "repetition": repetition,
    "object_index": object_index,
    "rows_per_object": rows_per_object,
    "partition_count": partition_count,
    "replay": replay,
    "accepted_row_count": accepted_row_count,
    "rejected_row_count": 0,
    "duplicate_row_count": 0,
    "inserted_row_count": inserted_row_count,
    "updated_row_count": updated_row_count,
    "queue_seconds": round(queue_seconds, 6),
    "elapsed_seconds": round(time.perf_counter() - worker_started, 6),
    "started_at_utc": worker_started_at.isoformat(),
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
