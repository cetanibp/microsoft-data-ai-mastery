CREATE TABLE [ctrl].[StrategyParameterDefinition] (
    [strategy_type]  VARCHAR (20)    NOT NULL,
    [parameter_key]  VARCHAR (100)   NOT NULL,
    [value_type]     VARCHAR (20)    NOT NULL,
    [is_required]    BIT             NOT NULL,
    [minimum_value]  DECIMAL (38, 9) NULL,
    [maximum_value]  DECIMAL (38, 9) NULL,
    [allowed_values] NVARCHAR (1000) NULL,
    [description]    NVARCHAR (1000) NOT NULL,
    CONSTRAINT [PK_ctrl_StrategyParameterDefinition] PRIMARY KEY CLUSTERED ([strategy_type] ASC, [parameter_key] ASC),
    CONSTRAINT [CK_ctrl_StrategyParameterDefinition_strategy] CHECK ([strategy_type]='SNAPSHOT' OR [strategy_type]='APPEND' OR [strategy_type]='WATERMARK' OR [strategy_type]='FULL'),
    CONSTRAINT [CK_ctrl_StrategyParameterDefinition_type] CHECK ([value_type]='BOOLEAN' OR [value_type]='DECIMAL' OR [value_type]='INTEGER' OR [value_type]='STRING')
);


GO

