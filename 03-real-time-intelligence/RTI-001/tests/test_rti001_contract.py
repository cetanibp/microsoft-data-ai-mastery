"""Contract checks for committed RTI-001 Fabric item definitions."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "workspace"
SCHEMA = WORKSPACE / "eh_northstar_operations.Eventhouse" / ".children" / "kqldb_northstar_operations.KQLDatabase" / "DatabaseSchema.kql"
EVENTSTREAM = WORKSPACE / "es_northstar_operational_events.Eventstream" / "eventstream.json"
NOTEBOOK = WORKSPACE / "nb_rti001_event_generator.Notebook" / "notebook-content.py"
QUERYSET = WORKSPACE / "qs_northstar_operational_monitoring.KQLQueryset" / "RealTimeQueryset.json"
DASHBOARD = WORKSPACE / "rtd_northstar_operational_monitoring.KQLDashboard" / "RealTimeDashboard.json"
ACTIVATOR = WORKSPACE / "act_northstar_operational_alerts.Reflex" / "ReflexEntities.json"


class Rti001ContractTests(unittest.TestCase):
    def test_schema_and_lifecycle(self) -> None:
        text = SCHEMA.read_text(encoding="utf-8")
        for token in (
            "OperationalEventRaw",
            "OperationalEventRejected",
            "OperationalEventValidated()",
            "OperationalEventAccepted()",
            "OperationalObjectCurrent()",
            "MISSING_EVENT_ID",
            "UNSUPPORTED_SCHEMA_VERSION",
            "arg_max(IngestedAtUtc, *) by EventId",
            "arg_max(SequenceNumber, *) by ObjectRunId",
            "IngestedAtUtc - 5m",
            '"SoftDeletePeriod":"30.00:00:00"',
            "time(7.00:00:00)",
        ):
            self.assertIn(token, text)

    def test_eventstream_route(self) -> None:
        definition = json.loads(EVENTSTREAM.read_text(encoding="utf-8"))
        self.assertEqual(definition["sources"][0]["name"], "src_northstar_operational_events")
        self.assertEqual(definition["sources"][0]["type"], "CustomEndpoint")
        destination = definition["destinations"][0]
        self.assertEqual(destination["name"], "dest_operational_event_raw")
        self.assertEqual(destination["properties"]["databaseName"], "kqldb_northstar_operations")
        self.assertEqual(destination["properties"]["tableName"], "OperationalEventRaw")
        self.assertEqual(destination["properties"]["inputSerialization"]["type"], "Json")

    def test_notebook_uses_key_vault_without_committed_secret(self) -> None:
        text = NOTEBOOK.read_text(encoding="utf-8")
        self.assertIn("notebookutils.credentials.getSecret", text)
        self.assertIn("rti001-eventstream-connection-string", text)
        for forbidden in ("Endpoint=sb://", "SharedAccessKey=", "SharedAccessKeyName="):
            self.assertNotIn(forbidden, text)

    def test_actionable_queryset(self) -> None:
        definition = json.loads(QUERYSET.read_text(encoding="utf-8"))
        tab = definition["queryset"]["tabs"][0]
        self.assertEqual(tab["title"], "ActionableFailures")
        query = tab["content"]
        for token in (
            "OperationalEventAccepted()",
            "ago(2m)",
            '"FAILED"',
            '"QUALITY_BLOCKED"',
            '"RECOVERY_REQUIRED"',
            '"ERROR"',
            '"CRITICAL"',
            "DetectionLatencySeconds",
            "CorrelationId",
        ):
            self.assertIn(token, query)

    def test_activator_rule(self) -> None:
        entities = json.loads(ACTIVATOR.read_text(encoding="utf-8"))
        source = next(entity for entity in entities if entity["type"] == "kqlSource-v1")
        self.assertEqual(source["payload"]["runSettings"]["executionIntervalInSeconds"], 60)
        rule_entity = next(
            entity
            for entity in entities
            if entity["type"] == "timeSeriesView-v1"
            and entity["payload"].get("name") == "RTI001_ActionableFailure"
        )
        rule = json.loads(rule_entity["payload"]["definition"]["instance"])
        self.assertEqual(rule["templateId"], "EventTrigger")
        serialized = json.dumps(rule)
        for field in (
            "EventId",
            "CorrelationId",
            "PipelineName",
            "ObjectName",
            "Status",
            "Severity",
            "ErrorClassification",
            "EmittedAtUtc",
            "IngestedAtUtc",
            "DetectionLatencySeconds",
        ):
            self.assertIn(field, serialized)

    def test_dashboard_contract(self) -> None:
        definition = json.loads(DASHBOARD.read_text(encoding="utf-8"))
        titles = {tile["title"] for tile in definition["tiles"]}
        self.assertEqual(
            titles,
            {
                "Current object-run state",
                "Active actionable conditions",
                "Event ingestion latency",
                "Recent operational events",
            },
        )
        queries = "\n".join(query["text"] for query in definition["queries"])
        for token in (
            "OperationalObjectCurrent()",
            "ActiveConditionCount",
            "percentile(IngestionLatencySeconds, 50)",
            "percentile(IngestionLatencySeconds, 95)",
            "OperationalEventValidated()",
            "RejectionReason",
            "IsLate",
        ):
            self.assertIn(token, queries)

    def test_no_connection_string_pattern_anywhere_in_text_definitions(self) -> None:
        secret_pattern = re.compile(r"(?:Endpoint=sb://|SharedAccessKey=|SharedAccessKeyName=)", re.I)
        for path in WORKSPACE.rglob("*"):
            if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.assertIsNone(secret_pattern.search(text), str(path))


if __name__ == "__main__":
    unittest.main()

