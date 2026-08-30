CREATE TABLE [ops].[WatermarkState] (
    [environment_id]          UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key]    VARCHAR (150)    NOT NULL,
    [definition_release_id]   UNIQUEIDENTIFIER NOT NULL,
    [logical_value_type]      VARCHAR (20)     NOT NULL,
    [committed_value]         NVARCHAR (4000)  NOT NULL,
    [state_version]           BIGINT           NOT NULL,
    [committed_object_run_id] UNIQUEIDENTIFIER NULL,
    [committed_at_utc]        DATETIME2 (7)    NOT NULL,
    [row_version]             ROWVERSION       NOT NULL,
    CONSTRAINT [PK_ops_WatermarkState] PRIMARY KEY CLUSTERED ([environment_id] ASC, [ingestion_object_key] ASC),
    CONSTRAINT [CK_ops_WatermarkState_type] CHECK ([logical_value_type]='STRING' OR [logical_value_type]='DECIMAL' OR [logical_value_type]='INTEGER' OR [logical_value_type]='BIGINT' OR [logical_value_type]='DATE' OR [logical_value_type]='DATETIME2'),
    CONSTRAINT [CK_ops_WatermarkState_version] CHECK ([state_version]>=(0)),
    CONSTRAINT [FK_ops_WatermarkState_definition] FOREIGN KEY ([definition_release_id], [ingestion_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ops_WatermarkState_environment] FOREIGN KEY ([environment_id]) REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ops_WatermarkState_object_run] FOREIGN KEY ([committed_object_run_id]) REFERENCES [ops].[ObjectRun] ([object_run_id])
);


GO

