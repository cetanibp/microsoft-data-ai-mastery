CREATE PROCEDURE [ops].[usp_BeginWatermarkAttempt]
    @run_id uniqueidentifier,
    @object_run_id uniqueidentifier,
    @candidate_id uniqueidentifier,
    @environment_code varchar(30),
    @release_id uniqueidentifier,
    @ingestion_object_key varchar(150),
    @attempt_number smallint,
    @trigger_type varchar(20),
    @trigger_reference nvarchar(300) = NULL,
    @correlation_id varchar(100),
    @requested_scope nvarchar(1000),
    @configuration_hash varchar(64),
    @input_boundary_hash varchar(64),
    @logical_value_type varchar(20),
    @from_value nvarchar(4000),
    @to_value nvarchar(4000),
    @observed_state_version bigint,
    @actor_identity nvarchar(200)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    IF @from_value = @to_value
        THROW 51010, 'A no-op boundary must not create a watermark candidate.', 1;

    IF @attempt_number NOT BETWEEN 1 AND 100
        THROW 51011, 'Attempt number is outside the supported range.', 1;

    DECLARE @environment_id uniqueidentifier;
    DECLARE @active_release_id uniqueidentifier;
    DECLARE @initial_value nvarchar(4000);
    DECLARE @configured_type varchar(20);
    DECLARE @now datetime2(7) = SYSUTCDATETIME();

    SELECT
        @environment_id = environment_id,
        @active_release_id = release_id,
        @initial_value = initial_value_literal,
        @configured_type = watermark_data_type
    FROM ctrl.vw_ActiveIngestionConfiguration
    WHERE environment_code = @environment_code
      AND ingestion_object_key = @ingestion_object_key
      AND strategy_type = 'WATERMARK';

    IF @environment_id IS NULL OR @active_release_id <> @release_id
        THROW 51012, 'The requested object does not match the active release.', 1;

    IF @configured_type <> @logical_value_type
        THROW 51013, 'The requested watermark type does not match metadata.', 1;

    BEGIN TRANSACTION;

    DECLARE @current_value nvarchar(4000);
    DECLARE @current_version bigint;

    SELECT
        @current_value = committed_value,
        @current_version = state_version
    FROM ops.WatermarkState WITH (UPDLOCK, HOLDLOCK)
    WHERE environment_id = @environment_id
      AND ingestion_object_key = @ingestion_object_key;

    IF @current_value IS NULL
    BEGIN
        IF @observed_state_version <> 0 OR @from_value <> @initial_value
        BEGIN
            ROLLBACK TRANSACTION;
            THROW 51014, 'Initial watermark state does not match the metadata contract.', 1;
        END;

        INSERT ops.WatermarkState
        (
            environment_id,
            ingestion_object_key,
            definition_release_id,
            logical_value_type,
            committed_value,
            state_version,
            committed_object_run_id,
            committed_at_utc
        )
        VALUES
        (
            @environment_id,
            @ingestion_object_key,
            @release_id,
            @logical_value_type,
            @from_value,
            0,
            NULL,
            @now
        );

        SET @current_value = @from_value;
        SET @current_version = 0;
    END;

    IF @current_version <> @observed_state_version OR @current_value <> @from_value
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51015, 'Watermark state changed before the attempt was claimed.', 1;
    END;

    IF NOT EXISTS (SELECT 1 FROM ops.ExecutionRun WHERE run_id = @run_id)
    BEGIN
        INSERT ops.ExecutionRun
        (
            run_id,
            environment_id,
            release_id,
            trigger_type,
            trigger_reference,
            correlation_id,
            requested_scope,
            configuration_hash,
            run_status,
            started_at_utc,
            completed_at_utc
        )
        VALUES
        (
            @run_id,
            @environment_id,
            @release_id,
            @trigger_type,
            @trigger_reference,
            @correlation_id,
            @requested_scope,
            @configuration_hash,
            'RUNNING',
            @now,
            NULL
        );

        INSERT audit.StateEvent
        (
            state_event_id,
            environment_id,
            release_id,
            run_id,
            object_run_id,
            event_type,
            actor_identity,
            reason,
            correlation_id,
            before_hash,
            after_hash,
            occurred_at_utc
        )
        VALUES
        (
            NEWID(), @environment_id, @release_id, @run_id, NULL,
            'RUN_REQUESTED', @actor_identity,
            N'Watermark ingestion run requested.', @correlation_id,
            NULL, @configuration_hash, @now
        );
    END;
    ELSE IF NOT EXISTS
    (
        SELECT 1
        FROM ops.ExecutionRun WITH (UPDLOCK, HOLDLOCK)
        WHERE run_id = @run_id
          AND environment_id = @environment_id
          AND release_id = @release_id
          AND correlation_id = @correlation_id
          AND run_status = 'RUNNING'
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 51016, 'Existing run is not eligible for another attempt.', 1;
    END;

    INSERT ops.ObjectRun
    (
        object_run_id,
        run_id,
        environment_id,
        release_id,
        ingestion_object_key,
        attempt_number,
        object_run_status,
        input_boundary_hash,
        started_at_utc,
        completed_at_utc
    )
    VALUES
    (
        @object_run_id, @run_id, @environment_id, @release_id,
        @ingestion_object_key, @attempt_number, 'CLAIMED',
        @input_boundary_hash, @now, NULL
    );

    INSERT ops.WatermarkCandidate
    (
        candidate_id,
        object_run_id,
        environment_id,
        ingestion_object_key,
        logical_value_type,
        from_value,
        to_value,
        observed_state_version,
        candidate_status,
        proposed_at_utc,
        resolved_at_utc,
        resolution_reason
    )
    VALUES
    (
        @candidate_id, @object_run_id, @environment_id,
        @ingestion_object_key, @logical_value_type,
        @from_value, @to_value, @observed_state_version,
        'PROPOSED', @now, NULL, NULL
    );

    INSERT audit.StateEvent
    (
        state_event_id, environment_id, release_id, run_id, object_run_id,
        event_type, actor_identity, reason, correlation_id,
        before_hash, after_hash, occurred_at_utc
    )
    VALUES
        (NEWID(), @environment_id, @release_id, @run_id, @object_run_id,
         'OBJECT_CLAIMED', @actor_identity, N'Object attempt claimed.',
         @correlation_id, NULL, @input_boundary_hash, @now),
        (NEWID(), @environment_id, @release_id, @run_id, @object_run_id,
         'WATERMARK_PROPOSED', @actor_identity, N'Fixed input boundary proposed.',
         @correlation_id,
         CONVERT(varchar(64), HASHBYTES('SHA2_256', @from_value), 2),
         CONVERT(varchar(64), HASHBYTES('SHA2_256', @to_value), 2), @now);

    COMMIT TRANSACTION;

    SELECT @run_id AS run_id, @object_run_id AS object_run_id,
           @candidate_id AS candidate_id, @correlation_id AS correlation_id;
END;
GO
