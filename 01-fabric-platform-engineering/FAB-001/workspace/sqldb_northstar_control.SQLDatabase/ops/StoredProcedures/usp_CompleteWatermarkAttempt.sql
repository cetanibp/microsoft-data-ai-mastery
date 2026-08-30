CREATE PROCEDURE [ops].[usp_CompleteWatermarkAttempt]
    @object_run_id uniqueidentifier,
    @candidate_id uniqueidentifier,
    @extracted_row_count bigint,
    @accepted_row_count bigint,
    @rejected_row_count bigint,
    @actor_identity nvarchar(200),
    @correlation_id varchar(100)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    IF @extracted_row_count < 0 OR @accepted_row_count < 0 OR @rejected_row_count < 0
        THROW 51020, 'Row counts cannot be negative.', 1;

    IF @accepted_row_count + @rejected_row_count > @extracted_row_count
        THROW 51021, 'Accepted and rejected counts exceed extracted rows.', 1;

    BEGIN TRANSACTION;

    DECLARE @environment_id uniqueidentifier;
    DECLARE @release_id uniqueidentifier;
    DECLARE @run_id uniqueidentifier;
    DECLARE @ingestion_object_key varchar(150);
    DECLARE @from_value nvarchar(4000);
    DECLARE @to_value nvarchar(4000);
    DECLARE @observed_state_version bigint;
    DECLARE @now datetime2(7) = SYSUTCDATETIME();

    SELECT
        @environment_id = candidate.environment_id,
        @release_id = object_run.release_id,
        @run_id = object_run.run_id,
        @ingestion_object_key = candidate.ingestion_object_key,
        @from_value = candidate.from_value,
        @to_value = candidate.to_value,
        @observed_state_version = candidate.observed_state_version
    FROM ops.WatermarkCandidate AS candidate WITH (UPDLOCK, HOLDLOCK)
    INNER JOIN ops.ObjectRun AS object_run WITH (UPDLOCK, HOLDLOCK)
        ON object_run.object_run_id = candidate.object_run_id
    INNER JOIN ops.ExecutionRun AS execution_run WITH (UPDLOCK, HOLDLOCK)
        ON execution_run.run_id = object_run.run_id
    WHERE candidate.candidate_id = @candidate_id
      AND candidate.object_run_id = @object_run_id
      AND candidate.candidate_status = 'PROPOSED'
      AND object_run.object_run_status IN ('CLAIMED', 'EXTRACTING', 'VALIDATING', 'PUBLISHING')
      AND execution_run.correlation_id = @correlation_id
      AND execution_run.run_status = 'RUNNING';

    IF @environment_id IS NULL
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51022, 'The candidate is not eligible for completion.', 1;
    END;

    UPDATE ops.WatermarkState
    SET committed_value = @to_value,
        state_version = state_version + 1,
        definition_release_id = @release_id,
        committed_object_run_id = @object_run_id,
        committed_at_utc = @now
    WHERE environment_id = @environment_id
      AND ingestion_object_key = @ingestion_object_key
      AND committed_value = @from_value
      AND state_version = @observed_state_version;

    IF @@ROWCOUNT = 0
    BEGIN
        UPDATE ops.WatermarkCandidate
        SET candidate_status = 'ABANDONED',
            resolved_at_utc = @now,
            resolution_reason = N'STALE_STATE_VERSION'
        WHERE candidate_id = @candidate_id;

        UPDATE ops.ObjectRun
        SET object_run_status = 'RECOVERY_REQUIRED',
            extracted_row_count = @extracted_row_count,
            accepted_row_count = @accepted_row_count,
            rejected_row_count = @rejected_row_count,
            error_classification = 'STALE_WATERMARK_CANDIDATE',
            error_summary = N'Target completed but watermark state changed before commit.',
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
            'WATERMARK_ABANDONED', @actor_identity,
            N'Stale state version requires forward recovery.', @correlation_id,
            CONVERT(varchar(64), HASHBYTES('SHA2_256', @from_value), 2),
            NULL, @now
        );

        COMMIT TRANSACTION;
        SELECT 'RECOVERY_REQUIRED' AS completion_status;
        RETURN;
    END;

    UPDATE ops.WatermarkCandidate
    SET candidate_status = 'COMMITTED',
        resolved_at_utc = @now,
        resolution_reason = N'TARGET_ACCEPTED'
    WHERE candidate_id = @candidate_id;

    UPDATE ops.ObjectRun
    SET object_run_status = CASE WHEN @rejected_row_count > 0
                                 THEN 'SUCCEEDED_WITH_WARNINGS' ELSE 'SUCCEEDED' END,
        extracted_row_count = @extracted_row_count,
        accepted_row_count = @accepted_row_count,
        rejected_row_count = @rejected_row_count,
        error_classification = NULL,
        error_summary = NULL,
        completed_at_utc = @now
    WHERE object_run_id = @object_run_id;

    UPDATE ops.ExecutionRun
    SET run_status = CASE WHEN @rejected_row_count > 0
                          THEN 'SUCCEEDED_WITH_WARNINGS' ELSE 'SUCCEEDED' END,
        completed_at_utc = @now
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
        'WATERMARK_COMMITTED', @actor_identity,
        N'Target accepted; fixed boundary committed.', @correlation_id,
        CONVERT(varchar(64), HASHBYTES('SHA2_256', @from_value), 2),
        CONVERT(varchar(64), HASHBYTES('SHA2_256', @to_value), 2), @now
    );

    COMMIT TRANSACTION;
    SELECT CASE WHEN @rejected_row_count > 0
                THEN 'SUCCEEDED_WITH_WARNINGS' ELSE 'SUCCEEDED' END
           AS completion_status;
END;
GO
