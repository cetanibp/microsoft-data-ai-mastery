CREATE VIEW [ops].[vw_OperationalOccurrence]
AS
WITH ranked_attempt AS
(
    SELECT
        object_run.*,
        execution_run.trigger_type,
        execution_run.correlation_id,
        execution_run.run_status,
        MIN(object_run.started_at_utc) OVER
        (
            PARTITION BY object_run.run_id, object_run.ingestion_object_key
        ) AS occurrence_started_at_utc,
        ROW_NUMBER() OVER
        (
            PARTITION BY object_run.run_id, object_run.ingestion_object_key
            ORDER BY object_run.attempt_number DESC,
                     object_run.started_at_utc DESC,
                     object_run.object_run_id DESC
        ) AS attempt_rank
    FROM ops.ObjectRun AS object_run
    INNER JOIN ops.ExecutionRun AS execution_run
        ON execution_run.run_id = object_run.run_id
)
SELECT
    attempt.environment_id,
    attempt.release_id,
    attempt.run_id,
    attempt.object_run_id,
    attempt.ingestion_object_key,
    attempt.attempt_number,
    attempt.input_boundary_hash,
    attempt.trigger_type,
    attempt.correlation_id,
    attempt.run_status,
    attempt.object_run_status,
    attempt.error_classification,
    attempt.extracted_row_count,
    attempt.accepted_row_count,
    attempt.rejected_row_count,
    attempt.occurrence_started_at_utc,
    attempt.completed_at_utc,
    CASE
        WHEN attempt.completed_at_utc IS NULL THEN NULL
        ELSE DATEDIFF_BIG(MILLISECOND, attempt.occurrence_started_at_utc,
                          attempt.completed_at_utc)
    END AS duration_ms,
    quality.decision_status AS quality_decision_status,
    quality.blocking_failure_count,
    quality.warning_count,
    quality.decided_at_utc AS quality_decided_at_utc,
    CASE
        WHEN quality.decision_status IN ('ACCEPTED', 'ACCEPTED_WITH_WARNING')
            THEN quality.decided_at_utc
        ELSE NULL
    END AS accepted_publication_at_utc,
    candidate.candidate_status AS watermark_candidate_status,
    candidate.resolved_at_utc AS watermark_resolved_at_utc,
    CASE
        WHEN quality.decision_status = 'BLOCKED'
         AND (attempt.object_run_status IN ('SUCCEEDED', 'SUCCEEDED_WITH_WARNINGS')
              OR candidate.candidate_status = 'COMMITTED'
              OR watermark.committed_object_run_id = attempt.object_run_id)
            THEN 'BREACH'
        WHEN quality.decision_status = 'BLOCKED' THEN 'PASS'
        ELSE 'NOT_APPLICABLE'
    END AS quality_enforcement_status,
    CASE
        WHEN quality.decision_status = 'BLOCKED' THEN 'QUALITY_BLOCKED'
        WHEN attempt.object_run_status IN ('SUCCEEDED', 'SUCCEEDED_WITH_WARNINGS')
            THEN 'RELIABLE'
        WHEN attempt.object_run_status IN ('FAILED', 'RECOVERY_REQUIRED', 'CANCELLED')
            THEN 'UNRELIABLE'
        ELSE 'IN_PROGRESS'
    END AS reliability_status
FROM ranked_attempt AS attempt
LEFT JOIN ops.QualityDecision AS quality
    ON quality.object_run_id = attempt.object_run_id
LEFT JOIN ops.WatermarkCandidate AS candidate
    ON candidate.object_run_id = attempt.object_run_id
LEFT JOIN ops.WatermarkState AS watermark
    ON watermark.environment_id = attempt.environment_id
   AND watermark.ingestion_object_key = attempt.ingestion_object_key
WHERE attempt.attempt_rank = 1;
GO
