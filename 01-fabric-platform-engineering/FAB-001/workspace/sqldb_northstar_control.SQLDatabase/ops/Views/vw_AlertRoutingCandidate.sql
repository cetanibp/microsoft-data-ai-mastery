CREATE VIEW [ops].[vw_AlertRoutingCandidate]
AS
SELECT
    breach.slo_evaluation_id,
    breach.environment_id,
    breach.environment_code,
    breach.release_id,
    breach.ingestion_object_key,
    breach.objective_key,
    breach.alert_severity,
    CASE breach.objective_key
        WHEN 'critical-freshness' THEN 'FRESHNESS'
        WHEN 'standard-freshness' THEN 'FRESHNESS'
        WHEN 'ingestion-reliability' THEN 'RELIABILITY'
        WHEN 'duration-compliance' THEN 'DURATION'
        WHEN 'quality-acceptance' THEN 'QUALITY'
        WHEN 'quality-enforcement' THEN 'QUALITY_ENFORCEMENT'
        WHEN 'critical-alert-latency' THEN 'ALERT_LATENCY'
    END AS detection_category,
    owner_assignment.ownership_role AS owner_role,
    owner_assignment.owner_group_key,
    owner_assignment.routing_alias,
    CASE WHEN breach.is_production = 1
        THEN 'NOTIFICATION_REQUESTED' ELSE 'SIMULATED' END AS delivery_mode,
    CASE WHEN owner_assignment.routing_alias IS NULL
        THEN 'NO_ROUTE' ELSE 'ROUTED' END AS decision_status,
    CONVERT(varchar(64), HASHBYTES('SHA2_256', CONCAT(
        CONVERT(varchar(36), breach.environment_id), '|',
        COALESCE(breach.ingestion_object_key, 'platform'), '|',
        breach.objective_key, '|', breach.alert_severity, '|',
        CONVERT(varchar(33), breach.window_end_utc, 126), '|',
        COALESCE(owner_assignment.routing_alias, 'no-route'))), 2) AS deduplication_key,
    breach.detected_at_utc,
    breach.window_start_utc,
    breach.window_end_utc,
    breach.observed_value,
    breach.target_value,
    breach.comparison_operator,
    breach.target_unit
FROM ops.vw_OpenSloBreach AS breach
OUTER APPLY
(
    SELECT TOP (1)
        ownership.ownership_role,
        ownership.owner_group_key,
        owner_group.routing_alias
    FROM ctrl.ObjectOwnership AS ownership
    INNER JOIN ctrl.OwnerGroup AS owner_group
        ON owner_group.release_id = ownership.release_id
       AND owner_group.owner_group_key = ownership.owner_group_key
    WHERE ownership.release_id = breach.release_id
      AND ownership.ingestion_object_key = breach.ingestion_object_key
    ORDER BY
        CASE
            WHEN breach.objective_key IN ('quality-enforcement', 'quality-acceptance',
                                          'critical-alert-latency')
             AND ownership.ownership_role = 'INCIDENT' THEN 1
            WHEN breach.objective_key IN ('critical-freshness', 'standard-freshness',
                                          'ingestion-reliability', 'duration-compliance')
             AND ownership.ownership_role = 'OPERATIONS' THEN 1
            WHEN ownership.ownership_role = 'INCIDENT' THEN 2
            WHEN ownership.ownership_role = 'OPERATIONS' THEN 3
            WHEN ownership.ownership_role = 'ENGINEERING' THEN 4
            WHEN ownership.ownership_role = 'SOURCE_STEWARD' THEN 5
            WHEN ownership.ownership_role = 'DATA_PRODUCT' THEN 6
            ELSE 7
        END,
        ownership.owner_group_key
) AS owner_assignment
WHERE breach.routing_status = 'UNROUTED';
GO
