from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid

SCHEMA_VERSION = "1.0"

class EventSource(str, Enum):
    HARDWARE_SENSOR = "hardware_sensor"
    SOFTWARE_SIMULATOR = "software_simulator"
    RUNTIME_MONITOR = "runtime_monitor"
    RESET_CONTROLLER = "reset_controller"

class EventType(str, Enum):
    NORMAL = "NORMAL"
    ANOMALY = "ANOMALY"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
    HARDWARE_WARNING = "HARDWARE_WARNING"
    RESET_EVENT = "RESET_EVENT"
    HEARTBEAT_TIMEOUT = "HEARTBEAT_TIMEOUT"
    RECOVERY = "RECOVERY"
    SENSOR_UNAVAILABLE = "SENSOR_UNAVAILABLE"

class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class VerificationStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    PENDING = "PENDING"
    ERROR = "ERROR"

class DefensiveResponse(str, Enum):
    NONE = "NONE"
    LOGGED = "LOGGED"
    ALERT = "ALERT"
    QUARANTINED = "QUARANTINED"
    VERIFYING = "VERIFYING"
    RECOVERED = "RECOVERED"
    LOCKDOWN = "LOCKDOWN"

class GlitchEventModel(BaseModel):
    schema_version: str = Field(default=SCHEMA_VERSION)
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_ns: int = Field(default_factory=lambda: int(datetime.now(timezone.utc).timestamp() * 1e9))
    source: EventSource
    event_type: EventType
    severity: Severity
    experiment_id: str = Field(default="BASELINE")
    device_session_id: str = Field(default="sess-default")
    evidence: Dict[str, Any] = Field(default_factory=dict)
    verification_status: VerificationStatus = Field(default=VerificationStatus.SKIPPED)
    response: DefensiveResponse = Field(default=DefensiveResponse.NONE)

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, v: str) -> str:
        if not v.startswith("1."):
            raise ValueError(f"Unsupported schema version: {v}. Expected 1.x")
        return v

def parse_event_json(raw_json: str) -> GlitchEventModel:
    """Parse and validate JSON string against GlitchEventModel schema."""
    return GlitchEventModel.model_validate_json(raw_json)
