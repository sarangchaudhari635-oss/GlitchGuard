# Changelog

All notable changes to GLITCHGUARD will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).  
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added — 2026-11-24 (Session 1 — Repository Bootstrap)

#### Repository Infrastructure
- Initial repository structure (36 directories)
- `README.md` with project overview and architecture diagram
- `CONTRIBUTING.md` with branch strategy and code standards
- `SECURITY.md` with responsible disclosure policy
- `LICENSE` (MIT)
- `.gitignore` for Rust, Python, Node, and embedded artifacts
- `Cargo.toml` workspace manifest
- `pyproject.toml` for host-tools

#### Documentation
- `docs/hardware/initial-device-inventory.md` — hardware inspection template
- `docs/hardware/hardware-capability-matrix.md` — capability status registry
- `docs/protocol/event-schema.md` — structured event JSON schema v1
- `docs/architecture/system-architecture.md` — full system design
- `research/threat-model.md` — threat model and attack surface

#### Firmware Scaffolds (Rust/Xous)
- `firmware/glitchguard-monitor/` — main monitoring service scaffold
- `firmware/hardware-observer/` — hardware sensor interface scaffold
- `firmware/event-engine/` — event processing scaffold
- `firmware/crypto-verification/` — cryptographic verification scaffold
- `firmware/recovery-engine/` — defensive FSM scaffold
- `firmware/common/` — shared types and event schema

#### Host Tools (Python)
- `host-tools/backend/main.py` — FastAPI server scaffold
- `host-tools/serial/connector.py` — serial communication layer
- `host-tools/parsers/event_parser.py` — event schema parser

#### Experiments
- `experiments/software-faults/simulator.py` — Python fault simulator framework

#### Project Tracking
- `PROJECT-STATUS.md` — phase and task tracking
- `CHANGELOG.md` — this file
- `docs/DEVELOPMENT-LOG.md` — development decision log

---

## Notes

- **Hardware verification status:** No hardware operations performed this session. Board not currently connected.
- **Flashing:** No firmware has been flashed. All firmware files are scaffold-only.
- **Simulations:** No simulations have been run yet.
