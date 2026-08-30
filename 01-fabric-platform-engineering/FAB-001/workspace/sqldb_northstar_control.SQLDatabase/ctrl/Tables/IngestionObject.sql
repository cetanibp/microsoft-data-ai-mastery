CREATE TABLE [ctrl].[IngestionObject] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key] VARCHAR (150)    NOT NULL,
    [display_name]         NVARCHAR (200)   NOT NULL,
    [domain_key]           VARCHAR (100)    NOT NULL,
    [source_object_key]    VARCHAR (150)    NOT NULL,
    [target_object_key]    VARCHAR (150)    NOT NULL,
    [load_policy_key]      VARCHAR (100)    NOT NULL,
    [execution_policy_key] VARCHAR (100)    NOT NULL,
    [is_required]          BIT              NOT NULL,
    CONSTRAINT [PK_ctrl_IngestionObject] PRIMARY KEY CLUSTERED ([release_id] ASC, [ingestion_object_key] ASC),
    CONSTRAINT [FK_ctrl_IngestionObject_execution_policy] FOREIGN KEY ([release_id], [execution_policy_key]) REFERENCES [ctrl].[ExecutionPolicy] ([release_id], [execution_policy_key]),
    CONSTRAINT [FK_ctrl_IngestionObject_load_policy] FOREIGN KEY ([release_id], [load_policy_key]) REFERENCES [ctrl].[LoadPolicy] ([release_id], [load_policy_key]),
    CONSTRAINT [FK_ctrl_IngestionObject_source] FOREIGN KEY ([release_id], [source_object_key]) REFERENCES [ctrl].[SourceObject] ([release_id], [source_object_key]),
    CONSTRAINT [FK_ctrl_IngestionObject_target] FOREIGN KEY ([release_id], [target_object_key]) REFERENCES [ctrl].[TargetObject] ([release_id], [target_object_key])
);


GO

CREATE NONCLUSTERED INDEX [IX_ctrl_IngestionObject_selection]
    ON [ctrl].[IngestionObject]([release_id] ASC, [domain_key] ASC, [ingestion_object_key] ASC);


GO

