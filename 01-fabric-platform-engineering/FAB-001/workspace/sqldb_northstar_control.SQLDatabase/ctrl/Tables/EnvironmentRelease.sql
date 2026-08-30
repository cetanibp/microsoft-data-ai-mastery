CREATE TABLE [ctrl].[EnvironmentRelease] (
    [environment_id]     UNIQUEIDENTIFIER NOT NULL,
    [release_id]         UNIQUEIDENTIFIER NOT NULL,
    [prior_release_id]   UNIQUEIDENTIFIER NULL,
    [approval_reference] NVARCHAR (300)   NOT NULL,
    [activation_reason]  NVARCHAR (1000)  NOT NULL,
    [activated_by]       NVARCHAR (200)   NOT NULL,
    [activated_at_utc]   DATETIME2 (7)    CONSTRAINT [DF_ctrl_EnvironmentRelease_activated_at] DEFAULT (sysutcdatetime()) NOT NULL,
    CONSTRAINT [PK_ctrl_EnvironmentRelease] PRIMARY KEY CLUSTERED ([environment_id] ASC),
    CONSTRAINT [CK_ctrl_EnvironmentRelease_distinct] CHECK ([prior_release_id] IS NULL OR [prior_release_id]<>[release_id]),
    CONSTRAINT [FK_ctrl_EnvironmentRelease_environment] FOREIGN KEY ([environment_id]) REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ctrl_EnvironmentRelease_prior_release] FOREIGN KEY ([prior_release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [FK_ctrl_EnvironmentRelease_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

