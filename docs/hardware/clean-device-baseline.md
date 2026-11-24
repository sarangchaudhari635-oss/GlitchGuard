# Clean Device Baseline: CrossBar Dabao / Baochip-1x

**Verification Date:** 2026-11-25  
**Silicon State:** LIVE PHYSICAL SILICON (Epistemic Tier: PHYSICAL_IO_BEHAVIOURAL)  
**Status:** HARDWARE_VERIFIED & OPERATIONAL  

---

## 1. Operating System & Firmware Identity

| Parameter | Observed Value | Physical Verification Method |
|---|---|---|
| **Operating System** | **Xous Microkernel** `v0.10.2-195-g99bbfcc15` | Read via `ver xous` on COM9 (PID 0x6197) |
| **Kernel Build Date** | Thu, 5 Nov 2026 17:16:18 +0000 | `apps-dabao/dabao-console/src/cmds/ver.rs:24` |
| **Bootloader Version** | `v0.10.0-61-g5397e1b48` | Read via `audit` on COM10 (PID 0x6196) |
| **Silicon Stepping** | Baochip-1x Stepping A0 (`bao2-0`) | Physical silicon register interrogation |
| **Public Serial Number** | `NNBT1T` | Xous kernel environment (`PUBLIC_SERIAL`) |
| **Device Serializer** | `4332af0a-3f263177-494a5f1c-68bbebf6` | Bootloader audit receipt |
| **Wafer Lot Tracking ID** | `47521066M06T` | IFR register offset 0x0A0 |
| **Mode** | `== IN DEVELOPER MODE ==` | CM7 & JTAG debug fused off |

---

## 2. Microkernel Process Tree (Live Sv32 MMU Translation)

```
PID  Process Name        State        satp         Mode  ASID  PPN       RAM Usage
---  ------------        -----        ----         ----  ----  ---       ---------
1    kernel              Ready(100)   0x804611ae   Sv32  1     611ae000  136 kB
2    xous-ticktimer      Sleeping     0x808611d8   Sv32  2     611d8000   96 kB
3    keystore            Sleeping     0x80c611d1   Sv32  3     611d1000   92 kB
4    xous-log            Ready(1000)  0x810611ca   Sv32  4     611ca000   80 kB
5    xous-names          Sleeping     0x814611c3   Sv32  5     611c3000   76 kB
6    usb-bao1x           Ready(100)   0x818611bc   Sv32  6     611bc000  132 kB
7    bao1x-hal-service   Sleeping     0x81c611b5   Sv32  7     611b5000  292 kB
8    dabao-console       Running(0)   0x820611a7   Sv32  8     611a7000  136 kB
---  ------------        -----        ----         ----  ----  ---       ---------
TOTAL PHYSICAL RAM MAPPED ACROSS XOUS MICROKERNEL:                 1,040 kB
```

---

## 3. Physical Hardware Security Features Confirmed

1. **Hardware Clock Skipping Jitter Countermeasure:** Confirmed live over bootloader (`skipping check` -> `Clock skipping: true / false`).
2. **Hardware Attack Attempt Counter:** Confirmed live (`Possible attack attempts: 1`).
3. **Hardware Keystore & Security Subsystem:** Active on IRQ 11 (`keystore` process).
4. **Hardware Ticktimer:** Active on IRQ 20 (`xous-ticktimer`).
5. **Hardware Sv32 MMU Isolation:** Confirmed active with individual ASID (1-8) and per-process page tables (`satp`).
