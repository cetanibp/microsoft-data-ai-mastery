CREATE TABLE [ops].[WatermarkCandidate] (
    [candidate_id]           UNIQUEIDENTIFIER NOT NULL,
    [object_run_id]          UNIQUEIDENTIFIER NOT NULL,
    [environment_id]         UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key]   VARCHAR (150)    NOT NULL,
    [logical_value_type]     VARCHAR (20)     NOT NULL,
    [from_value]             NVARCHAR (4000)  NOT NULL,
    [to_value]               NVARCHAR (4000)  NOT NULL,
    [observed_state_version] BIGINT           NOT NULL,
    [candidate_status]       VARCHAR (20)     NOT NULL,
    [proposed_at_utc]        DATETIME2 (7)    NOT NULL,
    [resolved_at_utc]        DATETIME2 (7)    NULL,
    [resolution_reason]      NVARCHAR (1000)  NULL,
    CONSTRAINT [PK_ops_WatermarkCandidate] PRIMARY KEY CLUSTERED ([candidate_id] ASC),
    CONSTRAINT [CK_ops_WatermarkCandidate_resolution] CHECK ([candidate_status]='PROPOSED' AND [resolved_at_utc] IS NULL AND [resolution_reason] IS NULL OR ([candidate_status]='ABANDONED' OR [candidate_status]='COMMITTED') AND [resolved_at_utc] IS NOT NULL AND [resolution_reason] IS NOT NULL),
    CONSTRAINT [CK_ops_WatermarkCandidate_status] CHECK ([candidate_status]='ABANDONED' OR [candidate_status]='COMMITTED' OR [candidate_status]='PROPOSED'),
    CONSTRAINT [CK_ops_WatermarkCandidate_type] CHECK ([logical_value_type]='STRING' OR [logical_value_type]='DECIMAL' OR [logical_value_type]='INTEGER' OR [logical_value_type]='BIGINT' OR [logical_value_type]='DATE' OR [logical_value_type]='DATETIME2'),
    CONSTRAINT [CK_ops_WatermarkCandidate_version] CHECK ([observed_state_version]>=(0)),
    CONSTRAINT [FK_ops_WatermarkCandidate_object_run] FOREIGN KEY ([object_run_id]) REFERENCES [ops].[ObjectRun] ([object_run_id]),
    CONSTRAINT [FK_ops_WatermarkCandidate_state] FOREIGN KEY ([environment_id], [ingestion_object_key]) REFERENCES [ops].[WatermarkState] ([environment_id], [ingestion_object_key]),
    CONSTRAINT [UQ_ops_WatermarkCandidate_object_run] UNIQUE NONCLUSTERED ([object_run_id] ASC)
);


GO

CREATE NONCLUSTERED INDEX [IX_ops_WatermarkCandidate_status]
    ON [ops].[WatermarkCandidate]([environment_id] ASC, [candidate_status] ASC, [ingestion_object_key] ASC, [proposed_at_utc] ASC);


GO

