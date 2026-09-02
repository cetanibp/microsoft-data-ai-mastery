CREATE PROCEDURE [ops].[usp_RecordSloEvaluation]
    @slo_evaluation_id UNIQUEIDENTIFIER,
    @evaluator_version VARCHAR(30),
    @environment_id UNIQUEIDENTIFIER,
    @release_id UNIQUEIDENTIFIER,
    @ingestion_object_key VARCHAR(150) = NULL,
    @objective_key VARCHAR(100),
    @source_slo_key VARCHAR(100) = NULL,
    @window_start_utc DATETIME2(7),
    @window_end_utc DATETIME2(7),
    @numerator_count BIGINT,
    @denominator_count BIGINT,
    @observed_value DECIMAL(19, 6) = NULL,
    @target_value DECIMAL(19, 6),
    @comparison_operator VARCHAR(10),
    @target_unit VARCHAR(30),
    @alert_severity VARCHAR(2),
    @error_budget_consumption DECIMAL(19, 6) = NULL,
    @excluded_count BIGINT = 0,
    @source_evidence_hash VARCHAR(64),
    @detected_at_utc DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    IF @window_start_utc >= @window_end_utc
        THROW 51000, 'SLO evaluation requires a bounded positive window.', 1;

    IF @numerator_count < 0 OR @denominator_count < 0
       OR @numerator_count > @denominator_count OR @excluded_count < 0
        THROW 51000, 'SLO evaluation counts are invalid.', 1;

    DECLARE @evaluation_status VARCHAR(20);
    IF @denominator_count = 0
    BEGIN
        IF @observed_value IS NOT NULL
            THROW 51000, 'NO_DATA evaluation cannot contain an observed value.', 1;
        SET @evaluation_status = 'NO_DATA';
    END
    ELSE
    BEGIN
        IF @observed_value IS NULL
            THROW 51000, 'Evaluated SLO requires an observed value.', 1;

        SET @evaluation_status = CASE
            WHEN @comparison_operator = '>=' AND @observed_value >= @target_value THEN 'PASS'
            WHEN @comparison_operator = '>'  AND @observed_value >  @target_value THEN 'PASS'
            WHEN @comparison_operator = '<=' AND @observed_value <= @target_value THEN 'PASS'
            WHEN @comparison_operator = '<'  AND @observed_value <  @target_value THEN 'PASS'
            WHEN @comparison_operator = '='  AND @observed_value =  @target_value THEN 'PASS'
            ELSE 'BREACH'
        END;
    END;

    BEGIN TRANSACTION;

    DECLARE @existing_id UNIQUEIDENTIFIER;
    SELECT @existing_id = slo_evaluation_id
    FROM ops.SloEvaluation WITH (UPDLOCK, HOLDLOCK)
    WHERE evaluator_version = @evaluator_version
      AND environment_id = @environment_id
      AND release_id = @release_id
      AND ((ingestion_object_key = @ingestion_object_key)
           OR (ingestion_object_key IS NULL AND @ingestion_object_key IS NULL))
      AND objective_key = @objective_key
      AND window_start_utc = @window_start_utc
      AND window_end_utc = @window_end_utc;

    IF @existing_id IS NOT NULL
    BEGIN
        IF NOT EXISTS
        (
            SELECT 1
            FROM ops.SloEvaluation
            WHERE slo_evaluation_id = @existing_id
              AND source_evidence_hash = @source_evidence_hash
              AND numerator_count = @numerator_count
              AND denominator_count = @denominator_count
              AND ((observed_value = @observed_value)
                   OR (observed_value IS NULL AND @observed_value IS NULL))
              AND target_value = @target_value
              AND comparison_operator = @comparison_operator
              AND target_unit = @target_unit
              AND evaluation_status = @evaluation_status
              AND alert_severity = @alert_severity
              AND excluded_count = @excluded_count
        )
        BEGIN
            ROLLBACK TRANSACTION;
            THROW 51000, 'SLO evaluation identity changed.', 1;
        END;

        COMMIT TRANSACTION;
        SELECT @existing_id AS slo_evaluation_id, @evaluation_status AS evaluation_status,
               CAST(0 AS bit) AS inserted;
        RETURN;
    END;

    INSERT ops.SloEvaluation
    (
        slo_evaluation_id, evaluator_version, environment_id, release_id,
        ingestion_object_key, objective_key, source_slo_key,
        window_start_utc, window_end_utc, numerator_count, denominator_count,
        observed_value, target_value, comparison_operator, target_unit,
        evaluation_status, alert_severity, error_budget_consumption,
        excluded_count, source_evidence_hash, detected_at_utc
    )
    VALUES
    (
        @slo_evaluation_id, @evaluator_version, @environment_id, @release_id,
        @ingestion_object_key, @objective_key, @source_slo_key,
        @window_start_utc, @window_end_utc, @numerator_count, @denominator_count,
        @observed_value, @target_value, @comparison_operator, @target_unit,
        @evaluation_status, @alert_severity, @error_budget_consumption,
        @excluded_count, @source_evidence_hash, @detected_at_utc
    );

    COMMIT TRANSACTION;
    SELECT @slo_evaluation_id AS slo_evaluation_id, @evaluation_status AS evaluation_status,
           CAST(1 AS bit) AS inserted;
END;
GO
