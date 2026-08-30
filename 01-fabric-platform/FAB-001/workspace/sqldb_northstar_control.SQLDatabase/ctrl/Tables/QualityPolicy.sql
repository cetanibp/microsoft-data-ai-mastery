CREATE TABLE [ctrl].[QualityPolicy] (
    [release_id]          UNIQUEIDENTIFIER NOT NULL,
    [quality_policy_key]  VARCHAR (100)    NOT NULL,
    [policy_version]      VARCHAR (50)     NOT NULL,
    [enforcement_level]   VARCHAR (10)     NOT NULL,
    [quarantine_required] BIT              NOT NULL,
    [contract_reference]  NVARCHAR (500)   NOT NULL,
    CONSTRAINT [PK_ctrl_QualityPolicy] PRIMARY KEY CLUSTERED ([release_id] ASC, [quality_policy_key] ASC),
    CONSTRAINT [CK_ctrl_QualityPolicy_enforcement] CHECK ([enforcement_level]='WARN' OR [enforcement_level]='BLOCK'),
    CONSTRAINT [FK_ctrl_QualityPolicy_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

