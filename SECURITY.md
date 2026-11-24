# Security Policy

## Responsible Disclosure

GLITCHGUARD is a hardware security **research** framework. We take security seriously.

If you discover a security vulnerability in this codebase:

1. **Do not** open a public GitHub issue.
2. Email the maintainers directly (see repository contacts).
3. Provide a description, reproduction steps, and potential impact.
4. Allow reasonable time for a fix before public disclosure.

## Scope

This policy covers:

- The GLITCHGUARD Rust firmware codebase
- The Python host-tools backend
- The React dashboard
- The event protocol and schema

## Out of Scope

- Vulnerabilities in third-party dependencies (report to upstream)
- Physical attacks against the Dabao board (this is the subject of research, not a vulnerability)
- Intentional fault-injection simulation scenarios (these are documented features)

## Security Design Principles

1. No private keys in logs, telemetry, or source code.
2. No hardcoded credentials anywhere in the codebase.
3. Event records are schema-validated on ingestion.
4. Simulated events are permanently tagged with `source: software_simulator`.
5. Hardware sensor outputs are never substituted with simulated values.
6. Serial communication uses length-delimited framing to prevent injection.
7. Dashboard API is never exposed to the public internet by default.
8. No destructive hardware operations are reachable through ordinary UI controls.
9. OTP memory, security fuses, and calibration data are never modified by software.
10. All `unsafe` Rust blocks are individually documented and reviewed.

## Supported Versions

| Version | Supported |
|---|---|
| `main` branch | ✅ Yes |
| Tagged releases | ✅ Yes |
| Development branches | ⚠️ Best effort |
