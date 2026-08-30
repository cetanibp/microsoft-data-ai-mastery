
CREATE   VIEW ctrl.vw_ObjectDependencyEdge
AS
SELECT
    od.release_id,
    od.predecessor_object_key,
    predecessor.display_name AS predecessor_display_name,
    od.successor_object_key,
    successor.display_name AS successor_display_name,
    od.dependency_condition,
    od.is_optional
FROM ctrl.ObjectDependency AS od
INNER JOIN ctrl.IngestionObject AS predecessor
    ON predecessor.release_id = od.release_id
   AND predecessor.ingestion_object_key = od.predecessor_object_key
INNER JOIN ctrl.IngestionObject AS successor
    ON successor.release_id = od.release_id
   AND successor.ingestion_object_key = od.successor_object_key;

GO

