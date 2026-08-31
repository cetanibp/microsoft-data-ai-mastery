CREATE PROCEDURE [ops].[usp_FailWatermarkAttempt]
    @object_run_id uniqueidentifier,
    @candidate_id uniqueidentifier,
    @extracted_row_count bigint = 0,
    @accepted_row_count bigint = 0,
    @rejected_row_count bigint = 0,
    @error_classification varchar(50),
    @error_summary nvarchar(2000),
    @is_terminal_run bit,
    @actor_identity nvarchar(200),
    @correlation_id varchar(100)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @error_classification NOT IN
       ('INJECTED_FAILURE', 'SOURCE_CONTRACT_VIOLATION', 'DUPLICATE_CONFLICT',
        'BREAKING_SCHEMA_DRIFT', 'SOURCE_READ_FAILURE', 'TARGET_WRITE_FAILURE')
        THROW 51030, 'Unsupported error classification.', 1;

    IF @extracted_row_count < 0 OR @accepted_row_count < 0 OR @rejected_row_count < 0
        THROW 51032, 'Row counts cannot be negative.', 1;

    IF @accepted_row_count + @rejected_row_count > @extracted_row_count
        THROW 51033, 'Accepted and rejected counts exceed extracted rows.', 1;

    BEGIN TRANSACTION;

    DECLARE @environment_id uniqueidentifier;
    DECLARE @release_id uniqueidentifier;
    DECLARE @run_id uniqueidentifier;
    DECLARE @from_value nvarchar(4000);
    DECLARE @now datetime2(7) = SYSUTCDATETIME();

    SELECT
        @environment_id = candidate.environment_id,
        @release_id = object_run.release_id,
        @run_id = object_run.run_id,
        @from_value = candidate.from_value
    FROM ops.WatermarkCandidate AS candidate WITH (UPDLOCK, HOLDLOCK)
    INNER JOIN ops.ObjectRun AS object_run WITH (UPDLOCK, HOLDLOCK)
        ON object_run.object_run_id = candidate.object_run_id
    INNER JOIN ops.ExecutionRun AS execution_run WITH (UPDLOCK, HOLDLOCK)
        ON execution_run.run_id = object_run.run_id
    WHERE candidate.candidate_id = @candidate_id
      AND candidate.object_run_id = @object_run_id
      AND candidate.candidate_status = 'PROPOSED'
      AND execution_run.correlation_id = @correlation_id
      AND execution_run.run_status = 'RUNNING';

    IF @environment_id IS NULL
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51031, 'The candidate is not eligible for failure handling.', 1;
    END;

    UPDATE ops.WatermarkCandidate
    SET candidate_status = 'ABANDONED',
        resolved_at_utc = @now,
        resolution_reason = @error_classification
    WHERE candidate_id = @candidate_id;

    UPDATE ops.ObjectRun
    SET object_run_status = 'FAILED',
        extracted_row_count = @extracted_row_count,
        accepted_row_count = @accepted_row_count,
        rejected_row_count = @rejected_row_count,
        error_classification = @error_classification,
        error_summary = LEFT(@error_summary, 2000),
        completed_at_utc = @now
    WHERE object_run_id = @object_run_id;

    IF @is_terminal_run = 1
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
        'WATERMARK_ABANDONED', @actor_identity,
        CONCAT(N'Attempt failed: ', @error_classification), @correlation_id,
        CONVERT(varchar(64), HASHBYTES('SHA2_256', @from_value), 2),
        NULL, @now
    );

    COMMIT TRANSACTION;
END;
GO
