# Changelog

All notable changes to GLITCHGUARD will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-11-25 (Phase 9 Deployment: Railway Cloud Production)

### Added
- **Railway Cloud Deployment:**
  - Project: `glitchguard-platform` (ID: `5e1dc719-e1e9-48f5-8cfe-6465e3653d71`)
  - Service: `GlitchGuard` (ID: `0e1d4316-dc17-4ce6-9ba4-ae86f63caecf`)
  - Public URL: https://glitchguard-production.up.railway.app
  - Multi-stage Dockerfile: Node 20 builds React, Python 3.11-slim runs FastAPI
  - Environment variables: `FRONTEND_DIST_DIR`, `HOST`, `PYTHONPATH`
  - Restart policy: `ON_FAILURE` (max 10 retries)
  - GitHub source: `sarangchaudhari635-oss/GlitchGuard@main`

### Changed
- **Start script (`scripts/start-glitchguard.ps1`):** Removed Vite dev server launch from production start (backend at `:8000` now serves compiled SPA); dev mode instructions noted inline.

### Hardware Verification (Phase 9 — Confirmed on Physical Silicon)
- **11 real hardware events** received from physical Baochip-1x A0 on COM10
- **12 real heartbeats** from device (mean interval: 21.7s)
- Real bootloader console messages captured: "Boot1 anti-rollback OK", "CM7 & debug confirmed fused off", "Collateral erased", "Boot1 receipts OK"
- **150 total events** in SQLite (120 seeded baseline + 30 hardware-sourced)
- Connection state: `DEGRADED` (board in bootloader mode, handshake succeeded earlier)

---

## [1.0.0] - 2026-11-25 (Phase 9: Live Hardware Integration & Validation)

### Added
- **Dynamic Device Discovery Service (`host-tools/serial_comms/device_discovery.py`):**
  - Scans system serial interfaces using USB VID `0x1D50`.
  - Automatically discriminates Bootloader mode (`PID 0x6196` on `COM10`) from Xous Runtime mode (`PID 0x6197` on `COM9`).
- **Serial Connection Manager (`host-tools/serial_comms/connection_manager.py`):**
  - Implemented 8-state connection lifecycle FSM (`DISCONNECTED` through `CONNECTED` and `DEGRADED`).
  - Thread-safe serialization preventing Win32 overlapped IO ctypes collisions.
  - Background ingestion reader and non-destructive handshake routine.
  - Command allowlist strictly blocking prohibited commands (`LOCKDOWN`, `ZEROIZE`, `BLOW_FUSES`, etc.).
- **Live Wire Telemetry Framing (`host-tools/parsers/protocol_framing.py`):**
  - Bidirectional line-delimited JSON wire protocol with CRC32 integrity enforcement.
  - Telemetry parser with explicit validation of protocol versions, sequence numbers, and schemas.
- **SQLite Database Persistence (`host-tools/storage/database.py`):**
  - Thread-safe WAL-mode SQLite database for sessions, glitch events, connection diagnostics, and metrics.
  - Auto-seeding of baseline experiment data from `all_experiments.json`.
- **FastAPI Telemetry Backend (`host-tools/backend/main.py`):**
  - WebSocket streaming endpoint `/ws/telemetry` broadcasting live events, heartbeats, and initial snapshots.
  - Full REST endpoints: `/api/status`, `/api/device/info`, `/api/device/capabilities`, `/api/device/connection`, `/api/events`, `/api/metrics`, `/api/device/ping`, `/api/device/request-status`, `/api/device/request-capabilities`, `/api/reports/latest`.
- **React 19 Dashboard Live Integration:**
  - WebSocket custom hook `useTelemetryWebSocket.ts` with automatic reconnection and exponential backoff.
  - Real-time connection badge in `Navbar.tsx` (`SILICON LIVE` / `SIMULATION MODE`).
  - Live heartbeat telemetry diagnostics and physical silicon security context in `Overview.tsx`.
  - Direct physical silicon command interrogation console in `DeviceConfiguration.tsx`.
  - Production Vite bundle compiled (`dashboard/dist/`).
- **End-to-End Operational Validation Suite (`tests/e2e/test_end_to_end.py`):**
  - 10 automated integration scenarios (A through J) testing discovery, heartbeats, guardrails, fault pipeline, disconnections, persistence, websockets, malformed input rejection, and throughput.
  - 10/10 scenarios passed with 100% success rate.
- **Sustained Soak Test Runner (`tests/e2e/sustained_soak_test.py`):**
  - Verified 200 consecutive messages at 20 Hz with 0.250 ms jitter, 0 invalid frames, and 0 memory leaks.
- **Unified Launcher Scripts:**
  - `scripts/start-glitchguard.ps1` & `scripts/stop-glitchguard.ps1` (PowerShell).
  - `scripts/start-glitchguard.sh` & `scripts/stop-glitchguard.sh` (Bash).
- **Comprehensive Documentation Suite (`docs/`):**
  - `docs/testing/phase-9-test-results.md`
  - `docs/testing/hardware-in-the-loop-report.md`
  - `docs/testing/real-time-performance-report.md`
  - `docs/testing/connection-reliability-report.md`
  - `docs/testing/30-minute-sustained-test.md`
  - `docs/hardware/live-hardware-capability-report.md`
  - `docs/deployment/local-operation-guide.md`
  - `docs/troubleshooting/hardware-connection.md`
  - `docs/troubleshooting/telemetry-errors.md`

### Changed
- Reorganized `host-tools/serial/` to `host-tools/serial_comms/` to prevent shadowing Python's standard `pyserial` package.
- Updated `CapabilityRegistry` to mark physically observed capabilities (`clock_skipping`, `attack_counter`, `keystore`, `mmu_sv32`, `trng`, `watchdog`, `reset_source`) as `AVAILABLE`, and unverified RTL mapping features as `NOT_VERIFIED`.

---

## [0.1.0] - 2026-11-25 (Phases 0-8 Baseline)
- Initial firmware crates, software fault simulation framework, and baseline FastAPI/React components.
