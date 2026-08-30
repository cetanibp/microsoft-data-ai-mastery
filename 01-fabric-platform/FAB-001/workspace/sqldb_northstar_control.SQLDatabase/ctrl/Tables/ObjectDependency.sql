CREATE TABLE [ctrl].[ObjectDependency] (
    [release_id]             UNIQUEIDENTIFIER NOT NULL,
    [predecessor_object_key] VARCHAR (150)    NOT NULL,
    [successor_object_key]   VARCHAR (150)    NOT NULL,
    [dependency_condition]   VARCHAR (30)     NOT NULL,
    [is_optional]            BIT              NOT NULL,
    CONSTRAINT [PK_ctrl_ObjectDependency] PRIMARY KEY CLUSTERED ([release_id] ASC, [predecessor_object_key] ASC, [successor_object_key] ASC),
    CONSTRAINT [CK_ctrl_ObjectDependency_condition] CHECK ([dependency_condition]='OPTIONAL' OR [dependency_condition]='DATA_AVAILABLE' OR [dependency_condition]='COMPLETION' OR [dependency_condition]='SUCCESS'),
    CONSTRAINT [CK_ctrl_ObjectDependency_distinct] CHECK ([predecessor_object_key]<>[successor_object_key]),
    CONSTRAINT [FK_ctrl_ObjectDependency_predecessor] FOREIGN KEY ([release_id], [predecessor_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ctrl_ObjectDependency_successor] FOREIGN KEY ([release_id], [successor_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key])
);


GO

CREATE NONCLUSTERED INDEX [IX_ctrl_ObjectDependency_successor]
    ON [ctrl].[ObjectDependency]([release_id] ASC, [successor_object_key] ASC, [predecessor_object_key] ASC);


GO

