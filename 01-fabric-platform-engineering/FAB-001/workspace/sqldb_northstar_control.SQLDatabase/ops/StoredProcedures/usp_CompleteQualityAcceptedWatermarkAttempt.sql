CREATE PROCEDURE [ops].[usp_CompleteQualityAcceptedWatermarkAttempt]
    @object_run_id UNIQUEIDENTIFIER,
    @candidate_id UNIQUEIDENTIFIER,
    @extracted_row_count BIGINT,
    @accepted_row_count BIGINT,
    @rejected_row_count BIGINT,
    @actor_identity NVARCHAR(200),
    @correlation_id VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    BEGIN TRANSACTION;

    IF NOT EXISTS
    (
        SELECT 1
        FROM ops.QualityDecision WITH (UPDLOCK, HOLDLOCK)
        WHERE object_run_id = @object_run_id
          AND watermark_commit_eligible = 1
          AND decision_status IN ('ACCEPTED', 'ACCEPTED_WITH_WARNING')
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51130, 'An accepted quality decision is required before watermark commit.', 1;
    END;

    EXEC ops.usp_CompleteWatermarkAttempt
        @object_run_id = @object_run_id,
        @candidate_id = @candidate_id,
        @extracted_row_count = @extracted_row_count,
        @accepted_row_count = @accepted_row_count,
        @rejected_row_count = @rejected_row_count,
        @actor_identity = @actor_identity,
        @correlation_id = @correlation_id;

    COMMIT TRANSACTION;
END;
GO
