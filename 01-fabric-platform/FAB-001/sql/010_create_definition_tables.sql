/*
FAB-001 — Versioned control-plane definitions
Target: SQL Database in Microsoft Fabric

Approved MetadataRelease rows and their child definitions are treated as
immutable by the deployment and permission model. Runtime identities receive
read access to ctrl and narrowly scoped write access to ops/audit.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

IF OBJECT_ID(N'ctrl.Environment', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.Environment
    (
        environment_id   uniqueidentifier NOT NULL,
        environment_code varchar(20)      NOT NULL,
        environment_name nvarchar(100)    NOT NULL,
        is_production    bit              NOT NULL
            CONSTRAINT DF_ctrl_Environment_is_production DEFAULT (0),
        created_at_utc   datetime2(7)     NOT NULL
            CONSTRAINT DF_ctrl_Environment_created_at DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_ctrl_Environment
            PRIMARY KEY CLUSTERED (environment_id),
        CONSTRAINT UQ_ctrl_Environment_code
            UNIQUE (environment_code),
        CONSTRAINT CK_ctrl_Environment_code
            CHECK (environment_code IN ('development', 'test', 'production'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.MetadataRelease', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.MetadataRelease
    (
        release_id        uniqueidentifier NOT NULL,
        release_version   varchar(50)      NOT NULL,
        release_status    varchar(20)      NOT NULL,
        content_hash      varchar(64)      NOT NULL,
        source_commit_sha varchar(40)      NOT NULL,
        change_reason     nvarchar(1000)   NOT NULL,
        created_by        nvarchar(200)    NOT NULL,
        created_at_utc    datetime2(7)     NOT NULL
            CONSTRAINT DF_ctrl_MetadataRelease_created_at DEFAULT (SYSUTCDATETIME()),
        approved_by       nvarchar(200)    NULL,
        approved_at_utc   datetime2(7)     NULL,

        CONSTRAINT PK_ctrl_MetadataRelease
            PRIMARY KEY CLUSTERED (release_id),
        CONSTRAINT UQ_ctrl_MetadataRelease_version
            UNIQUE (release_version),
        CONSTRAINT CK_ctrl_MetadataRelease_status
            CHECK (release_status IN
                ('DRAFT', 'REJECTED', 'APPROVED', 'ACTIVE', 'SUPERSEDED', 'RETIRED')),
        CONSTRAINT CK_ctrl_MetadataRelease_hash
            CHECK (LEN(content_hash) = 64),
        CONSTRAINT CK_ctrl_MetadataRelease_commit
            CHECK (LEN(source_commit_sha) = 40),
        CONSTRAINT CK_ctrl_MetadataRelease_approval
            CHECK
            (
                (release_status IN ('DRAFT', 'REJECTED'))
                OR (approved_by IS NOT NULL AND approved_at_utc IS NOT NULL)
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.EnvironmentRelease', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.EnvironmentRelease
    (
        environment_id     uniqueidentifier NOT NULL,
        release_id         uniqueidentifier NOT NULL,
        prior_release_id   uniqueidentifier NULL,
        approval_reference nvarchar(300)    NOT NULL,
        activation_reason  nvarchar(1000)   NOT NULL,
        activated_by       nvarchar(200)    NOT NULL,
        activated_at_utc   datetime2(7)     NOT NULL
            CONSTRAINT DF_ctrl_EnvironmentRelease_activated_at DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_ctrl_EnvironmentRelease
            PRIMARY KEY CLUSTERED (environment_id),
        CONSTRAINT FK_ctrl_EnvironmentRelease_environment
            FOREIGN KEY (environment_id)
            REFERENCES ctrl.Environment (environment_id),
        CONSTRAINT FK_ctrl_EnvironmentRelease_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT FK_ctrl_EnvironmentRelease_prior_release
            FOREIGN KEY (prior_release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_EnvironmentRelease_distinct
            CHECK (prior_release_id IS NULL OR prior_release_id <> release_id)
    );
END;
GO

IF OBJECT_ID(N'ctrl.OwnerGroup', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.OwnerGroup
    (
        release_id       uniqueidentifier NOT NULL,
        owner_group_key  varchar(100)     NOT NULL,
        display_name     nvarchar(200)    NOT NULL,
        routing_alias    varchar(200)     NOT NULL,

        CONSTRAINT PK_ctrl_OwnerGroup
            PRIMARY KEY CLUSTERED (release_id, owner_group_key),
        CONSTRAINT FK_ctrl_OwnerGroup_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_OwnerGroup_routing_alias
            CHECK
            (
                routing_alias NOT LIKE '%@%'
                AND routing_alias NOT LIKE '%://%'
                AND routing_alias NOT LIKE '%=%'
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.WatermarkPolicy', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.WatermarkPolicy
    (
        release_id             uniqueidentifier NOT NULL,
        watermark_policy_key   varchar(100)     NOT NULL,
        column_name            nvarchar(256)    NOT NULL,
        logical_data_type      varchar(20)      NOT NULL,
        comparison_operator    varchar(10)      NOT NULL,
        overlap_amount         int              NOT NULL
            CONSTRAINT DF_ctrl_WatermarkPolicy_overlap DEFAULT (0),
        overlap_unit           varchar(20)      NULL,
        initial_value_policy   varchar(30)      NOT NULL,
        initial_value_literal  nvarchar(4000)   NULL,
        upper_bound_mode       varchar(30)      NOT NULL,
        late_arrival_behavior  varchar(30)      NOT NULL,

        CONSTRAINT PK_ctrl_WatermarkPolicy
            PRIMARY KEY CLUSTERED (release_id, watermark_policy_key),
        CONSTRAINT FK_ctrl_WatermarkPolicy_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_WatermarkPolicy_data_type
            CHECK (logical_data_type IN
                ('DATETIME2', 'DATE', 'BIGINT', 'INTEGER', 'DECIMAL', 'STRING')),
        CONSTRAINT CK_ctrl_WatermarkPolicy_operator
            CHECK (comparison_operator IN ('>', '>=', '<', '<=')),
        CONSTRAINT CK_ctrl_WatermarkPolicy_overlap
            CHECK
            (
                overlap_amount >= 0
                AND
                (
                    (overlap_amount = 0 AND overlap_unit IS NULL)
                    OR
                    (overlap_amount > 0 AND overlap_unit IN
                        ('SECOND', 'MINUTE', 'HOUR', 'DAY', 'ROW'))
                )
            ),
        CONSTRAINT CK_ctrl_WatermarkPolicy_initial
            CHECK (initial_value_policy IN
                ('EXPLICIT', 'SOURCE_MINIMUM', 'CURRENT_TIME', 'BEGINNING')),
        CONSTRAINT CK_ctrl_WatermarkPolicy_initial_literal
            CHECK
            (
                (initial_value_policy = 'EXPLICIT' AND initial_value_literal IS NOT NULL)
                OR
                (initial_value_policy <> 'EXPLICIT' AND initial_value_literal IS NULL)
            ),
        CONSTRAINT CK_ctrl_WatermarkPolicy_upper_bound
            CHECK (upper_bound_mode IN
                ('SOURCE_MAX_AT_START', 'CURRENT_TIME_AT_START', 'EXPLICIT')),
        CONSTRAINT CK_ctrl_WatermarkPolicy_late_arrival
            CHECK (late_arrival_behavior IN
                ('OVERLAP_AND_DEDUPLICATE', 'REPROCESS_WINDOW', 'NOT_SUPPORTED'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.LoadPolicy', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.LoadPolicy
    (
        release_id             uniqueidentifier NOT NULL,
        load_policy_key        varchar(100)     NOT NULL,
        strategy_type          varchar(20)      NOT NULL,
        watermark_policy_key   varchar(100)     NULL,
        duplicate_behavior     varchar(30)      NOT NULL,
        delete_behavior        varchar(30)      NOT NULL,
        schema_behavior        varchar(30)      NOT NULL,
        idempotency_contract   nvarchar(1000)   NOT NULL,

        CONSTRAINT PK_ctrl_LoadPolicy
            PRIMARY KEY CLUSTERED (release_id, load_policy_key),
        CONSTRAINT FK_ctrl_LoadPolicy_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT FK_ctrl_LoadPolicy_watermark
            FOREIGN KEY (release_id, watermark_policy_key)
            REFERENCES ctrl.WatermarkPolicy (release_id, watermark_policy_key),
        CONSTRAINT CK_ctrl_LoadPolicy_strategy
            CHECK (strategy_type IN ('FULL', 'WATERMARK', 'APPEND', 'SNAPSHOT')),
        CONSTRAINT CK_ctrl_LoadPolicy_watermark_usage
            CHECK
            (
                (strategy_type = 'WATERMARK' AND watermark_policy_key IS NOT NULL)
                OR
                (strategy_type <> 'WATERMARK' AND watermark_policy_key IS NULL)
            ),
        CONSTRAINT CK_ctrl_LoadPolicy_duplicate
            CHECK (duplicate_behavior IN
                ('REJECT', 'IGNORE', 'UPSERT_BY_KEY', 'DEDUPLICATE_BY_KEY')),
        CONSTRAINT CK_ctrl_LoadPolicy_delete
            CHECK (delete_behavior IN
                ('IGNORE', 'SOFT_DELETE', 'HARD_DELETE', 'SNAPSHOT_RECONCILE')),
        CONSTRAINT CK_ctrl_LoadPolicy_schema
            CHECK (schema_behavior IN
                ('FAIL', 'QUARANTINE', 'ALLOW_ADDITIVE', 'ROUTE_FOR_REVIEW'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.StrategyParameterDefinition', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.StrategyParameterDefinition
    (
        strategy_type   varchar(20)    NOT NULL,
        parameter_key   varchar(100)   NOT NULL,
        value_type      varchar(20)    NOT NULL,
        is_required     bit            NOT NULL,
        minimum_value   decimal(38, 9) NULL,
        maximum_value   decimal(38, 9) NULL,
        allowed_values  nvarchar(1000) NULL,
        description     nvarchar(1000) NOT NULL,

        CONSTRAINT PK_ctrl_StrategyParameterDefinition
            PRIMARY KEY CLUSTERED (strategy_type, parameter_key),
        CONSTRAINT CK_ctrl_StrategyParameterDefinition_strategy
            CHECK (strategy_type IN ('FULL', 'WATERMARK', 'APPEND', 'SNAPSHOT')),
        CONSTRAINT CK_ctrl_StrategyParameterDefinition_type
            CHECK (value_type IN ('STRING', 'INTEGER', 'DECIMAL', 'BOOLEAN'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.LoadPolicyParameter', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.LoadPolicyParameter
    (
        release_id      uniqueidentifier NOT NULL,
        load_policy_key varchar(100)     NOT NULL,
        strategy_type   varchar(20)      NOT NULL,
        parameter_key   varchar(100)     NOT NULL,
        value_type      varchar(20)      NOT NULL,
        value_string    nvarchar(4000)   NULL,
        value_integer   bigint           NULL,
        value_decimal   decimal(38, 9)   NULL,
        value_boolean   bit              NULL,

        CONSTRAINT PK_ctrl_LoadPolicyParameter
            PRIMARY KEY CLUSTERED (release_id, load_policy_key, parameter_key),
        CONSTRAINT FK_ctrl_LoadPolicyParameter_policy
            FOREIGN KEY (release_id, load_policy_key)
            REFERENCES ctrl.LoadPolicy (release_id, load_policy_key),
        CONSTRAINT FK_ctrl_LoadPolicyParameter_definition
            FOREIGN KEY (strategy_type, parameter_key)
            REFERENCES ctrl.StrategyParameterDefinition (strategy_type, parameter_key),
        CONSTRAINT CK_ctrl_LoadPolicyParameter_type
            CHECK (value_type IN ('STRING', 'INTEGER', 'DECIMAL', 'BOOLEAN')),
        CONSTRAINT CK_ctrl_LoadPolicyParameter_one_value
            CHECK
            (
                (CASE WHEN value_string  IS NULL THEN 0 ELSE 1 END)
              + (CASE WHEN value_integer IS NULL THEN 0 ELSE 1 END)
              + (CASE WHEN value_decimal IS NULL THEN 0 ELSE 1 END)
              + (CASE WHEN value_boolean IS NULL THEN 0 ELSE 1 END)
              = 1
            ),
        CONSTRAINT CK_ctrl_LoadPolicyParameter_secret
            CHECK
            (
                value_string IS NULL
                OR
                (
                    value_string NOT LIKE '%password=%'
                    AND value_string NOT LIKE '%secret=%'
                    AND value_string NOT LIKE '%token=%'
                    AND value_string NOT LIKE '%://%'
                )
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.ExecutionPolicy', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.ExecutionPolicy
    (
        release_id             uniqueidentifier NOT NULL,
        execution_policy_key   varchar(100)     NOT NULL,
        timeout_minutes        int              NOT NULL,
        max_retries            int              NOT NULL,
        retry_delay_seconds    int              NOT NULL,
        default_priority       tinyint          NOT NULL,
        concurrency_group      varchar(100)     NOT NULL,
        max_parallelism        smallint         NOT NULL,
        recovery_mode          varchar(30)      NOT NULL,

        CONSTRAINT PK_ctrl_ExecutionPolicy
            PRIMARY KEY CLUSTERED (release_id, execution_policy_key),
        CONSTRAINT FK_ctrl_ExecutionPolicy_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_ExecutionPolicy_timeout
            CHECK (timeout_minutes BETWEEN 1 AND 1440),
        CONSTRAINT CK_ctrl_ExecutionPolicy_retries
            CHECK (max_retries BETWEEN 0 AND 10),
        CONSTRAINT CK_ctrl_ExecutionPolicy_retry_delay
            CHECK (retry_delay_seconds BETWEEN 0 AND 86400),
        CONSTRAINT CK_ctrl_ExecutionPolicy_priority
            CHECK (default_priority BETWEEN 1 AND 100),
        CONSTRAINT CK_ctrl_ExecutionPolicy_parallelism
            CHECK (max_parallelism BETWEEN 1 AND 100),
        CONSTRAINT CK_ctrl_ExecutionPolicy_recovery
            CHECK (recovery_mode IN
                ('RESTART_SAFE', 'REPLAY_RANGE', 'FORWARD_RECOVERY', 'MANUAL_REVIEW'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.Schedule', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.Schedule
    (
        release_id             uniqueidentifier NOT NULL,
        schedule_key           varchar(100)     NOT NULL,
        schedule_type          varchar(20)      NOT NULL,
        iana_time_zone         varchar(100)     NOT NULL,
        trigger_alias          varchar(100)     NOT NULL,
        daily_local_start      time(0)          NULL,
        eligibility_window_min int              NULL,
        interval_minutes       int              NULL,
        event_alias            varchar(100)     NULL,
        is_catchup_enabled      bit              NOT NULL
            CONSTRAINT DF_ctrl_Schedule_catchup DEFAULT (1),

        CONSTRAINT PK_ctrl_Schedule
            PRIMARY KEY CLUSTERED (release_id, schedule_key),
        CONSTRAINT FK_ctrl_Schedule_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_Schedule_type
            CHECK (schedule_type IN ('DAILY', 'INTERVAL', 'EVENT', 'MANUAL')),
        CONSTRAINT CK_ctrl_Schedule_shape
            CHECK
            (
                (schedule_type = 'DAILY'
                    AND daily_local_start IS NOT NULL
                    AND eligibility_window_min IS NOT NULL)
                OR
                (schedule_type = 'INTERVAL' AND interval_minutes IS NOT NULL)
                OR
                (schedule_type = 'EVENT' AND event_alias IS NOT NULL)
                OR
                (schedule_type = 'MANUAL')
            ),
        CONSTRAINT CK_ctrl_Schedule_window
            CHECK (eligibility_window_min IS NULL OR eligibility_window_min BETWEEN 1 AND 1440),
        CONSTRAINT CK_ctrl_Schedule_interval
            CHECK (interval_minutes IS NULL OR interval_minutes BETWEEN 1 AND 10080),
        CONSTRAINT CK_ctrl_Schedule_safe_aliases
            CHECK
            (
                trigger_alias NOT LIKE '%://%'
                AND trigger_alias NOT LIKE '%=%'
                AND (event_alias IS NULL OR
                    (event_alias NOT LIKE '%://%' AND event_alias NOT LIKE '%=%'))
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.SloDefinition', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.SloDefinition
    (
        release_id           uniqueidentifier NOT NULL,
        slo_key              varchar(100)     NOT NULL,
        metric_type          varchar(20)      NOT NULL,
        comparison_operator  varchar(10)      NOT NULL,
        target_value         decimal(19, 6)   NOT NULL,
        target_unit          varchar(30)      NOT NULL,
        evaluation_window    varchar(30)      NOT NULL,
        severity             varchar(20)      NOT NULL,
        breach_policy        varchar(30)      NOT NULL,

        CONSTRAINT PK_ctrl_SloDefinition
            PRIMARY KEY CLUSTERED (release_id, slo_key),
        CONSTRAINT FK_ctrl_SloDefinition_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_SloDefinition_metric
            CHECK (metric_type IN ('FRESHNESS', 'RELIABILITY', 'DURATION', 'QUALITY')),
        CONSTRAINT CK_ctrl_SloDefinition_operator
            CHECK (comparison_operator IN ('<', '<=', '>', '>=')),
        CONSTRAINT CK_ctrl_SloDefinition_target
            CHECK (target_value >= 0),
        CONSTRAINT CK_ctrl_SloDefinition_unit
            CHECK (target_unit IN ('MINUTES', 'HOURS', 'PERCENT')),
        CONSTRAINT CK_ctrl_SloDefinition_window
            CHECK (evaluation_window IN ('PER_RUN', 'DAILY', 'ROLLING_30_DAY', 'MONTHLY')),
        CONSTRAINT CK_ctrl_SloDefinition_severity
            CHECK (severity IN ('INFO', 'WARNING', 'CRITICAL')),
        CONSTRAINT CK_ctrl_SloDefinition_breach
            CHECK (breach_policy IN ('RECORD', 'ALERT', 'BLOCK_PUBLICATION', 'ESCALATE'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.QualityPolicy', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.QualityPolicy
    (
        release_id           uniqueidentifier NOT NULL,
        quality_policy_key   varchar(100)     NOT NULL,
        policy_version       varchar(50)      NOT NULL,
        enforcement_level    varchar(10)      NOT NULL,
        quarantine_required  bit              NOT NULL,
        contract_reference   nvarchar(500)    NOT NULL,

        CONSTRAINT PK_ctrl_QualityPolicy
            PRIMARY KEY CLUSTERED (release_id, quality_policy_key),
        CONSTRAINT FK_ctrl_QualityPolicy_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_QualityPolicy_enforcement
            CHECK (enforcement_level IN ('BLOCK', 'WARN'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.SourceSystem', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.SourceSystem
    (
        release_id              uniqueidentifier NOT NULL,
        source_system_key       varchar(100)     NOT NULL,
        source_system_name      nvarchar(200)    NOT NULL,
        domain_key              varchar(100)     NOT NULL,
        source_type             varchar(30)      NOT NULL,
        default_connection_key  varchar(100)     NOT NULL,
        data_classification     varchar(30)      NOT NULL,

        CONSTRAINT PK_ctrl_SourceSystem
            PRIMARY KEY CLUSTERED (release_id, source_system_key),
        CONSTRAINT FK_ctrl_SourceSystem_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_SourceSystem_source_type
            CHECK (source_type IN
                ('SQL_DATABASE', 'ORACLE_DATABASE', 'REST_API', 'FILE', 'EVENT_STREAM')),
        CONSTRAINT CK_ctrl_SourceSystem_classification
            CHECK (data_classification IN
                ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED')),
        CONSTRAINT CK_ctrl_SourceSystem_connection_key
            CHECK
            (
                default_connection_key NOT LIKE '%://%'
                AND default_connection_key NOT LIKE '%=%'
                AND default_connection_key NOT LIKE '%@%'
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.SourceEnvironmentConfig', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.SourceEnvironmentConfig
    (
        release_id               uniqueidentifier NOT NULL,
        environment_id           uniqueidentifier NOT NULL,
        source_system_key        varchar(100)     NOT NULL,
        connection_reference_key varchar(100)     NOT NULL,
        landing_zone_key         varchar(100)     NOT NULL,
        max_connection_concurrency smallint       NOT NULL,
        is_enabled               bit              NOT NULL,

        CONSTRAINT PK_ctrl_SourceEnvironmentConfig
            PRIMARY KEY CLUSTERED
                (release_id, environment_id, source_system_key),
        CONSTRAINT FK_ctrl_SourceEnvironmentConfig_source
            FOREIGN KEY (release_id, source_system_key)
            REFERENCES ctrl.SourceSystem (release_id, source_system_key),
        CONSTRAINT FK_ctrl_SourceEnvironmentConfig_environment
            FOREIGN KEY (environment_id)
            REFERENCES ctrl.Environment (environment_id),
        CONSTRAINT CK_ctrl_SourceEnvironmentConfig_concurrency
            CHECK (max_connection_concurrency BETWEEN 1 AND 100),
        CONSTRAINT CK_ctrl_SourceEnvironmentConfig_safe_values
            CHECK
            (
                connection_reference_key NOT LIKE '%://%'
                AND connection_reference_key NOT LIKE '%=%'
                AND connection_reference_key NOT LIKE '%@%'
                AND landing_zone_key NOT LIKE '%://%'
                AND landing_zone_key NOT LIKE '%=%'
                AND landing_zone_key NOT LIKE '%@%'
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.SourceObject', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.SourceObject
    (
        release_id            uniqueidentifier NOT NULL,
        source_object_key     varchar(150)     NOT NULL,
        source_system_key     varchar(100)     NOT NULL,
        namespace_name        nvarchar(256)    NOT NULL,
        object_name           nvarchar(256)    NOT NULL,
        object_type           varchar(30)      NOT NULL,
        business_key_contract nvarchar(1000)   NULL,
        schema_drift_policy   varchar(30)      NOT NULL,
        data_classification   varchar(30)      NOT NULL,

        CONSTRAINT PK_ctrl_SourceObject
            PRIMARY KEY CLUSTERED (release_id, source_object_key),
        CONSTRAINT UQ_ctrl_SourceObject_name
            UNIQUE (release_id, source_system_key, namespace_name, object_name),
        CONSTRAINT FK_ctrl_SourceObject_system
            FOREIGN KEY (release_id, source_system_key)
            REFERENCES ctrl.SourceSystem (release_id, source_system_key),
        CONSTRAINT CK_ctrl_SourceObject_type
            CHECK (object_type IN ('TABLE', 'VIEW', 'QUERY', 'FILE_SET', 'EVENT')),
        CONSTRAINT CK_ctrl_SourceObject_drift
            CHECK (schema_drift_policy IN
                ('FAIL', 'QUARANTINE', 'ALLOW_ADDITIVE', 'ROUTE_FOR_REVIEW')),
        CONSTRAINT CK_ctrl_SourceObject_classification
            CHECK (data_classification IN
                ('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', 'RESTRICTED'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.TargetObject', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.TargetObject
    (
        release_id          uniqueidentifier NOT NULL,
        target_object_key   varchar(150)     NOT NULL,
        target_layer        varchar(20)      NOT NULL,
        store_alias         varchar(100)     NOT NULL,
        namespace_name      nvarchar(256)    NOT NULL,
        object_name         nvarchar(256)    NOT NULL,
        write_disposition   varchar(30)      NOT NULL,
        publication_boundary varchar(30)     NOT NULL,

        CONSTRAINT PK_ctrl_TargetObject
            PRIMARY KEY CLUSTERED (release_id, target_object_key),
        CONSTRAINT UQ_ctrl_TargetObject_name
            UNIQUE (release_id, store_alias, namespace_name, object_name),
        CONSTRAINT FK_ctrl_TargetObject_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ctrl_TargetObject_layer
            CHECK (target_layer IN ('BRONZE', 'SILVER', 'GOLD', 'DATA_PRODUCT')),
        CONSTRAINT CK_ctrl_TargetObject_write
            CHECK (write_disposition IN
                ('REPLACE', 'APPEND', 'MERGE', 'SNAPSHOT')),
        CONSTRAINT CK_ctrl_TargetObject_publication
            CHECK (publication_boundary IN
                ('INTERNAL_STAGE', 'QUALITY_GATED', 'PUBLISHED')),
        CONSTRAINT CK_ctrl_TargetObject_store_alias
            CHECK
            (
                store_alias NOT LIKE '%://%'
                AND store_alias NOT LIKE '%=%'
                AND store_alias NOT LIKE '%@%'
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.IngestionObject', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.IngestionObject
    (
        release_id            uniqueidentifier NOT NULL,
        ingestion_object_key  varchar(150)     NOT NULL,
        display_name          nvarchar(200)    NOT NULL,
        domain_key            varchar(100)     NOT NULL,
        source_object_key     varchar(150)     NOT NULL,
        target_object_key     varchar(150)     NOT NULL,
        load_policy_key       varchar(100)     NOT NULL,
        execution_policy_key  varchar(100)     NOT NULL,
        is_required           bit              NOT NULL,

        CONSTRAINT PK_ctrl_IngestionObject
            PRIMARY KEY CLUSTERED (release_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_IngestionObject_source
            FOREIGN KEY (release_id, source_object_key)
            REFERENCES ctrl.SourceObject (release_id, source_object_key),
        CONSTRAINT FK_ctrl_IngestionObject_target
            FOREIGN KEY (release_id, target_object_key)
            REFERENCES ctrl.TargetObject (release_id, target_object_key),
        CONSTRAINT FK_ctrl_IngestionObject_load_policy
            FOREIGN KEY (release_id, load_policy_key)
            REFERENCES ctrl.LoadPolicy (release_id, load_policy_key),
        CONSTRAINT FK_ctrl_IngestionObject_execution_policy
            FOREIGN KEY (release_id, execution_policy_key)
            REFERENCES ctrl.ExecutionPolicy (release_id, execution_policy_key)
    );
END;
GO

IF OBJECT_ID(N'ctrl.ObjectEnvironmentConfig', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.ObjectEnvironmentConfig
    (
        release_id            uniqueidentifier NOT NULL,
        environment_id        uniqueidentifier NOT NULL,
        ingestion_object_key  varchar(150)     NOT NULL,
        is_enabled            bit              NOT NULL,
        priority_override     tinyint          NULL,
        routing_alias         varchar(100)     NOT NULL,

        CONSTRAINT PK_ctrl_ObjectEnvironmentConfig
            PRIMARY KEY CLUSTERED
                (release_id, environment_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_ObjectEnvironmentConfig_object
            FOREIGN KEY (release_id, ingestion_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_ObjectEnvironmentConfig_environment
            FOREIGN KEY (environment_id)
            REFERENCES ctrl.Environment (environment_id),
        CONSTRAINT CK_ctrl_ObjectEnvironmentConfig_priority
            CHECK (priority_override IS NULL OR priority_override BETWEEN 1 AND 100),
        CONSTRAINT CK_ctrl_ObjectEnvironmentConfig_routing
            CHECK
            (
                routing_alias NOT LIKE '%://%'
                AND routing_alias NOT LIKE '%=%'
                AND routing_alias NOT LIKE '%@%'
            )
    );
END;
GO

IF OBJECT_ID(N'ctrl.ObjectDependency', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.ObjectDependency
    (
        release_id              uniqueidentifier NOT NULL,
        predecessor_object_key  varchar(150)     NOT NULL,
        successor_object_key    varchar(150)     NOT NULL,
        dependency_condition    varchar(30)      NOT NULL,
        is_optional             bit              NOT NULL,

        CONSTRAINT PK_ctrl_ObjectDependency
            PRIMARY KEY CLUSTERED
                (release_id, predecessor_object_key, successor_object_key),
        CONSTRAINT FK_ctrl_ObjectDependency_predecessor
            FOREIGN KEY (release_id, predecessor_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_ObjectDependency_successor
            FOREIGN KEY (release_id, successor_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT CK_ctrl_ObjectDependency_distinct
            CHECK (predecessor_object_key <> successor_object_key),
        CONSTRAINT CK_ctrl_ObjectDependency_condition
            CHECK (dependency_condition IN
                ('SUCCESS', 'COMPLETION', 'DATA_AVAILABLE', 'OPTIONAL'))
    );
END;
GO

IF OBJECT_ID(N'ctrl.ObjectSchedule', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.ObjectSchedule
    (
        release_id              uniqueidentifier NOT NULL,
        ingestion_object_key    varchar(150)     NOT NULL,
        schedule_key            varchar(100)     NOT NULL,
        deadline_offset_minutes int              NULL,

        CONSTRAINT PK_ctrl_ObjectSchedule
            PRIMARY KEY CLUSTERED
                (release_id, ingestion_object_key, schedule_key),
        CONSTRAINT FK_ctrl_ObjectSchedule_object
            FOREIGN KEY (release_id, ingestion_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_ObjectSchedule_schedule
            FOREIGN KEY (release_id, schedule_key)
            REFERENCES ctrl.Schedule (release_id, schedule_key),
        CONSTRAINT CK_ctrl_ObjectSchedule_deadline
            CHECK (deadline_offset_minutes IS NULL OR
                   deadline_offset_minutes BETWEEN 0 AND 10080)
    );
END;
GO

IF OBJECT_ID(N'ctrl.ObjectSlo', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.ObjectSlo
    (
        release_id            uniqueidentifier NOT NULL,
        ingestion_object_key  varchar(150)     NOT NULL,
        slo_key               varchar(100)     NOT NULL,
        blocks_publication    bit              NOT NULL,

        CONSTRAINT PK_ctrl_ObjectSlo
            PRIMARY KEY CLUSTERED
                (release_id, ingestion_object_key, slo_key),
        CONSTRAINT FK_ctrl_ObjectSlo_object
            FOREIGN KEY (release_id, ingestion_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_ObjectSlo_slo
            FOREIGN KEY (release_id, slo_key)
            REFERENCES ctrl.SloDefinition (release_id, slo_key)
    );
END;
GO

IF OBJECT_ID(N'ctrl.ObjectQualityPolicy', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.ObjectQualityPolicy
    (
        release_id            uniqueidentifier NOT NULL,
        ingestion_object_key  varchar(150)     NOT NULL,
        quality_policy_key    varchar(100)     NOT NULL,
        evaluation_order      smallint         NOT NULL,

        CONSTRAINT PK_ctrl_ObjectQualityPolicy
            PRIMARY KEY CLUSTERED
                (release_id, ingestion_object_key, quality_policy_key),
        CONSTRAINT UQ_ctrl_ObjectQualityPolicy_order
            UNIQUE (release_id, ingestion_object_key, evaluation_order),
        CONSTRAINT FK_ctrl_ObjectQualityPolicy_object
            FOREIGN KEY (release_id, ingestion_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_ObjectQualityPolicy_policy
            FOREIGN KEY (release_id, quality_policy_key)
            REFERENCES ctrl.QualityPolicy (release_id, quality_policy_key),
        CONSTRAINT CK_ctrl_ObjectQualityPolicy_order
            CHECK (evaluation_order BETWEEN 1 AND 1000)
    );
END;
GO

IF OBJECT_ID(N'ctrl.ObjectOwnership', N'U') IS NULL
BEGIN
    CREATE TABLE ctrl.ObjectOwnership
    (
        release_id            uniqueidentifier NOT NULL,
        ingestion_object_key  varchar(150)     NOT NULL,
        owner_group_key       varchar(100)     NOT NULL,
        ownership_role        varchar(30)      NOT NULL,

        CONSTRAINT PK_ctrl_ObjectOwnership
            PRIMARY KEY CLUSTERED
                (release_id, ingestion_object_key, owner_group_key, ownership_role),
        CONSTRAINT FK_ctrl_ObjectOwnership_object
            FOREIGN KEY (release_id, ingestion_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT FK_ctrl_ObjectOwnership_owner
            FOREIGN KEY (release_id, owner_group_key)
            REFERENCES ctrl.OwnerGroup (release_id, owner_group_key),
        CONSTRAINT CK_ctrl_ObjectOwnership_role
            CHECK (ownership_role IN
                ('ENGINEERING', 'SOURCE_STEWARD', 'DATA_PRODUCT',
                 'OPERATIONS', 'INCIDENT', 'APPROVER'))
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'ctrl.IngestionObject')
      AND name = N'IX_ctrl_IngestionObject_selection'
)
    CREATE INDEX IX_ctrl_IngestionObject_selection
        ON ctrl.IngestionObject
            (release_id, domain_key, ingestion_object_key);
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'ctrl.ObjectEnvironmentConfig')
      AND name = N'IX_ctrl_ObjectEnvironmentConfig_enabled'
)
    CREATE INDEX IX_ctrl_ObjectEnvironmentConfig_enabled
        ON ctrl.ObjectEnvironmentConfig
            (environment_id, release_id, is_enabled, ingestion_object_key);
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'ctrl.ObjectDependency')
      AND name = N'IX_ctrl_ObjectDependency_successor'
)
    CREATE INDEX IX_ctrl_ObjectDependency_successor
        ON ctrl.ObjectDependency
            (release_id, successor_object_key, predecessor_object_key);
GO
