CREATE VIEW [ops].[vw_QualityEnforcementIntegrity]
AS
SELECT
    occurrence.environment_id,
    occurrence.release_id,
    occurrence.run_id,
    occurrence.object_run_id,
    occurrence.ingestion_object_key,
    occurrence.correlation_id,
    occurrence.quality_decided_at_utc AS detected_at_utc,
    occurrence.object_run_status,
    occurrence.watermark_candidate_status,
    occurrence.watermark_resolved_at_utc,
    occurrence.quality_enforcement_status AS integrity_status,
    CASE
        WHEN occurrence.quality_enforcement_status = 'BREACH'
            THEN 'Blocked quality decision advanced or retained committed state.'
        WHEN occurrence.object_run_status IN ('SUCCEEDED', 'SUCCEEDED_WITH_WARNINGS')
            THEN 'Blocked quality decision ended in an accepted object-run status.'
        ELSE 'Blocked quality decision preserved the publication boundary.'
    END AS integrity_summary
FROM ops.vw_OperationalOccurrence AS occurrence
WHERE occurrence.quality_decision_status = 'BLOCKED';
GO
