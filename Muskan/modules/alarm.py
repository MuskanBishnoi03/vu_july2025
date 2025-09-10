import json, os, uuid
from datetime import datetime, timezone
import boto3

TABLE_NAME = os.environ["TABLE_NAME"]
ddb = boto3.resource("dynamodb").Table(TABLE_NAME)

def handler(event, context):
    for record in event.get("Records", []):
        msg_str = record["Sns"]["Message"]
        try:
            msg = json.loads(msg_str)
        except Exception:
            msg = {"RawMessage": msg_str}

        alarm_name = msg.get("AlarmName", "UnknownAlarm")
        new_state  = msg.get("NewStateValue", "UNKNOWN")
        reason     = msg.get("NewStateReason", "")
        change_time= msg.get("StateChangeTime", datetime.now(timezone.utc).isoformat())

        site_name = None
        trigger = msg.get("Trigger", {})
        for dim in trigger.get("Dimensions", []):
            n = dim.get("name") or dim.get("Name")
            if n == "SiteName":
                site_name = dim.get("value") or dim.get("Value")
                break

        ddb.put_item(Item={
            "id": str(uuid.uuid4()),
            "alarm_name": alarm_name,
            "site_name": site_name or "Unknown",
            "new_state": new_state,                    # ALARM | OK | INSUFFICIENT_DATA
            "reason": reason,
            "state_change_time": change_time,
            "inserted_at": datetime.now(timezone.utc).isoformat(),
            "namespace": trigger.get("Namespace"),
            "metric_name": trigger.get("MetricName"),
        })

    return {"ok": True}
