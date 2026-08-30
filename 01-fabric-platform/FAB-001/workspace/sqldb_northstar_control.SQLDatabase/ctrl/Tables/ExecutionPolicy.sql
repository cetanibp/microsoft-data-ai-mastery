CREATE TABLE [ctrl].[ExecutionPolicy] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [execution_policy_key] VARCHAR (100)    NOT NULL,
    [timeout_minutes]      INT              NOT NULL,
    [max_retries]          INT              NOT NULL,
    [retry_delay_seconds]  INT              NOT NULL,
    [default_priority]     TINYINT          NOT NULL,
    [concurrency_group]    VARCHAR (100)    NOT NULL,
    [max_parallelism]      SMALLINT         NOT NULL,
    [recovery_mode]        VARCHAR (30)     NOT NULL,
    CONSTRAINT [PK_ctrl_ExecutionPolicy] PRIMARY KEY CLUSTERED ([release_id] ASC, [execution_policy_key] ASC),
    CONSTRAINT [CK_ctrl_ExecutionPolicy_parallelism] CHECK ([max_parallelism]>=(1) AND [max_parallelism]<=(100)),
    CONSTRAINT [CK_ctrl_ExecutionPolicy_priority] CHECK ([default_priority]>=(1) AND [default_priority]<=(100)),
    CONSTRAINT [CK_ctrl_ExecutionPolicy_recovery] CHECK ([recovery_mode]='MANUAL_REVIEW' OR [recovery_mode]='FORWARD_RECOVERY' OR [recovery_mode]='REPLAY_RANGE' OR [recovery_mode]='RESTART_SAFE'),
    CONSTRAINT [CK_ctrl_ExecutionPolicy_retries] CHECK ([max_retries]>=(0) AND [max_retries]<=(10)),
    CONSTRAINT [CK_ctrl_ExecutionPolicy_retry_delay] CHECK ([retry_delay_seconds]>=(0) AND [retry_delay_seconds]<=(86400)),
    CONSTRAINT [CK_ctrl_ExecutionPolicy_timeout] CHECK ([timeout_minutes]>=(1) AND [timeout_minutes]<=(1440)),
    CONSTRAINT [FK_ctrl_ExecutionPolicy_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

