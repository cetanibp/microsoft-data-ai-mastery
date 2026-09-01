CREATE PROCEDURE [ops].[usp_ResolveQualityPolicy]
    @object_run_id UNIQUEIDENTIFIER
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        object_run.environment_id,
        object_run.release_id,
        object_run.run_id,
        object_run.object_run_id,
        object_run.ingestion_object_key,
        object_run.input_boundary_hash,
        object_policy.evaluation_order,
        policy.quality_policy_key,
        policy.policy_version,
        policy.enforcement_level,
        policy.quarantine_required,
        policy.contract_reference
    FROM ops.ObjectRun AS object_run
    INNER JOIN ctrl.ObjectQualityPolicy AS object_policy
        ON object_policy.release_id = object_run.release_id
       AND object_policy.ingestion_object_key = object_run.ingestion_object_key
    INNER JOIN ctrl.QualityPolicy AS policy
        ON policy.release_id = object_policy.release_id
       AND policy.quality_policy_key = object_policy.quality_policy_key
    WHERE object_run.object_run_id = @object_run_id
      AND object_run.object_run_status IN ('CLAIMED', 'EXTRACTING', 'VALIDATING', 'PUBLISHING')
    ORDER BY object_policy.evaluation_order;
END;
GO
