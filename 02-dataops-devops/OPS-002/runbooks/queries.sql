/*
OPS-002 read-only triage query pack.
Set one or more safe identifiers. Do not paste payloads or credentials.
*/

DECLARE @environment_code varchar(20) = 'development';
DECLARE @ingestion_object_key varchar(150) = 'ingest-clinical-encounter';
DECLARE @correlation_id varchar(100) = NULL;
DECLARE @object_run_id uniqueidentifier = NULL;

-- 1. Open breaches and routing state.
SELECT
    breach.environment_code,
    breach.ingestion_object_key,
    breach.objective_key,
    breach.evaluation_status,
    breach.observed_value,
    breach.comparison_operator,
    breach.target_value,
    breach.target_unit,
    breach.alert_severity,
    breach.error_budget_consumption,
    breach.routing_status,
    breach.detected_at_utc
FROM ops.vw_OpenSloBreach AS breach
WHERE breach.environment_code = @environment_code
  AND (@ingestion_object_key IS NULL
       OR breach.ingestion_object_key = @ingestion_object_key)
ORDER BY breach.alert_severity, breach.detected_at_utc DESC;

-- 2. Correlated occurrence evidence.
SELECT TOP (50)
    dashboard.*
FROM ops.vw_OperationsDashboard AS dashboard
WHERE dashboard.environment_code = @environment_code
  AND (@ingestion_object_key IS NULL
       OR dashboard.ingestion_object_key = @ingestion_object_key)
  AND (@correlation_id IS NULL OR dashboard.correlation_id = @correlation_id)
  AND (@object_run_id IS NULL OR dashboard.object_run_id = @object_run_id)
ORDER BY dashboard.occurrence_started_at_utc DESC;

-- 3. Quality-enforcement integrity. Any BREACH is P1.
SELECT
    integrity.*
FROM ops.vw_QualityEnforcementIntegrity AS integrity
INNER JOIN ctrl.Environment AS environment
    ON environment.environment_id = integrity.environment_id
WHERE environment.environment_code = @environment_code
  AND (@ingestion_object_key IS NULL
       OR integrity.ingestion_object_key = @ingestion_object_key)
  AND (@object_run_id IS NULL OR integrity.object_run_id = @object_run_id)
ORDER BY integrity.detected_at_utc DESC;

-- 4. Candidate and committed watermark state.
SELECT
    object_run.run_id,
    object_run.object_run_id,
    object_run.ingestion_object_key,
    object_run.input_boundary_hash,
    object_run.object_run_status,
    candidate.candidate_status,
    candidate.observed_state_version,
    candidate.proposed_at_utc,
    candidate.resolved_at_utc,
    watermark.state_version,
    watermark.committed_object_run_id,
    watermark.committed_at_utc
FROM ops.ObjectRun AS object_run
LEFT JOIN ops.WatermarkCandidate AS candidate
    ON candidate.object_run_id = object_run.object_run_id
LEFT JOIN ops.WatermarkState AS watermark
    ON watermark.environment_id = object_run.environment_id
   AND watermark.ingestion_object_key = object_run.ingestion_object_key
INNER JOIN ctrl.Environment AS environment
    ON environment.environment_id = object_run.environment_id
WHERE environment.environment_code = @environment_code
  AND (@ingestion_object_key IS NULL
       OR object_run.ingestion_object_key = @ingestion_object_key)
  AND (@object_run_id IS NULL OR object_run.object_run_id = @object_run_id)
ORDER BY object_run.started_at_utc DESC;

-- 5. Evaluation and routing history.
SELECT
    evaluation.objective_key,
    evaluation.evaluator_version,
    evaluation.window_start_utc,
    evaluation.window_end_utc,
    evaluation.observed_value,
    evaluation.target_value,
    evaluation.evaluation_status,
    evaluation.source_evidence_hash,
    decision.delivery_mode,
    decision.decision_status,
    decision.owner_role,
    decision.owner_group_key,
    decision.routing_alias,
    decision.deduplication_key,
    decision.detected_at_utc,
    decision.routed_at_utc
FROM ops.SloEvaluation AS evaluation
LEFT JOIN ops.AlertRoutingDecision AS decision
    ON decision.slo_evaluation_id = evaluation.slo_evaluation_id
INNER JOIN ctrl.Environment AS environment
    ON environment.environment_id = evaluation.environment_id
WHERE environment.environment_code = @environment_code
  AND (@ingestion_object_key IS NULL
       OR evaluation.ingestion_object_key = @ingestion_object_key)
ORDER BY evaluation.detected_at_utc DESC;
