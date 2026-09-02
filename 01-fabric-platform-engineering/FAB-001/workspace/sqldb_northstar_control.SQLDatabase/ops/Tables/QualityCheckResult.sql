CREATE TABLE [ops].[QualityCheckResult] (
    [quality_result_id]    UNIQUEIDENTIFIER NOT NULL,
    [object_run_id]        UNIQUEIDENTIFIER NOT NULL,
    [release_id]           UNIQUEIDENTIFIER NOT NULL,
    [quality_policy_key]   VARCHAR (100)    NOT NULL,
    [policy_version]       VARCHAR (50)     NOT NULL,
    [quality_rule_key]     VARCHAR (100)    NOT NULL,
    [check_type]           VARCHAR (30)     NOT NULL,
    [observed_value]       DECIMAL (38, 10) NULL,
    [comparison_operator]  VARCHAR (2)      NOT NULL,
    [threshold_value]      DECIMAL (38, 10) NOT NULL,
    [result_status]        VARCHAR (10)     NOT NULL,
    [enforcement_level]    VARCHAR (10)     NOT NULL,
    [error_classification] VARCHAR (50)     NULL,
    [duration_ms]          BIGINT           NOT NULL,
    [evaluated_at_utc]     DATETIME2 (7)    NOT NULL,
    CONSTRAINT [PK_ops_QualityCheckResult] PRIMARY KEY CLUSTERED ([quality_result_id] ASC),
    CONSTRAINT [UQ_ops_QualityCheckResult_rule] UNIQUE NONCLUSTERED
        ([object_run_id] ASC, [quality_policy_key] ASC, [quality_rule_key] ASC),
    CONSTRAINT [CK_ops_QualityCheckResult_check] CHECK
        ([check_type] IN ('ROW_COUNT_BALANCE', 'TARGET_COUNT', 'NULL_RATE',
                          'DISTINCT_KEY', 'MIN_VALUE', 'MAX_VALUE', 'SUM_VALUE')),
    CONSTRAINT [CK_ops_QualityCheckResult_operator] CHECK
        ([comparison_operator] IN ('EQ', 'NE', 'LT', 'LE', 'GT', 'GE')),
    CONSTRAINT [CK_ops_QualityCheckResult_status] CHECK
        ([result_status] IN ('PASS', 'WARN', 'FAIL', 'ERROR')),
    CONSTRAINT [CK_ops_QualityCheckResult_enforcement] CHECK
        ([enforcement_level] IN ('BLOCK', 'WARN')),
    CONSTRAINT [CK_ops_QualityCheckResult_duration] CHECK ([duration_ms] >= 0),
    CONSTRAINT [CK_ops_QualityCheckResult_error] CHECK
        (([result_status] = 'ERROR' AND [error_classification] IS NOT NULL)
         OR ([result_status] IN ('PASS', 'FAIL') AND [error_classification] IS NULL)
         OR [result_status] = 'WARN'),
    CONSTRAINT [FK_ops_QualityCheckResult_object_run] FOREIGN KEY ([object_run_id])
        REFERENCES [ops].[ObjectRun] ([object_run_id]),
    CONSTRAINT [FK_ops_QualityCheckResult_policy] FOREIGN KEY
        ([release_id], [quality_policy_key])
        REFERENCES [ctrl].[QualityPolicy] ([release_id], [quality_policy_key])
);
GO

CREATE NONCLUSTERED INDEX [IX_ops_QualityCheckResult_review]
    ON [ops].[QualityCheckResult]
       ([result_status] ASC, [enforcement_level] ASC, [evaluated_at_utc] DESC)
    INCLUDE ([object_run_id], [quality_policy_key], [quality_rule_key]);
GO
