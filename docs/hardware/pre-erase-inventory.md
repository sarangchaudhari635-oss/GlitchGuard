# Pre-Erase Inventory & Classification Plan

**Target:** CrossBar Dabao Development Board  
**Objective:** Clean baseline preparation without bricking or erasing immutable silicon assets.

---

## 1. Component Classification Matrix

| Component | Classification | Required Action | Rationale |
|---|---|---|---|
| Previous Project App | Transient Software | **REMOVE** | Clean baseline for GLITCHGUARD |
| Previous User Data | Transient State | **REMOVE** | Prevent cross-project data leakage |
| Previous Config | User Space | **RESET** | Return to default Xous configuration |
| Xous Operating System | System Firmware | **REINSTALL CLEAN** | Ensure matching known-good system services |
| Bootloader | Immutable Baseline | **PRESERVE** | Replacement risks bricking; keep unless required |
| OTP Memory | Permanent Silicon | **NEVER TOUCH** | Irreversible write-once memory |
| Security Fuses | Permanent Silicon | **NEVER TOUCH** | Irreversible hardware lockouts |
| Device Identity / Keys | Factory Calibrated | **PRESERVE** | Cryptographic root of trust |
| Analog Calibration | Factory Calibrated | **PRESERVE** | Clock/voltage reference parameters |

---

## 2. Safe Erasure and Installation Sequence

1. **Inspection:** Capture serial console output of existing firmware before wiping.
2. **Backup:** Extract any readable configuration logs via serial interface.
3. **Firmware Verification:** Prepare official Xous console build artifact.
4. **User Approval Checkpoint:** Submit binary checksum and exact flashing commands for explicit user approval.
5. **Targeted Flash:** Write exclusively to application / OS flash partition. Do not touch bootloader or OTP sectors.
6. **Post-Flash Verification:** Read serial boot banner to verify clean Xous environment.
