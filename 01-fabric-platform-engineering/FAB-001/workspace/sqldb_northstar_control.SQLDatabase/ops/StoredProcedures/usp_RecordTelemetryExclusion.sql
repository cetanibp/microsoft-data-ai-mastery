CREATE PROCEDURE [ops].[usp_RecordTelemetryExclusion]
    @telemetry_exclusion_id UNIQUEIDENTIFIER,
    @environment_id UNIQUEIDENTIFIER,
    @release_id UNIQUEIDENTIFIER,
    @ingestion_object_key VARCHAR(150) = NULL,
    @exclusion_type VARCHAR(30),
    @effective_start_utc DATETIME2(7),
    @effective_end_utc DATETIME2(7),
    @actor_identity NVARCHAR(200),
    @reason NVARCHAR(1000),
    @approval_reference NVARCHAR(300),
    @approved_at_utc DATETIME2(7),
    @created_at_utc DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    IF @effective_start_utc >= @effective_end_utc
        THROW 51000, 'Telemetry exclusion requires a bounded positive interval.', 1;

    IF @approved_at_utc > @effective_start_utc OR @created_at_utc > @effective_start_utc
        THROW 51000, 'Telemetry exclusion must be approved and recorded before it begins.', 1;

    IF NULLIF(LTRIM(RTRIM(@actor_identity)), N'') IS NULL
       OR NULLIF(LTRIM(RTRIM(@reason)), N'') IS NULL
       OR NULLIF(LTRIM(RTRIM(@approval_reference)), N'') IS NULL
        THROW 51000, 'Telemetry exclusion requires actor, reason, and approval evidence.', 1;

    BEGIN TRANSACTION;

    DECLARE @existing_id UNIQUEIDENTIFIER;
    SELECT @existing_id = telemetry_exclusion_id
    FROM ops.TelemetryExclusion WITH (UPDLOCK, HOLDLOCK)
    WHERE environment_id = @environment_id
      AND release_id = @release_id
      AND ((ingestion_object_key = @ingestion_object_key)
           OR (ingestion_object_key IS NULL AND @ingestion_object_key IS NULL))
      AND exclusion_type = @exclusion_type
      AND effective_start_utc = @effective_start_utc
      AND effective_end_utc = @effective_end_utc;

    IF @existing_id IS NOT NULL
    BEGIN
        IF NOT EXISTS
        (
            SELECT 1
            FROM ops.TelemetryExclusion
            WHERE telemetry_exclusion_id = @existing_id
              AND actor_identity = @actor_identity
              AND reason = @reason
              AND approval_reference = @approval_reference
              AND approved_at_utc = @approved_at_utc
        )
        BEGIN
            ROLLBACK TRANSACTION;
            THROW 51000, 'Telemetry exclusion identity changed.', 1;
        END;

        COMMIT TRANSACTION;
        SELECT @existing_id AS telemetry_exclusion_id, CAST(0 AS bit) AS inserted;
        RETURN;
    END;

    INSERT ops.TelemetryExclusion
    (
        telemetry_exclusion_id, environment_id, release_id,
        ingestion_object_key, exclusion_type, effective_start_utc,
        effective_end_utc, actor_identity, reason, approval_reference,
        approved_at_utc, created_at_utc
    )
    VALUES
    (
        @telemetry_exclusion_id, @environment_id, @release_id,
        @ingestion_object_key, @exclusion_type, @effective_start_utc,
        @effective_end_utc, @actor_identity, @reason, @approval_reference,
        @approved_at_utc, @created_at_utc
    );

    COMMIT TRANSACTION;
    SELECT @telemetry_exclusion_id AS telemetry_exclusion_id, CAST(1 AS bit) AS inserted;
END;
GO
