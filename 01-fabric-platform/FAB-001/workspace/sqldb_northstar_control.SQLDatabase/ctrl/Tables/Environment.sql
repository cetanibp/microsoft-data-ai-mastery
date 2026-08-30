CREATE TABLE [ctrl].[Environment] (
    [environment_id]   UNIQUEIDENTIFIER NOT NULL,
    [environment_code] VARCHAR (20)     NOT NULL,
    [environment_name] NVARCHAR (100)   NOT NULL,
    [is_production]    BIT              CONSTRAINT [DF_ctrl_Environment_is_production] DEFAULT ((0)) NOT NULL,
    [created_at_utc]   DATETIME2 (7)    CONSTRAINT [DF_ctrl_Environment_created_at] DEFAULT (sysutcdatetime()) NOT NULL,
    CONSTRAINT [PK_ctrl_Environment] PRIMARY KEY CLUSTERED ([environment_id] ASC),
    CONSTRAINT [CK_ctrl_Environment_code] CHECK ([environment_code]='production' OR [environment_code]='test' OR [environment_code]='development'),
    CONSTRAINT [UQ_ctrl_Environment_code] UNIQUE NONCLUSTERED ([environment_code] ASC)
);


GO

