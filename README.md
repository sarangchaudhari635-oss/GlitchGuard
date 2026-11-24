# GLITCHGUARD

**Open-Silicon Hardware Attack Detection & Defence Framework**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/rust-stable-orange.svg)](https://www.rust-lang.org/)
[![Platform](https://img.shields.io/badge/platform-Dabao%20%2F%20Baochip--1x-blue.svg)](docs/hardware/)
[![OS](https://img.shields.io/badge/OS-Xous-green.svg)](https://github.com/betrusted-io/xous-core)

---

## Overview

GLITCHGUARD is an open-source hardware security research framework for detecting, investigating and responding to physical fault-injection indicators and runtime execution anomalies on the **Dabao / Baochip-1x** open-silicon development platform running the **Xous** operating system.

The framework combines hardware-level security sensor observation, software runtime integrity monitoring, controlled fault simulation, cryptographic verification, and defensive state-machine recovery into a unified research system.

---

## Research Motivation

Embedded systems are vulnerable to physical attacks that can interfere with processor execution without leaving obvious traces in software logs. Known attack classes include:

| Attack Class | Description |
|---|---|
| Voltage glitching | Momentary power supply disruption to skip instructions |
| Clock glitching | Injecting rogue clock edges to cause pipeline errors |
| EM fault injection | Targeted EM pulses near die to induce bit flips |
| Laser fault injection | Optical beams targeted at flip-flops or memory cells |
| Memory corruption | Physical or electrical attacks on SRAM or flash |
| Execution anomalies | Fault-induced instruction reordering or skipping |

Traditional software security monitoring cannot reliably detect faults that affect the processor itself. GLITCHGUARD investigates how **hardware-level sensors, runtime software monitoring, cryptographic integrity checks, and defensive recovery** can work together on a fully open-source silicon platform.

---

## Core Research Question

> Can an open-source silicon platform detect, classify, record, and respond to physical fault indicators and execution anomalies using a combination of hardware-level monitoring and software-level verification?

---

## Hardware Platform

| Property | Value |
|---|---|
| Board | Dabao Development Board |
| SoC | Baochip-1x |
| CPU | RISC-V (riscv32imac) |
| Operating System | Xous |
| Firmware Language | Rust |

> **Note:** Hardware capability status (AVAILABLE / UNAVAILABLE / NOT_VERIFIED) for each security sensor is recorded in [`docs/hardware/hardware-capability-matrix.md`](docs/hardware/hardware-capability-matrix.md).

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│              React Dashboard (TypeScript)         │  Layer 7
├─────────────────────────────────────────────────┤
│         FastAPI Host Backend (Python)             │  Layer 6
├─────────────────────────────────────────────────┤
│      Serial Telemetry / USB Serial Protocol       │  Layer 5
├─────────────────────────────────────────────────┤
│    GlitchGuard Monitor Service (Xous / Rust)      │  Layer 4
│  ┌───────────────┬──────────────┬─────────────┐  │
│  │ Hardware Obs  │ Event Engine │ Crypto Verif│  │
│  └───────────────┴──────────────┴─────────────┘  │
│  ┌────────────────────────────────────────────┐   │
│  │       Defensive Recovery Engine (FSM)      │   │
│  └────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│          Baochip-1x Hardware / Dabao Board        │  Layer 1
│  Glitch Sensors · TRNG · Crypto Accel · ECC Mem  │
└─────────────────────────────────────────────────┘
```

---

## Repository Structure

```
glitchguard/
├── firmware/                    # Rust/Xous firmware modules
│   ├── glitchguard-monitor/    # Main monitoring service
│   ├── hardware-observer/       # Hardware sensor interface
│   ├── event-engine/            # Structured event processing
│   ├── crypto-verification/     # Cryptographic integrity checks
│   ├── recovery-engine/         # Defensive FSM
│   └── common/                  # Shared types and protocols
├── experiments/                 # Research experiments
│   ├── software-faults/         # Python fault simulator
│   ├── hardware-observations/   # Hardware sensor test records
│   ├── integrity-tests/         # Cryptographic test records
│   ├── recovery-tests/          # FSM recovery test records
│   └── results/                 # Experiment datasets
├── host-tools/                  # Python host-side tooling
│   ├── backend/                 # FastAPI server
│   ├── serial/                  # Serial communication layer
│   ├── parsers/                 # Event schema parsers
│   ├── exporters/               # JSON/CSV report exporters
│   └── tests/                   # Host-tools test suite
├── dashboard/                   # React + TypeScript UI
│   └── src/
│       ├── components/          # Shared UI components
│       ├── pages/               # Dashboard pages
│       ├── services/            # API service layer
│       ├── hooks/               # React hooks
│       └── types/               # TypeScript type definitions
├── research/                    # Research documentation
├── docs/                        # Technical documentation
└── scripts/                     # Build and setup scripts
```

---

## Quick Start

### Prerequisites

| Tool | Required Version |
|---|---|
| Rust (stable) | ≥ 1.75 |
| cargo | matches Rust |
| Python | ≥ 3.11 |
| Node.js | ≥ 20 |
| pnpm | ≥ 8 |
| Git | any recent |

### 1. Clone and Setup

```bash
https://github.com/sarangchaudhari635-oss/GlitchGuard.git
cd GlitchGuard
./scripts/setup.sh
```

### 2. Build Firmware

```bash
./scripts/build.sh
```

> **Note:** Flashing requires physical board access and explicit approval. See [`docs/hardware/firmware-installation.md`](docs/hardware/firmware-installation.md).

### 3. Start Backend

```bash
cd host-tools
pip install -e ".[dev]"
uvicorn backend.main:app --reload
```

### 4. Start Dashboard

```bash
cd dashboard
pnpm install
pnpm dev
```

---

## Project Status

See [`PROJECT-STATUS.md`](PROJECT-STATUS.md) for the current development phase and task tracking.

---

## Safety Notes

> [!CAUTION]
> Never erase OTP memory, security fuses, bootloader, or calibration data. These are permanent and device-identity-critical.

> [!WARNING]
> Firmware flashing requires explicit user approval. GLITCHGUARD autonomous development never flashes the device without confirmation.

> [!IMPORTANT]
> Software fault simulations are clearly labeled `SIMULATED EVENT` throughout. No simulation result is ever presented as a physical hardware measurement.

---

## Team

| Role | Responsibilities |
|---|---|
| Hardware Security Researcher | RTL analysis, sensor mapping, hardware experiments |
| Firmware Engineer | Xous integration, Rust services, cryptography |
| Platform & Testing Engineer | Python simulator, backend, dashboard, testing |

---

## License

MIT License — see [LICENSE](LICENSE).

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

See [SECURITY.md](SECURITY.md).
