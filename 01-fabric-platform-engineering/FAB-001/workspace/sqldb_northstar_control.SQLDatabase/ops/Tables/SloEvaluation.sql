CREATE TABLE [ops].[SloEvaluation] (
    [slo_evaluation_id]       UNIQUEIDENTIFIER NOT NULL,
    [evaluator_version]       VARCHAR (30)     NOT NULL,
    [environment_id]          UNIQUEIDENTIFIER NOT NULL,
    [release_id]              UNIQUEIDENTIFIER NOT NULL,
    [ingestion_object_key]    VARCHAR (150)    NULL,
    [objective_key]           VARCHAR (100)    NOT NULL,
    [source_slo_key]          VARCHAR (100)    NULL,
    [window_start_utc]        DATETIME2 (7)    NOT NULL,
    [window_end_utc]          DATETIME2 (7)    NOT NULL,
    [numerator_count]         BIGINT           NOT NULL,
    [denominator_count]       BIGINT           NOT NULL,
    [observed_value]          DECIMAL (19, 6)  NULL,
    [target_value]            DECIMAL (19, 6)  NOT NULL,
    [comparison_operator]     VARCHAR (10)     NOT NULL,
    [target_unit]             VARCHAR (30)     NOT NULL,
    [evaluation_status]       VARCHAR (20)     NOT NULL,
    [alert_severity]          VARCHAR (2)      NOT NULL,
    [error_budget_consumption] DECIMAL (19, 6) NULL,
    [excluded_count]          BIGINT           CONSTRAINT [DF_ops_SloEvaluation_excluded] DEFAULT ((0)) NOT NULL,
    [source_evidence_hash]    VARCHAR (64)     NOT NULL,
    [detected_at_utc]         DATETIME2 (7)    NOT NULL,
    [created_at_utc]          DATETIME2 (7)    CONSTRAINT [DF_ops_SloEvaluation_created] DEFAULT (sysutcdatetime()) NOT NULL,
    CONSTRAINT [PK_ops_SloEvaluation] PRIMARY KEY CLUSTERED ([slo_evaluation_id] ASC),
    CONSTRAINT [CK_ops_SloEvaluation_objective] CHECK
        ([objective_key] IN ('critical-freshness', 'standard-freshness',
         'ingestion-reliability', 'duration-compliance', 'quality-acceptance',
         'quality-enforcement', 'critical-alert-latency')),
    CONSTRAINT [CK_ops_SloEvaluation_window] CHECK ([window_start_utc] < [window_end_utc]),
    CONSTRAINT [CK_ops_SloEvaluation_counts] CHECK
        ([numerator_count] >= 0 AND [denominator_count] >= 0
         AND [numerator_count] <= [denominator_count]
         AND [excluded_count] >= 0),
    CONSTRAINT [CK_ops_SloEvaluation_operator] CHECK
        ([comparison_operator] IN ('>=', '>', '<=', '<', '=')),
    CONSTRAINT [CK_ops_SloEvaluation_unit] CHECK
        ([target_unit] IN ('PERCENT', 'HOURS', 'MINUTES')),
    CONSTRAINT [CK_ops_SloEvaluation_status] CHECK
        ([evaluation_status] IN ('PASS', 'BREACH', 'NO_DATA')),
    CONSTRAINT [CK_ops_SloEvaluation_no_data] CHECK
        (([denominator_count] = 0 AND [observed_value] IS NULL
          AND [evaluation_status] = 'NO_DATA')
         OR ([denominator_count] > 0 AND [observed_value] IS NOT NULL
             AND [evaluation_status] IN ('PASS', 'BREACH'))),
    CONSTRAINT [CK_ops_SloEvaluation_severity] CHECK ([alert_severity] IN ('P1', 'P2', 'P3', 'P4')),
    CONSTRAINT [CK_ops_SloEvaluation_budget] CHECK
        ([error_budget_consumption] IS NULL OR [error_budget_consumption] >= 0),
    CONSTRAINT [CK_ops_SloEvaluation_hash] CHECK (LEN([source_evidence_hash]) = 64),
    CONSTRAINT [FK_ops_SloEvaluation_environment] FOREIGN KEY ([environment_id])
        REFERENCES [ctrl].[Environment] ([environment_id]),
    CONSTRAINT [FK_ops_SloEvaluation_release] FOREIGN KEY ([release_id])
        REFERENCES [ctrl].[MetadataRelease] ([release_id]),
    CONSTRAINT [FK_ops_SloEvaluation_object] FOREIGN KEY ([release_id], [ingestion_object_key])
        REFERENCES [ctrl].[IngestionObject] ([release_id], [ingestion_object_key]),
    CONSTRAINT [FK_ops_SloEvaluation_source_slo] FOREIGN KEY ([release_id], [source_slo_key])
        REFERENCES [ctrl].[SloDefinition] ([release_id], [slo_key]),
    CONSTRAINT [UQ_ops_SloEvaluation_identity] UNIQUE NONCLUSTERED
        ([evaluator_version], [environment_id], [release_id], [ingestion_object_key],
         [objective_key], [window_start_utc], [window_end_utc])
);
GO

CREATE NONCLUSTERED INDEX [IX_ops_SloEvaluation_breach]
    ON [ops].[SloEvaluation]
        ([environment_id], [evaluation_status], [alert_severity], [window_end_utc] DESC)
    INCLUDE ([objective_key], [ingestion_object_key], [observed_value], [target_value]);
GO
