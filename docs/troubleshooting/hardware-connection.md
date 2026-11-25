# GLITCHGUARD Troubleshooting: Hardware & Serial Connection

This document provides diagnostic steps for physical connectivity issues with the CrossBar Dabao board.

---

## 1. Issue: Device Not Detected (`scan_ports` returns 0 devices)

### Symptoms
- `device_discovery.py` outputs `No physical Dabao hardware found`.
- Dashboard shows `SIMULATION MODE`.

### Root Causes & Solutions
1. **USB Cable Type:**
   - Some USB-C cables are charge-only. Use a verified USB-IF certified data cable.
2. **Device in Suspended or Low-Power Mode:**
   - Press the hardware reset or wake button on the Dabao board.
3. **USB Device Permissions (Windows):**
   - Check Windows Device Manager under `Ports (COM & LPT)`. Ensure `USB Serial Device (COM10)` or `(COM9)` appears without a yellow exclamation mark.
4. **USB Driver Issue (Linux / WSL2):**
   - Ensure the user belongs to the `dialout` group:
     ```bash
     sudo usermod -a -G dialout $USER
     ```
   - On WSL2, attach the USB device via `usbipd`:
     ```powershell
     usbipd bind --busid <busid>
     usbipd attach --wsl --busid <busid>
     ```

---

## 2. Issue: `PermissionError: [Errno 13] Access is denied`

### Symptoms
- Exception when `ConnectionManager` attempts to open `COM10` or `COM9`.

### Root Causes & Solutions
1. **Port Contention from Another Terminal:**
   - A PuTTY, Tera Term, minicom, or previous python process may hold the COM port open.
   - Close all serial terminal sessions.
   - Run `Get-Process | Where-Object { $_.ProcessName -match "python|putty" }` to terminate stale processes.
2. **Standard Sandbox Mode:**
   - In sandboxed developer environments, direct access to physical hardware COM ports requires elevated host execution. Ensure `BypassSandbox: true` is granted for serial communication scripts.

---

## 3. Issue: Port Disappears during Boot (`COM10` $\to$ `COM9`)

### Explanation
When the Dabao board transitions from the Bootloader to the Xous operating system (via `boot` command), the USB controller re-enumerates:
- Bootloader PID: `0x6196` (e.g. `COM10`)
- Xous PID: `0x6197` (e.g. `COM9`)

`ConnectionManager` automatically detects this transition and re-attaches to the new port without manual user intervention.
