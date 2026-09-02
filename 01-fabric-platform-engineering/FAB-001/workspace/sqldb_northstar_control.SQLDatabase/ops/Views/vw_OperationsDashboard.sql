CREATE VIEW [ops].[vw_OperationsDashboard]
AS
WITH breach_count AS
(
    SELECT
        environment_id,
        release_id,
        ingestion_object_key,
        COUNT_BIG(*) AS open_breach_count,
        MIN(alert_severity) AS highest_open_severity
    FROM ops.vw_OpenSloBreach
    GROUP BY environment_id, release_id, ingestion_object_key
)
SELECT
    occurrence.environment_id,
    environment.environment_code,
    occurrence.release_id,
    occurrence.run_id,
    occurrence.object_run_id,
    occurrence.ingestion_object_key,
    ingestion_object.display_name AS ingestion_object_name,
    occurrence.correlation_id,
    occurrence.object_run_status,
    occurrence.reliability_status,
    occurrence.quality_decision_status,
    occurrence.quality_enforcement_status,
    occurrence.watermark_candidate_status,
    occurrence.occurrence_started_at_utc,
    occurrence.completed_at_utc,
    occurrence.accepted_publication_at_utc,
    occurrence.duration_ms,
    occurrence.extracted_row_count,
    occurrence.accepted_row_count,
    occurrence.rejected_row_count,
    occurrence.error_classification,
    COALESCE(breach.open_breach_count, 0) AS open_breach_count,
    breach.highest_open_severity
FROM ops.vw_OperationalOccurrence AS occurrence
INNER JOIN ctrl.Environment AS environment
    ON environment.environment_id = occurrence.environment_id
INNER JOIN ctrl.IngestionObject AS ingestion_object
    ON ingestion_object.release_id = occurrence.release_id
   AND ingestion_object.ingestion_object_key = occurrence.ingestion_object_key
LEFT JOIN breach_count AS breach
    ON breach.environment_id = occurrence.environment_id
   AND breach.release_id = occurrence.release_id
   AND (breach.ingestion_object_key = occurrence.ingestion_object_key
        OR breach.ingestion_object_key IS NULL);
GO
