CREATE TABLE [ops].[QualityDecision] (
    [object_run_id]              UNIQUEIDENTIFIER NOT NULL,
    [decision_status]            VARCHAR (30)     NOT NULL,
    [watermark_commit_eligible]  BIT              NOT NULL,
    [evaluated_rule_count]       SMALLINT         NOT NULL,
    [blocking_failure_count]     SMALLINT         NOT NULL,
    [warning_count]              SMALLINT         NOT NULL,
    [result_set_hash]            VARCHAR (64)     NOT NULL,
    [decided_at_utc]             DATETIME2 (7)    NOT NULL,
    CONSTRAINT [PK_ops_QualityDecision] PRIMARY KEY CLUSTERED ([object_run_id] ASC),
    CONSTRAINT [CK_ops_QualityDecision_status] CHECK
        ([decision_status] IN ('ACCEPTED', 'ACCEPTED_WITH_WARNING', 'BLOCKED')),
    CONSTRAINT [CK_ops_QualityDecision_counts] CHECK
        ([evaluated_rule_count] >= 1 AND [blocking_failure_count] >= 0
         AND [warning_count] >= 0
         AND [blocking_failure_count] + [warning_count] <= [evaluated_rule_count]),
    CONSTRAINT [CK_ops_QualityDecision_hash] CHECK (LEN([result_set_hash]) = 64),
    CONSTRAINT [CK_ops_QualityDecision_eligibility] CHECK
        (([decision_status] = 'BLOCKED' AND [watermark_commit_eligible] = 0
          AND [blocking_failure_count] > 0)
         OR ([decision_status] IN ('ACCEPTED', 'ACCEPTED_WITH_WARNING')
             AND [watermark_commit_eligible] = 1
             AND [blocking_failure_count] = 0)),
    CONSTRAINT [FK_ops_QualityDecision_object_run] FOREIGN KEY ([object_run_id])
        REFERENCES [ops].[ObjectRun] ([object_run_id])
);
GO

CREATE NONCLUSTERED INDEX [IX_ops_QualityDecision_review]
    ON [ops].[QualityDecision]([decision_status] ASC, [decided_at_utc] DESC);
GO
