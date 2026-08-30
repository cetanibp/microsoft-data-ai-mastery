CREATE TABLE [ctrl].[TargetObject] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [target_object_key]    VARCHAR (150)    NOT NULL,
    [target_layer]         VARCHAR (20)     NOT NULL,
    [store_alias]          VARCHAR (100)    NOT NULL,
    [namespace_name]       NVARCHAR (256)   NOT NULL,
    [object_name]          NVARCHAR (256)   NOT NULL,
    [write_disposition]    VARCHAR (30)     NOT NULL,
    [publication_boundary] VARCHAR (30)     NOT NULL,
    CONSTRAINT [PK_ctrl_TargetObject] PRIMARY KEY CLUSTERED ([release_id] ASC, [target_object_key] ASC),
    CONSTRAINT [CK_ctrl_TargetObject_layer] CHECK ([target_layer]='DATA_PRODUCT' OR [target_layer]='GOLD' OR [target_layer]='SILVER' OR [target_layer]='BRONZE'),
    CONSTRAINT [CK_ctrl_TargetObject_publication] CHECK ([publication_boundary]='PUBLISHED' OR [publication_boundary]='QUALITY_GATED' OR [publication_boundary]='INTERNAL_STAGE'),
    CONSTRAINT [CK_ctrl_TargetObject_store_alias] CHECK (NOT [store_alias] like '%://%' AND NOT [store_alias] like '%=%' AND NOT [store_alias] like '%@%'),
    CONSTRAINT [CK_ctrl_TargetObject_write] CHECK ([write_disposition]='SNAPSHOT' OR [write_disposition]='MERGE' OR [write_disposition]='APPEND' OR [write_disposition]='REPLACE'),
    CONSTRAINT [FK_ctrl_TargetObject_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [UQ_ctrl_TargetObject_name] UNIQUE NONCLUSTERED ([release_id] ASC, [store_alias] ASC, [namespace_name] ASC, [object_name] ASC)
);


GO

