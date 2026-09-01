# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "25ba06a6-d77c-460d-ba5e-970957ca2429",
# META       "default_lakehouse_name": "lh_northstar_data",
# META       "default_lakehouse_workspace_id": "a06e3c03-3020-476e-941e-3ebb621fecc0",
# META       "known_lakehouses": [
# META         {
# META           "id": "25ba06a6-d77c-460d-ba5e-970957ca2429"
# META         }
# META       ]
# META     }
# META   }
# META }

# PARAMETERS CELL ********************

environment_name = "development"
release_id = "00000000-0000-0000-0000-000000000000"
run_id = "00000000-0000-0000-0000-000000000000"
object_run_id = "00000000-0000-0000-0000-000000000000"
correlation_id = "unconfigured"
input_boundary_hash = "0" * 64
extracted_row_count = 0
accepted_row_count = 0
rejected_row_count = 0
duplicate_row_count = 0
target_table = "bronze_clinical_encounter"
quality_policy_json = "[]"
duplicate_identity_hashes_json = "[]"
quality_results_table = "fab003_quality_check_results"
quarantine_table = "fab003_quarantine_evidence"
quality_test_mode = ""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql import types as T


ALLOWED_ENVIRONMENTS = {"development", "test", "production"}
ALLOWED_TEST_MODES = {"", "BLOCK_TARGET_COUNT", "REQUIRED_ERROR"}
ALLOWED_CHECK_TYPES = {
    "ROW_COUNT_BALANCE",
    "TARGET_COUNT",
    "NULL_RATE",
    "DISTINCT_KEY",
    "MIN_VALUE",
    "MAX_VALUE",
    "SUM_VALUE",
}
ALLOWED_OPERATORS = {"EQ", "NE", "LT", "LE", "GT", "GE"}
ALLOWED_FIELDS = {
    "encounter_id",
    "facility_id",
    "encounter_status",
    "updated_at_utc",
    "source_sequence",
}

CONTRACTS = {
    ("quality/contracts/critical-keys-and-counts", "1.0.0"): [
        {
            "quality_rule_key": "row-count-balance",
            "check_type": "ROW_COUNT_BALANCE",
            "field_name": None,
            "measurement_mode": "ABSOLUTE",
            "operator": "EQ",
            "threshold": "0",
            "required": True,
        },
        {
            "quality_rule_key": "target-count",
            "check_type": "TARGET_COUNT",
            "field_name": None,
            "measurement_mode": "ABSOLUTE",
            "operator": "EQ",
            "threshold": "0",
            "required": True,
        },
        {
            "quality_rule_key": "encounter-id-null-rate",
            "check_type": "NULL_RATE",
            "field_name": "encounter_id",
            "measurement_mode": "PERCENTAGE",
            "operator": "EQ",
            "threshold": "0",
            "required": True,
        },
        {
            "quality_rule_key": "encounter-id-distinct",
            "check_type": "DISTINCT_KEY",
            "field_name": "encounter_id",
            "measurement_mode": "ABSOLUTE",
            "operator": "EQ",
            "threshold": "0",
            "required": True,
        },
    ],
    ("quality/contracts/reference-count-warning", "1.0.0"): [
        {
            "quality_rule_key": "target-count-warning",
            "check_type": "TARGET_COUNT",
            "field_name": None,
            "measurement_mode": "PERCENTAGE",
            "operator": "LE",
            "threshold": "1",
            "required": False,
        }
    ],
}


def stable_hash(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def deterministic_uuid(value):
    return str(uuid.UUID(stable_hash(value)[:32]))


def decimal_value(value):
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("REQUIRED_OBSERVATION_UNAVAILABLE") from error
    if not parsed.is_finite():
        raise ValueError("REQUIRED_OBSERVATION_UNAVAILABLE")
    return parsed


def compare(observed, operator, threshold):
    return {
        "EQ": observed == threshold,
        "NE": observed != threshold,
        "LT": observed < threshold,
        "LE": observed <= threshold,
        "GT": observed > threshold,
        "GE": observed >= threshold,
    }[operator]


assert environment_name in ALLOWED_ENVIRONMENTS, "Unsupported environment."
assert quality_test_mode in ALLOWED_TEST_MODES, "Unsupported quality test mode."
assert quality_test_mode == "" or environment_name == "development", (
    "Failure injection is restricted to development."
)
assert release_id != "00000000-0000-0000-0000-000000000000"
assert run_id != "00000000-0000-0000-0000-000000000000"
assert object_run_id != "00000000-0000-0000-0000-000000000000"
assert correlation_id != "unconfigured"
assert len(input_boundary_hash) == 64
for count in (
    extracted_row_count,
    accepted_row_count,
    rejected_row_count,
    duplicate_row_count,
):
    assert isinstance(count, int) and count >= 0, "Counts must be nonnegative integers."

policies = json.loads(quality_policy_json)
duplicate_identity_hashes = json.loads(duplicate_identity_hashes_json)
assert isinstance(policies, list) and policies, "An active quality policy is required."
assert isinstance(duplicate_identity_hashes, list)
assert all(len(value) == 64 for value in duplicate_identity_hashes)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

assert spark.catalog.tableExists(target_table), "TARGET_OBSERVATION_UNAVAILABLE"
target_scope = spark.table(target_table).where(
    F.col("_fab002_object_run_id") == F.lit(object_run_id)
)
target_count = target_scope.count()


def observe(rule):
    check_type = rule["check_type"]
    field_name = rule["field_name"]
    if check_type == "ROW_COUNT_BALANCE":
        accounted = accepted_row_count + rejected_row_count + duplicate_row_count
        return Decimal(abs(extracted_row_count - accounted))
    if check_type == "TARGET_COUNT":
        variance = abs(accepted_row_count - target_count)
        if quality_test_mode == "BLOCK_TARGET_COUNT":
            variance += 1
        if rule["measurement_mode"] == "PERCENTAGE":
            if accepted_row_count == 0:
                return Decimal(0 if variance == 0 else 100)
            return Decimal(variance) * Decimal(100) / Decimal(accepted_row_count)
        return Decimal(variance)
    if field_name not in ALLOWED_FIELDS or field_name not in target_scope.columns:
        raise ValueError("REQUIRED_OBSERVATION_UNAVAILABLE")
    if check_type == "NULL_RATE":
        if target_count == 0:
            return Decimal(0)
        null_count = target_scope.where(F.col(field_name).isNull()).count()
        return Decimal(null_count) * Decimal(100) / Decimal(target_count)
    if check_type == "DISTINCT_KEY":
        distinct_count = target_scope.select(field_name).distinct().count()
        return Decimal(target_count - distinct_count)
    aggregate_name = {
        "MIN_VALUE": "minimum",
        "MAX_VALUE": "maximum",
        "SUM_VALUE": "total",
    }.get(check_type)
    if aggregate_name is None:
        raise ValueError("REQUIRED_OBSERVATION_UNAVAILABLE")
    aggregate = target_scope.agg(
        {"MIN_VALUE": F.min, "MAX_VALUE": F.max, "SUM_VALUE": F.sum}[check_type](
            F.col(field_name)
        ).alias(aggregate_name)
    ).first()[aggregate_name]
    return decimal_value(aggregate)


results = []
for policy in sorted(policies, key=lambda item: int(item["evaluation_order"])):
    contract_key = (policy["contract_reference"], policy["policy_version"])
    rules = CONTRACTS.get(contract_key)
    if rules is None:
        raise ValueError("UNSUPPORTED_QUALITY_CONTRACT")
    enforcement = policy["enforcement_level"]
    assert enforcement in {"BLOCK", "WARN"}
    for rule in rules:
        started = time.perf_counter()
        assert rule["check_type"] in ALLOWED_CHECK_TYPES
        assert rule["operator"] in ALLOWED_OPERATORS
        observed = None
        error_classification = None
        try:
            if quality_test_mode == "REQUIRED_ERROR" and rule["required"]:
                raise ValueError("REQUIRED_OBSERVATION_UNAVAILABLE")
            observed = observe(rule)
            passed = compare(observed, rule["operator"], Decimal(rule["threshold"]))
            status = "PASS" if passed else ("FAIL" if enforcement == "BLOCK" else "WARN")
        except (ValueError, TypeError, ArithmeticError):
            error_classification = "REQUIRED_OBSERVATION_UNAVAILABLE"
            status = "ERROR" if rule["required"] or enforcement == "BLOCK" else "WARN"
        identity = {
            "object_run_id": object_run_id,
            "input_boundary_hash": input_boundary_hash,
            "quality_policy_key": policy["quality_policy_key"],
            "policy_version": policy["policy_version"],
            "quality_rule_key": rule["quality_rule_key"],
        }
        results.append(
            {
                "quality_result_id": deterministic_uuid(identity),
                "object_run_id": object_run_id,
                "release_id": release_id,
                "quality_policy_key": policy["quality_policy_key"],
                "policy_version": policy["policy_version"],
                "quality_rule_key": rule["quality_rule_key"],
                "check_type": rule["check_type"],
                "observed_value": None if observed is None else str(observed),
                "comparison_operator": rule["operator"],
                "threshold_value": rule["threshold"],
                "result_status": status,
                "enforcement_level": enforcement,
                "error_classification": error_classification,
                "duration_ms": max(0, int((time.perf_counter() - started) * 1000)),
                "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

quarantine_records = []
quarantine_policy = next(
    (policy for policy in policies if bool(policy["quarantine_required"])), None
)
if duplicate_identity_hashes and quarantine_policy is None:
    raise ValueError("QUARANTINE_POLICY_REQUIRED")
for record_hash in duplicate_identity_hashes:
    identity = {
        "object_run_id": object_run_id,
        "input_boundary_hash": input_boundary_hash,
        "quality_policy_key": quarantine_policy["quality_policy_key"],
        "quality_rule_key": "encounter-id-distinct",
        "reason_code": "DUPLICATE_BUSINESS_KEY",
        "source_record_identity_hash": record_hash,
    }
    quarantine_records.append(
        {
            "quarantine_id": stable_hash(identity),
            "object_run_id": object_run_id,
            "release_id": release_id,
            "quality_policy_key": quarantine_policy["quality_policy_key"],
            "quality_rule_key": "encounter-id-distinct",
            "reason_code": "DUPLICATE_BUSINESS_KEY",
            "source_record_identity_hash": record_hash,
            "input_boundary_hash": input_boundary_hash,
            "quarantined_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    )

blocking_failures = sum(
    result["result_status"] == "ERROR"
    or (
        result["enforcement_level"] == "BLOCK"
        and result["result_status"] == "FAIL"
    )
    for result in results
)
warnings = sum(result["result_status"] == "WARN" for result in results)
decision_status = (
    "BLOCKED"
    if blocking_failures
    else ("ACCEPTED_WITH_WARNING" if warnings else "ACCEPTED")
)
result_set_hash = stable_hash(
    [
        {
            "quality_result_id": result["quality_result_id"],
            "observed_value": result["observed_value"],
            "result_status": result["result_status"],
            "error_classification": result["error_classification"],
        }
        for result in results
    ]
)


def persist_delta(records, table_name, schema, key_column):
    if not records:
        return
    frame = spark.createDataFrame(records, schema=schema)
    if spark.catalog.tableExists(table_name):
        target = DeltaTable.forName(spark, table_name)
        (
            target.alias("target")
            .merge(frame.alias("source"), f"target.{key_column} = source.{key_column}")
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        frame.write.format("delta").mode("errorifexists").saveAsTable(table_name)


result_schema = T.StructType(
    [
        T.StructField("quality_result_id", T.StringType(), False),
        T.StructField("object_run_id", T.StringType(), False),
        T.StructField("release_id", T.StringType(), False),
        T.StructField("quality_policy_key", T.StringType(), False),
        T.StructField("policy_version", T.StringType(), False),
        T.StructField("quality_rule_key", T.StringType(), False),
        T.StructField("check_type", T.StringType(), False),
        T.StructField("observed_value", T.StringType(), True),
        T.StructField("comparison_operator", T.StringType(), False),
        T.StructField("threshold_value", T.StringType(), False),
        T.StructField("result_status", T.StringType(), False),
        T.StructField("enforcement_level", T.StringType(), False),
        T.StructField("error_classification", T.StringType(), True),
        T.StructField("duration_ms", T.LongType(), False),
        T.StructField("evaluated_at_utc", T.StringType(), False),
    ]
)
quarantine_schema = T.StructType(
    [
        T.StructField("quarantine_id", T.StringType(), False),
        T.StructField("object_run_id", T.StringType(), False),
        T.StructField("release_id", T.StringType(), False),
        T.StructField("quality_policy_key", T.StringType(), False),
        T.StructField("quality_rule_key", T.StringType(), False),
        T.StructField("reason_code", T.StringType(), False),
        T.StructField("source_record_identity_hash", T.StringType(), False),
        T.StructField("input_boundary_hash", T.StringType(), False),
        T.StructField("quarantined_at_utc", T.StringType(), False),
    ]
)
persist_delta(results, quality_results_table, result_schema, "quality_result_id")
persist_delta(quarantine_records, quarantine_table, quarantine_schema, "quarantine_id")

output = {
    "status": decision_status,
    "watermark_commit_eligible": blocking_failures == 0,
    "environment": environment_name,
    "release_id": release_id,
    "run_id": run_id,
    "object_run_id": object_run_id,
    "correlation_id": correlation_id,
    "input_boundary_hash": input_boundary_hash,
    "expected_rule_count": len(results),
    "blocking_failure_count": blocking_failures,
    "warning_count": warnings,
    "result_set_hash": result_set_hash,
    "quality_results": results,
    "quarantine_records": quarantine_records,
    "completed_at_utc": datetime.now(timezone.utc).isoformat(),
}
output_json = json.dumps(output, sort_keys=True)
print(output_json)
notebookutils.notebook.exit(output_json)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
