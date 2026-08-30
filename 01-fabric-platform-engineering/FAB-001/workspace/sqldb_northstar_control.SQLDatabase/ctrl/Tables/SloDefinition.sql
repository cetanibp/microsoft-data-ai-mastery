CREATE TABLE [ctrl].[SloDefinition] (
    [release_id]          UNIQUEIDENTIFIER NOT NULL,
    [slo_key]             VARCHAR (100)    NOT NULL,
    [metric_type]         VARCHAR (20)     NOT NULL,
    [comparison_operator] VARCHAR (10)     NOT NULL,
    [target_value]        DECIMAL (19, 6)  NOT NULL,
    [target_unit]         VARCHAR (30)     NOT NULL,
    [evaluation_window]   VARCHAR (30)     NOT NULL,
    [severity]            VARCHAR (20)     NOT NULL,
    [breach_policy]       VARCHAR (30)     NOT NULL,
    CONSTRAINT [PK_ctrl_SloDefinition] PRIMARY KEY CLUSTERED ([release_id] ASC, [slo_key] ASC),
    CONSTRAINT [CK_ctrl_SloDefinition_breach] CHECK ([breach_policy]='ESCALATE' OR [breach_policy]='BLOCK_PUBLICATION' OR [breach_policy]='ALERT' OR [breach_policy]='RECORD'),
    CONSTRAINT [CK_ctrl_SloDefinition_metric] CHECK ([metric_type]='QUALITY' OR [metric_type]='DURATION' OR [metric_type]='RELIABILITY' OR [metric_type]='FRESHNESS'),
    CONSTRAINT [CK_ctrl_SloDefinition_operator] CHECK ([comparison_operator]='>=' OR [comparison_operator]='>' OR [comparison_operator]='<=' OR [comparison_operator]='<'),
    CONSTRAINT [CK_ctrl_SloDefinition_severity] CHECK ([severity]='CRITICAL' OR [severity]='WARNING' OR [severity]='INFO'),
    CONSTRAINT [CK_ctrl_SloDefinition_target] CHECK ([target_value]>=(0)),
    CONSTRAINT [CK_ctrl_SloDefinition_unit] CHECK ([target_unit]='PERCENT' OR [target_unit]='HOURS' OR [target_unit]='MINUTES'),
    CONSTRAINT [CK_ctrl_SloDefinition_window] CHECK ([evaluation_window]='MONTHLY' OR [evaluation_window]='ROLLING_30_DAY' OR [evaluation_window]='DAILY' OR [evaluation_window]='PER_RUN'),
    CONSTRAINT [FK_ctrl_SloDefinition_release] FOREIGN KEY ([release_id]) REFERENCES [ctrl].[MetadataRelease] ([release_id])
);


GO

