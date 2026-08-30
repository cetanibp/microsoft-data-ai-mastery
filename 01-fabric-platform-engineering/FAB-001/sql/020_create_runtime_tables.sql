/*
FAB-001 — Mutable runtime state and append-only evidence
Target: SQL Database in Microsoft Fabric

These tables are isolated from immutable definition deployment. Later runtime
work may add stored procedures, but it must preserve the identities, release
resolution, and watermark compare-and-commit contract defined here.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

IF OBJECT_ID(N'ops.ExecutionRun', N'U') IS NULL
BEGIN
    CREATE TABLE ops.ExecutionRun
    (
        run_id             uniqueidentifier NOT NULL,
        environment_id     uniqueidentifier NOT NULL,
        release_id         uniqueidentifier NOT NULL,
        trigger_type       varchar(20)      NOT NULL,
        trigger_reference  nvarchar(300)    NULL,
        correlation_id     varchar(100)     NOT NULL,
        requested_scope    nvarchar(1000)   NOT NULL,
        configuration_hash varchar(64)      NOT NULL,
        run_status         varchar(20)      NOT NULL,
        started_at_utc     datetime2(7)     NOT NULL,
        completed_at_utc   datetime2(7)     NULL,

        CONSTRAINT PK_ops_ExecutionRun
            PRIMARY KEY CLUSTERED (run_id),
        CONSTRAINT UQ_ops_ExecutionRun_correlation
            UNIQUE (correlation_id),
        CONSTRAINT UQ_ops_ExecutionRun_scope
            UNIQUE (run_id, environment_id, release_id),
        CONSTRAINT FK_ops_ExecutionRun_environment
            FOREIGN KEY (environment_id)
            REFERENCES ctrl.Environment (environment_id),
        CONSTRAINT FK_ops_ExecutionRun_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT CK_ops_ExecutionRun_trigger
            CHECK (trigger_type IN ('DAILY', 'INTERVAL', 'EVENT', 'MANUAL', 'RECOVERY')),
        CONSTRAINT CK_ops_ExecutionRun_status
            CHECK (run_status IN
                ('REQUESTED', 'RUNNING', 'SUCCEEDED', 'SUCCEEDED_WITH_WARNINGS',
                 'FAILED', 'CANCELLED')),
        CONSTRAINT CK_ops_ExecutionRun_hash
            CHECK (LEN(configuration_hash) = 64),
        CONSTRAINT CK_ops_ExecutionRun_completion
            CHECK
            (
                (run_status IN ('REQUESTED', 'RUNNING') AND completed_at_utc IS NULL)
                OR
                (run_status IN
                    ('SUCCEEDED', 'SUCCEEDED_WITH_WARNINGS', 'FAILED', 'CANCELLED')
                 AND completed_at_utc IS NOT NULL)
            )
    );
END;
GO

IF OBJECT_ID(N'ops.ObjectRun', N'U') IS NULL
BEGIN
    CREATE TABLE ops.ObjectRun
    (
        object_run_id          uniqueidentifier NOT NULL,
        run_id                 uniqueidentifier NOT NULL,
        environment_id         uniqueidentifier NOT NULL,
        release_id             uniqueidentifier NOT NULL,
        ingestion_object_key   varchar(150)     NOT NULL,
        attempt_number         smallint         NOT NULL,
        object_run_status      varchar(30)      NOT NULL,
        input_boundary_hash    varchar(64)      NOT NULL,
        extracted_row_count    bigint           NULL,
        accepted_row_count     bigint           NULL,
        rejected_row_count     bigint           NULL,
        error_classification   varchar(50)      NULL,
        error_summary          nvarchar(2000)   NULL,
        started_at_utc         datetime2(7)     NOT NULL,
        completed_at_utc       datetime2(7)     NULL,

        CONSTRAINT PK_ops_ObjectRun
            PRIMARY KEY CLUSTERED (object_run_id),
        CONSTRAINT UQ_ops_ObjectRun_attempt
            UNIQUE (run_id, ingestion_object_key, attempt_number),
        CONSTRAINT FK_ops_ObjectRun_run_scope
            FOREIGN KEY (run_id, environment_id, release_id)
            REFERENCES ops.ExecutionRun (run_id, environment_id, release_id),
        CONSTRAINT FK_ops_ObjectRun_object
            FOREIGN KEY (release_id, ingestion_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT CK_ops_ObjectRun_attempt
            CHECK (attempt_number BETWEEN 1 AND 100),
        CONSTRAINT CK_ops_ObjectRun_status
            CHECK (object_run_status IN
                ('REQUESTED', 'CLAIMED', 'EXTRACTING', 'VALIDATING', 'PUBLISHING',
                 'SUCCEEDED', 'SUCCEEDED_WITH_WARNINGS', 'FAILED', 'CANCELLED',
                 'RECOVERY_REQUIRED')),
        CONSTRAINT CK_ops_ObjectRun_hash
            CHECK (LEN(input_boundary_hash) = 64),
        CONSTRAINT CK_ops_ObjectRun_counts
            CHECK
            (
                (extracted_row_count IS NULL OR extracted_row_count >= 0)
                AND (accepted_row_count IS NULL OR accepted_row_count >= 0)
                AND (rejected_row_count IS NULL OR rejected_row_count >= 0)
            ),
        CONSTRAINT CK_ops_ObjectRun_completion
            CHECK
            (
                (object_run_status IN
                    ('REQUESTED', 'CLAIMED', 'EXTRACTING', 'VALIDATING', 'PUBLISHING')
                 AND completed_at_utc IS NULL)
                OR
                (object_run_status IN
                    ('SUCCEEDED', 'SUCCEEDED_WITH_WARNINGS', 'FAILED', 'CANCELLED',
                     'RECOVERY_REQUIRED')
                 AND completed_at_utc IS NOT NULL)
            )
    );
END;
GO

IF OBJECT_ID(N'ops.WatermarkState', N'U') IS NULL
BEGIN
    CREATE TABLE ops.WatermarkState
    (
        environment_id          uniqueidentifier NOT NULL,
        ingestion_object_key    varchar(150)     NOT NULL,
        definition_release_id   uniqueidentifier NOT NULL,
        logical_value_type      varchar(20)      NOT NULL,
        committed_value         nvarchar(4000)   NOT NULL,
        state_version           bigint           NOT NULL,
        committed_object_run_id uniqueidentifier NULL,
        committed_at_utc        datetime2(7)     NOT NULL,
        row_version             rowversion       NOT NULL,

        CONSTRAINT PK_ops_WatermarkState
            PRIMARY KEY CLUSTERED (environment_id, ingestion_object_key),
        CONSTRAINT FK_ops_WatermarkState_environment
            FOREIGN KEY (environment_id)
            REFERENCES ctrl.Environment (environment_id),
        CONSTRAINT FK_ops_WatermarkState_definition
            FOREIGN KEY (definition_release_id, ingestion_object_key)
            REFERENCES ctrl.IngestionObject (release_id, ingestion_object_key),
        CONSTRAINT FK_ops_WatermarkState_object_run
            FOREIGN KEY (committed_object_run_id)
            REFERENCES ops.ObjectRun (object_run_id),
        CONSTRAINT CK_ops_WatermarkState_type
            CHECK (logical_value_type IN
                ('DATETIME2', 'DATE', 'BIGINT', 'INTEGER', 'DECIMAL', 'STRING')),
        CONSTRAINT CK_ops_WatermarkState_version
            CHECK (state_version >= 0)
    );
END;
GO

IF OBJECT_ID(N'ops.WatermarkCandidate', N'U') IS NULL
BEGIN
    CREATE TABLE ops.WatermarkCandidate
    (
        candidate_id            uniqueidentifier NOT NULL,
        object_run_id           uniqueidentifier NOT NULL,
        environment_id          uniqueidentifier NOT NULL,
        ingestion_object_key    varchar(150)     NOT NULL,
        logical_value_type      varchar(20)      NOT NULL,
        from_value              nvarchar(4000)   NOT NULL,
        to_value                nvarchar(4000)   NOT NULL,
        observed_state_version  bigint           NOT NULL,
        candidate_status        varchar(20)      NOT NULL,
        proposed_at_utc         datetime2(7)     NOT NULL,
        resolved_at_utc         datetime2(7)     NULL,
        resolution_reason       nvarchar(1000)   NULL,

        CONSTRAINT PK_ops_WatermarkCandidate
            PRIMARY KEY CLUSTERED (candidate_id),
        CONSTRAINT UQ_ops_WatermarkCandidate_object_run
            UNIQUE (object_run_id),
        CONSTRAINT FK_ops_WatermarkCandidate_object_run
            FOREIGN KEY (object_run_id)
            REFERENCES ops.ObjectRun (object_run_id),
        CONSTRAINT FK_ops_WatermarkCandidate_state
            FOREIGN KEY (environment_id, ingestion_object_key)
            REFERENCES ops.WatermarkState (environment_id, ingestion_object_key),
        CONSTRAINT CK_ops_WatermarkCandidate_type
            CHECK (logical_value_type IN
                ('DATETIME2', 'DATE', 'BIGINT', 'INTEGER', 'DECIMAL', 'STRING')),
        CONSTRAINT CK_ops_WatermarkCandidate_version
            CHECK (observed_state_version >= 0),
        CONSTRAINT CK_ops_WatermarkCandidate_status
            CHECK (candidate_status IN ('PROPOSED', 'COMMITTED', 'ABANDONED')),
        CONSTRAINT CK_ops_WatermarkCandidate_resolution
            CHECK
            (
                (candidate_status = 'PROPOSED'
                    AND resolved_at_utc IS NULL
                    AND resolution_reason IS NULL)
                OR
                (candidate_status IN ('COMMITTED', 'ABANDONED')
                    AND resolved_at_utc IS NOT NULL
                    AND resolution_reason IS NOT NULL)
            )
    );
END;
GO

IF OBJECT_ID(N'audit.StateEvent', N'U') IS NULL
BEGIN
    CREATE TABLE audit.StateEvent
    (
        state_event_id   uniqueidentifier NOT NULL,
        environment_id   uniqueidentifier NOT NULL,
        release_id       uniqueidentifier NOT NULL,
        run_id            uniqueidentifier NULL,
        object_run_id     uniqueidentifier NULL,
        event_type        varchar(40)      NOT NULL,
        actor_identity    nvarchar(200)    NOT NULL,
        reason            nvarchar(2000)   NOT NULL,
        correlation_id    varchar(100)     NOT NULL,
        before_hash       varchar(64)      NULL,
        after_hash        varchar(64)      NULL,
        occurred_at_utc   datetime2(7)     NOT NULL
            CONSTRAINT DF_audit_StateEvent_occurred_at DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_audit_StateEvent
            PRIMARY KEY CLUSTERED (state_event_id),
        CONSTRAINT FK_audit_StateEvent_environment
            FOREIGN KEY (environment_id)
            REFERENCES ctrl.Environment (environment_id),
        CONSTRAINT FK_audit_StateEvent_release
            FOREIGN KEY (release_id)
            REFERENCES ctrl.MetadataRelease (release_id),
        CONSTRAINT FK_audit_StateEvent_run
            FOREIGN KEY (run_id)
            REFERENCES ops.ExecutionRun (run_id),
        CONSTRAINT FK_audit_StateEvent_object_run
            FOREIGN KEY (object_run_id)
            REFERENCES ops.ObjectRun (object_run_id),
        CONSTRAINT CK_audit_StateEvent_type
            CHECK (event_type IN
                ('RELEASE_ACTIVATED', 'RUN_REQUESTED', 'OBJECT_CLAIMED',
                 'STATUS_CHANGED', 'WATERMARK_PROPOSED', 'WATERMARK_COMMITTED',
                 'WATERMARK_ABANDONED', 'STATE_CORRECTED', 'RECOVERY_REQUESTED')),
        CONSTRAINT CK_audit_StateEvent_before_hash
            CHECK (before_hash IS NULL OR LEN(before_hash) = 64),
        CONSTRAINT CK_audit_StateEvent_after_hash
            CHECK (after_hash IS NULL OR LEN(after_hash) = 64)
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'ops.ObjectRun')
      AND name = N'IX_ops_ObjectRun_status'
)
    CREATE INDEX IX_ops_ObjectRun_status
        ON ops.ObjectRun
            (environment_id, object_run_status, ingestion_object_key, started_at_utc);
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'ops.WatermarkCandidate')
      AND name = N'IX_ops_WatermarkCandidate_status'
)
    CREATE INDEX IX_ops_WatermarkCandidate_status
        ON ops.WatermarkCandidate
            (environment_id, candidate_status, ingestion_object_key, proposed_at_utc);
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'audit.StateEvent')
      AND name = N'IX_audit_StateEvent_correlation'
)
    CREATE INDEX IX_audit_StateEvent_correlation
        ON audit.StateEvent (correlation_id, occurred_at_utc);
GO
