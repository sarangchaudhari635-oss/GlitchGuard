import csv
import io
import json
from typing import List
from parsers.event_parser import GlitchEventModel

class ReportExporter:
    @staticmethod
    def export_json(events: List[GlitchEventModel]) -> str:
        return json.dumps([e.model_dump() for e in events], indent=2)

    @staticmethod
    def export_csv(events: List[GlitchEventModel]) -> str:
        output = io.StringIO()
        fieldnames = [
            "schema_version",
            "event_id",
            "timestamp_ns",
            "source",
            "event_type",
            "severity",
            "experiment_id",
            "device_session_id",
            "verification_status",
            "response",
            "evidence"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for e in events:
            row = e.model_dump()
            row["evidence"] = json.dumps(row.get("evidence", {}))
            writer.writerow(row)
        return output.getvalue()
