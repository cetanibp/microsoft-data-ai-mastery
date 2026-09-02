CREATE TABLE [ops].[AlertRoutingDecision] (
    [alert_routing_decision_id] UNIQUEIDENTIFIER NOT NULL,
    [slo_evaluation_id]         UNIQUEIDENTIFIER NULL,
    [object_run_id]             UNIQUEIDENTIFIER NULL,
    [environment_id]            UNIQUEIDENTIFIER NOT NULL,
    [release_id]                UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key]      VARCHAR (150)    NULL,
    [detection_category]        VARCHAR (40)     NOT NULL,
    [alert_severity]            VARCHAR (2)      NOT NULL,
    [owner_role]                VARCHAR (30)     NULL,
    [owner_group_key]           VARCHAR (100)    NULL,
    [routing_alias]             VARCHAR (200)    NULL,
    [delivery_mode]             VARCHAR (30)     NOT NULL,
    [decision_status]           VARCHAR (20)     NOT NULL,
    [deduplication_key]         VARCHAR (64)     NOT NULL,
    [decision_reason]           NVARCHAR (1000)  NOT NULL,
    [detected_at_utc]           DATETIME2 (7)    NOT NULL,
    [routed_at_utc]             DATETIME2 (7)    NOT NULL,
    [created_at_utc]            DATETIME2 (7)    CONSTRAINT [DF_ops_AlertRoutingDecision_created] DEFAULT (sysutcdatetime()) NOT NULL,
    CONSTRAINT [PK_ops_AlertRoutingDecision] PRIMARY KEY CLUSTERED ([alert_routing_decision_id] ASC),
    CONSTRAINT [CK_ops_AlertRoutingDecision_evidence] CHECK
        ([slo_evaluation_id] IS NOT NULL OR [object_run_id] IS NOT NULL),
    CONSTRAINT [CK_ops_AlertRoutingDecision_category] CHECK
        ([detection_category] IN ('FRESHNESS', 'RELIABILITY', 'DURATION', 'QUALITY',
         'QUALITY_ENFORCEMENT', 'ALERT_LATENCY', 'EXECUTION', 'TELEMETRY')),
    CONSTRAINT [CK_ops_AlertRoutingDecision_severity] CHECK ([alert_severity] IN ('P1', 'P2', 'P3', 'P4')),
    CONSTRAINT [CK_ops_AlertRoutingDecision_role] CHECK
        ([owner_role] IS NULL OR [owner_role] IN ('ENGINEERING', 'SOURCE_STEWARD',
         'DATA_PRODUCT', 'OPERATIONS', 'INCIDENT', 'APPROVER')),
    CONSTRAINT [CK_ops_AlertRoutingDecision_delivery] CHECK
        ([delivery_mode] IN ('SIMULATED', 'NOTIFICATION_REQUESTED')),
    CONSTRAINT [CK_ops_AlertRoutingDecision_status] CHECK
        ([decision_status] IN ('ROUTED', 'SUPPRESSED', 'NO_ROUTE')),
    CONSTRAINT [CK_ops_AlertRoutingDecision_p1] CHECK
        ([alert_severity] <> 'P1' OR [decision_status] <> 'SUPPRESSED'),
    CONSTRAINT [CK_ops_AlertRoutingDecision_hash] CHECK (LEN([deduplication_key]) = 64),
    CONSTRAINT [CK_ops_AlertRoutingDecision_route_shape] CHECK
        (([decision_status] = 'NO_ROUTE' AND [owner_role] IS NULL
          AND [owner_group_key] IS NULL AND [routing_alias] IS NULL)
         OR ([decision_status] IN ('ROUTED', 'SUPPRESSED')
             AND [owner_role] IS NOT NULL AND [owner_group_key] IS NOT NULL
             AND [routing_alias] IS NOT NULL
             AND LEN(LTRIM(RTRIM([routing_alias]))) > 0
             AND [routing_alias] NOT LIKE '%@%'
             AND [routing_alias] NOT LIKE '%://%'
             AND [routing_alias] NOT LIKE '%=%')),
    CONSTRAINT [CK_ops_AlertRoutingDecision_time] CHECK
        ([detected_at_utc] <= [routed_at_utc]),
    CONSTRAINT [FK_ops_AlertRoutingDecision_evaluation] FOREIGN KEY ([slo_evaluation_id])
        REFERENCES [ops].[SloEvaluation] ([slo_evaluation_id]),
    CONSTRAINT [FK_ops_AlertRoutingDecision_object_run] FOREIGN KEY ([object_run_id])
        REFERENCES [ops].[ObjectRun] ([object_run_id]),
    CONSTRAINT [FK_ops_AlertRoutingDecision_environment] FOREIGN KEY ([environment_id])
        REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ops_AlertRoutingDecision_release] FOREIGN KEY ([release_id])
        REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [FK_ops_AlertRoutingDecision_object] FOREIGN KEY ([release_id], [ingestion_object_key])
        REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ops_AlertRoutingDecision_owner] FOREIGN KEY ([release_id], [owner_group_key])
        REFERENCES [ctrl].[OwnerGroup] ([release_id], [owner_group_key]),
    CONSTRAINT [UQ_ops_AlertRoutingDecision_dedup] UNIQUE NONCLUSTERED
        ([deduplication_key], [routing_alias])
);
GO

CREATE NONCLUSTERED INDEX [IX_ops_AlertRoutingDecision_review]
    ON [ops].[AlertRoutingDecision]
        ([environment_id], [decision_status], [alert_severity], [routed_at_utc] DESC)
    INCLUDE ([detection_category], [ingestion_object_key], [routing_alias]);
GO
