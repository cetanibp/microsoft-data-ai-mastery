CREATE TABLE [ctrl].[MetadataRelease] (
    [release_id]        UNIQUEIDENTIFIER NOT NULL,
    [release_version]   VARCHAR (50)     NOT NULL,
    [release_status]    VARCHAR (20)     NOT NULL,
    [content_hash]      VARCHAR (64)     NOT NULL,
    [source_commit_sha] VARCHAR (40)     NOT NULL,
    [change_reason]     NVARCHAR (1000)  NOT NULL,
    [created_by]        NVARCHAR (200)   NOT NULL,
    [created_at_utc]    DATETIME2 (7)    CONSTRAINT [DF_ctrl_MetadataRelease_created_at] DEFAULT (sysutcdatetime()) NOT NULL,
    [approved_by]       NVARCHAR (200)   NULL,
    [approved_at_utc]   DATETIME2 (7)    NULL,
    CONSTRAINT [PK_ctrl_MetadataRelease] PRIMARY KEY CLUSTERED ([release_id] ASC),
    CONSTRAINT [CK_ctrl_MetadataRelease_approval] CHECK ([release_status]='REJECTED' OR [release_status]='DRAFT' OR [approved_by] IS NOT NULL AND [approved_at_utc] IS NOT NULL),
    CONSTRAINT [CK_ctrl_MetadataRelease_commit] CHECK (len([source_commit_sha])=(40)),
    CONSTRAINT [CK_ctrl_MetadataRelease_hash] CHECK (len([content_hash])=(64)),
    CONSTRAINT [CK_ctrl_MetadataRelease_status] CHECK ([release_status]='RETIRED' OR [release_status]='SUPERSEDED' OR [release_status]='ACTIVE' OR [release_status]='APPROVED' OR [release_status]='REJECTED' OR [release_status]='DRAFT'),
    CONSTRAINT [UQ_ctrl_MetadataRelease_version] UNIQUE NONCLUSTERED ([release_version] ASC)
);


GO

