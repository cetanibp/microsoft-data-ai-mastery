CREATE PROCEDURE [ops].[usp_ResolveWatermarkContext]
    @environment_code varchar(30),
    @ingestion_object_key varchar(150)
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF
    (
        SELECT COUNT_BIG(*)
        FROM ctrl.vw_ActiveIngestionConfiguration
        WHERE environment_code = @environment_code
          AND ingestion_object_key = @ingestion_object_key
    ) <> 1
        THROW 51001, 'Expected exactly one active ingestion configuration.', 1;

    IF EXISTS
    (
        SELECT 1
        FROM ctrl.vw_ActiveIngestionConfiguration
        WHERE environment_code = @environment_code
          AND ingestion_object_key = @ingestion_object_key
          AND
          (
              strategy_type <> 'WATERMARK'
              OR watermark_comparison_operator <> '>'
              OR watermark_policy_key IS NULL
          )
    )
        THROW 51002, 'The active object is not a supported watermark configuration.', 1;

    SELECT
        config.*,
        COALESCE(state.committed_value, config.initial_value_literal) AS committed_value,
        COALESCE(state.state_version, CONVERT(bigint, 0)) AS state_version,
        state.committed_object_run_id,
        state.committed_at_utc
    FROM ctrl.vw_ActiveIngestionConfiguration AS config
    LEFT JOIN ops.WatermarkState AS state
        ON state.environment_id = config.environment_id
       AND state.ingestion_object_key = config.ingestion_object_key
    WHERE config.environment_code = @environment_code
      AND config.ingestion_object_key = @ingestion_object_key;
END;
GO
