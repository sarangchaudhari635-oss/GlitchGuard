# Initial Device Inventory: Dabao / Baochip-1x

**Inspection Date:** 2026-11-24  
**Status:** HARDWARE_VERIFIED (Live physical silicon inspection on COM10)  
**Target:** CrossBar Dabao Development Board (Baochip-1x)  

---

## 1. Verified Hardware State

| Parameter | Observed Value | Verification Status |
|---|---|---|
| Board Presence | Connected via USB (VID:PID `1D50:6196`) on **`COM10`** | **HARDWARE_VERIFIED** |
| Board Type | `Dabao` | **HARDWARE_VERIFIED** (via `boardtype` command) |
| Silicon Stepping | `A0` | **HARDWARE_VERIFIED** (via `audit` command) |
| Bootloader Semver | `v0.10.0-61-g5397e1b48` | **HARDWARE_VERIFIED** |
| Silicon Description | `bao2-0` | **HARDWARE_VERIFIED** |
| Device Serializer | `4332af0a-3f263177-494a5f1c-68bbebf6` | **HARDWARE_VERIFIED** |
| Public Serial Number | `NNBT1T` | **HARDWARE_VERIFIED** |
| Device UUID | `0b4d2b1c-198122bd-2cb59a01-3aebf575` | **HARDWARE_VERIFIED** |
| Wafer Lot Tracking ID | `47521066M06T` | **HARDWARE_VERIFIED** (from IFR offset 0x0A0) |
| Developer Mode | `== IN DEVELOPER MODE ==` | **HARDWARE_VERIFIED** |
| Paranoid Mode | `0/0` | **HARDWARE_VERIFIED** |
| Possible Attack Attempts | `1` | **HARDWARE_VERIFIED** |
| Security Requirements | CM7 & debug confirmed fused off; Boot1 receipts OK; anti-rollback OK | **HARDWARE_VERIFIED** |

---

## 2. Partition & Memory Map (From Live Audit)

| Stage | Key Index | Flash Address | Status / Hash |
|---|---|---|---|
| **Boot0** | key 0/0 (bao1) | `0x60000000` | `a0680a73106600c4ece34f9393fc5c8eed4885e844b1b78b58fb3a8a299a885cd...` (Code: `563802e7...`) |
| **Boot1** | key 0/0 (bao1) | `0x60020000` | `a12eb17f37c88e834bb7beef3f5163f232824e8044fcbab3bb37c6ac54d10f78...` (Code: `e42b5aba...`) |
| **Next Stage (App)** | key 3/3 (dev ) | `0x60060000` | Application target partition |

---

## 3. Supported Bootloader Commands

Discovered via live console interrogation:
```
altboot, audit, boot, boardtype, bootwait, echo, idmode, ifr, localecho, lockdown, paranoid, reset, self_destruct, skipping, uf2
```

> [!CAUTION]
> Dangerous commands strictly blocked by GLITCHGUARD safety rules:
> `self_destruct`, `lockdown`, `paranoid`, `blow_fuses`, `zeroize`.
