CREATE PROCEDURE [ops].[usp_RecordAlertRoutingDecision]
    @alert_routing_decision_id UNIQUEIDENTIFIER,
    @slo_evaluation_id UNIQUEIDENTIFIER = NULL,
    @object_run_id UNIQUEIDENTIFIER = NULL,
    @environment_id UNIQUEIDENTIFIER,
    @release_id UNIQUEIDENTIFIER,
    @ingestion_object_key VARCHAR(150) = NULL,
    @detection_category VARCHAR(40),
    @alert_severity VARCHAR(2),
    @owner_role VARCHAR(30) = NULL,
    @owner_group_key VARCHAR(100) = NULL,
    @routing_alias VARCHAR(200) = NULL,
    @decision_status VARCHAR(20),
    @deduplication_scope VARCHAR(300),
    @decision_reason NVARCHAR(1000),
    @detected_at_utc DATETIME2(7),
    @routed_at_utc DATETIME2(7)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

    IF @slo_evaluation_id IS NULL AND @object_run_id IS NULL
        THROW 51000, 'Alert routing requires evaluation or object-run evidence.', 1;

    IF @alert_severity = 'P1' AND @decision_status = 'SUPPRESSED'
        THROW 51000, 'P1 alert routing cannot be suppressed.', 1;

    IF @detected_at_utc > @routed_at_utc
        THROW 51000, 'Alert routing cannot precede detection.', 1;

    DECLARE @is_production BIT;
    SELECT @is_production = is_production
    FROM ctrl.Environment
    WHERE environment_id = @environment_id;

    IF @is_production IS NULL
        THROW 51000, 'Alert routing environment does not exist.', 1;

    DECLARE @delivery_mode VARCHAR(30) =
        CASE WHEN @is_production = 1
            THEN 'NOTIFICATION_REQUESTED' ELSE 'SIMULATED' END;

    IF @decision_status = 'NO_ROUTE'
    BEGIN
        SET @owner_role = NULL;
        SET @owner_group_key = NULL;
        SET @routing_alias = NULL;
    END
    ELSE IF NOT EXISTS
    (
        SELECT 1
        FROM ctrl.OwnerGroup AS owner_group
        WHERE owner_group.release_id = @release_id
          AND owner_group.owner_group_key = @owner_group_key
          AND owner_group.routing_alias = @routing_alias
    )
        THROW 51000, 'Alert routing alias does not match the release owner group.', 1;

    IF @decision_status <> 'NO_ROUTE' AND @ingestion_object_key IS NOT NULL
       AND NOT EXISTS
    (
        SELECT 1
        FROM ctrl.ObjectOwnership
        WHERE release_id = @release_id
          AND ingestion_object_key = @ingestion_object_key
          AND owner_group_key = @owner_group_key
          AND ownership_role = @owner_role
    )
        THROW 51000, 'Alert routing owner is not assigned to the ingestion object.', 1;

    DECLARE @deduplication_key VARCHAR(64) = CONVERT(varchar(64),
        HASHBYTES('SHA2_256', CONCAT(
            CONVERT(varchar(36), @environment_id), '|',
            COALESCE(@ingestion_object_key, 'platform'), '|',
            @detection_category, '|', @alert_severity, '|',
            @deduplication_scope, '|', COALESCE(@routing_alias, 'no-route'))), 2);

    BEGIN TRANSACTION;

    DECLARE @existing_id UNIQUEIDENTIFIER;
    SELECT @existing_id = alert_routing_decision_id
    FROM ops.AlertRoutingDecision WITH (UPDLOCK, HOLDLOCK)
    WHERE deduplication_key = @deduplication_key
      AND ((routing_alias = @routing_alias)
           OR (routing_alias IS NULL AND @routing_alias IS NULL));

    IF @existing_id IS NOT NULL
    BEGIN
        IF NOT EXISTS
        (
            SELECT 1
            FROM ops.AlertRoutingDecision
            WHERE alert_routing_decision_id = @existing_id
              AND environment_id = @environment_id
              AND release_id = @release_id
              AND detection_category = @detection_category
              AND alert_severity = @alert_severity
              AND delivery_mode = @delivery_mode
              AND decision_status = @decision_status
        )
        BEGIN
            ROLLBACK TRANSACTION;
            THROW 51000, 'Alert routing identity changed.', 1;
        END;

        COMMIT TRANSACTION;
        SELECT @existing_id AS alert_routing_decision_id,
               @deduplication_key AS deduplication_key, CAST(0 AS bit) AS inserted;
        RETURN;
    END;

    INSERT ops.AlertRoutingDecision
    (
        alert_routing_decision_id, slo_evaluation_id, object_run_id,
        environment_id, release_id, ingestion_object_key, detection_category,
        alert_severity, owner_role, owner_group_key, routing_alias,
        delivery_mode, decision_status, deduplication_key, decision_reason,
        detected_at_utc, routed_at_utc
    )
    VALUES
    (
        @alert_routing_decision_id, @slo_evaluation_id, @object_run_id,
        @environment_id, @release_id, @ingestion_object_key, @detection_category,
        @alert_severity, @owner_role, @owner_group_key, @routing_alias,
        @delivery_mode, @decision_status, @deduplication_key, @decision_reason,
        @detected_at_utc, @routed_at_utc
    );

    COMMIT TRANSACTION;
    SELECT @alert_routing_decision_id AS alert_routing_decision_id,
           @deduplication_key AS deduplication_key, CAST(1 AS bit) AS inserted;
END;
GO
