import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app, serial_conn

# Mock serial port enumeration in test environment to avoid Windows WMI sandbox timeout
serial_conn.list_available_ports = staticmethod(lambda: [
    {"device": "COM9", "description": "USB Serial Device (Dabao OS)", "hwid": "1D50:6197"}
])

def test_api_status():
    with TestClient(app) as client:
        resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "connected" in data
        assert "available_ports" in data
        assert "total_events" in data

def test_api_capabilities():
    with TestClient(app) as client:
        resp = client.get("/api/capabilities")
        assert resp.status_code == 200
        data = resp.json()
        assert data["clock_skipping"] == "AVAILABLE"
        assert data["attack_counter"] == "AVAILABLE"
        assert data["glitch_detector"] == "NOT_VERIFIED"

def test_record_and_query_event():
    with TestClient(app) as client:
        event_payload = {
            "schema_version": "1.0",
            "source": "software_simulator",
            "event_type": "INTEGRITY_FAILURE",
            "severity": "HIGH",
            "experiment_id": "UNIT-TEST-EXP",
            "evidence": {"test": True},
            "verification_status": "FAILED",
            "response": "QUARANTINED"
        }
        resp = client.post("/api/events/record", json=event_payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "recorded"

        # Query back
        resp = client.get("/api/events?limit=10")
        assert resp.status_code == 200
        events = resp.json()
        assert len(events) >= 1
        assert events[-1]["experiment_id"] == "UNIT-TEST-EXP"

def test_metrics_calculation():
    with TestClient(app) as client:
        resp = client.get("/api/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_events" in data
        assert "simulated_events" in data
        assert "hardware_events" in data
        assert "recovery_success_rate" in data

def test_export_report():
    with TestClient(app) as client:
        resp = client.get("/api/reports/latest?format=json")
        assert resp.status_code == 200
        resp_csv = client.get("/api/reports/latest?format=csv")
        assert resp_csv.status_code == 200
        assert "schema_version" in resp_csv.text

if __name__ == "__main__":
    test_api_status()
    print("test_api_status: PASS")
    test_api_capabilities()
    print("test_api_capabilities: PASS")
    test_record_and_query_event()
    print("test_record_and_query_event: PASS")
    test_metrics_calculation()
    print("test_metrics_calculation: PASS")
    test_export_report()
    print("test_export_report: PASS")
    print("ALL BACKEND TESTS PASSED SUCCESSFULLY!")
