# GLITCHGUARD Troubleshooting: Telemetry & Wire Protocol Errors

This document provides diagnostic steps for wire protocol framing, CRC32 verification, and heartbeat timeout errors.

---

## 1. CRC32 Integrity Mismatch

### Symptoms
- Error logged: `CRC32 mismatch: calculated 0x... != received 0x...`.
- Diagnostics `invalid_messages` counter increments.

### Root Causes & Solutions
1. **Payload Modification after Hash Computation:**
   - The CRC32 checksum covers the canonical sorted JSON bytes of the `payload` field:
     ```python
     payload_bytes = json.dumps(self.payload, sort_keys=True).encode("utf-8")
     crc = binascii.crc32(payload_bytes)
     ```
   - Ensure keys in `payload` are not modified between serialization and transmission.
2. **Baud Rate Mismatch / Electrical Noise:**
   - Ensure host and Dabao are both configured for `115200 8N1`. Electrical noise on long cables may induce bit flips.

---

## 2. Heartbeat Deadline Exceeded / State Transition to `DEGRADED`

### Symptoms
- Connection manager logs: `Heartbeat deadline exceeded. Transitioning to DEGRADED`.
- Navbar status changes to yellow `DEGRADED` or red `RECONNECTING`.

### Root Causes & Solutions
1. **Target Board In Busy Loop / CPU Glitched:**
   - If the processor halts or hangs due to a simulated or physical glitch, heartbeats cease.
   - The watchdog service will attempt to reset the CPU after its configured window.
   - Click **Send PING** in the **Device Configuration** console to query board responsiveness.
2. **Buffer Backlog:**
   - If large debug bursts overflow the serial input FIFO, heartbeats may be delayed. Ensure log levels are set to `INFO` rather than `TRACE` during high-frequency telemetry.

---

## 3. WebSocket Disconnect / Reconnection Loops

### Symptoms
- React dashboard displays `POLLING` instead of `LIVE STREAM`.

### Root Causes & Solutions
1. **Backend Server Down:**
   - Verify that the FastAPI backend is running on `127.0.0.1:8000`:
     ```bash
     curl http://127.0.0.1:8000/api/status
     ```
2. **CORS / Hostname Mismatch:**
   - If accessing the dashboard from another machine on your LAN, update the WebSocket connection URL to use `window.location.hostname` instead of `127.0.0.1`.
