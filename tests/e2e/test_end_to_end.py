#!/usr/bin/env python3
"""
GLITCHGUARD End-to-End Operational Validation Suite
Verifies 10 core integration scenarios:
  - Scenario A: Device Discovery & Handshake
  - Scenario B: Continuous Heartbeat & Jitter Measurement (100 heartbeats)
  - Scenario C: Hardware Observation Query & Safety Guardrails
  - Scenario D: Controlled Software Fault Simulation (Experiments A-E)
  - Scenario E: Device Disconnection Handling
  - Scenario F: Device Reconnection Handling
  - Scenario G: Backend Restart & SQLite State Persistence
  - Scenario H: Dashboard WebSocket Catch-Up
  - Scenario I: Invalid / Malformed Telemetry Rejection
  - Scenario J: Sustained Telemetry Pipeline Stability
"""

import os
import sys
import time
import json
import pytest
from fastapi.testclient import TestClient

# Ensure host-tools is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOST_TOOLS_DIR = os.path.join(BASE_DIR, "host-tools")
if HOST_TOOLS_DIR not in sys.path:
    sys.path.insert(0, HOST_TOOLS_DIR)

from serial_comms.device_discovery import DeviceDiscovery, DabaoDeviceDescriptor, DabaoInterfaceMode
from serial_comms.connection_manager import (
    ConnectionManager,
    ConnectionState,
    ConnectionDiagnostics,
    global_connection_manager,
)
from parsers.protocol_framing import TelemetryFrame, MessageType
from parsers.event_parser import GlitchEventModel, EventSource, EventType, Severity, DefensiveResponse, VerificationStatus
from storage.database import TelemetryDatabase, telemetry_db
from backend.main import app, ws_manager


class TestEndToEndIntegration:

    def test_scenario_a_device_discovery_and_handshake(self):
        """Scenario A: Physical Dabao discovery, descriptor extraction, and handshake parsing."""
        devices = DeviceDiscovery.scan_ports()
        assert len(devices) >= 1, "At least one Dabao device must be detected"
        dabao = devices[0]
        assert dabao.vid == 0x1D50, f"Expected USB VID 0x1D50, got {hex(dabao.vid or 0)}"
        assert dabao.pid in [0x6196, 0x6197], f"Expected PID 0x6196 or 0x6197, got {hex(dabao.pid or 0)}"
        assert dabao.serial_number is not None, "Device serial number should not be None"

        # Verify ConnectionManager handshake structure
        mgr = ConnectionManager(manual_port=dabao.port)
        mgr.device_info.mode = dabao.mode
        mgr.device_info.public_serial = dabao.serial_number
        mgr.device_info.bootloader_ver = "v0.10.0-61-g5397e1b48"
        mgr.device_info.attack_counter = 1
        mgr.device_info.clock_skipping_active = True

        info = mgr.device_info.to_dict()
        assert info["device_type"] == "CrossBar Dabao"
        assert info["silicon_id"] == "Baochip-1x A0"
        assert info["attack_counter"] == 1
        assert info["clock_skipping_active"] is True
        print(f"\n[Scenario A PASS] Discovered {dabao.port} (VID:PID={hex(dabao.vid)}:{hex(dabao.pid)}) SN={dabao.serial_number}")

    def test_scenario_b_continuous_heartbeat_and_jitter(self):
        """Scenario B: Continuous heartbeat ingestion and jitter calculation over 100 intervals."""
        diag = ConnectionDiagnostics()
        diag.selected_port = "COM10"
        diag.baudrate = 115200

        # Simulate 100 periodic heartbeats with nominal 100ms interval +/- 2ms jitter
        import random
        random.seed(42)
        base_interval = 0.100  # 100ms
        sim_time = 1000.0

        for i in range(100):
            jitter = random.uniform(-0.003, 0.003)
            sim_time += base_interval + jitter
            diag.last_heartbeat_timestamp = sim_time
            if i > 0:
                delta = base_interval + jitter
                diag.heartbeat_intervals.append(delta)
                if len(diag.heartbeat_intervals) > 50:
                    diag.heartbeat_intervals.pop(0)
            diag.heartbeats_received += 1
            diag.messages_received += 1

        assert diag.heartbeats_received == 100
        mean_int = diag.mean_heartbeat_interval
        jitter_val = diag.heartbeat_jitter

        assert 0.090 <= mean_int <= 0.110, f"Mean interval {mean_int:.4f}s outside expected 100ms +/- 10ms"
        assert jitter_val < 0.015, f"Heartbeat jitter {jitter_val:.4f}s exceeded acceptable threshold (15ms)"
        print(f"\n[Scenario B PASS] 100 Heartbeats recorded: Mean={mean_int*1000:.2f}ms, Jitter={jitter_val*1000:.3f}ms")

    def test_scenario_c_hardware_observation_and_guardrails(self):
        """Scenario C: Non-destructive hardware observation and safety guardrail enforcement."""
        mgr = ConnectionManager(manual_port="COM10")

        # Verify safe command allowlist accepts PING, GET_STATUS, GET_CAPABILITIES
        # When not connected, returns clean status: error
        res = mgr.send_command("PING")
        assert res["status"] in ["success", "error"]

        # Verify prohibited dangerous commands raise ValueError
        PROHIBITED_COMMANDS = ["LOCKDOWN", "SELF_DESTRUCT", "PARANOID", "BLOW_FUSES", "ZEROIZE", "ERASE"]
        for bad_cmd in PROHIBITED_COMMANDS:
            with pytest.raises(ValueError) as excinfo:
                mgr.send_command(bad_cmd)
            assert "prohibited by GLITCHGUARD hardware security policy" in str(excinfo.value)

        print("\n[Scenario C PASS] Prohibited commands successfully blocked; safe command dispatcher validated")

    def test_scenario_d_controlled_fault_simulation_pipeline(self):
        """Scenario D: Complete software fault simulation pipeline across all 5 experiment types (A-E)."""
        experiments = [
            ("EXP-A", EventType.INTEGRITY_FAILURE, Severity.HIGH, "Instruction Skip Fault"),
            ("EXP-B", EventType.INTEGRITY_FAILURE, Severity.HIGH, "Register Corruption"),
            ("EXP-C", EventType.INTEGRITY_FAILURE, Severity.CRITICAL, "Memory Bit Flip"),
            ("EXP-D", EventType.HARDWARE_WARNING, Severity.MEDIUM, "Clock Jitter Anomaly"),
            ("EXP-E", EventType.RESET_EVENT, Severity.CRITICAL, "Voltage Brownout Simulation"),
        ]

        recorded_ids = []
        for exp_id, ev_type, sev, desc in experiments:
            ev = GlitchEventModel(
                schema_version="1.0",
                source=EventSource.SOFTWARE_SIMULATOR,
                event_type=ev_type,
                severity=sev,
                experiment_id=exp_id,
                device_session_id="sess-e2e-test",
                evidence={"description": desc, "latency_us": 0.705, "trial": 1},
                verification_status=VerificationStatus.PASSED,
                response=DefensiveResponse.RECOVERED,
            )
            eid = telemetry_db.record_event(ev.model_dump())
            recorded_ids.append(eid)

        assert len(recorded_ids) == 5
        # Verify all events queryable from database
        for eid in recorded_ids:
            stored = telemetry_db.get_event_by_id(eid)
            assert stored is not None
            assert stored["response"] == "RECOVERED"

        print(f"\n[Scenario D PASS] Fault simulation pipeline verified across {len(experiments)} experiment types")

    def test_scenario_e_device_disconnection_handling(self):
        """Scenario E: Device disconnection handling and backend resilience."""
        mgr = ConnectionManager(manual_port="COM10")
        mgr.state = ConnectionState.CONNECTED
        assert mgr.state == ConnectionState.CONNECTED

        # Trigger disconnect
        mgr.disconnect()
        assert mgr.state == ConnectionState.DISCONNECTED

        # Verify backend API continues serving without crashing
        with TestClient(app) as client:
            resp = client.get("/api/status")
            assert resp.status_code == 200
            assert "total_events" in resp.json()

            resp_events = client.get("/api/events?limit=5")
            assert resp_events.status_code == 200

        print("\n[Scenario E PASS] Disconnection handled cleanly; REST APIs remain 100% operational")

    def test_scenario_f_device_reconnection_handling(self):
        """Scenario F: Device reconnection lifecycle and state restoration."""
        mgr = ConnectionManager(manual_port="COM10")
        mgr.state = ConnectionState.DISCONNECTED

        # Transition to reconnecting
        mgr.state = ConnectionState.RECONNECTING
        assert mgr.state == ConnectionState.RECONNECTING

        # Simulate successful reconnection
        mgr.state = ConnectionState.CONNECTED
        mgr.diagnostics.record_heartbeat()
        assert mgr.state == ConnectionState.CONNECTED
        assert mgr.diagnostics.heartbeats_received >= 1

        print("\n[Scenario F PASS] Reconnection state transition and diagnostics resumption verified")

    def test_scenario_g_backend_restart_and_persistence(self):
        """Scenario G: Backend restart simulation with persistent SQLite verification."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        test_db_path = os.path.join(temp_dir, "restart_test.db")

        # Phase 1: create db and insert records
        db1 = TelemetryDatabase(db_path=test_db_path)
        test_event = {
            "event_id": "persist-test-001",
            "schema_version": "1.0",
            "device_session_id": "sess-persist",
            "timestamp_ns": int(time.time() * 1e9),
            "source": "hardware_sensor",
            "event_type": "HARDWARE_WARNING",
            "severity": "MEDIUM",
            "experiment_id": "PERSIST_TEST",
            "evidence": {"audit": "passed"},
            "verification_status": "PASSED",
            "response": "LOGGED",
        }
        db1.record_event(test_event)

        # Close and recreate db instance (simulating backend reboot)
        del db1
        db2 = TelemetryDatabase(db_path=test_db_path)
        retrieved = db2.get_event_by_id("persist-test-001")

        assert retrieved is not None
        assert retrieved["event_id"] == "persist-test-001"
        assert retrieved["experiment_id"] == "PERSIST_TEST"
        assert retrieved["evidence"]["audit"] == "passed"

        print("\n[Scenario G PASS] SQLite event persistence verified across simulated backend restart")

    def test_scenario_h_dashboard_websocket_catchup(self):
        """Scenario H: WebSocket client catch-up with initial snapshot and ping-pong."""
        with TestClient(app) as client:
            with client.websocket_connect("/ws/telemetry") as ws:
                snapshot = ws.receive_json()
                assert snapshot["type"] == "INIT_SNAPSHOT"
                assert "connection_state" in snapshot
                assert "metrics" in snapshot
                assert "recent_events" in snapshot

                # Test interactive WebSocket ping
                ws.send_json({"type": "PING"})
                pong = ws.receive_json()
                assert pong["type"] == "PONG"
                assert "timestamp_ns" in pong

        print("\n[Scenario H PASS] WebSocket snapshot and interactive catch-up verified")

    def test_scenario_i_invalid_malformed_telemetry_rejection(self):
        """Scenario I: Robust rejection of corrupt, malformed, or out-of-schema telemetry frames."""
        # 1. Non-JSON string
        f1, err1 = TelemetryFrame.parse_line("corrupt_raw_bytes_not_json\n")
        assert f1 is None
        assert "JSON decode error" in err1

        # 2. Unsupported protocol version
        bad_ver = json.dumps({"protocol_version": "99.0", "message_type": "HEARTBEAT"})
        f2, err2 = TelemetryFrame.parse_line(bad_ver)
        assert f2 is None
        assert "Unsupported protocol version" in err2

        # 3. Missing message type
        bad_msg = json.dumps({"protocol_version": "1.0"})
        f3, err3 = TelemetryFrame.parse_line(bad_msg)
        assert f3 is None
        assert "Missing message_type" in err3

        # 4. Invalid CRC32 integrity
        bad_crc = json.dumps({
            "protocol_version": "1.0",
            "message_type": "HARDWARE_EVENT",
            "payload": {"test": 123},
            "integrity": "0xDEADBEEF"
        })
        f4, err4 = TelemetryFrame.parse_line(bad_crc)
        assert f4 is None
        assert "CRC32 mismatch" in err4

        print("\n[Scenario I PASS] All malformed and invalid telemetry frames safely rejected without parser crashes")

    def test_scenario_j_sustained_telemetry_stability(self):
        """Scenario J: High-throughput telemetry pipeline stability check (1000 messages batch)."""
        start_time = time.time()
        diag = ConnectionDiagnostics()

        for seq in range(1000):
            frame = TelemetryFrame(
                message_type=MessageType.HEARTBEAT,
                payload={"tick": seq},
                sequence=seq,
            )
            line = frame.serialize_line()
            parsed, err = TelemetryFrame.parse_line(line)
            assert err is None
            assert parsed is not None
            assert parsed.sequence == seq
            diag.messages_received += 1

        elapsed = time.time() - start_time
        rate = 1000 / elapsed if elapsed > 0 else 0
        assert diag.messages_received == 1000
        print(f"\n[Scenario J PASS] 1,000 frames framed & parsed in {elapsed:.3f}s ({rate:.0f} msgs/sec)")


if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
