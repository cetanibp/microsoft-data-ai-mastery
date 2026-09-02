CREATE VIEW [ops].[vw_OpenSloBreach]
AS
SELECT
    evaluation.slo_evaluation_id,
    evaluation.evaluator_version,
    evaluation.environment_id,
    environment.environment_code,
    environment.is_production,
    evaluation.release_id,
    evaluation.ingestion_object_key,
    ingestion_object.display_name AS ingestion_object_name,
    evaluation.objective_key,
    evaluation.window_start_utc,
    evaluation.window_end_utc,
    evaluation.observed_value,
    evaluation.target_value,
    evaluation.comparison_operator,
    evaluation.target_unit,
    evaluation.alert_severity,
    evaluation.error_budget_consumption,
    evaluation.detected_at_utc,
    CASE
        WHEN EXISTS
        (
            SELECT 1
            FROM ops.AlertRoutingDecision AS decision
            WHERE decision.slo_evaluation_id = evaluation.slo_evaluation_id
              AND decision.decision_status IN ('ROUTED', 'SUPPRESSED')
        ) THEN 'DECIDED'
        ELSE 'UNROUTED'
    END AS routing_status
FROM ops.vw_SloEvaluationLatest AS evaluation
INNER JOIN ctrl.Environment AS environment
    ON environment.environment_id = evaluation.environment_id
LEFT JOIN ctrl.IngestionObject AS ingestion_object
    ON ingestion_object.release_id = evaluation.release_id
   AND ingestion_object.ingestion_object_key = evaluation.ingestion_object_key
WHERE evaluation.evaluation_status = 'BREACH';
GO
