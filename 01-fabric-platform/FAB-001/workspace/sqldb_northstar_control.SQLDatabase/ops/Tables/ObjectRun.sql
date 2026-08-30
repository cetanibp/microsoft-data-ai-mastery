CREATE TABLE [ops].[ObjectRun] (
    [object_run_id]        UNIQUEIDENTIFIER NOT NULL,
    [run_id]               UNIQUEIDENTIFIER NOT NULL,
    [environment_id]       UNIQUEIDENTIFIER NOT NULL,
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key] VARCHAR (150)    NOT NULL,
    [attempt_number]       SMALLINT         NOT NULL,
    [object_run_status]    VARCHAR (30)     NOT NULL,
    [input_boundary_hash]  VARCHAR (64)     NOT NULL,
    [extracted_row_count]  BIGINT           NULL,
    [accepted_row_count]   BIGINT           NULL,
    [rejected_row_count]   BIGINT           NULL,
    [error_classification] VARCHAR (50)     NULL,
    [error_summary]        NVARCHAR (2000)  NULL,
    [started_at_utc]       DATETIME2 (7)    NOT NULL,
    [completed_at_utc]     DATETIME2 (7)    NULL,
    CONSTRAINT [PK_ops_ObjectRun] PRIMARY KEY CLUSTERED ([object_run_id] ASC),
    CONSTRAINT [CK_ops_ObjectRun_attempt] CHECK ([attempt_number]>=(1) AND [attempt_number]<=(100)),
    CONSTRAINT [CK_ops_ObjectRun_completion] CHECK (([object_run_status]='PUBLISHING' OR [object_run_status]='VALIDATING' OR [object_run_status]='EXTRACTING' OR [object_run_status]='CLAIMED' OR [object_run_status]='REQUESTED') AND [completed_at_utc] IS NULL OR ([object_run_status]='RECOVERY_REQUIRED' OR [object_run_status]='CANCELLED' OR [object_run_status]='FAILED' OR [object_run_status]='SUCCEEDED_WITH_WARNINGS' OR [object_run_status]='SUCCEEDED') AND [completed_at_utc] IS NOT NULL),
    CONSTRAINT [CK_ops_ObjectRun_counts] CHECK (([extracted_row_count] IS NULL OR [extracted_row_count]>=(0)) AND ([accepted_row_count] IS NULL OR [accepted_row_count]>=(0)) AND ([rejected_row_count] IS NULL OR [rejected_row_count]>=(0))),
    CONSTRAINT [CK_ops_ObjectRun_hash] CHECK (len([input_boundary_hash])=(64)),
    CONSTRAINT [CK_ops_ObjectRun_status] CHECK ([object_run_status]='RECOVERY_REQUIRED' OR [object_run_status]='CANCELLED' OR [object_run_status]='FAILED' OR [object_run_status]='SUCCEEDED_WITH_WARNINGS' OR [object_run_status]='SUCCEEDED' OR [object_run_status]='PUBLISHING' OR [object_run_status]='VALIDATING' OR [object_run_status]='EXTRACTING' OR [object_run_status]='CLAIMED' OR [object_run_status]='REQUESTED'),
    CONSTRAINT [FK_ops_ObjectRun_object] FOREIGN KEY ([release_id], [ingestion_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ops_ObjectRun_run_scope] FOREIGN KEY ([run_id], [environment_id], [release_id]) REFERENCES [ops].[ExecutionRun] ([run_id], [environment_id], [release_id]),
    CONSTRAINT [UQ_ops_ObjectRun_attempt] UNIQUE NONCLUSTERED ([run_id] ASC, [ingestion_object_key] ASC, [attempt_number] ASC)
);


GO

CREATE NONCLUSTERED INDEX [IX_ops_ObjectRun_status]
    ON [ops].[ObjectRun]([environment_id] ASC, [object_run_status] ASC, [ingestion_object_key] ASC, [started_at_utc] ASC);


GO

