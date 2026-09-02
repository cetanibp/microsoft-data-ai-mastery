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
release_id = "00000000-0000-0000-0000-000000000000"
run_id = "00000000-0000-0000-0000-000000000000"
object_run_id = "00000000-0000-0000-0000-000000000000"
correlation_id = "unconfigured"
lower_bound = "2026-01-01T00:00:00Z"
upper_bound = "2026-08-30T12:15:00Z"
scenario = "baseline"
failure_stage = ""
target_table = "bronze_clinical_encounter"
drift_table = "fab002_schema_drift_events"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
from datetime import datetime, timezone

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.window import Window


ALLOWED_ENVIRONMENTS = {"development", "test", "production"}
ALLOWED_SCENARIOS = {"baseline", "replay", "additive_drift", "breaking_drift"}
ALLOWED_FAILURE_STAGES = {"", "AFTER_EXTRACT", "AFTER_TARGET_WRITE"}
APPROVED_COLUMNS = (
    "encounter_id",
    "facility_id",
    "encounter_status",
    "updated_at_utc",
    "source_sequence",
)

assert environment_name in ALLOWED_ENVIRONMENTS, "Unsupported environment."
assert scenario in ALLOWED_SCENARIOS, "Unsupported synthetic scenario."
assert failure_stage in ALLOWED_FAILURE_STAGES, "Unsupported failure stage."
assert correlation_id != "unconfigured", "A correlation ID is required."
assert release_id != "00000000-0000-0000-0000-000000000000", (
    "A pinned metadata release ID is required."
)
assert run_id != "00000000-0000-0000-0000-000000000000", "A run ID is required."
assert object_run_id != "00000000-0000-0000-0000-000000000000", (
    "An object-run ID is required."
)
assert lower_bound < upper_bound, "The fixed watermark window must advance."

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

synthetic_rows = [
    ("enc-001", "fac-001", "complete", "2026-08-30T12:01:00Z", 1),
    ("enc-002", "fac-001", "arrived", "2026-08-30T12:03:00Z", 2),
    ("enc-002", "fac-001", "complete", "2026-08-30T12:05:00Z", 3),
    ("enc-003", "fac-002", "complete", "2026-08-30T12:15:00Z", 4),
    ("enc-004", "fac-002", "future", "2026-08-30T12:16:00Z", 5),
    ("enc-005", "fac-003", "arrived", "2026-08-30T12:22:00Z", 6),
    ("enc-005", "fac-003", "complete", "2026-08-30T12:23:00Z", 7),
]

source_schema = T.StructType(
    [
        T.StructField("encounter_id", T.StringType(), False),
        T.StructField("facility_id", T.StringType(), False),
        T.StructField("encounter_status", T.StringType(), False),
        T.StructField("updated_at_utc", T.StringType(), False),
        T.StructField("source_sequence", T.LongType(), False),
    ]
)
source = spark.createDataFrame(synthetic_rows, source_schema).withColumn(
    "updated_at_utc", F.to_timestamp("updated_at_utc")
)

if scenario == "additive_drift":
    source = source.withColumn("source_comment", F.lit("synthetic-additive-field"))
elif scenario == "breaking_drift":
    source = source.drop("encounter_id")

source_columns = set(source.columns)
approved_columns = set(APPROVED_COLUMNS)
missing_columns = sorted(approved_columns - source_columns)
extra_columns = sorted(source_columns - approved_columns)

if missing_columns:
    raise RuntimeError(
        "BREAKING_SCHEMA_DRIFT: required columns are missing; watermark preserved"
    )

drift_event_count = 0
if extra_columns:
    drift_event = [
        (
            environment_name,
            release_id,
            object_run_id,
            correlation_id,
            "ingest-clinical-encounter",
            "ADDITIVE",
            "QUARANTINE",
            json.dumps(extra_columns),
            datetime.now(timezone.utc),
        )
    ]
    drift_schema = T.StructType(
        [
            T.StructField("environment_name", T.StringType(), False),
            T.StructField("release_id", T.StringType(), False),
            T.StructField("object_run_id", T.StringType(), False),
            T.StructField("correlation_id", T.StringType(), False),
            T.StructField("ingestion_object_key", T.StringType(), False),
            T.StructField("drift_classification", T.StringType(), False),
            T.StructField("drift_route", T.StringType(), False),
            T.StructField("column_names_json", T.StringType(), False),
            T.StructField("detected_at_utc", T.TimestampType(), False),
        ]
    )
    drift_event_frame = spark.createDataFrame(drift_event, drift_schema)
    if spark.catalog.tableExists(drift_table):
        drift_target = DeltaTable.forName(spark, drift_table)
        (
            drift_target.alias("target")
            .merge(
                drift_event_frame.alias("source"),
                "target.object_run_id = source.object_run_id",
            )
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        drift_event_frame.write.format("delta").mode("errorifexists").saveAsTable(
            drift_table
        )
    drift_event_count = 1
    source = source.select(*APPROVED_COLUMNS)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

windowed = source.where(
    (F.col("updated_at_utc") > F.to_timestamp(F.lit(lower_bound)))
    & (F.col("updated_at_utc") <= F.to_timestamp(F.lit(upper_bound)))
)
extracted_row_count = windowed.count()

if failure_stage == "AFTER_EXTRACT":
    raise RuntimeError("INJECTED_FAILURE: intentional failure after extraction")

dedupe_window = Window.partitionBy("encounter_id").orderBy(
    F.col("updated_at_utc").desc(), F.col("source_sequence").desc()
)
ranked = windowed.withColumn("_rank", F.row_number().over(dedupe_window))
duplicate_identity_hashes = [
    row["source_record_identity_hash"]
    for row in (
        ranked.where(F.col("_rank") > 1)
        .select(
            F.sha2(
                F.concat_ws(
                    "||",
                    F.lit("fab003-duplicate-v1"),
                    F.col("encounter_id"),
                    F.date_format(F.col("updated_at_utc"), "yyyy-MM-dd'T'HH:mm:ss.SSSXXX"),
                    F.col("source_sequence").cast("string"),
                ),
                256,
            ).alias("source_record_identity_hash")
        )
        .orderBy("source_record_identity_hash")
        .collect()
    )
]
accepted = (
    ranked.where(F.col("_rank") == 1)
    .drop("_rank")
    .withColumn("_fab002_run_id", F.lit(run_id))
    .withColumn("_fab002_object_run_id", F.lit(object_run_id))
    .withColumn("_fab002_correlation_id", F.lit(correlation_id))
    .withColumn("_fab002_ingested_at_utc", F.current_timestamp())
)
accepted_row_count = accepted.count()
duplicate_row_count = extracted_row_count - accepted_row_count

target_exists = spark.catalog.tableExists(target_table)
if target_exists:
    target = DeltaTable.forName(spark, target_table)
    (
        target.alias("target")
        .merge(accepted.alias("source"), "target.encounter_id = source.encounter_id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute()
    )
    metrics = target.history(1).select("operationMetrics").first()[0]
    inserted_row_count = int(metrics.get("numTargetRowsInserted", "0"))
    updated_row_count = int(metrics.get("numTargetRowsUpdated", "0"))
else:
    accepted.write.format("delta").mode("errorifexists").saveAsTable(target_table)
    inserted_row_count = accepted_row_count
    updated_row_count = 0

if failure_stage == "AFTER_TARGET_WRITE":
    raise RuntimeError("INJECTED_FAILURE: intentional failure after target write")

result = {
    "status": "SUCCEEDED_WITH_WARNINGS" if drift_event_count else "SUCCEEDED",
    "environment": environment_name,
    "release_id": release_id,
    "run_id": run_id,
    "object_run_id": object_run_id,
    "correlation_id": correlation_id,
    "ingestion_object_key": "ingest-clinical-encounter",
    "lower_exclusive": lower_bound,
    "upper_inclusive": upper_bound,
    "extracted_row_count": extracted_row_count,
    "accepted_row_count": accepted_row_count,
    "rejected_row_count": 0,
    "duplicate_row_count": duplicate_row_count,
    "duplicate_identity_hashes": duplicate_identity_hashes,
    "inserted_row_count": inserted_row_count,
    "updated_row_count": updated_row_count,
    "schema_drift_event_count": drift_event_count,
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
}
result_json = json.dumps(result, sort_keys=True)
print(result_json)
notebookutils.notebook.exit(result_json)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
