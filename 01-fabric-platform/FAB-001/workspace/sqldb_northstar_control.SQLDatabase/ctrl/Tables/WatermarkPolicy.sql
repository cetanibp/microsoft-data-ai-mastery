CREATE TABLE [ctrl].[WatermarkPolicy] (
    [release_id]            UNIQUEIDENTIFIER NOT NULL,
    [watermark_policy_key]  VARCHAR (100)    NOT NULL,
    [column_name]           NVARCHAR (256)   NOT NULL,
    [logical_data_type]     VARCHAR (20)     NOT NULL,
    [comparison_operator]   VARCHAR (10)     NOT NULL,
    [overlap_amount]        INT              CONSTRAINT [DF_ctrl_WatermarkPolicy_overlap] DEFAULT ((0)) NOT NULL,
    [overlap_unit]          VARCHAR (20)     NULL,
    [initial_value_policy]  VARCHAR (30)     NOT NULL,
    [initial_value_literal] NVARCHAR (4000)  NULL,
    [upper_bound_mode]      VARCHAR (30)     NOT NULL,
    [late_arrival_behavior] VARCHAR (30)     NOT NULL,
    CONSTRAINT [PK_ctrl_WatermarkPolicy] PRIMARY KEY CLUSTERED ([release_id] ASC, [watermark_policy_key] ASC),
    CONSTRAINT [CK_ctrl_WatermarkPolicy_data_type] CHECK ([logical_data_type]='STRING' OR [logical_data_type]='DECIMAL' OR [logical_data_type]='INTEGER' OR [logical_data_type]='BIGINT' OR [logical_data_type]='DATE' OR [logical_data_type]='DATETIME2'),
    CONSTRAINT [CK_ctrl_WatermarkPolicy_initial] CHECK ([initial_value_policy]='BEGINNING' OR [initial_value_policy]='CURRENT_TIME' OR [initial_value_policy]='SOURCE_MINIMUM' OR [initial_value_policy]='EXPLICIT'),
    CONSTRAINT [CK_ctrl_WatermarkPolicy_initial_literal] CHECK ([initial_value_policy]='EXPLICIT' AND [initial_value_literal] IS NOT NULL OR [initial_value_policy]<>'EXPLICIT' AND [initial_value_literal] IS NULL),
    CONSTRAINT [CK_ctrl_WatermarkPolicy_late_arrival] CHECK ([late_arrival_behavior]='NOT_SUPPORTED' OR [late_arrival_behavior]='REPROCESS_WINDOW' OR [late_arrival_behavior]='OVERLAP_AND_DEDUPLICATE'),
    CONSTRAINT [CK_ctrl_WatermarkPolicy_operator] CHECK ([comparison_operator]='<=' OR [comparison_operator]='<' OR [comparison_operator]='>=' OR [comparison_operator]='>'),
    CONSTRAINT [CK_ctrl_WatermarkPolicy_overlap] CHECK ([overlap_amount]>=(0) AND ([overlap_amount]=(0) AND [overlap_unit] IS NULL OR [overlap_amount]>(0) AND ([overlap_unit]='ROW' OR [overlap_unit]='DAY' OR [overlap_unit]='HOUR' OR [overlap_unit]='MINUTE' OR [overlap_unit]='SECOND'))),
    CONSTRAINT [CK_ctrl_WatermarkPolicy_upper_bound] CHECK ([upper_bound_mode]='EXPLICIT' OR [upper_bound_mode]='CURRENT_TIME_AT_START' OR [upper_bound_mode]='SOURCE_MAX_AT_START'),
    CONSTRAINT [FK_ctrl_WatermarkPolicy_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

