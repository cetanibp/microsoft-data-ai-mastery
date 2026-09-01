CREATE PROCEDURE [ops].[usp_FinalizeQualityDecision]
    @object_run_id UNIQUEIDENTIFIER,
    @candidate_id UNIQUEIDENTIFIER,
    @expected_rule_count SMALLINT,
    @result_set_hash VARCHAR(64),
    @actor_identity NVARCHAR(200),
    @correlation_id VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    IF @expected_rule_count < 1 OR LEN(@result_set_hash) <> 64
        THROW 51120, 'Quality decision inputs are invalid.', 1;

    BEGIN TRANSACTION;

    DECLARE @environment_id UNIQUEIDENTIFIER;
    DECLARE @release_id UNIQUEIDENTIFIER;
    DECLARE @run_id UNIQUEIDENTIFIER;
    DECLARE @recorded_rule_count SMALLINT;
    DECLARE @blocking_failure_count SMALLINT;
    DECLARE @warning_count SMALLINT;
    DECLARE @decision_status VARCHAR(30);
    DECLARE @eligible BIT;
    DECLARE @now DATETIME2(7) = SYSUTCDATETIME();

    SELECT
        @environment_id = object_run.environment_id,
        @release_id = object_run.release_id,
        @run_id = object_run.run_id
    FROM ops.ObjectRun AS object_run WITH (UPDLOCK, HOLDLOCK)
    INNER JOIN ops.ExecutionRun AS execution_run WITH (UPDLOCK, HOLDLOCK)
        ON execution_run.run_id = object_run.run_id
    INNER JOIN ops.WatermarkCandidate AS candidate WITH (UPDLOCK, HOLDLOCK)
        ON candidate.object_run_id = object_run.object_run_id
    WHERE object_run.object_run_id = @object_run_id
      AND candidate.candidate_id = @candidate_id
      AND candidate.candidate_status = 'PROPOSED'
      AND object_run.object_run_status IN ('CLAIMED', 'EXTRACTING', 'VALIDATING', 'PUBLISHING')
      AND execution_run.run_status = 'RUNNING'
      AND execution_run.correlation_id = @correlation_id;

    IF @environment_id IS NULL
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51121, 'The object run is not eligible for a quality decision.', 1;
    END;

    SELECT
        @recorded_rule_count = COUNT(*),
        @blocking_failure_count = COALESCE(SUM(
            CASE WHEN result_status = 'ERROR'
                       OR (enforcement_level = 'BLOCK' AND result_status = 'FAIL')
                 THEN 1 ELSE 0 END), 0),
        @warning_count = COALESCE(SUM(
            CASE WHEN result_status = 'WARN' THEN 1 ELSE 0 END), 0)
    FROM ops.QualityCheckResult WITH (UPDLOCK, HOLDLOCK)
    WHERE object_run_id = @object_run_id;

    IF @recorded_rule_count <> @expected_rule_count
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51122, 'Required quality results are missing or duplicated.', 1;
    END;

    SET @decision_status = CASE
        WHEN @blocking_failure_count > 0 THEN 'BLOCKED'
        WHEN @warning_count > 0 THEN 'ACCEPTED_WITH_WARNING'
        ELSE 'ACCEPTED' END;
    SET @eligible = CASE WHEN @blocking_failure_count > 0 THEN 0 ELSE 1 END;

    UPDATE ops.QualityDecision
    SET decision_status = @decision_status,
        watermark_commit_eligible = @eligible,
        evaluated_rule_count = @recorded_rule_count,
        blocking_failure_count = @blocking_failure_count,
        warning_count = @warning_count,
        result_set_hash = @result_set_hash,
        decided_at_utc = @now
    WHERE object_run_id = @object_run_id;

    IF @@ROWCOUNT = 0
        INSERT ops.QualityDecision
        (
            object_run_id, decision_status, watermark_commit_eligible,
            evaluated_rule_count, blocking_failure_count, warning_count,
            result_set_hash, decided_at_utc
        )
        VALUES
        (
            @object_run_id, @decision_status, @eligible,
            @recorded_rule_count, @blocking_failure_count, @warning_count,
            @result_set_hash, @now
        );

    IF @eligible = 0
    BEGIN
        UPDATE ops.WatermarkCandidate
        SET candidate_status = 'ABANDONED',
            resolved_at_utc = @now,
            resolution_reason = N'QUALITY_GATE_BLOCKED'
        WHERE candidate_id = @candidate_id;

        UPDATE ops.ObjectRun
        SET object_run_status = 'FAILED',
            error_classification = 'QUALITY_GATE_BLOCKED',
            error_summary = N'Required quality checks blocked publication acceptance.',
            completed_at_utc = @now
        WHERE object_run_id = @object_run_id;

        UPDATE ops.ExecutionRun
        SET run_status = 'FAILED', completed_at_utc = @now
        WHERE run_id = @run_id;

        INSERT audit.StateEvent
        (
            state_event_id, environment_id, release_id, run_id, object_run_id,
            event_type, actor_identity, reason, correlation_id,
            before_hash, after_hash, occurred_at_utc
        )
        VALUES
        (
            NEWID(), @environment_id, @release_id, @run_id, @object_run_id,
            'STATUS_CHANGED', @actor_identity,
            N'Quality gate blocked acceptance; watermark candidate abandoned.',
            @correlation_id, NULL, @result_set_hash, @now
        );
    END;

    COMMIT TRANSACTION;

    SELECT
        @decision_status AS decision_status,
        @eligible AS watermark_commit_eligible,
        @recorded_rule_count AS evaluated_rule_count,
        @blocking_failure_count AS blocking_failure_count,
        @warning_count AS warning_count;
END;
GO
