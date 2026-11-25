import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from serial_comms.device_discovery import DeviceDiscovery, DabaoDeviceDescriptor, DabaoInterfaceMode

# Mock serial port discovery in test environment to avoid Windows WMI sandbox timeout
DeviceDiscovery.scan_ports = staticmethod(lambda: [
    DabaoDeviceDescriptor(
        port="COM10",
        description="CrossBar Dabao Bootloader (1D50:6196)",
        hwid="USB\\VID_1D50&PID_6196",
        vid=0x1D50,
        pid=0x6196,
        serial_number="NNBT1T",
        mode=DabaoInterfaceMode.BOOTLOADER
    )
])


def test_api_status():
    with TestClient(app) as client:
        resp = client.get("/api/status")
        assert resp.status_code == 200
        data = resp.json()
        assert "connected" in data
        assert "connection_state" in data
        assert "available_ports" in data
        assert "total_events" in data
        assert "current_security_state" in data


def test_api_device_info():
    with TestClient(app) as client:
        resp = client.get("/api/device/info")
        assert resp.status_code == 200
        data = resp.json()
        assert "device_type" in data
        assert "silicon_id" in data
        assert "connection_state" in data


def test_api_capabilities():
    with TestClient(app) as client:
        resp = client.get("/api/device/capabilities")
        assert resp.status_code == 200
        data = resp.json()
        assert data["clock_skipping"] == "AVAILABLE"
        assert data["attack_counter"] == "AVAILABLE"
        assert data["glitch_detector"] == "NOT_VERIFIED"


def test_api_device_connection():
    with TestClient(app) as client:
        resp = client.get("/api/device/connection")
        assert resp.status_code == 200
        data = resp.json()
        assert "state" in data
        assert "diagnostics" in data


def test_record_and_query_event():
    with TestClient(app) as client:
        event_payload = {
            "schema_version": "1.0",
            "source": "software_simulator",
            "event_type": "INTEGRITY_FAILURE",
            "severity": "HIGH",
            "experiment_id": "UNIT-TEST-EXP",
            "evidence": {"test": True, "latency_us": 0.72},
            "verification_status": "FAILED",
            "response": "QUARANTINED"
        }
        resp = client.post("/api/events/record", json=event_payload)
        assert resp.status_code == 200
        recorded_id = resp.json()["event_id"]
        assert resp.json()["status"] == "recorded"

        # Query list
        resp = client.get("/api/events?limit=10")
        assert resp.status_code == 200
        events = resp.json()
        assert len(events) >= 1

        # Query single event
        resp_single = client.get(f"/api/events/{recorded_id}")
        assert resp_single.status_code == 200
        single_data = resp_single.json()
        assert single_data["event_id"] == recorded_id
        assert single_data["experiment_id"] == "UNIT-TEST-EXP"


def test_experiment_lifecycle():
    with TestClient(app) as client:
        start_payload = {
            "experiment_id": "EXP-A",
            "experiment_name": "Instruction Skip Fault",
            "target": "software_simulator",
            "iterations": 20
        }
        resp = client.post("/api/experiments/start", json=start_payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "started"

        stop_resp = client.post("/api/experiments/stop")
        assert stop_resp.status_code == 200
        assert stop_resp.json()["status"] == "stopped"


def test_metrics_calculation():
    with TestClient(app) as client:
        resp = client.get("/api/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_events" in data
        assert "simulated_events" in data
        assert "hardware_events" in data
        assert "recovery_success_rate" in data

        resp_det = client.get("/api/metrics/detection")
        assert resp_det.status_code == 200
        assert "mean_latency_us" in resp_det.json()

        resp_rec = client.get("/api/metrics/recovery")
        assert resp_rec.status_code == 200
        assert "recovery_success_rate" in resp_rec.json()


def test_device_commands_when_disconnected():
    with TestClient(app) as client:
        resp_ping = client.post("/api/device/ping")
        assert resp_ping.status_code == 200
        # Returns either success or clean error status
        assert "status" in resp_ping.json()

        resp_status = client.post("/api/device/request-status")
        assert resp_status.status_code == 200
        assert "status" in resp_status.json()

        resp_caps = client.post("/api/device/request-capabilities")
        assert resp_caps.status_code == 200
        assert "status" in resp_caps.json()


def test_export_report():
    with TestClient(app) as client:
        resp = client.get("/api/reports/latest?format=json")
        assert resp.status_code == 200
        resp_csv = client.get("/api/reports/latest?format=csv")
        assert resp_csv.status_code == 200
        assert "schema_version" in resp_csv.text


def test_websocket_telemetry():
    with TestClient(app) as client:
        with client.websocket_connect("/ws/telemetry") as ws:
            # First message should be INIT_SNAPSHOT
            data = ws.receive_json()
            assert data["type"] == "INIT_SNAPSHOT"
            assert "connection_state" in data
            assert "metrics" in data

            # Send ping
            ws.send_json({"type": "PING"})
            pong = ws.receive_json()
            assert pong["type"] == "PONG"
            assert "timestamp_ns" in pong


if __name__ == "__main__":
    pytest.main(["-v", __file__])
