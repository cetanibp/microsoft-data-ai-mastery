/*
FAB-001 — Live watermark transaction protocol validation
Target: SQL Database in Microsoft Fabric

This test uses only synthetic identifiers and rolls back every change. It proves:
1. an abandoned candidate cannot advance committed watermark state;
2. a successful compare-and-commit advances the value and state version once;
3. a stale candidate is rejected by optimistic concurrency.

Expected final result: four PASS rows and no persistent data changes.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @release_id uniqueidentifier =
    '20000000-0000-0000-0000-000000000001';
DECLARE @environment_id uniqueidentifier =
    '10000000-0000-0000-0000-000000000001';
DECLARE @object_key varchar(150) =
    'ingest-clinical-encounter';

DECLARE @run_id uniqueidentifier =
    '30000000-0000-0000-0000-000000000001';
DECLARE @failed_object_run_id uniqueidentifier =
    '31000000-0000-0000-0000-000000000001';
DECLARE @success_object_run_id uniqueidentifier =
    '31000000-0000-0000-0000-000000000002';
DECLARE @stale_object_run_id uniqueidentifier =
    '31000000-0000-0000-0000-000000000003';

DECLARE @failed_candidate_id uniqueidentifier =
    '32000000-0000-0000-0000-000000000001';
DECLARE @success_candidate_id uniqueidentifier =
    '32000000-0000-0000-0000-000000000002';
DECLARE @stale_candidate_id uniqueidentifier =
    '32000000-0000-0000-0000-000000000003';

DECLARE @initial_value nvarchar(4000) =
    N'2026-08-29T00:00:00Z';
DECLARE @next_value nvarchar(4000) =
    N'2026-08-29T00:15:00Z';
DECLARE @stale_value nvarchar(4000) =
    N'2026-08-29T00:30:00Z';

DECLARE @failed_state_unchanged bit = 0;
DECLARE @successful_commit_rows int = 0;
DECLARE @stale_commit_rows int = 0;
DECLARE @success_state_correct bit = 0;
DECLARE @audit_event_count int = 0;
DECLARE @overall_pass bit = 0;

BEGIN TRY
    BEGIN TRANSACTION;

    IF EXISTS
    (
        SELECT 1
        FROM ops.WatermarkState
        WHERE environment_id = @environment_id
          AND ingestion_object_key = @object_key
    )
        THROW 51000,
            'Validation requires no pre-existing Development watermark state for ingest-clinical-encounter.',
            1;

    INSERT ops.ExecutionRun
    (
        run_id,
        environment_id,
        release_id,
        trigger_type,
        trigger_reference,
        correlation_id,
        requested_scope,
        configuration_hash,
        run_status,
        started_at_utc,
        completed_at_utc
    )
    VALUES
    (
        @run_id,
        @environment_id,
        @release_id,
        'MANUAL',
        N'FAB-001 live transaction validation',
        'fab-001-watermark-live-validation',
        N'{"object":"ingest-clinical-encounter"}',
        REPLICATE('a', 64),
        'RUNNING',
        SYSUTCDATETIME(),
        NULL
    );

    INSERT ops.WatermarkState
    (
        environment_id,
        ingestion_object_key,
        definition_release_id,
        logical_value_type,
        committed_value,
        state_version,
        committed_object_run_id,
        committed_at_utc
    )
    VALUES
    (
        @environment_id,
        @object_key,
        @release_id,
        'DATETIME2',
        @initial_value,
        0,
        NULL,
        SYSUTCDATETIME()
    );

    /* Scenario 1: a failed attempt abandons its proposal. */
    INSERT ops.ObjectRun
    (
        object_run_id,
        run_id,
        environment_id,
        release_id,
        ingestion_object_key,
        attempt_number,
        object_run_status,
        input_boundary_hash,
        extracted_row_count,
        accepted_row_count,
        rejected_row_count,
        error_classification,
        error_summary,
        started_at_utc,
        completed_at_utc
    )
    VALUES
    (
        @failed_object_run_id,
        @run_id,
        @environment_id,
        @release_id,
        @object_key,
        1,
        'FAILED',
        REPLICATE('b', 64),
        100,
        0,
        100,
        'SYNTHETIC_VALIDATION',
        N'Intentional failure used to verify safe restart behavior.',
        DATEADD(second, -3, SYSUTCDATETIME()),
        SYSUTCDATETIME()
    );

    INSERT ops.WatermarkCandidate
    (
        candidate_id,
        object_run_id,
        environment_id,
        ingestion_object_key,
        logical_value_type,
        from_value,
        to_value,
        observed_state_version,
        candidate_status,
        proposed_at_utc,
        resolved_at_utc,
        resolution_reason
    )
    VALUES
    (
        @failed_candidate_id,
        @failed_object_run_id,
        @environment_id,
        @object_key,
        'DATETIME2',
        @initial_value,
        @next_value,
        0,
        'ABANDONED',
        DATEADD(second, -2, SYSUTCDATETIME()),
        SYSUTCDATETIME(),
        N'Intentional validation failure; committed state must remain unchanged.'
    );

    INSERT audit.StateEvent
    (
        state_event_id,
        environment_id,
        release_id,
        run_id,
        object_run_id,
        event_type,
        actor_identity,
        reason,
        correlation_id,
        before_hash,
        after_hash,
        occurred_at_utc
    )
    VALUES
    (
        '33000000-0000-0000-0000-000000000001',
        @environment_id,
        @release_id,
        @run_id,
        @failed_object_run_id,
        'WATERMARK_ABANDONED',
        N'validation:fab-001',
        N'Intentional failed-attempt validation.',
        'fab-001-watermark-live-validation',
        NULL,
        NULL,
        SYSUTCDATETIME()
    );

    SET @failed_state_unchanged =
        CASE WHEN EXISTS
        (
            SELECT 1
            FROM ops.WatermarkState
            WHERE environment_id = @environment_id
              AND ingestion_object_key = @object_key
              AND committed_value = @initial_value
              AND state_version = 0
              AND committed_object_run_id IS NULL
        )
        THEN 1 ELSE 0 END;

    /* Scenario 2: a successful attempt commits exactly once. */
    INSERT ops.ObjectRun
    (
        object_run_id,
        run_id,
        environment_id,
        release_id,
        ingestion_object_key,
        attempt_number,
        object_run_status,
        input_boundary_hash,
        extracted_row_count,
        accepted_row_count,
        rejected_row_count,
        error_classification,
        error_summary,
        started_at_utc,
        completed_at_utc
    )
    VALUES
    (
        @success_object_run_id,
        @run_id,
        @environment_id,
        @release_id,
        @object_key,
        2,
        'SUCCEEDED',
        REPLICATE('c', 64),
        100,
        100,
        0,
        NULL,
        NULL,
        DATEADD(second, -2, SYSUTCDATETIME()),
        SYSUTCDATETIME()
    );

    INSERT ops.WatermarkCandidate
    (
        candidate_id,
        object_run_id,
        environment_id,
        ingestion_object_key,
        logical_value_type,
        from_value,
        to_value,
        observed_state_version,
        candidate_status,
        proposed_at_utc,
        resolved_at_utc,
        resolution_reason
    )
    VALUES
    (
        @success_candidate_id,
        @success_object_run_id,
        @environment_id,
        @object_key,
        'DATETIME2',
        @initial_value,
        @next_value,
        0,
        'PROPOSED',
        SYSUTCDATETIME(),
        NULL,
        NULL
    );

    UPDATE ops.WatermarkState
    SET committed_value = @next_value,
        state_version = state_version + 1,
        committed_object_run_id = @success_object_run_id,
        committed_at_utc = SYSUTCDATETIME()
    WHERE environment_id = @environment_id
      AND ingestion_object_key = @object_key
      AND state_version = 0
      AND committed_value = @initial_value;

    SET @successful_commit_rows = @@ROWCOUNT;

    IF @successful_commit_rows = 1
    BEGIN
        UPDATE ops.WatermarkCandidate
        SET candidate_status = 'COMMITTED',
            resolved_at_utc = SYSUTCDATETIME(),
            resolution_reason =
                N'Compare-and-commit succeeded at observed state version 0.'
        WHERE candidate_id = @success_candidate_id;
    END;

    INSERT audit.StateEvent
    (
        state_event_id,
        environment_id,
        release_id,
        run_id,
        object_run_id,
        event_type,
        actor_identity,
        reason,
        correlation_id,
        before_hash,
        after_hash,
        occurred_at_utc
    )
    VALUES
    (
        '33000000-0000-0000-0000-000000000002',
        @environment_id,
        @release_id,
        @run_id,
        @success_object_run_id,
        'WATERMARK_COMMITTED',
        N'validation:fab-001',
        N'Successful compare-and-commit validation.',
        'fab-001-watermark-live-validation',
        REPLICATE('d', 64),
        REPLICATE('e', 64),
        SYSUTCDATETIME()
    );

    SET @success_state_correct =
        CASE WHEN EXISTS
        (
            SELECT 1
            FROM ops.WatermarkState
            WHERE environment_id = @environment_id
              AND ingestion_object_key = @object_key
              AND committed_value = @next_value
              AND state_version = 1
              AND committed_object_run_id = @success_object_run_id
        )
        AND EXISTS
        (
            SELECT 1
            FROM ops.WatermarkCandidate
            WHERE candidate_id = @success_candidate_id
              AND candidate_status = 'COMMITTED'
              AND resolved_at_utc IS NOT NULL
        )
        THEN 1 ELSE 0 END;

    /* Scenario 3: a stale observed version cannot overwrite state. */
    INSERT ops.ObjectRun
    (
        object_run_id,
        run_id,
        environment_id,
        release_id,
        ingestion_object_key,
        attempt_number,
        object_run_status,
        input_boundary_hash,
        extracted_row_count,
        accepted_row_count,
        rejected_row_count,
        error_classification,
        error_summary,
        started_at_utc,
        completed_at_utc
    )
    VALUES
    (
        @stale_object_run_id,
        @run_id,
        @environment_id,
        @release_id,
        @object_key,
        3,
        'RECOVERY_REQUIRED',
        REPLICATE('f', 64),
        100,
        100,
        0,
        'STALE_STATE_VERSION',
        N'Intentional stale-write validation.',
        DATEADD(second, -1, SYSUTCDATETIME()),
        SYSUTCDATETIME()
    );

    INSERT ops.WatermarkCandidate
    (
        candidate_id,
        object_run_id,
        environment_id,
        ingestion_object_key,
        logical_value_type,
        from_value,
        to_value,
        observed_state_version,
        candidate_status,
        proposed_at_utc,
        resolved_at_utc,
        resolution_reason
    )
    VALUES
    (
        @stale_candidate_id,
        @stale_object_run_id,
        @environment_id,
        @object_key,
        'DATETIME2',
        @initial_value,
        @stale_value,
        0,
        'PROPOSED',
        SYSUTCDATETIME(),
        NULL,
        NULL
    );

    UPDATE ops.WatermarkState
    SET committed_value = @stale_value,
        state_version = state_version + 1,
        committed_object_run_id = @stale_object_run_id,
        committed_at_utc = SYSUTCDATETIME()
    WHERE environment_id = @environment_id
      AND ingestion_object_key = @object_key
      AND state_version = 0;

    SET @stale_commit_rows = @@ROWCOUNT;

    UPDATE ops.WatermarkCandidate
    SET candidate_status = 'ABANDONED',
        resolved_at_utc = SYSUTCDATETIME(),
        resolution_reason =
            N'Stale observed state version rejected; recovery is required.'
    WHERE candidate_id = @stale_candidate_id
      AND @stale_commit_rows = 0;

    INSERT audit.StateEvent
    (
        state_event_id,
        environment_id,
        release_id,
        run_id,
        object_run_id,
        event_type,
        actor_identity,
        reason,
        correlation_id,
        before_hash,
        after_hash,
        occurred_at_utc
    )
    VALUES
    (
        '33000000-0000-0000-0000-000000000003',
        @environment_id,
        @release_id,
        @run_id,
        @stale_object_run_id,
        'RECOVERY_REQUESTED',
        N'validation:fab-001',
        N'Stale candidate correctly rejected by optimistic concurrency.',
        'fab-001-watermark-live-validation',
        NULL,
        NULL,
        SYSUTCDATETIME()
    );

    SELECT @audit_event_count = COUNT(*)
    FROM audit.StateEvent
    WHERE correlation_id = 'fab-001-watermark-live-validation';

    SET @overall_pass =
        CASE
            WHEN @failed_state_unchanged = 1
             AND @successful_commit_rows = 1
             AND @success_state_correct = 1
             AND @stale_commit_rows = 0
             AND @audit_event_count = 3
            THEN 1
            ELSE 0
        END;

    SELECT
        scenario,
        expected_result,
        actual_result,
        validation_status
    FROM
    (
        VALUES
            (
                'Failed attempt preserves committed state',
                'initial value; version 0',
                CASE WHEN @failed_state_unchanged = 1
                    THEN 'initial value; version 0'
                    ELSE 'state changed unexpectedly'
                END,
                CASE WHEN @failed_state_unchanged = 1 THEN 'PASS' ELSE 'FAIL' END
            ),
            (
                'Successful compare-and-commit',
                '1 affected row; version 1',
                CONCAT(@successful_commit_rows, ' affected row; state verified=',
                    @success_state_correct),
                CASE WHEN @successful_commit_rows = 1
                       AND @success_state_correct = 1
                    THEN 'PASS' ELSE 'FAIL'
                END
            ),
            (
                'Stale candidate rejected',
                '0 affected rows',
                CONCAT(@stale_commit_rows, ' affected rows'),
                CASE WHEN @stale_commit_rows = 0 THEN 'PASS' ELSE 'FAIL' END
            ),
            (
                'Audit evidence appended',
                '3 events',
                CONCAT(@audit_event_count, ' events'),
                CASE WHEN @audit_event_count = 3 THEN 'PASS' ELSE 'FAIL' END
            )
    ) AS results
    (
        scenario,
        expected_result,
        actual_result,
        validation_status
    );

    ROLLBACK TRANSACTION;

    IF @overall_pass = 0
        THROW 51001, 'FAB-001 watermark protocol validation failed.', 1;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
