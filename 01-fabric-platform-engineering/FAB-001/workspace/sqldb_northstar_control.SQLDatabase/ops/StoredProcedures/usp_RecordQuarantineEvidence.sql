CREATE PROCEDURE [ops].[usp_RecordQuarantineEvidence]
    @quarantine_id VARCHAR(64),
    @object_run_id UNIQUEIDENTIFIER,
    @release_id UNIQUEIDENTIFIER,
    @quality_policy_key VARCHAR(100),
    @quality_rule_key VARCHAR(100),
    @reason_code VARCHAR(50),
    @source_record_identity_hash VARCHAR(64),
    @input_boundary_hash VARCHAR(64),
    @quarantined_at_utc DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    IF NOT EXISTS
    (
        SELECT 1
        FROM ops.ObjectRun AS object_run
        INNER JOIN ctrl.ObjectQualityPolicy AS object_policy
            ON object_policy.release_id = object_run.release_id
           AND object_policy.ingestion_object_key = object_run.ingestion_object_key
        WHERE object_run.object_run_id = @object_run_id
          AND object_run.release_id = @release_id
          AND object_run.input_boundary_hash = @input_boundary_hash
          AND object_policy.quality_policy_key = @quality_policy_key
    )
        THROW 51110, 'Quarantine evidence does not match the active object run.', 1;

    BEGIN TRANSACTION;

    UPDATE ops.QuarantineEvidence
    SET release_id = @release_id,
        quality_policy_key = @quality_policy_key,
        quality_rule_key = @quality_rule_key,
        reason_code = @reason_code,
        source_record_identity_hash = @source_record_identity_hash,
        input_boundary_hash = @input_boundary_hash,
        quarantined_at_utc = @quarantined_at_utc
    WHERE quarantine_id = @quarantine_id
      AND object_run_id = @object_run_id;

    IF @@ROWCOUNT = 0
        INSERT ops.QuarantineEvidence
        (
            quarantine_id, object_run_id, release_id, quality_policy_key,
            quality_rule_key, reason_code, source_record_identity_hash,
            input_boundary_hash, quarantined_at_utc
        )
        VALUES
        (
            @quarantine_id, @object_run_id, @release_id, @quality_policy_key,
            @quality_rule_key, @reason_code, @source_record_identity_hash,
            @input_boundary_hash, @quarantined_at_utc
        );

    COMMIT TRANSACTION;
END;
GO
