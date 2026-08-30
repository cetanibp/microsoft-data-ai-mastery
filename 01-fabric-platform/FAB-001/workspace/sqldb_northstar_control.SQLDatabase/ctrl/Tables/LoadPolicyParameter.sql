CREATE TABLE [ctrl].[LoadPolicyParameter] (
    [release_id]      UNIQUEIDENTIFIER NOT NULL,
    [load_policy_key] VARCHAR (100)    NOT NULL,
    [strategy_type]   VARCHAR (20)     NOT NULL,
    [parameter_key]   VARCHAR (100)    NOT NULL,
    [value_type]      VARCHAR (20)     NOT NULL,
    [value_string]    NVARCHAR (4000)  NULL,
    [value_integer]   BIGINT           NULL,
    [value_decimal]   DECIMAL (38, 9)  NULL,
    [value_boolean]   BIT              NULL,
    CONSTRAINT [PK_ctrl_LoadPolicyParameter] PRIMARY KEY CLUSTERED ([release_id] ASC, [load_policy_key] ASC, [parameter_key] ASC),
    CONSTRAINT [CK_ctrl_LoadPolicyParameter_one_value] CHECK ((((case when [value_string] IS NULL then (0) else (1) end+case when [value_integer] IS NULL then (0) else (1) end)+case when [value_decimal] IS NULL then (0) else (1) end)+case when [value_boolean] IS NULL then (0) else (1) end)=(1)),
    CONSTRAINT [CK_ctrl_LoadPolicyParameter_secret] CHECK ([value_string] IS NULL OR NOT [value_string] like '%password=%' AND NOT [value_string] like '%secret=%' AND NOT [value_string] like '%token=%' AND NOT [value_string] like '%://%'),
    CONSTRAINT [CK_ctrl_LoadPolicyParameter_type] CHECK ([value_type]='BOOLEAN' OR [value_type]='DECIMAL' OR [value_type]='INTEGER' OR [value_type]='STRING'),
    CONSTRAINT [FK_ctrl_LoadPolicyParameter_definition] FOREIGN KEY ([strategy_type], [parameter_key]) REFERENCES [ctrl].[StrategyParameterDefinition] ([strategy_type], [parameter_key]),
    CONSTRAINT [FK_ctrl_LoadPolicyParameter_policy] FOREIGN KEY ([release_id], [load_policy_key]) REFERENCES [ctrl].[LoadPolicy] ([release_id], [load_policy_key])
);


GO

