CREATE TABLE [ctrl].[LoadPolicy] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [load_policy_key]      VARCHAR (100)    NOT NULL,
    [strategy_type]        VARCHAR (20)     NOT NULL,
    [watermark_policy_key] VARCHAR (100)    NULL,
    [duplicate_behavior]   VARCHAR (30)     NOT NULL,
    [delete_behavior]      VARCHAR (30)     NOT NULL,
    [schema_behavior]      VARCHAR (30)     NOT NULL,
    [idempotency_contract] NVARCHAR (1000)  NOT NULL,
    CONSTRAINT [PK_ctrl_LoadPolicy] PRIMARY KEY CLUSTERED ([release_id] ASC, [load_policy_key] ASC),
    CONSTRAINT [CK_ctrl_LoadPolicy_delete] CHECK ([delete_behavior]='SNAPSHOT_RECONCILE' OR [delete_behavior]='HARD_DELETE' OR [delete_behavior]='SOFT_DELETE' OR [delete_behavior]='IGNORE'),
    CONSTRAINT [CK_ctrl_LoadPolicy_duplicate] CHECK ([duplicate_behavior]='DEDUPLICATE_BY_KEY' OR [duplicate_behavior]='UPSERT_BY_KEY' OR [duplicate_behavior]='IGNORE' OR [duplicate_behavior]='REJECT'),
    CONSTRAINT [CK_ctrl_LoadPolicy_schema] CHECK ([schema_behavior]='ROUTE_FOR_REVIEW' OR [schema_behavior]='ALLOW_ADDITIVE' OR [schema_behavior]='QUARANTINE' OR [schema_behavior]='FAIL'),
    CONSTRAINT [CK_ctrl_LoadPolicy_strategy] CHECK ([strategy_type]='SNAPSHOT' OR [strategy_type]='APPEND' OR [strategy_type]='WATERMARK' OR [strategy_type]='FULL'),
    CONSTRAINT [CK_ctrl_LoadPolicy_watermark_usage] CHECK ([strategy_type]='WATERMARK' AND [watermark_policy_key] IS NOT NULL OR [strategy_type]<>'WATERMARK' AND [watermark_policy_key] IS NULL),
    CONSTRAINT [FK_ctrl_LoadPolicy_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [FK_ctrl_LoadPolicy_watermark] FOREIGN KEY ([release_id], [watermark_policy_key]) REFERENCES [ctrl].[WatermarkPolicy] ([release_id], [watermark_policy_key])
);


GO

