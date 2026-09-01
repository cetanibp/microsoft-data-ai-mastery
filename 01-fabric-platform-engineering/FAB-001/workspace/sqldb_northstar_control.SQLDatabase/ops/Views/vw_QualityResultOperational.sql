CREATE VIEW [ops].[vw_QualityResultOperational]
AS
SELECT
    object_run.environment_id,
    object_run.release_id,
    object_run.run_id,
    object_run.object_run_id,
    object_run.ingestion_object_key,
    object_run.attempt_number,
    object_run.input_boundary_hash,
    decision.decision_status,
    decision.watermark_commit_eligible,
    decision.evaluated_rule_count,
    decision.blocking_failure_count,
    decision.warning_count,
    decision.result_set_hash,
    decision.decided_at_utc,
    result.quality_policy_key,
    result.policy_version,
    result.quality_rule_key,
    result.check_type,
    result.observed_value,
    result.comparison_operator,
    result.threshold_value,
    result.result_status,
    result.enforcement_level,
    result.error_classification,
    result.duration_ms,
    result.evaluated_at_utc
FROM ops.ObjectRun AS object_run
INNER JOIN ops.QualityDecision AS decision
    ON decision.object_run_id = object_run.object_run_id
INNER JOIN ops.QualityCheckResult AS result
    ON result.object_run_id = object_run.object_run_id;
GO
