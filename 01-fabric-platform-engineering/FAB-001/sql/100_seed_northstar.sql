/*
FAB-001 — Synthetic Northstar metadata release 1.0.0
Target: SQL Database in Microsoft Fabric

All names, values, and volumes are fictional. Logical connection and routing
keys are resolved by the OPS-001 environment boundary. This script contains no
endpoints, workspace identifiers, credentials, patient data, or proprietary
metadata.

The release seed is idempotent as a bundle: if release 1.0.0 exists, no rows
are changed. Approved releases are immutable; create a new release to change
definitions.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

DECLARE @release_id uniqueidentifier =
    '20000000-0000-0000-0000-000000000001';
DECLARE @development_id uniqueidentifier =
    '10000000-0000-0000-0000-000000000001';
DECLARE @test_id uniqueidentifier =
    '10000000-0000-0000-0000-000000000002';
DECLARE @production_id uniqueidentifier =
    '10000000-0000-0000-0000-000000000003';

BEGIN TRANSACTION;

IF NOT EXISTS
(
    SELECT 1
    FROM ctrl.MetadataRelease
    WHERE release_version = '1.0.0'
)
BEGIN
    INSERT ctrl.Environment
        (environment_id, environment_code, environment_name, is_production)
    SELECT *
    FROM
    (
        VALUES
            (@development_id, 'development', N'Development', CAST(0 AS bit)),
            (@test_id,        'test',        N'Test',        CAST(0 AS bit)),
            (@production_id,  'production',  N'Production',  CAST(1 AS bit))
    ) AS seed(environment_id, environment_code, environment_name, is_production)
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM ctrl.Environment AS existing
        WHERE existing.environment_id = seed.environment_id
           OR existing.environment_code = seed.environment_code
    );

    INSERT ctrl.MetadataRelease
    (
        release_id,
        release_version,
        release_status,
        content_hash,
        source_commit_sha,
        change_reason,
        created_by,
        created_at_utc,
        approved_by,
        approved_at_utc
    )
    VALUES
    (
        @release_id,
        '1.0.0',
        'APPROVED',
        CONVERT(varchar(64),
            HASHBYTES('SHA2_256', N'northstar-fab001-release-1.0.0'), 2),
        '0f0244cc1117643e557f490fbf5c7213ad6fd08e',
        N'Initial synthetic Northstar ingestion control-plane release.',
        N'github:cetanibp',
        '2026-08-29T00:00:00Z',
        N'github:cetanibp',
        '2026-08-29T00:00:00Z'
    );

    INSERT ctrl.OwnerGroup
        (release_id, owner_group_key, display_name, routing_alias)
    VALUES
        (@release_id, 'platform-engineering', N'Platform Engineering',
            'route-platform-engineering'),
        (@release_id, 'data-operations', N'Data Operations',
            'route-data-operations'),
        (@release_id, 'clinical-stewards', N'Clinical Data Stewards',
            'route-clinical-stewards'),
        (@release_id, 'pharmacy-stewards', N'Pharmacy Data Stewards',
            'route-pharmacy-stewards'),
        (@release_id, 'finance-stewards', N'Finance Data Stewards',
            'route-finance-stewards'),
        (@release_id, 'facilities-stewards', N'Facilities Data Stewards',
            'route-facilities-stewards'),
        (@release_id, 'clinical-data-product', N'Clinical Data Product',
            'route-clinical-data-product'),
        (@release_id, 'operations-data-product', N'Operations Data Product',
            'route-operations-data-product');

    INSERT ctrl.StrategyParameterDefinition
    (
        strategy_type,
        parameter_key,
        value_type,
        is_required,
        minimum_value,
        maximum_value,
        allowed_values,
        description
    )
    SELECT *
    FROM
    (
        VALUES
            ('FULL', 'batch_size', 'INTEGER', CAST(1 AS bit),
                CAST(1 AS decimal(38, 9)), CAST(1000000 AS decimal(38, 9)),
                NULL, N'Maximum rows handled in a processing batch.'),
            ('WATERMARK', 'batch_size', 'INTEGER', CAST(1 AS bit),
                CAST(1 AS decimal(38, 9)), CAST(1000000 AS decimal(38, 9)),
                NULL, N'Maximum rows handled in a processing batch.'),
            ('APPEND', 'batch_size', 'INTEGER', CAST(1 AS bit),
                CAST(1 AS decimal(38, 9)), CAST(1000000 AS decimal(38, 9)),
                NULL, N'Maximum events handled in a processing batch.'),
            ('SNAPSHOT', 'batch_size', 'INTEGER', CAST(1 AS bit),
                CAST(1 AS decimal(38, 9)), CAST(1000000 AS decimal(38, 9)),
                NULL, N'Maximum rows handled in a processing batch.')
    ) AS seed
    (
        strategy_type,
        parameter_key,
        value_type,
        is_required,
        minimum_value,
        maximum_value,
        allowed_values,
        description
    )
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM ctrl.StrategyParameterDefinition AS existing
        WHERE existing.strategy_type = seed.strategy_type
          AND existing.parameter_key = seed.parameter_key
    );

    INSERT ctrl.WatermarkPolicy
    (
        release_id,
        watermark_policy_key,
        column_name,
        logical_data_type,
        comparison_operator,
        overlap_amount,
        overlap_unit,
        initial_value_policy,
        initial_value_literal,
        upper_bound_mode,
        late_arrival_behavior
    )
    VALUES
        (
            @release_id,
            'wm-updated-at-5m-overlap',
            N'updated_at_utc',
            'DATETIME2',
            '>',
            5,
            'MINUTE',
            'EXPLICIT',
            N'2026-01-01T00:00:00Z',
            'SOURCE_MAX_AT_START',
            'OVERLAP_AND_DEDUPLICATE'
        ),
        (
            @release_id,
            'wm-order-sequence',
            N'order_sequence',
            'BIGINT',
            '>',
            0,
            NULL,
            'EXPLICIT',
            N'0',
            'SOURCE_MAX_AT_START',
            'NOT_SUPPORTED'
        );

    INSERT ctrl.LoadPolicy
    (
        release_id,
        load_policy_key,
        strategy_type,
        watermark_policy_key,
        duplicate_behavior,
        delete_behavior,
        schema_behavior,
        idempotency_contract
    )
    VALUES
        (
            @release_id,
            'full-reference-replace',
            'FULL',
            NULL,
            'DEDUPLICATE_BY_KEY',
            'SNAPSHOT_RECONCILE',
            'FAIL',
            N'Replace the accepted reference snapshot; rerunning the same snapshot produces the same target state.'
        ),
        (
            @release_id,
            'watermark-timestamp-merge',
            'WATERMARK',
            'wm-updated-at-5m-overlap',
            'UPSERT_BY_KEY',
            'SOFT_DELETE',
            'QUARANTINE',
            N'Merge by the declared business key and source update timestamp; overlap is deduplicated.'
        ),
        (
            @release_id,
            'watermark-sequence-merge',
            'WATERMARK',
            'wm-order-sequence',
            'UPSERT_BY_KEY',
            'IGNORE',
            'ROUTE_FOR_REVIEW',
            N'Merge by order identifier and monotonically increasing source sequence.'
        ),
        (
            @release_id,
            'append-event-identity',
            'APPEND',
            NULL,
            'IGNORE',
            'IGNORE',
            'QUARANTINE',
            N'Append once by immutable event identifier; repeated events are ignored.'
        ),
        (
            @release_id,
            'daily-effective-snapshot',
            'SNAPSHOT',
            NULL,
            'DEDUPLICATE_BY_KEY',
            'SNAPSHOT_RECONCILE',
            'FAIL',
            N'Write one immutable snapshot per effective date; repeated snapshots replace that date only.'
        );

    INSERT ctrl.LoadPolicyParameter
    (
        release_id,
        load_policy_key,
        strategy_type,
        parameter_key,
        value_type,
        value_integer
    )
    VALUES
        (@release_id, 'full-reference-replace',
            'FULL', 'batch_size', 'INTEGER', 100000),
        (@release_id, 'watermark-timestamp-merge',
            'WATERMARK', 'batch_size', 'INTEGER', 250000),
        (@release_id, 'watermark-sequence-merge',
            'WATERMARK', 'batch_size', 'INTEGER', 250000),
        (@release_id, 'append-event-identity',
            'APPEND', 'batch_size', 'INTEGER', 50000),
        (@release_id, 'daily-effective-snapshot',
            'SNAPSHOT', 'batch_size', 'INTEGER', 100000);

    INSERT ctrl.ExecutionPolicy
    (
        release_id,
        execution_policy_key,
        timeout_minutes,
        max_retries,
        retry_delay_seconds,
        default_priority,
        concurrency_group,
        max_parallelism,
        recovery_mode
    )
    VALUES
        (@release_id, 'standard-batch', 120, 2, 300, 50,
            'standard-batch', 10, 'RESTART_SAFE'),
        (@release_id, 'critical-incremental', 60, 3, 120, 90,
            'critical-source', 5, 'REPLAY_RANGE'),
        (@release_id, 'low-latency-event', 15, 3, 30, 95,
            'event-ingestion', 20, 'REPLAY_RANGE'),
        (@release_id, 'daily-snapshot', 180, 1, 600, 40,
            'snapshot-loads', 4, 'FORWARD_RECOVERY');

    INSERT ctrl.Schedule
    (
        release_id,
        schedule_key,
        schedule_type,
        iana_time_zone,
        trigger_alias,
        daily_local_start,
        eligibility_window_min,
        interval_minutes,
        event_alias,
        is_catchup_enabled
    )
    VALUES
        (
            @release_id, 'daily-0100-pacific', 'DAILY',
            'America/Los_Angeles', 'trigger-daily-batch',
            '01:00:00', 120, NULL, NULL, 1
        ),
        (
            @release_id, 'interval-15-minute', 'INTERVAL',
            'Etc/UTC', 'trigger-quarter-hour',
            NULL, NULL, 15, NULL, 1
        ),
        (
            @release_id, 'facility-event-arrival', 'EVENT',
            'Etc/UTC', 'trigger-facility-event',
            NULL, NULL, NULL, 'event-facility-status', 0
        );

    INSERT ctrl.SloDefinition
    (
        release_id,
        slo_key,
        metric_type,
        comparison_operator,
        target_value,
        target_unit,
        evaluation_window,
        severity,
        breach_policy
    )
    VALUES
        (@release_id, 'freshness-critical-15m', 'FRESHNESS',
            '<=', 15, 'MINUTES', 'PER_RUN', 'CRITICAL', 'ALERT'),
        (@release_id, 'freshness-batch-by-0600', 'FRESHNESS',
            '<=', 5, 'HOURS', 'DAILY', 'CRITICAL', 'ESCALATE'),
        (@release_id, 'reliability-monthly-99_5', 'RELIABILITY',
            '>=', 99.5, 'PERCENT', 'MONTHLY', 'CRITICAL', 'ESCALATE'),
        (@release_id, 'duration-standard-120m', 'DURATION',
            '<=', 120, 'MINUTES', 'PER_RUN', 'WARNING', 'ALERT'),
        (@release_id, 'quality-critical-100pct', 'QUALITY',
            '>=', 100, 'PERCENT', 'PER_RUN', 'CRITICAL', 'BLOCK_PUBLICATION');

    INSERT ctrl.QualityPolicy
    (
        release_id,
        quality_policy_key,
        policy_version,
        enforcement_level,
        quarantine_required,
        contract_reference
    )
    VALUES
        (@release_id, 'critical-keys-and-counts', '1.0.0',
            'BLOCK', 1, N'quality/contracts/critical-keys-and-counts'),
        (@release_id, 'reference-count-warning', '1.0.0',
            'WARN', 0, N'quality/contracts/reference-count-warning');

    INSERT ctrl.SourceSystem
    (
        release_id,
        source_system_key,
        source_system_name,
        domain_key,
        source_type,
        default_connection_key,
        data_classification
    )
    VALUES
        (@release_id, 'enterprise-ehr', N'Northstar Enterprise EHR',
            'clinical', 'SQL_DATABASE', 'connection-ehr-reader', 'RESTRICTED'),
        (@release_id, 'pharmacy-platform', N'Northstar Pharmacy Platform',
            'pharmacy', 'ORACLE_DATABASE', 'connection-pharmacy-reader', 'RESTRICTED'),
        (@release_id, 'facility-reference-api', N'Northstar Facility Reference',
            'enterprise-reference', 'REST_API', 'connection-facility-api', 'INTERNAL'),
        (@release_id, 'facility-event-stream', N'Northstar Facility Event Stream',
            'operations', 'EVENT_STREAM', 'connection-facility-events', 'CONFIDENTIAL'),
        (@release_id, 'finance-file-exchange', N'Northstar Finance File Exchange',
            'finance', 'FILE', 'connection-finance-files', 'CONFIDENTIAL');

    INSERT ctrl.SourceEnvironmentConfig
    (
        release_id,
        environment_id,
        source_system_key,
        connection_reference_key,
        landing_zone_key,
        max_connection_concurrency,
        is_enabled
    )
    SELECT
        @release_id,
        env.environment_id,
        src.source_system_key,
        CONCAT(src.connection_key_prefix, '-', env.environment_code),
        CONCAT(src.landing_key_prefix, '-', env.environment_code),
        CASE env.environment_code
            WHEN 'development' THEN 2
            WHEN 'test' THEN 4
            WHEN 'production' THEN 8
        END,
        CAST(1 AS bit)
    FROM
    (
        VALUES
            (@development_id, 'development'),
            (@test_id, 'test'),
            (@production_id, 'production')
    ) AS env(environment_id, environment_code)
    CROSS JOIN
    (
        VALUES
            ('enterprise-ehr', 'connection-ehr-reader', 'landing-clinical'),
            ('pharmacy-platform', 'connection-pharmacy-reader', 'landing-pharmacy'),
            ('facility-reference-api', 'connection-facility-api', 'landing-reference'),
            ('facility-event-stream', 'connection-facility-events', 'landing-operations'),
            ('finance-file-exchange', 'connection-finance-files', 'landing-finance')
    ) AS src(source_system_key, connection_key_prefix, landing_key_prefix);

    INSERT ctrl.SourceObject
    (
        release_id,
        source_object_key,
        source_system_key,
        namespace_name,
        object_name,
        object_type,
        business_key_contract,
        schema_drift_policy,
        data_classification
    )
    VALUES
        (@release_id, 'facility-reference', 'facility-reference-api',
            N'v1', N'facilities', 'QUERY',
            N'facility_id', 'FAIL', 'INTERNAL'),
        (@release_id, 'clinical-encounter', 'enterprise-ehr',
            N'clinical', N'encounter', 'TABLE',
            N'encounter_id', 'QUARANTINE', 'RESTRICTED'),
        (@release_id, 'pharmacy-order', 'pharmacy-platform',
            N'pharmacy', N'orders', 'TABLE',
            N'order_id', 'ROUTE_FOR_REVIEW', 'RESTRICTED'),
        (@release_id, 'facility-status-event', 'facility-event-stream',
            N'operations', N'facility_status', 'EVENT',
            N'event_id', 'QUARANTINE', 'CONFIDENTIAL'),
        (@release_id, 'finance-daily-census', 'finance-file-exchange',
            N'daily', N'facility_census', 'FILE_SET',
            N'facility_id,effective_date', 'FAIL', 'CONFIDENTIAL');

    INSERT ctrl.TargetObject
    (
        release_id,
        target_object_key,
        target_layer,
        store_alias,
        namespace_name,
        object_name,
        write_disposition,
        publication_boundary
    )
    VALUES
        (@release_id, 'bronze-facility-reference', 'BRONZE',
            'store-bronze', N'enterprise_reference', N'facility',
            'REPLACE', 'INTERNAL_STAGE'),
        (@release_id, 'bronze-clinical-encounter', 'BRONZE',
            'store-bronze', N'clinical', N'encounter',
            'MERGE', 'QUALITY_GATED'),
        (@release_id, 'bronze-pharmacy-order', 'BRONZE',
            'store-bronze', N'pharmacy', N'orders',
            'MERGE', 'QUALITY_GATED'),
        (@release_id, 'bronze-facility-status-event', 'BRONZE',
            'store-bronze', N'operations', N'facility_status_event',
            'APPEND', 'QUALITY_GATED'),
        (@release_id, 'bronze-finance-daily-census', 'BRONZE',
            'store-bronze', N'finance', N'facility_census',
            'SNAPSHOT', 'QUALITY_GATED');

    INSERT ctrl.IngestionObject
    (
        release_id,
        ingestion_object_key,
        display_name,
        domain_key,
        source_object_key,
        target_object_key,
        load_policy_key,
        execution_policy_key,
        is_required
    )
    VALUES
        (@release_id, 'ingest-facility-reference',
            N'Facility reference',
            'enterprise-reference',
            'facility-reference',
            'bronze-facility-reference',
            'full-reference-replace',
            'standard-batch',
            1),
        (@release_id, 'ingest-clinical-encounter',
            N'Clinical encounter',
            'clinical',
            'clinical-encounter',
            'bronze-clinical-encounter',
            'watermark-timestamp-merge',
            'critical-incremental',
            1),
        (@release_id, 'ingest-pharmacy-order',
            N'Pharmacy order',
            'pharmacy',
            'pharmacy-order',
            'bronze-pharmacy-order',
            'watermark-sequence-merge',
            'critical-incremental',
            1),
        (@release_id, 'ingest-facility-status-event',
            N'Facility status event',
            'operations',
            'facility-status-event',
            'bronze-facility-status-event',
            'append-event-identity',
            'low-latency-event',
            0),
        (@release_id, 'ingest-finance-daily-census',
            N'Finance daily census',
            'finance',
            'finance-daily-census',
            'bronze-finance-daily-census',
            'daily-effective-snapshot',
            'daily-snapshot',
            1);

    INSERT ctrl.ObjectEnvironmentConfig
    (
        release_id,
        environment_id,
        ingestion_object_key,
        is_enabled,
        priority_override,
        routing_alias
    )
    SELECT
        @release_id,
        env.environment_id,
        obj.ingestion_object_key,
        CASE
            WHEN env.environment_code = 'production'
             AND obj.ingestion_object_key = 'ingest-facility-status-event'
                THEN CAST(0 AS bit)
            ELSE CAST(1 AS bit)
        END,
        CASE env.environment_code
            WHEN 'development' THEN NULL
            WHEN 'test' THEN obj.test_priority
            WHEN 'production' THEN obj.production_priority
        END,
        CONCAT('route-', obj.routing_key, '-', env.environment_code)
    FROM
    (
        VALUES
            (@development_id, 'development'),
            (@test_id, 'test'),
            (@production_id, 'production')
    ) AS env(environment_id, environment_code)
    CROSS JOIN
    (
        VALUES
            ('ingest-facility-reference', 'facility-reference',
                CAST(55 AS tinyint), CAST(60 AS tinyint)),
            ('ingest-clinical-encounter', 'clinical-encounter',
                CAST(90 AS tinyint), CAST(95 AS tinyint)),
            ('ingest-pharmacy-order', 'pharmacy-order',
                CAST(85 AS tinyint), CAST(90 AS tinyint)),
            ('ingest-facility-status-event', 'facility-status-event',
                CAST(95 AS tinyint), CAST(95 AS tinyint)),
            ('ingest-finance-daily-census', 'finance-daily-census',
                CAST(45 AS tinyint), CAST(50 AS tinyint))
    ) AS obj
    (
        ingestion_object_key,
        routing_key,
        test_priority,
        production_priority
    );

    INSERT ctrl.ObjectDependency
    (
        release_id,
        predecessor_object_key,
        successor_object_key,
        dependency_condition,
        is_optional
    )
    VALUES
        (@release_id, 'ingest-facility-reference',
            'ingest-clinical-encounter', 'DATA_AVAILABLE', 0),
        (@release_id, 'ingest-clinical-encounter',
            'ingest-pharmacy-order', 'SUCCESS', 0),
        (@release_id, 'ingest-facility-reference',
            'ingest-finance-daily-census', 'COMPLETION', 0);

    INSERT ctrl.ObjectSchedule
    (
        release_id,
        ingestion_object_key,
        schedule_key,
        deadline_offset_minutes
    )
    VALUES
        (@release_id, 'ingest-facility-reference',
            'daily-0100-pacific', 300),
        (@release_id, 'ingest-clinical-encounter',
            'interval-15-minute', 15),
        (@release_id, 'ingest-pharmacy-order',
            'interval-15-minute', 15),
        (@release_id, 'ingest-facility-status-event',
            'facility-event-arrival', 5),
        (@release_id, 'ingest-finance-daily-census',
            'daily-0100-pacific', 300);

    INSERT ctrl.ObjectSlo
    (
        release_id,
        ingestion_object_key,
        slo_key,
        blocks_publication
    )
    VALUES
        (@release_id, 'ingest-facility-reference',
            'freshness-batch-by-0600', 0),
        (@release_id, 'ingest-facility-reference',
            'reliability-monthly-99_5', 0),
        (@release_id, 'ingest-clinical-encounter',
            'freshness-critical-15m', 1),
        (@release_id, 'ingest-clinical-encounter',
            'quality-critical-100pct', 1),
        (@release_id, 'ingest-pharmacy-order',
            'freshness-critical-15m', 1),
        (@release_id, 'ingest-pharmacy-order',
            'quality-critical-100pct', 1),
        (@release_id, 'ingest-facility-status-event',
            'freshness-critical-15m', 0),
        (@release_id, 'ingest-finance-daily-census',
            'freshness-batch-by-0600', 1),
        (@release_id, 'ingest-finance-daily-census',
            'duration-standard-120m', 0);

    INSERT ctrl.ObjectQualityPolicy
    (
        release_id,
        ingestion_object_key,
        quality_policy_key,
        evaluation_order
    )
    VALUES
        (@release_id, 'ingest-facility-reference',
            'reference-count-warning', 1),
        (@release_id, 'ingest-clinical-encounter',
            'critical-keys-and-counts', 1),
        (@release_id, 'ingest-pharmacy-order',
            'critical-keys-and-counts', 1),
        (@release_id, 'ingest-facility-status-event',
            'critical-keys-and-counts', 1),
        (@release_id, 'ingest-finance-daily-census',
            'critical-keys-and-counts', 1);

    INSERT ctrl.ObjectOwnership
    (
        release_id,
        ingestion_object_key,
        owner_group_key,
        ownership_role
    )
    SELECT
        @release_id,
        obj.ingestion_object_key,
        assignment.owner_group_key,
        assignment.ownership_role
    FROM
    (
        VALUES
            ('ingest-facility-reference', 'facilities-stewards',
                'operations-data-product'),
            ('ingest-clinical-encounter', 'clinical-stewards',
                'clinical-data-product'),
            ('ingest-pharmacy-order', 'pharmacy-stewards',
                'clinical-data-product'),
            ('ingest-facility-status-event', 'facilities-stewards',
                'operations-data-product'),
            ('ingest-finance-daily-census', 'finance-stewards',
                'operations-data-product')
    ) AS obj(ingestion_object_key, steward_group_key, product_group_key)
    CROSS APPLY
    (
        VALUES
            ('platform-engineering', 'ENGINEERING'),
            (obj.steward_group_key, 'SOURCE_STEWARD'),
            ('data-operations', 'OPERATIONS'),
            ('data-operations', 'INCIDENT'),
            (obj.product_group_key, 'DATA_PRODUCT')
    ) AS assignment(owner_group_key, ownership_role);

    INSERT ctrl.EnvironmentRelease
    (
        environment_id,
        release_id,
        prior_release_id,
        approval_reference,
        activation_reason,
        activated_by,
        activated_at_utc
    )
    VALUES
        (
            @development_id,
            @release_id,
            NULL,
            N'FAB-001 synthetic seed approval',
            N'Activate the initial Development metadata contract.',
            N'github:cetanibp',
            '2026-08-29T00:00:00Z'
        ),
        (
            @test_id,
            @release_id,
            NULL,
            N'FAB-001 synthetic seed approval',
            N'Activate the initial Test metadata contract.',
            N'github:cetanibp',
            '2026-08-29T00:00:00Z'
        ),
        (
            @production_id,
            @release_id,
            NULL,
            N'FAB-001 synthetic design evidence only',
            N'Represent Production resolution without deploying to an actual production system.',
            N'github:cetanibp',
            '2026-08-29T00:00:00Z'
        );
END;

COMMIT TRANSACTION;
GO

SELECT
    environment_code,
    release_version,
    ingestion_object_key,
    strategy_type,
    connection_reference_key,
    target_store_alias,
    effective_priority
FROM ctrl.vw_ActiveIngestionConfiguration
ORDER BY environment_code, effective_priority DESC, ingestion_object_key;
GO

SELECT
    release_id,
    issue_code,
    severity,
    entity_type,
    entity_key,
    issue_message
FROM ctrl.vw_MetadataValidationIssue
ORDER BY severity DESC, issue_code, entity_key;
GO
