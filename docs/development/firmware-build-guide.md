# Firmware Build, Flashing & Validation Guide

**Target Board:** CrossBar Dabao Development Platform  
**Target Architecture:** RISC-V `riscv32imac-unknown-none-elf`  

---

## 1. Toolchain Verification

Confirm the bare-metal RISC-V target is installed:

```bash
rustup target list --installed | grep riscv32imac
# Output: riscv32imac-unknown-none-elf
```

---

## 2. Building Firmware Crates

To compile all bare-metal firmware crates for the Baochip-1x:

```bash
cd "c:\Users\Sarang Chaudhari\OneDrive\Desktop\DABAO 2.0\glitchguard"
cargo build --target riscv32imac-unknown-none-elf --release -p glitchguard-common -p hardware-observer -p event-engine -p crypto-verification -p recovery-engine
```

All artifacts will be generated in `target/riscv32imac-unknown-none-elf/release/`.

---

## 3. Non-Destructive Flash Verification Procedure

Before writing any binary to the Dabao board:

1. **Calculate SHA-256 of generated binary:**
   ```powershell
   Get-FileHash target\riscv32imac-unknown-none-elf\release\glitchguard-monitor.bin -Algorithm SHA256
   ```
2. **Verify target partition address:**
   - Target: **`0x60060000`** (Next Stage Application Partition)
   - Do NOT flash to `0x60000000` (Boot0) or `0x60020000` (Boot1).
3. **Connect to COM10 bootloader:**
   ```bash
   python -c "import serial; s=serial.Serial('COM10', 115200); s.write(b'audit\r\n'); print(s.read(2048).decode()); s.close()"
   ```
4. **Request explicit user confirmation before issuing write command.**
