/*
FAB-001 — Runtime-resolution and metadata-validation views
Target: SQL Database in Microsoft Fabric
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

CREATE OR ALTER VIEW ctrl.vw_ActiveIngestionConfiguration
AS
SELECT
    e.environment_id,
    e.environment_code,
    mr.release_id,
    mr.release_version,
    mr.content_hash AS release_content_hash,
    io.ingestion_object_key,
    io.display_name,
    io.domain_key,
    io.is_required,
    ss.source_system_key,
    ss.source_type,
    ss.data_classification AS source_system_classification,
    sec.connection_reference_key,
    sec.landing_zone_key,
    sec.max_connection_concurrency,
    so.source_object_key,
    so.namespace_name AS source_namespace,
    so.object_name AS source_object_name,
    so.object_type AS source_object_type,
    so.business_key_contract,
    so.schema_drift_policy,
    so.data_classification AS source_object_classification,
    tgt.target_object_key,
    tgt.target_layer,
    tgt.store_alias AS target_store_alias,
    tgt.namespace_name AS target_namespace,
    tgt.object_name AS target_object_name,
    tgt.write_disposition,
    tgt.publication_boundary,
    lp.load_policy_key,
    lp.strategy_type,
    lp.duplicate_behavior,
    lp.delete_behavior,
    lp.schema_behavior,
    lp.idempotency_contract,
    wp.watermark_policy_key,
    wp.column_name AS watermark_column_name,
    wp.logical_data_type AS watermark_data_type,
    wp.comparison_operator AS watermark_comparison_operator,
    wp.overlap_amount AS watermark_overlap_amount,
    wp.overlap_unit AS watermark_overlap_unit,
    wp.initial_value_policy,
    wp.initial_value_literal,
    wp.upper_bound_mode,
    wp.late_arrival_behavior,
    ep.execution_policy_key,
    ep.timeout_minutes,
    ep.max_retries,
    ep.retry_delay_seconds,
    COALESCE(oec.priority_override, ep.default_priority) AS effective_priority,
    ep.concurrency_group,
    ep.max_parallelism,
    ep.recovery_mode,
    oec.routing_alias
FROM ctrl.Environment AS e
INNER JOIN ctrl.EnvironmentRelease AS er
    ON er.environment_id = e.environment_id
INNER JOIN ctrl.MetadataRelease AS mr
    ON mr.release_id = er.release_id
INNER JOIN ctrl.ObjectEnvironmentConfig AS oec
    ON oec.environment_id = e.environment_id
   AND oec.release_id = mr.release_id
   AND oec.is_enabled = 1
INNER JOIN ctrl.IngestionObject AS io
    ON io.release_id = oec.release_id
   AND io.ingestion_object_key = oec.ingestion_object_key
INNER JOIN ctrl.SourceObject AS so
    ON so.release_id = io.release_id
   AND so.source_object_key = io.source_object_key
INNER JOIN ctrl.SourceSystem AS ss
    ON ss.release_id = so.release_id
   AND ss.source_system_key = so.source_system_key
INNER JOIN ctrl.SourceEnvironmentConfig AS sec
    ON sec.release_id = ss.release_id
   AND sec.environment_id = e.environment_id
   AND sec.source_system_key = ss.source_system_key
   AND sec.is_enabled = 1
INNER JOIN ctrl.TargetObject AS tgt
    ON tgt.release_id = io.release_id
   AND tgt.target_object_key = io.target_object_key
INNER JOIN ctrl.LoadPolicy AS lp
    ON lp.release_id = io.release_id
   AND lp.load_policy_key = io.load_policy_key
LEFT JOIN ctrl.WatermarkPolicy AS wp
    ON wp.release_id = lp.release_id
   AND wp.watermark_policy_key = lp.watermark_policy_key
INNER JOIN ctrl.ExecutionPolicy AS ep
    ON ep.release_id = io.release_id
   AND ep.execution_policy_key = io.execution_policy_key
WHERE mr.release_status IN ('APPROVED', 'ACTIVE');
GO

CREATE OR ALTER VIEW ctrl.vw_MetadataValidationIssue
AS
    SELECT
        mr.release_id,
        CAST('RELEASE_NOT_APPROVABLE' AS varchar(60)) AS issue_code,
        CAST('ERROR' AS varchar(10)) AS severity,
        CAST('MetadataRelease' AS varchar(50)) AS entity_type,
        mr.release_version AS entity_key,
        CAST('An environment points to a release that is not APPROVED or ACTIVE.'
             AS nvarchar(1000)) AS issue_message
    FROM ctrl.EnvironmentRelease AS er
    INNER JOIN ctrl.MetadataRelease AS mr
        ON mr.release_id = er.release_id
    WHERE mr.release_status NOT IN ('APPROVED', 'ACTIVE')

    UNION ALL

    SELECT
        lp.release_id,
        'PARAMETER_STRATEGY_MISMATCH',
        'ERROR',
        'LoadPolicyParameter',
        CONCAT(lp.load_policy_key, '/', lpp.parameter_key),
        'The parameter strategy does not match its load policy strategy.'
    FROM ctrl.LoadPolicyParameter AS lpp
    INNER JOIN ctrl.LoadPolicy AS lp
        ON lp.release_id = lpp.release_id
       AND lp.load_policy_key = lpp.load_policy_key
    WHERE lpp.strategy_type <> lp.strategy_type

    UNION ALL

    SELECT
        lpp.release_id,
        'PARAMETER_TYPE_MISMATCH',
        'ERROR',
        'LoadPolicyParameter',
        CONCAT(lpp.load_policy_key, '/', lpp.parameter_key),
        'The supplied value type does not match the allowlisted parameter type.'
    FROM ctrl.LoadPolicyParameter AS lpp
    INNER JOIN ctrl.StrategyParameterDefinition AS spd
        ON spd.strategy_type = lpp.strategy_type
       AND spd.parameter_key = lpp.parameter_key
    WHERE lpp.value_type <> spd.value_type

    UNION ALL

    SELECT
        lp.release_id,
        'REQUIRED_PARAMETER_MISSING',
        'ERROR',
        'LoadPolicy',
        lp.load_policy_key,
        CONCAT('Required parameter is missing: ', spd.parameter_key)
    FROM ctrl.LoadPolicy AS lp
    INNER JOIN ctrl.StrategyParameterDefinition AS spd
        ON spd.strategy_type = lp.strategy_type
       AND spd.is_required = 1
    LEFT JOIN ctrl.LoadPolicyParameter AS lpp
        ON lpp.release_id = lp.release_id
       AND lpp.load_policy_key = lp.load_policy_key
       AND lpp.strategy_type = spd.strategy_type
       AND lpp.parameter_key = spd.parameter_key
    WHERE lpp.parameter_key IS NULL

    UNION ALL

    SELECT
        oec.release_id,
        'SOURCE_ENVIRONMENT_CONFIG_MISSING',
        'ERROR',
        'IngestionObject',
        oec.ingestion_object_key,
        CONCAT('Enabled object has no enabled source configuration for environment ',
               e.environment_code, '.')
    FROM ctrl.ObjectEnvironmentConfig AS oec
    INNER JOIN ctrl.Environment AS e
        ON e.environment_id = oec.environment_id
    INNER JOIN ctrl.IngestionObject AS io
        ON io.release_id = oec.release_id
       AND io.ingestion_object_key = oec.ingestion_object_key
    INNER JOIN ctrl.SourceObject AS so
        ON so.release_id = io.release_id
       AND so.source_object_key = io.source_object_key
    LEFT JOIN ctrl.SourceEnvironmentConfig AS sec
        ON sec.release_id = so.release_id
       AND sec.environment_id = oec.environment_id
       AND sec.source_system_key = so.source_system_key
       AND sec.is_enabled = 1
    WHERE oec.is_enabled = 1
      AND sec.source_system_key IS NULL

    UNION ALL

    SELECT
        oec.release_id,
        'SCHEDULE_MISSING',
        'ERROR',
        'IngestionObject',
        oec.ingestion_object_key,
        'Enabled object has no schedule.'
    FROM ctrl.ObjectEnvironmentConfig AS oec
    LEFT JOIN ctrl.ObjectSchedule AS os
        ON os.release_id = oec.release_id
       AND os.ingestion_object_key = oec.ingestion_object_key
    WHERE oec.is_enabled = 1
      AND os.schedule_key IS NULL

    UNION ALL

    SELECT
        oec.release_id,
        'PRODUCTION_SLO_MISSING',
        'ERROR',
        'IngestionObject',
        oec.ingestion_object_key,
        'Production-enabled object has no SLO.'
    FROM ctrl.ObjectEnvironmentConfig AS oec
    INNER JOIN ctrl.Environment AS e
        ON e.environment_id = oec.environment_id
       AND e.is_production = 1
    LEFT JOIN ctrl.ObjectSlo AS os
        ON os.release_id = oec.release_id
       AND os.ingestion_object_key = oec.ingestion_object_key
    WHERE oec.is_enabled = 1
      AND os.slo_key IS NULL

    UNION ALL

    SELECT
        oec.release_id,
        'PRODUCTION_OWNERSHIP_MISSING',
        'ERROR',
        'IngestionObject',
        oec.ingestion_object_key,
        CONCAT('Production-enabled object lacks required ownership role: ', roles.ownership_role)
    FROM ctrl.ObjectEnvironmentConfig AS oec
    INNER JOIN ctrl.Environment AS e
        ON e.environment_id = oec.environment_id
       AND e.is_production = 1
    CROSS JOIN
    (
        SELECT CAST('ENGINEERING' AS varchar(30)) AS ownership_role
        UNION ALL SELECT 'SOURCE_STEWARD'
        UNION ALL SELECT 'OPERATIONS'
    ) AS roles
    LEFT JOIN ctrl.ObjectOwnership AS oo
        ON oo.release_id = oec.release_id
       AND oo.ingestion_object_key = oec.ingestion_object_key
       AND oo.ownership_role = roles.ownership_role
    WHERE oec.is_enabled = 1
      AND oo.owner_group_key IS NULL

    UNION ALL

    SELECT
        od.release_id,
        'OPTIONAL_DEPENDENCY_INCONSISTENT',
        'ERROR',
        'ObjectDependency',
        CONCAT(od.predecessor_object_key, '->', od.successor_object_key),
        'OPTIONAL dependency condition and is_optional flag must agree.'
    FROM ctrl.ObjectDependency AS od
    WHERE
        (od.dependency_condition = 'OPTIONAL' AND od.is_optional = 0)
        OR
        (od.dependency_condition <> 'OPTIONAL' AND od.is_optional = 1);
GO

CREATE OR ALTER VIEW ctrl.vw_ObjectDependencyEdge
AS
SELECT
    od.release_id,
    od.predecessor_object_key,
    predecessor.display_name AS predecessor_display_name,
    od.successor_object_key,
    successor.display_name AS successor_display_name,
    od.dependency_condition,
    od.is_optional
FROM ctrl.ObjectDependency AS od
INNER JOIN ctrl.IngestionObject AS predecessor
    ON predecessor.release_id = od.release_id
   AND predecessor.ingestion_object_key = od.predecessor_object_key
INNER JOIN ctrl.IngestionObject AS successor
    ON successor.release_id = od.release_id
   AND successor.ingestion_object_key = od.successor_object_key;
GO
