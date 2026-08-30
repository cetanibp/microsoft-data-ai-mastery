CREATE TABLE [ctrl].[ObjectSlo] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key] VARCHAR (150)    NOT NULL,
    [slo_key]              VARCHAR (100)    NOT NULL,
    [blocks_publication]   BIT              NOT NULL,
    CONSTRAINT [PK_ctrl_ObjectSlo] PRIMARY KEY CLUSTERED ([release_id] ASC, [ingestion_object_key] ASC, [slo_key] ASC),
    CONSTRAINT [FK_ctrl_ObjectSlo_object] FOREIGN KEY ([release_id], [ingestion_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ctrl_ObjectSlo_slo] FOREIGN KEY ([release_id], [slo_key]) REFERENCES [ctrl].[SloDefinition] ([release_id], [slo_key])
);


GO

