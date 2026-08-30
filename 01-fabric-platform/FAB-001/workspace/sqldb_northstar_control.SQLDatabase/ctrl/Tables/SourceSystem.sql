CREATE TABLE [ctrl].[SourceSystem] (
    [release_id]             UNIQUEIDENTIFIER NOT NULL,
    [source_system_key]      VARCHAR (100)    NOT NULL,
    [source_system_name]     NVARCHAR (200)   NOT NULL,
    [domain_key]             VARCHAR (100)    NOT NULL,
    [source_type]            VARCHAR (30)     NOT NULL,
    [default_connection_key] VARCHAR (100)    NOT NULL,
    [data_classification]    VARCHAR (30)     NOT NULL,
    CONSTRAINT [PK_ctrl_SourceSystem] PRIMARY KEY CLUSTERED ([release_id] ASC, [source_system_key] ASC),
    CONSTRAINT [CK_ctrl_SourceSystem_classification] CHECK ([data_classification]='RESTRICTED' OR [data_classification]='CONFIDENTIAL' OR [data_classification]='INTERNAL' OR [data_classification]='PUBLIC'),
    CONSTRAINT [CK_ctrl_SourceSystem_connection_key] CHECK (NOT [default_connection_key] like '%://%' AND NOT [default_connection_key] like '%=%' AND NOT [default_connection_key] like '%@%'),
    CONSTRAINT [CK_ctrl_SourceSystem_source_type] CHECK ([source_type]='EVENT_STREAM' OR [source_type]='FILE' OR [source_type]='REST_API' OR [source_type]='ORACLE_DATABASE' OR [source_type]='SQL_DATABASE'),
    CONSTRAINT [FK_ctrl_SourceSystem_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

