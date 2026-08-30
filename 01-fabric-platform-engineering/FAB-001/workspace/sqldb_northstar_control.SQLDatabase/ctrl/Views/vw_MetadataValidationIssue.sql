
CREATE   VIEW ctrl.vw_MetadataValidationIssue
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

