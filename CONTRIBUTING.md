# Contributing to GLITCHGUARD

## Branch Strategy

| Branch | Purpose |
|---|---|
| `main` | Stable, reviewed code only |
| `dev` | Integration branch |
| `firmware/*` | Firmware feature branches |
| `host/*` | Backend and host-tool branches |
| `dashboard/*` | React dashboard branches |
| `docs/*` | Documentation branches |
| `experiment/*` | Research experiment branches |

## Pull Request Requirements

Every PR must:

1. Reference a GitHub issue.
2. Include a description of changes.
3. Pass all CI checks (`cargo check`, `cargo test`, `cargo clippy`, `pytest`, TypeScript build).
4. Have a reviewer assigned.
5. Update `PROJECT-STATUS.md` if a phase task is completed.
6. Update `CHANGELOG.md` under `[Unreleased]`.

## Commit Message Format

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `security`

Scopes: `firmware`, `hardware-observer`, `event-engine`, `crypto`, `recovery`, `backend`, `dashboard`, `simulator`, `docs`

## Hardware Verification Rules

- **Never mark a feature `HARDWARE_VERIFIED` based only on compilation or software simulation.**
- Hardware-verified features must include: board revision, firmware revision, test procedure, and observed output.
- Record all hardware tests in `docs/testing/hardware-test-records.md`.

## Security Rules

- Never commit private keys, credentials, or device identifiers.
- Never mix simulated and hardware event sources in experiment records.
- Always label simulated events with `source: "software_simulator"`.

## Code Standards

### Rust
- Run `cargo fmt` and `cargo clippy` before every commit.
- Document every `unsafe` block with a safety justification comment.
- Never write arbitrary register addresses without an RTL/documentation reference.

### Python
- Run `ruff check` and `mypy` before every commit.
- Validate all incoming serial data against the event schema.
- Handle serial disconnection gracefully.

### TypeScript/React
- Run `tsc --noEmit` and `eslint` before every commit.
- Never display hardware-sourced data without a source label.
- Always show a `SIMULATED EVENT` badge on simulation outputs.
