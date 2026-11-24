# System Architecture — GLITCHGUARD

**Version:** 1.0  
**Status:** Draft — pending hardware verification  

---

## Overview

GLITCHGUARD is a layered hardware security research platform. Each layer has a clearly defined interface and responsibility. No layer directly accesses the layer below its documented interface.

---

## Layer Stack

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 7: React Dashboard (TypeScript + Vite + Tailwind)          │
│  · 7 pages: Overview, Hardware Monitor, Attack Simulation,        │
│    Event Explorer, Analytics, Reports, Configuration             │
├──────────────────────────────────────────────────────────────────┤
│  Layer 6: FastAPI Host Backend (Python 3.11+)                     │
│  · REST API · Serial parser · Event store · Report exporter      │
├──────────────────────────────────────────────────────────────────┤
│  Layer 5: USB Serial Transport                                    │
│  · Length-delimited JSON frames · 115200 baud (default)          │
│  · Connection-loss handling · Reconnection with backoff           │
├──────────────────────────────────────────────────────────────────┤
│  Layer 4: GlitchGuard Monitor (Xous server, Rust)                 │
│  · Main monitoring service process                               │
│  · Receives hardware events, software anomalies, heartbeats      │
│  · Classifies events · Drives defensive FSM                      │
│  · Emits telemetry to serial                                      │
├───────────┬─────────────────┬────────────────────────────────────┤
│  Hardware │  Event Engine   │  Crypto Verification               │
│  Observer │  (event-engine) │  (crypto-verification)             │
│  ─────── │  ─────────────  │  ────────────────────              │
│  Reads hw │  Structures,    │  SHA-256/HMAC integrity            │
│  sensor   │  timestamps,    │  TRNG challenge generation         │
│  registers│  deduplicates   │  Hardware crypto if available       │
│  Capability│  events        │  Software fallback if not          │
│  registry │                 │                                    │
├───────────┴─────────────────┴────────────────────────────────────┤
│  Recovery Engine (Finite State Machine)                           │
│  · NORMAL → SUSPECTED_ANOMALY → QUARANTINED → VERIFYING          │
│  · VERIFYING → RECOVERED → NORMAL  (success)                     │
│  · VERIFYING → LOCKDOWN            (failure)                     │
│  · State transitions logged with timestamp and evidence ref      │
├──────────────────────────────────────────────────────────────────┤
│  Layer 2: Xous IPC and Process Isolation                          │
│  · Xous message-passing between services                         │
│  · Memory isolation between processes                            │
│  · Capability-based access to hardware                           │
├──────────────────────────────────────────────────────────────────┤
│  Layer 1: Baochip-1x Hardware / Dabao Board                       │
│  · RISC-V riscv32imac core                                       │
│  · Hardware glitch detection (capability: NOT_VERIFIED)          │
│  · Security mesh (capability: NOT_VERIFIED)                      │
│  · TRNG (capability: NOT_VERIFIED)                               │
│  · Hardware AES/SHA accelerator (capability: NOT_VERIFIED)       │
│  · ECC-protected memory (capability: NOT_VERIFIED)               │
│  · Watchdog timer (capability: NOT_VERIFIED)                     │
│  · Reset source register (capability: NOT_VERIFIED)              │
└──────────────────────────────────────────────────────────────────┘

Parallel Input:
┌────────────────────────────────┐
│  Python Fault Simulator        │
│  (experiments/software-faults) │
│  · Generates SIMULATED events  │
│  · Source: software_simulator  │
│  · Connected to backend API    │
└────────────────────────────────┘
```

---

## Module Responsibilities

### glitchguard-monitor (Xous Server)

**Location:** `firmware/glitchguard-monitor/`  
**Owner:** Firmware Engineer  

Responsibilities:
- Initialises all subsystems at startup
- Registers with Xous server infrastructure
- Runs the main event loop
- Routes events to the event engine
- Drives the recovery FSM on anomaly events
- Emits serialised JSON telemetry to UART

### hardware-observer

**Location:** `firmware/hardware-observer/`  
**Owner:** Hardware Security Researcher  

Responsibilities:
- Abstracts access to all hardware security sensors
- Maintains the capability registry (AVAILABLE / UNAVAILABLE / UNSUPPORTED / NOT_VERIFIED / ERROR)
- Reads documented hardware registers using verified addresses only
- Never substitutes simulated values for real hardware readings
- Reports SENSOR_UNAVAILABLE events when a sensor cannot be read

### event-engine

**Location:** `firmware/event-engine/`  
**Owner:** Firmware Engineer  

Responsibilities:
- Defines the GlitchEvent struct (matches the JSON schema)
- Assigns monotonic timestamps
- Assigns unique event IDs
- Maintains a ring-buffer event history
- Provides serialisation to the JSON wire format

### crypto-verification

**Location:** `firmware/crypto-verification/`  
**Owner:** Firmware Engineer  

Responsibilities:
- Generates TRNG-seeded random challenges
- Computes SHA-256 (or hardware equivalent) over test payloads
- Performs challenge-response integrity verification
- Reports whether hardware acceleration was used
- Never exposes keys or seeds in logs

### recovery-engine

**Location:** `firmware/recovery-engine/`  
**Owner:** Firmware Engineer  

Responsibilities:
- Implements the security FSM
- Manages state transitions with evidence references
- Quarantines affected application processes
- Triggers integrity verification before recovery
- Enters LOCKDOWN on repeated failures

### host-tools/backend

**Location:** `host-tools/backend/`  
**Owner:** Platform & Testing Engineer  

Responsibilities:
- Receives JSON events from serial
- Validates events against the Pydantic schema
- Stores events in an in-process event store (SQLite for persistence)
- Exposes REST API for the dashboard
- Never presents host-generated data as hardware-sourced

### experiments/software-faults

**Location:** `experiments/software-faults/`  
**Owner:** Platform & Testing Engineer  

Responsibilities:
- Generates reproducible synthetic fault scenarios
- Tags all events with `source: software_simulator`
- Never claims to be a real physical fault injection tool
- Sends events directly to the host backend API

### dashboard

**Location:** `dashboard/`  
**Owner:** Platform & Testing Engineer  

Responsibilities:
- Displays real-time telemetry and event history
- Clearly labels simulated events with `SIMULATED EVENT` badge
- Provides experiment controls
- Never triggers destructive hardware operations

---

## Inter-Process Communication (Xous)

Xous uses a capability-based message-passing model. All communication between GLITCHGUARD firmware crates passes through Xous IPC rather than shared memory.

```
hardware-observer  ──IPC──►  glitchguard-monitor
crypto-verification ──IPC──►  glitchguard-monitor
                              │
                              ▼
                        event-engine
                              │
                              ▼
                        recovery-engine
                              │
                              ▼
                        UART / Serial
```

> **Note:** Exact IPC message definitions depend on the Xous version installed. These will be verified against `xous-core` before implementation.

---

## Serial Protocol

Events are framed over USB serial (CDC-ACM) as:

```
[4-byte big-endian length][JSON payload bytes][newline]
```

Baud rate: 115200 (default; configurable)  
Encoding: UTF-8  
Maximum event size: 4096 bytes  

---

## Data Flow — Normal Operation

```
Dabao Hardware Sensors
        │
        ▼
hardware-observer (polls sensors on 100ms interval)
        │
        ▼
glitchguard-monitor (event loop)
        │
        ├──► event-engine (timestamp, classify, store)
        │
        ├──► crypto-verification (integrity check on demand)
        │
        └──► recovery-engine (FSM evaluation)
                    │
                    ▼
              UART serialisation
                    │
                    ▼
         host-tools/backend (FastAPI)
                    │
                    ├──► event store (SQLite)
                    │
                    └──► dashboard WebSocket / REST API
```

---

## Data Flow — Software Fault Simulation

```
experiments/software-faults/simulator.py
        │
        │  POST /api/experiments/inject
        ▼
host-tools/backend
        │
        ▼
event store (source: software_simulator)
        │
        ▼
dashboard (displayed with SIMULATED EVENT badge)
```

Simulated events never enter the firmware event pipeline. They are injected directly at the host-backend layer and are always distinguishable from firmware-originated events by their `source` field.
