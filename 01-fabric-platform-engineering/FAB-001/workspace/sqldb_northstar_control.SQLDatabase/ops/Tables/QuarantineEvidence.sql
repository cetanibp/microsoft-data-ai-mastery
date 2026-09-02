CREATE TABLE [ops].[QuarantineEvidence] (
    [quarantine_id]              VARCHAR (64)     NOT NULL,
    [object_run_id]              UNIQUEIDENTIFIER NOT NULL,
    [release_id]                 UNIQUEIDENTIFIER NOT NULL,
    [quality_policy_key]         VARCHAR (100)    NOT NULL,
    [quality_rule_key]           VARCHAR (100)    NOT NULL,
    [reason_code]                VARCHAR (50)     NOT NULL,
    [source_record_identity_hash] VARCHAR (64)    NOT NULL,
    [input_boundary_hash]        VARCHAR (64)     NOT NULL,
    [quarantined_at_utc]         DATETIME2 (7)    NOT NULL,
    CONSTRAINT [PK_ops_QuarantineEvidence] PRIMARY KEY CLUSTERED ([quarantine_id] ASC),
    CONSTRAINT [CK_ops_QuarantineEvidence_hashes] CHECK
        (LEN([quarantine_id]) = 64 AND LEN([source_record_identity_hash]) = 64
         AND LEN([input_boundary_hash]) = 64),
    CONSTRAINT [CK_ops_QuarantineEvidence_reason] CHECK
        ([reason_code] IN ('DUPLICATE_BUSINESS_KEY', 'NULL_REQUIRED_VALUE',
                           'OUT_OF_RANGE_VALUE', 'COUNT_RECONCILIATION')),
    CONSTRAINT [FK_ops_QuarantineEvidence_object_run] FOREIGN KEY ([object_run_id])
        REFERENCES [ops].[ObjectRun] ([object_run_id]),
    CONSTRAINT [FK_ops_QuarantineEvidence_policy] FOREIGN KEY
        ([release_id], [quality_policy_key])
        REFERENCES [ctrl].[QualityPolicy] ([release_id], [quality_policy_key])
);
GO

CREATE NONCLUSTERED INDEX [IX_ops_QuarantineEvidence_review]
    ON [ops].[QuarantineEvidence]
       ([quality_policy_key] ASC, [reason_code] ASC, [quarantined_at_utc] DESC)
    INCLUDE ([object_run_id], [quality_rule_key]);
GO
