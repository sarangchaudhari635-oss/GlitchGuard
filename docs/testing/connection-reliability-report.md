# GLITCHGUARD Connection Reliability & Fault Recovery Report

**System:** GLITCHGUARD Serial Communications Subsystem (`host-tools/serial_comms/`)  
**Scope:** Device discovery, port contention handling, Win32 overlapped IO synchronization, automatic reconnection, and WebSocket failover.

---

## 1. Thread Safety & Win32 Overlapped IO Handling

### The Problem
On Microsoft Windows, concurrent calls to `in_waiting`, `readline()`, and `write()` on a single `pyserial.Serial` instance across distinct threads result in Win32 ctypes memory collision exceptions (`ctypes instance, not 'NoneType'`) and thread deadlock.

### The Solution
The `ConnectionManager` implements an explicit mutual exclusion lock (`threading.Lock`):
```python
with self._lock:
    if self._ser and self._ser.in_waiting > 0:
        line_bytes = self._ser.readline()
```
All read, write, and probe operations are strictly serialized across the background ingestion thread and host-command callers, completely eliminating overlapped IO collisions.

---

## 2. Reconnection State Machine

The connection lifecycle is modeled as a formal 8-state Finite State Machine:

```text
    +-------------------------------------------------------+
    |                                                       |
    v                                                       |
[DISCONNECTED] ---> [DISCOVERING] ---> [CONNECTING] ---> [HANDSHAKING]
      ^                                                         |
      |                                                         v
  (manual)                                                 [CONNECTED]
      |                                                    /         \
      |                                    (heartbeat ok) /           \ (timeout > 5s)
      |                                                  /             v
   [ERROR] <-------------------------------------- [RECONNECTING] <-- [DEGRADED]
```

### Verification Scenarios Tested
1. **Cable Disconnect / Physical Port Loss:**
   - When port is abruptly unplugged, Win32 raises `SerialException`.
   - The reader catches the exception, updates `connection_errors`, releases port handle, and transitions to `RECONNECTING`.
   - Watchdog thread polls for device reappearance every 2.0 seconds.
2. **Device Re-Enumeration (Bootloader to Xous):**
   - When board boots from Bootloader (`COM10`) into Xous (`COM9`), port `COM10` closes.
   - The manager detects port loss, triggers discovery, identifies `COM9` (`1D50:6197`), and performs a Xous handshake without requiring a backend restart.
3. **WebSocket Client Automatic Recovery:**
   - React hook `useTelemetryWebSocket` implements automatic reconnection backoff (2.5 s intervals).
   - Upon reconnect, the backend immediately sends `INIT_SNAPSHOT`, synchronizing the UI with past events without data loss.
