CREATE TABLE [ops].[TelemetryExclusion] (
    [telemetry_exclusion_id] UNIQUEIDENTIFIER NOT NULL,
    [environment_id]        UNIQUEIDENTIFIER NOT NULL,
    [release_id]            UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key]  VARCHAR (150)    NULL,
    [exclusion_type]        VARCHAR (30)     NOT NULL,
    [effective_start_utc]   DATETIME2 (7)    NOT NULL,
    [effective_end_utc]     DATETIME2 (7)    NOT NULL,
    [actor_identity]        NVARCHAR (200)   NOT NULL,
    [reason]                NVARCHAR (1000)  NOT NULL,
    [approval_reference]    NVARCHAR (300)   NOT NULL,
    [approved_at_utc]       DATETIME2 (7)    NOT NULL,
    [created_at_utc]        DATETIME2 (7)    CONSTRAINT [DF_ops_TelemetryExclusion_created] DEFAULT (sysutcdatetime()) NOT NULL,
    CONSTRAINT [PK_ops_TelemetryExclusion] PRIMARY KEY CLUSTERED ([telemetry_exclusion_id] ASC),
    CONSTRAINT [CK_ops_TelemetryExclusion_type] CHECK
        ([exclusion_type] IN ('PLANNED_MAINTENANCE', 'DISABLED_OBJECT', 'FAILURE_EXERCISE')),
    CONSTRAINT [CK_ops_TelemetryExclusion_window] CHECK
        ([effective_start_utc] < [effective_end_utc]
         AND [approved_at_utc] <= [effective_start_utc]
         AND [created_at_utc] <= [effective_start_utc]),
    CONSTRAINT [CK_ops_TelemetryExclusion_evidence] CHECK
        (LEN(LTRIM(RTRIM([actor_identity]))) > 0
         AND LEN(LTRIM(RTRIM([reason]))) > 0
         AND LEN(LTRIM(RTRIM([approval_reference]))) > 0),
    CONSTRAINT [FK_ops_TelemetryExclusion_environment] FOREIGN KEY ([environment_id])
        REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ops_TelemetryExclusion_release] FOREIGN KEY ([release_id])
        REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [FK_ops_TelemetryExclusion_object] FOREIGN KEY ([release_id], [ingestion_object_key])
        REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [UQ_ops_TelemetryExclusion_scope] UNIQUE NONCLUSTERED
        ([environment_id], [release_id], [ingestion_object_key], [exclusion_type],
         [effective_start_utc], [effective_end_utc])
);
GO

CREATE NONCLUSTERED INDEX [IX_ops_TelemetryExclusion_effective]
    ON [ops].[TelemetryExclusion]
        ([environment_id], [effective_start_utc], [effective_end_utc], [ingestion_object_key]);
GO
