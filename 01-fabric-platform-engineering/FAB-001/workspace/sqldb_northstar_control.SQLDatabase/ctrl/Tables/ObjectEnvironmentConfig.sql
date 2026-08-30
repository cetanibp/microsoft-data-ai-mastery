CREATE TABLE [ctrl].[ObjectEnvironmentConfig] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [environment_id]       UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key] VARCHAR (150)    NOT NULL,
    [is_enabled]           BIT              NOT NULL,
    [priority_override]    TINYINT          NULL,
    [routing_alias]        VARCHAR (100)    NOT NULL,
    CONSTRAINT [PK_ctrl_ObjectEnvironmentConfig] PRIMARY KEY CLUSTERED ([release_id] ASC, [environment_id] ASC, [ingestion_object_key] ASC),
    CONSTRAINT [CK_ctrl_ObjectEnvironmentConfig_priority] CHECK ([priority_override] IS NULL OR [priority_override]>=(1) AND [priority_override]<=(100)),
    CONSTRAINT [CK_ctrl_ObjectEnvironmentConfig_routing] CHECK (NOT [routing_alias] like '%://%' AND NOT [routing_alias] like '%=%' AND NOT [routing_alias] like '%@%'),
    CONSTRAINT [FK_ctrl_ObjectEnvironmentConfig_environment] FOREIGN KEY ([environment_id]) REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ctrl_ObjectEnvironmentConfig_object] FOREIGN KEY ([release_id], [ingestion_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key])
);


GO

CREATE NONCLUSTERED INDEX [IX_ctrl_ObjectEnvironmentConfig_enabled]
    ON [ctrl].[ObjectEnvironmentConfig]([environment_id] ASC, [release_id] ASC, [is_enabled] ASC, [ingestion_object_key] ASC);


GO

