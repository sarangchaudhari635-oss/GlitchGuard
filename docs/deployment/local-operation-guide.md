# GLITCHGUARD Local Operation & Deployment Guide

This guide describes how to run and operate the complete GLITCHGUARD framework locally on a development host connected to the CrossBar Dabao board.

---

## 1. System Requirements

- **Operating System:** Windows 10/11, Ubuntu 22.04 LTS, or WSL2
- **Python:** Python 3.10+ (tested on Python 3.13)
- **Node.js:** Node.js 18+ (tested on Node.js 20/22)
- **Hardware:** 1x CrossBar Dabao Development Platform (Baochip-1x Stepping A0)
- **Cables:** 1x USB Type-C to Type-A / Type-C data cable

---

## 2. Quick Start (One-Click Launch)

### On Windows PowerShell:
```powershell
cd "c:\Users\Sarang Chaudhari\OneDrive\Desktop\DABAO 2.0\glitchguard"
.\scripts\start-glitchguard.ps1
```

### On Linux / WSL2:
```bash
cd glitchguard
chmod +x scripts/*.sh
./scripts/start-glitchguard.sh
```

### Access Endpoints:
- **Web Security Dashboard:** [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **FastAPI Telemetry Backend:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Live WebSocket Stream:** `ws://127.0.0.1:8000/ws/telemetry`

---

## 3. Manual Component Startup

### Step 1: Discover Physical Hardware
Verify your board is enumerated by running:
```bash
python host-tools/serial_comms/device_discovery.py
```
Expected output:
```text
Scanning for physical Dabao hardware...
Found 1 Dabao device(s):
  <DabaoDevice COM10 [BOOTLOADER] VID:PID=1D50:6196 SN=NNBT1T>
```

### Step 2: Start the FastAPI Backend
```bash
cd host-tools
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Start the React Dashboard
```bash
cd dashboard
npm run dev
```

---

## 4. Running Validation Tests

### Rust Firmware Workspace Tests:
```bash
cd firmware
cargo test --workspace
```

### Host Tools & API Unit Tests:
```bash
pytest host-tools/tests/test_backend.py -v
```

### End-to-End Operational Validation Suite:
```bash
pytest tests/e2e/test_end_to_end.py -v -s
```

### Sustained Telemetry Soak Test:
```bash
python tests/e2e/sustained_soak_test.py --duration 30 --rate 20
```

---

## 5. Shutting Down
To gracefully stop all background services and release serial COM port handles:
```powershell
.\scripts\stop-glitchguard.ps1
```
