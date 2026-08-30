CREATE TABLE [ctrl].[SourceEnvironmentConfig] (
    [release_id]                 UNIQUEIDENTIFIER NOT NULL,
    [environment_id]             UNIQUEIDENTIFIER NOT NULL,
    [source_system_key]          VARCHAR (100)    NOT NULL,
    [connection_reference_key]   VARCHAR (100)    NOT NULL,
    [landing_zone_key]           VARCHAR (100)    NOT NULL,
    [max_connection_concurrency] SMALLINT         NOT NULL,
    [is_enabled]                 BIT              NOT NULL,
    CONSTRAINT [PK_ctrl_SourceEnvironmentConfig] PRIMARY KEY CLUSTERED ([release_id] ASC, [environment_id] ASC, [source_system_key] ASC),
    CONSTRAINT [CK_ctrl_SourceEnvironmentConfig_concurrency] CHECK ([max_connection_concurrency]>=(1) AND [max_connection_concurrency]<=(100)),
    CONSTRAINT [CK_ctrl_SourceEnvironmentConfig_safe_values] CHECK (NOT [connection_reference_key] like '%://%' AND NOT [connection_reference_key] like '%=%' AND NOT [connection_reference_key] like '%@%' AND NOT [landing_zone_key] like '%://%' AND NOT [landing_zone_key] like '%=%' AND NOT [landing_zone_key] like '%@%'),
    CONSTRAINT [FK_ctrl_SourceEnvironmentConfig_environment] FOREIGN KEY ([environment_id]) REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ctrl_SourceEnvironmentConfig_source] FOREIGN KEY ([release_id], [source_system_key]) REFERENCES [ctrl].[SourceSystem] ([release_id], [source_system_key])
);


GO

