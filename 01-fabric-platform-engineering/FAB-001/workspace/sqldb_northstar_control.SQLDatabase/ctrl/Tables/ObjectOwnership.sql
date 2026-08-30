CREATE TABLE [ctrl].[ObjectOwnership] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key] VARCHAR (150)    NOT NULL,
    [owner_group_key]      VARCHAR (100)    NOT NULL,
    [ownership_role]       VARCHAR (30)     NOT NULL,
    CONSTRAINT [PK_ctrl_ObjectOwnership] PRIMARY KEY CLUSTERED ([release_id] ASC, [ingestion_object_key] ASC, [owner_group_key] ASC, [ownership_role] ASC),
    CONSTRAINT [CK_ctrl_ObjectOwnership_role] CHECK ([ownership_role]='APPROVER' OR [ownership_role]='INCIDENT' OR [ownership_role]='OPERATIONS' OR [ownership_role]='DATA_PRODUCT' OR [ownership_role]='SOURCE_STEWARD' OR [ownership_role]='ENGINEERING'),
    CONSTRAINT [FK_ctrl_ObjectOwnership_object] FOREIGN KEY ([release_id], [ingestion_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ctrl_ObjectOwnership_owner] FOREIGN KEY ([release_id], [owner_group_key]) REFERENCES [ctrl].[OwnerGroup] ([release_id], [owner_group_key])
);


GO

