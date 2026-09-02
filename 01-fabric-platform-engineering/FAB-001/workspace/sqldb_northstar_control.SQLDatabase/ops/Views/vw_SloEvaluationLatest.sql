CREATE VIEW [ops].[vw_SloEvaluationLatest]
AS
WITH ranked_evaluation AS
(
    SELECT
        evaluation.*,
        ROW_NUMBER() OVER
        (
            PARTITION BY evaluation.environment_id,
                         evaluation.release_id,
                         evaluation.ingestion_object_key,
                         evaluation.objective_key,
                         evaluation.window_start_utc,
                         evaluation.window_end_utc
            ORDER BY evaluation.created_at_utc DESC,
                     evaluation.evaluator_version DESC,
                     evaluation.slo_evaluation_id DESC
        ) AS evaluation_rank
    FROM ops.SloEvaluation AS evaluation
)
SELECT
    slo_evaluation_id,
    evaluator_version,
    environment_id,
    release_id,
    ingestion_object_key,
    objective_key,
    source_slo_key,
    window_start_utc,
    window_end_utc,
    numerator_count,
    denominator_count,
    excluded_count,
    observed_value,
    target_value,
    comparison_operator,
    target_unit,
    evaluation_status,
    alert_severity,
    error_budget_consumption,
    source_evidence_hash,
    detected_at_utc,
    created_at_utc
FROM ranked_evaluation
WHERE evaluation_rank = 1;
GO
