import os
import sys
import pytest

# Add host-tools to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parsers.event_parser import (
    GlitchEventModel,
    EventSource,
    EventType,
    Severity,
    VerificationStatus,
    DefensiveResponse,
    parse_event_json,
)

def test_event_schema_valid():
    event = GlitchEventModel(
        source=EventSource.SOFTWARE_SIMULATOR,
        event_type=EventType.INTEGRITY_FAILURE,
        severity=Severity.HIGH,
        experiment_id="TEST-001",
        evidence={"detail": "unit-test"},
        verification_status=VerificationStatus.FAILED,
        response=DefensiveResponse.QUARANTINED,
    )
    raw = event.model_dump_json()
    parsed = parse_event_json(raw)
    assert parsed.event_id == event.event_id
    assert parsed.source == EventSource.SOFTWARE_SIMULATOR
    assert parsed.severity == Severity.HIGH

def test_invalid_schema_version_rejected():
    data = {
        "schema_version": "2.0",
        "source": "software_simulator",
        "event_type": "NORMAL",
        "severity": "INFO",
    }
    with pytest.raises(Exception):
        GlitchEventModel.model_validate(data)

def test_hardware_sensor_source_distinct_from_simulator():
    assert EventSource.HARDWARE_SENSOR != EventSource.SOFTWARE_SIMULATOR
