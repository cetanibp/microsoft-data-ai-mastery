# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

%pip install azure-eventhub -q

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import uuid
from datetime import datetime, timezone

from azure.eventhub import EventData, EventHubProducerClient

connection_string = notebookutils.credentials.getSecret(
    "https://kv-work-diary.vault.azure.net/",
    "rti001-eventstream-connection-string"
)

now_utc = datetime.now(timezone.utc).isoformat()

sample_event = {
    "EventId": str(uuid.uuid4()),
    "SchemaVersion": "1.0.0",
    "EventType": "OBJECT_RUN_COMPLETED",
    "EventTimeUtc": now_utc,
    "EmittedAtUtc": now_utc,
    "SequenceNumber": 1,
    "Environment": "development",
    "PipelineName": "PL_FAB002_IncrementalEncounter",
    "ObjectName": "Encounter",
    "RunId": str(uuid.uuid4()),
    "ObjectRunId": str(uuid.uuid4()),
    "CorrelationId": "RTI-001-SAMPLE",
    "Status": "SUCCEEDED",
    "Severity": "INFO",
    "ErrorClassification": "",
    "AcceptedRowCount": 4_000_000,
    "RejectedRowCount": 0,
    "ElapsedSeconds": 30.0,
    "MaximumWorkerQueueSeconds": 12.0,
    "Details": {
        "scenario": "RTI-001",
        "workload": "synthetic-sample",
        "alternative": "PAR4",
        "capacitySku": "F256"
    }
}

producer = None

try:
    producer = EventHubProducerClient.from_connection_string(
        conn_str=connection_string
    )

    batch = producer.create_batch()
    batch.add(EventData(json.dumps(sample_event)))
    producer.send_batch(batch)

    print("Event sent successfully")
    print(f"EventId: {sample_event['EventId']}")
    print(f"EventTimeUtc: {sample_event['EventTimeUtc']}")

finally:
    if producer is not None:
        producer.close()

    connection_string = None

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import uuid
from datetime import datetime, timedelta, timezone

from azure.eventhub import EventData, EventHubProducerClient

connection_string = notebookutils.credentials.getSecret(
    "https://kv-work-diary.vault.azure.net/",
    "rti001-eventstream-connection-string"
)

now_utc = datetime.now(timezone.utc)
test_id = str(uuid.uuid4())
correlation_id = f"RTI-001-EDGE-{test_id}"
run_id = str(uuid.uuid4())
out_of_order_object_run_id = str(uuid.uuid4())


def build_event(
    event_type,
    status,
    sequence_number,
    scenario,
    *,
    event_id=None,
    object_run_id=None,
    event_time=None,
    severity="INFO",
    error_classification=""
):
    timestamp = event_time or now_utc

    return {
        "EventId": event_id if event_id is not None else str(uuid.uuid4()),
        "SchemaVersion": "1.0.0",
        "EventType": event_type,
        "EventTimeUtc": timestamp.isoformat(),
        "EmittedAtUtc": now_utc.isoformat(),
        "SequenceNumber": sequence_number,
        "Environment": "development",
        "PipelineName": "PL_FAB002_IncrementalEncounter",
        "ObjectName": "Encounter",
        "RunId": run_id,
        "ObjectRunId": object_run_id or str(uuid.uuid4()),
        "CorrelationId": correlation_id,
        "Status": status,
        "Severity": severity,
        "ErrorClassification": error_classification,
        "AcceptedRowCount": 4_000_000,
        "RejectedRowCount": 0,
        "ElapsedSeconds": 30.0,
        "MaximumWorkerQueueSeconds": 12.0,
        "Details": {
            "scenario": scenario,
            "testId": test_id
        }
    }


# Control event
control_event = build_event(
    "OBJECT_RUN_COMPLETED",
    "SUCCEEDED",
    1,
    "CONTROL"
)

# Event time is ten minutes behind ingestion time
late_event = build_event(
    "OBJECT_RUN_COMPLETED",
    "SUCCEEDED",
    1,
    "LATE",
    event_time=now_utc - timedelta(minutes=10)
)

# Same EventId and payload sent twice
duplicate_event_id = str(uuid.uuid4())
duplicate_event = build_event(
    "STATUS_CHANGED",
    "RUNNING",
    1,
    "DUPLICATE",
    event_id=duplicate_event_id
)

# Syntactically valid JSON that violates the event contract
malformed_event = build_event(
    "",
    "UNKNOWN",
    0,
    "MALFORMED",
    event_id=""
)

# Sequence 2 is deliberately emitted before sequence 1
sequence_two_event = build_event(
    "STATUS_CHANGED",
    "FAILED",
    2,
    "OUT_OF_ORDER_SEQUENCE_2",
    object_run_id=out_of_order_object_run_id,
    severity="ERROR",
    error_classification="TEST_FAILURE"
)

sequence_one_event = build_event(
    "OBJECT_CLAIMED",
    "CLAIMED",
    1,
    "OUT_OF_ORDER_SEQUENCE_1",
    object_run_id=out_of_order_object_run_id
)

events = [
    control_event,
    late_event,
    duplicate_event,
    duplicate_event.copy(),
    sequence_two_event,
    sequence_one_event,
    malformed_event
]

producer = None

try:
    producer = EventHubProducerClient.from_connection_string(
        conn_str=connection_string
    )

    batch = producer.create_batch()

    for event in events:
        batch.add(EventData(json.dumps(event)))

    producer.send_batch(batch)

    print("Edge-case batch sent successfully")
    print(f"CorrelationId: {correlation_id}")
    print(f"Physical events sent: {len(events)}")
    print(f"Duplicate EventId: {duplicate_event_id}")
    print(f"Out-of-order ObjectRunId: {out_of_order_object_run_id}")

finally:
    if producer is not None:
        producer.close()

    connection_string = None

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import json
import uuid
from datetime import datetime, timezone

from azure.eventhub import EventData, EventHubProducerClient

connection_string = notebookutils.credentials.getSecret(
    "https://kv-work-diary.vault.azure.net/",
    "rti001-eventstream-connection-string"
)

now_utc = datetime.now(timezone.utc)

alert_event = {
    "EventId": str(uuid.uuid4()),
    "SchemaVersion": "1.0.0",
    "EventType": "STATUS_CHANGED",
    "EventTimeUtc": now_utc.isoformat(),
    "EmittedAtUtc": now_utc.isoformat(),
    "SequenceNumber": 1,
    "Environment": "development",
    "PipelineName": "PL_FAB002_IncrementalEncounter",
    "ObjectName": "Encounter",
    "RunId": str(uuid.uuid4()),
    "ObjectRunId": str(uuid.uuid4()),
    "CorrelationId": f"RTI-001-ALERT-{uuid.uuid4()}",
    "Status": "QUALITY_BLOCKED",
    "Severity": "ERROR",
    "ErrorClassification": "QUALITY_BLOCKED",
    "AcceptedRowCount": 0,
    "RejectedRowCount": 1,
    "ElapsedSeconds": 30.0,
    "MaximumWorkerQueueSeconds": 12.0,
    "Details": {
        "scenario": "ALERT_TRIGGER_TEST",
        "exercise": "RTI-001"
    }
}

producer = None

try:
    producer = EventHubProducerClient.from_connection_string(
        conn_str=connection_string
    )

    batch = producer.create_batch()
    batch.add(EventData(json.dumps(alert_event)))
    producer.send_batch(batch)

    print("Alert test event sent successfully")
    print(f"EventId: {alert_event['EventId']}")
    print(f"CorrelationId: {alert_event['CorrelationId']}")
    print(f"EmittedAtUtc: {alert_event['EmittedAtUtc']}")

finally:
    if producer is not None:
        producer.close()

    connection_string = None

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
