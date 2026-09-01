CREATE PROCEDURE [ops].[usp_RecordQualityCheckResult]
    @quality_result_id UNIQUEIDENTIFIER,
    @object_run_id UNIQUEIDENTIFIER,
    @release_id UNIQUEIDENTIFIER,
    @quality_policy_key VARCHAR(100),
    @policy_version VARCHAR(50),
    @quality_rule_key VARCHAR(100),
    @check_type VARCHAR(30),
    @observed_value DECIMAL(38, 10) = NULL,
    @comparison_operator VARCHAR(2),
    @threshold_value DECIMAL(38, 10),
    @result_status VARCHAR(10),
    @enforcement_level VARCHAR(10),
    @error_classification VARCHAR(50) = NULL,
    @duration_ms BIGINT,
    @evaluated_at_utc DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF NOT EXISTS
    (
        SELECT 1
        FROM ops.ObjectRun AS object_run
        INNER JOIN ctrl.ObjectQualityPolicy AS object_policy
            ON object_policy.release_id = object_run.release_id
           AND object_policy.ingestion_object_key = object_run.ingestion_object_key
        INNER JOIN ctrl.QualityPolicy AS policy
            ON policy.release_id = object_policy.release_id
           AND policy.quality_policy_key = object_policy.quality_policy_key
        WHERE object_run.object_run_id = @object_run_id
          AND object_run.release_id = @release_id
          AND object_run.object_run_status IN ('CLAIMED', 'EXTRACTING', 'VALIDATING', 'PUBLISHING')
          AND policy.quality_policy_key = @quality_policy_key
          AND policy.policy_version = @policy_version
          AND policy.enforcement_level = @enforcement_level
    )
        THROW 51100, 'Quality result does not match the active object-run policy.', 1;

    BEGIN TRANSACTION;

    UPDATE ops.QualityCheckResult
    SET quality_result_id = @quality_result_id,
        policy_version = @policy_version,
        check_type = @check_type,
        observed_value = @observed_value,
        comparison_operator = @comparison_operator,
        threshold_value = @threshold_value,
        result_status = @result_status,
        enforcement_level = @enforcement_level,
        error_classification = @error_classification,
        duration_ms = @duration_ms,
        evaluated_at_utc = @evaluated_at_utc
    WHERE object_run_id = @object_run_id
      AND quality_policy_key = @quality_policy_key
      AND quality_rule_key = @quality_rule_key;

    IF @@ROWCOUNT = 0
        INSERT ops.QualityCheckResult
        (
            quality_result_id, object_run_id, release_id, quality_policy_key,
            policy_version, quality_rule_key, check_type, observed_value,
            comparison_operator, threshold_value, result_status,
            enforcement_level, error_classification, duration_ms, evaluated_at_utc
        )
        VALUES
        (
            @quality_result_id, @object_run_id, @release_id, @quality_policy_key,
            @policy_version, @quality_rule_key, @check_type, @observed_value,
            @comparison_operator, @threshold_value, @result_status,
            @enforcement_level, @error_classification, @duration_ms, @evaluated_at_utc
        );

    COMMIT TRANSACTION;
END;
GO
