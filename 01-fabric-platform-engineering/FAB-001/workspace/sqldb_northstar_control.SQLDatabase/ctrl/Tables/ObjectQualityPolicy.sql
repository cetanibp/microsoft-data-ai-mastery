CREATE TABLE [ctrl].[ObjectQualityPolicy] (
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key] VARCHAR (150)    NOT NULL,
    [quality_policy_key]   VARCHAR (100)    NOT NULL,
    [evaluation_order]     SMALLINT         NOT NULL,
    CONSTRAINT [PK_ctrl_ObjectQualityPolicy] PRIMARY KEY CLUSTERED ([release_id] ASC, [ingestion_object_key] ASC, [quality_policy_key] ASC),
    CONSTRAINT [CK_ctrl_ObjectQualityPolicy_order] CHECK ([evaluation_order]>=(1) AND [evaluation_order]<=(1000)),
    CONSTRAINT [FK_ctrl_ObjectQualityPolicy_object] FOREIGN KEY ([release_id], [ingestion_object_key]) REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ctrl_ObjectQualityPolicy_policy] FOREIGN KEY ([release_id], [quality_policy_key]) REFERENCES [ctrl].[QualityPolicy] ([release_id], [quality_policy_key]),
    CONSTRAINT [UQ_ctrl_ObjectQualityPolicy_order] UNIQUE NONCLUSTERED ([release_id] ASC, [ingestion_object_key] ASC, [evaluation_order] ASC)
);


GO

