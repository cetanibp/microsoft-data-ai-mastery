CREATE TABLE [ctrl].[OwnerGroup] (
    [release_id]      UNIQUEIDENTIFIER NOT NULL,
    [owner_group_key] VARCHAR (100)    NOT NULL,
    [display_name]    NVARCHAR (200)   NOT NULL,
    [routing_alias]   VARCHAR (200)    NOT NULL,
    CONSTRAINT [PK_ctrl_OwnerGroup] PRIMARY KEY CLUSTERED ([release_id] ASC, [owner_group_key] ASC),
    CONSTRAINT [CK_ctrl_OwnerGroup_routing_alias] CHECK (NOT [routing_alias] like '%@%' AND NOT [routing_alias] like '%://%' AND NOT [routing_alias] like '%=%'),
    CONSTRAINT [FK_ctrl_OwnerGroup_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

