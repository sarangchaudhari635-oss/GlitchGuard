# Threat Model: GLITCHGUARD

**Scope:** Hardware Fault-Injection Attacks on Embedded Open-Silicon (Baochip-1x / Dabao)

---

## 1. Threat Actors & Capabilities

| Actor Tier | Access Level | Tools & Equipment | Goal |
|---|---|---|---|
| Physical Attacker (Lab) | Direct physical access to PCB / silicon package | Glitch amplifiers, power probes, EM injection coils, pulse generators | Skip security checks, corrupt cryptographic keys, force privilege escalation |
| Proximity Attacker | Physical proximity without decapping | Electromagnetic fault injection (EMFI), power supply modulation | Induce transient execution bitflips |
| Logical / Software Attacker | Unprivileged process on Xous OS | Malicious IPC payloads, memory corruption triggers | Subvert process isolation, exploit unverified state |

---

## 2. Attack Vectors

```
Physical Faults
  ├─ Voltage Glitching (Vcc drop during critical instruction)
  ├─ Clock Glitching (Overdrive pulse shortening cycle)
  ├─ EMFI (Localized electromagnetic pulse at ALU/Registers)
  └─ Thermal / Optical disturbance
        │
        ▼ Induces
Fault Indicators
  ├─ Instruction Skipping (Bypass conditional jump: BEQ -> NOP)
  ├─ Register Bit Corruption (Flip privilege bit or memory pointer)
  ├─ Memory Bus Corruption (Transient read error)
  └─ Watchdog Reset / Hardware Exception
```

---

## 3. Defense-in-Depth Mechanisms

1. **Hardware Layer:**
   - Dedicated glitch sensors to detect rapid dV/dt or clock jitter.
   - TRNG for non-deterministic execution padding.
   - Watchdog timer to trap deadlocks and execution halts.
2. **Operating System Layer (Xous):**
   - Memory Management Unit (MMU) process isolation.
   - Capability-based message passing.
3. **GLITCHGUARD Runtime Monitor:**
   - Real-time heartbeat checking.
   - Cryptographic payload integrity verification.
   - Defensive Finite State Machine (FSM): Quarantine affected processes upon anomalous behavior.
