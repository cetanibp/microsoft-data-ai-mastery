CREATE TABLE [ctrl].[SourceObject] (
    [release_id]            UNIQUEIDENTIFIER NOT NULL,
    [source_object_key]     VARCHAR (150)    NOT NULL,
    [source_system_key]     VARCHAR (100)    NOT NULL,
    [namespace_name]        NVARCHAR (256)   NOT NULL,
    [object_name]           NVARCHAR (256)   NOT NULL,
    [object_type]           VARCHAR (30)     NOT NULL,
    [business_key_contract] NVARCHAR (1000)  NULL,
    [schema_drift_policy]   VARCHAR (30)     NOT NULL,
    [data_classification]   VARCHAR (30)     NOT NULL,
    CONSTRAINT [PK_ctrl_SourceObject] PRIMARY KEY CLUSTERED ([release_id] ASC, [source_object_key] ASC),
    CONSTRAINT [CK_ctrl_SourceObject_classification] CHECK ([data_classification]='RESTRICTED' OR [data_classification]='CONFIDENTIAL' OR [data_classification]='INTERNAL' OR [data_classification]='PUBLIC'),
    CONSTRAINT [CK_ctrl_SourceObject_drift] CHECK ([schema_drift_policy]='ROUTE_FOR_REVIEW' OR [schema_drift_policy]='ALLOW_ADDITIVE' OR [schema_drift_policy]='QUARANTINE' OR [schema_drift_policy]='FAIL'),
    CONSTRAINT [CK_ctrl_SourceObject_type] CHECK ([object_type]='EVENT' OR [object_type]='FILE_SET' OR [object_type]='QUERY' OR [object_type]='VIEW' OR [object_type]='TABLE'),
    CONSTRAINT [FK_ctrl_SourceObject_system] FOREIGN KEY ([release_id], [source_system_key]) REFERENCES [ctrl].[SourceSystem] ([release_id], [source_system_key]),
    CONSTRAINT [UQ_ctrl_SourceObject_name] UNIQUE NONCLUSTERED ([release_id] ASC, [source_system_key] ASC, [namespace_name] ASC, [object_name] ASC)
);


GO

