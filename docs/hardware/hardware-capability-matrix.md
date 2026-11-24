# Hardware Capability Matrix: Baochip-1x / Dabao

**Evaluation Date:** 2026-11-25  
**Methodology:** Live physical silicon register interrogation, bootloader audit, and Xous microkernel process inspection.  

---

## Verified Capability Status Registry

Status legend:
- `AVAILABLE`: Confirmed accessible and physically verified on the live hardware.
- `UNAVAILABLE`: Known silicon feature, not routed or accessible on this board revision.
- `UNSUPPORTED`: Not present in silicon architecture.
- `NOT_VERIFIED`: Documented in architectural reference but not yet validated on physical hardware.
- `ERROR`: Access attempt failed.

| Hardware Feature | Capability Status | Xous Interface / Driver | Register / CSR Ref | Physical Verification Notes |
|---|---|---|---|---|
| **Hardware Clock Skipping Countermeasure** | **AVAILABLE** | Bootloader / Silicon CSR | Clock control registers | **HARDWARE_VERIFIED** via `skipping check` (`true/false`) |
| **Hardware Attack Attempt Counter** | **AVAILABLE** | Bootloader Security Block | Tamper Audit CSR | **HARDWARE_VERIFIED** via `audit` (`Possible attack attempts: 1`) |
| **Hardware Keystore & Key Storage** | **AVAILABLE** | `keystore` service (PID 3) | Secure Keystore CSR (IRQ 11) | **HARDWARE_VERIFIED** active in Xous process table |
| **Hardware Sv32 MMU Memory Isolation** | **AVAILABLE** | Kernel Page Tables (PID 1) | `satp` Mode 1 (ASID 1-8) | **HARDWARE_VERIFIED** active across all 8 microkernel processes |
| **Hardware Ticktimer** | **AVAILABLE** | `xous-ticktimer` (PID 2) | Ticktimer CSR (IRQ 20) | **HARDWARE_VERIFIED** active in Xous interrupt table |
| **TRNG** | **AVAILABLE** | `trng` service | TRNG CSR `0x4004_0000` | Hardware entropy provider for keystore |
| **Hardware SHA-256 Co-Processor** | **NOT_VERIFIED** | `sha2` / `engine-25519` | Hardware accelerator CSR | Software SHA-256 fallback verified in firmware |
| **Hardware AES Engine** | **NOT_VERIFIED** | `aes` service | AES Engine Base `0x4003_1000` | Reserved for secure enclave storage |
| **Security Mesh / Die Shield** | **NOT_VERIFIED** | Security Supervisor | Mesh Status Register | Silicon die shield present; status query pending RTL check |

> **Mandatory Rule:** No item in this matrix may be upgraded to `AVAILABLE` without a verified physical hardware test record. Emulation or software simulation does not qualify.
