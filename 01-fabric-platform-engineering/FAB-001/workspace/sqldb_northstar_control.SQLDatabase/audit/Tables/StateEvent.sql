CREATE TABLE [audit].[StateEvent] (
    [state_event_id]  UNIQUEIDENTIFIER NOT NULL,
    [environment_id]  UNIQUEIDENTIFIER NOT NULL,
    [release_id]      UNIQUEIDENTIFIER NOT NULL,
    [run_id]          UNIQUEIDENTIFIER NULL,
    [object_run_id]   UNIQUEIDENTIFIER NULL,
    [event_type]      VARCHAR (40)     NOT NULL,
    [actor_identity]  NVARCHAR (200)   NOT NULL,
    [reason]          NVARCHAR (2000)  NOT NULL,
    [correlation_id]  VARCHAR (100)    NOT NULL,
    [before_hash]     VARCHAR (64)     NULL,
    [after_hash]      VARCHAR (64)     NULL,
    [occurred_at_utc] DATETIME2 (7)    CONSTRAINT [DF_audit_StateEvent_occurred_at] DEFAULT (sysutcdatetime()) NOT NULL,
    CONSTRAINT [PK_audit_StateEvent] PRIMARY KEY CLUSTERED ([state_event_id] ASC),
    CONSTRAINT [CK_audit_StateEvent_after_hash] CHECK ([after_hash] IS NULL OR len([after_hash])=(64)),
    CONSTRAINT [CK_audit_StateEvent_before_hash] CHECK ([before_hash] IS NULL OR len([before_hash])=(64)),
    CONSTRAINT [CK_audit_StateEvent_type] CHECK ([event_type]='RECOVERY_REQUESTED' OR [event_type]='STATE_CORRECTED' OR [event_type]='WATERMARK_ABANDONED' OR [event_type]='WATERMARK_COMMITTED' OR [event_type]='WATERMARK_PROPOSED' OR [event_type]='STATUS_CHANGED' OR [event_type]='OBJECT_CLAIMED' OR [event_type]='RUN_REQUESTED' OR [event_type]='RELEASE_ACTIVATED'),
    CONSTRAINT [FK_audit_StateEvent_environment] FOREIGN KEY ([environment_id]) REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_audit_StateEvent_object_run] FOREIGN KEY ([object_run_id]) REFERENCES [ops].[ObjectRun] ([object_run_id]),
    CONSTRAINT [FK_audit_StateEvent_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [FK_audit_StateEvent_run] FOREIGN KEY ([run_id]) REFERENCES [ops].[ExecutionRun] ([run_id])
);


GO

CREATE NONCLUSTERED INDEX [IX_audit_StateEvent_correlation]
    ON [audit].[StateEvent]([correlation_id] ASC, [occurred_at_utc] ASC);


GO

