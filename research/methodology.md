# Research Methodology & Experimental Protocol

**Framework:** GLITCHGUARD  
**Epistemic Principles:** Strict separation of physical observations vs. software simulations.

---

## 1. Epistemic Classification Tiers

Every finding and event in GLITCHGUARD belongs to one of four strict epistemic tiers:

| Tier | Label | Evidence Source | Overwrite / Spoof Rule |
|---|---|---|---|
| **Tier 1** | `PHYSICAL_SILICON_AUDIT` | Direct serial interrogation of Baochip-1x IFR registers and bootloader on COM10 | Read-only; cannot be altered by software |
| **Tier 2** | `PHYSICAL_HARDWARE_SENSOR` | Live readings from physical glitch detection registers or reset source latches | Must originate from physical hardware MMIO read |
| **Tier 3** | `SOFTWARE_FAULT_SIMULATION` | Controlled synthetic fault injection executed via Python test harness | MUST carry `source: software_simulator` |
| **Tier 4** | `RUNTIME_MICROKERNEL_MONITOR` | Xous software-level heartbeat monitoring and MMU page table attestation | Software observations of process health |

---

## 2. Experimental Procedure

1. **Baseline Verification:** Run 20 normal operating cycles with zero fault injection to verify 0.0% false-positive rate.
2. **Injection Protocol:**
   - Experiment A: Flip bit 0 of payload buffer before SHA-256 computation.
   - Experiment B: Delay heartbeat dispatch beyond the 500 ms deadline.
   - Experiment C: Abort process execution midway through key derivation.
   - Experiment D: Corrupt 4 bytes in a 4096-byte page frame.
   - Experiment E: Dispatch 5 consecutive anomalies within 60 seconds.
3. **Telemetry Capture:** Validate all emitted JSON events against `docs/protocol/event-schema.md`.
4. **Metric Logging:** Record detection latency ($\Delta t = t_{\text{detect}} - t_{\text{inject}}$) using high-precision hardware timestamps.
