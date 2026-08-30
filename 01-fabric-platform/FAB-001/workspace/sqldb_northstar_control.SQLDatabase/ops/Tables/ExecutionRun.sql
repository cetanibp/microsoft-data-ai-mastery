CREATE TABLE [ops].[ExecutionRun] (
    [run_id]             UNIQUEIDENTIFIER NOT NULL,
    [environment_id]     UNIQUEIDENTIFIER NOT NULL,
    [release_id]         UNIQUEIDENTIFIER NOT NULL,
    [trigger_type]       VARCHAR (20)     NOT NULL,
    [trigger_reference]  NVARCHAR (300)   NULL,
    [correlation_id]     VARCHAR (100)    NOT NULL,
    [requested_scope]    NVARCHAR (1000)  NOT NULL,
    [configuration_hash] VARCHAR (64)     NOT NULL,
    [run_status]         VARCHAR (20)     NOT NULL,
    [started_at_utc]     DATETIME2 (7)    NOT NULL,
    [completed_at_utc]   DATETIME2 (7)    NULL,
    CONSTRAINT [PK_ops_ExecutionRun] PRIMARY KEY CLUSTERED ([run_id] ASC),
    CONSTRAINT [CK_ops_ExecutionRun_completion] CHECK (([run_status]='RUNNING' OR [run_status]='REQUESTED') AND [completed_at_utc] IS NULL OR ([run_status]='CANCELLED' OR [run_status]='FAILED' OR [run_status]='SUCCEEDED_WITH_WARNINGS' OR [run_status]='SUCCEEDED') AND [completed_at_utc] IS NOT NULL),
    CONSTRAINT [CK_ops_ExecutionRun_hash] CHECK (len([configuration_hash])=(64)),
    CONSTRAINT [CK_ops_ExecutionRun_status] CHECK ([run_status]='CANCELLED' OR [run_status]='FAILED' OR [run_status]='SUCCEEDED_WITH_WARNINGS' OR [run_status]='SUCCEEDED' OR [run_status]='RUNNING' OR [run_status]='REQUESTED'),
    CONSTRAINT [CK_ops_ExecutionRun_trigger] CHECK ([trigger_type]='RECOVERY' OR [trigger_type]='MANUAL' OR [trigger_type]='EVENT' OR [trigger_type]='INTERVAL' OR [trigger_type]='DAILY'),
    CONSTRAINT [FK_ops_ExecutionRun_environment] FOREIGN KEY ([environment_id]) REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ops_ExecutionRun_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [UQ_ops_ExecutionRun_correlation] UNIQUE NONCLUSTERED ([correlation_id] ASC),
    CONSTRAINT [UQ_ops_ExecutionRun_scope] UNIQUE NONCLUSTERED ([run_id] ASC, [environment_id] ASC, [release_id] ASC)
);


GO

