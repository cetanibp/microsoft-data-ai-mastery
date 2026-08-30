
CREATE   VIEW ctrl.vw_ActiveIngestionConfiguration
AS
SELECT
    e.environment_id,
    e.environment_code,
    mr.release_id,
    mr.release_version,
    mr.content_hash AS release_content_hash,
    io.ingestion_object_key,
    io.display_name,
    io.domain_key,
    io.is_required,
    ss.source_system_key,
    ss.source_type,
    ss.data_classification AS source_system_classification,
    sec.connection_reference_key,
    sec.landing_zone_key,
    sec.max_connection_concurrency,
    so.source_object_key,
    so.namespace_name AS source_namespace,
    so.object_name AS source_object_name,
    so.object_type AS source_object_type,
    so.business_key_contract,
    so.schema_drift_policy,
    so.data_classification AS source_object_classification,
    tgt.target_object_key,
    tgt.target_layer,
    tgt.store_alias AS target_store_alias,
    tgt.namespace_name AS target_namespace,
    tgt.object_name AS target_object_name,
    tgt.write_disposition,
    tgt.publication_boundary,
    lp.load_policy_key,
    lp.strategy_type,
    lp.duplicate_behavior,
    lp.delete_behavior,
    lp.schema_behavior,
    lp.idempotency_contract,
    wp.watermark_policy_key,
    wp.column_name AS watermark_column_name,
    wp.logical_data_type AS watermark_data_type,
    wp.comparison_operator AS watermark_comparison_operator,
    wp.overlap_amount AS watermark_overlap_amount,
    wp.overlap_unit AS watermark_overlap_unit,
    wp.initial_value_policy,
    wp.initial_value_literal,
    wp.upper_bound_mode,
    wp.late_arrival_behavior,
    ep.execution_policy_key,
    ep.timeout_minutes,
    ep.max_retries,
    ep.retry_delay_seconds,
    COALESCE(oec.priority_override, ep.default_priority) AS effective_priority,
    ep.concurrency_group,
    ep.max_parallelism,
    ep.recovery_mode,
    oec.routing_alias
FROM ctrl.Environment AS e
INNER JOIN ctrl.EnvironmentRelease AS er
    ON er.environment_id = e.environment_id
INNER JOIN ctrl.MetadataRelease AS mr
    ON mr.release_id = er.release_id
INNER JOIN ctrl.ObjectEnvironmentConfig AS oec
    ON oec.environment_id = e.environment_id
   AND oec.release_id = mr.release_id
   AND oec.is_enabled = 1
INNER JOIN ctrl.IngestionObject AS io
    ON io.release_id = oec.release_id
   AND io.ingestion_object_key = oec.ingestion_object_key
INNER JOIN ctrl.SourceObject AS so
    ON so.release_id = io.release_id
   AND so.source_object_key = io.source_object_key
INNER JOIN ctrl.SourceSystem AS ss
    ON ss.release_id = so.release_id
   AND ss.source_system_key = so.source_system_key
INNER JOIN ctrl.SourceEnvironmentConfig AS sec
    ON sec.release_id = ss.release_id
   AND sec.environment_id = e.environment_id
   AND sec.source_system_key = ss.source_system_key
   AND sec.is_enabled = 1
INNER JOIN ctrl.TargetObject AS tgt
    ON tgt.release_id = io.release_id
   AND tgt.target_object_key = io.target_object_key
INNER JOIN ctrl.LoadPolicy AS lp
    ON lp.release_id = io.release_id
   AND lp.load_policy_key = io.load_policy_key
LEFT JOIN ctrl.WatermarkPolicy AS wp
    ON wp.release_id = lp.release_id
   AND wp.watermark_policy_key = lp.watermark_policy_key
INNER JOIN ctrl.ExecutionPolicy AS ep
    ON ep.release_id = io.release_id
   AND ep.execution_policy_key = io.execution_policy_key
WHERE mr.release_status IN ('APPROVED', 'ACTIVE');

GO

