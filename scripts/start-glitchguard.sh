#!/usr/bin/env bash
# GLITCHGUARD Unified Start Script (Linux/WSL2)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$ROOT_DIR/host-tools"
DASHBOARD_DIR="$ROOT_DIR/dashboard"

echo "=== GLITCHGUARD: Open-Silicon Security Framework ==="

# 1. Hardware Discovery Check
echo "[1/3] Interrogating physical serial interfaces..."
python3 "$BACKEND_DIR/serial_comms/device_discovery.py" || true

# 2. Start FastAPI Telemetry Backend
echo "[2/3] Starting FastAPI Telemetry Backend (Port 8000)..."
cd "$BACKEND_DIR"
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 > /tmp/glitchguard_backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# 3. Start React Dashboard
echo "[3/3] Starting React Dashboard (Port 5173)..."
cd "$DASHBOARD_DIR"
npm run dev -- --host 127.0.0.1 > /tmp/glitchguard_dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "Dashboard started with PID: $DASHBOARD_PID"

echo "{\"backend_pid\": $BACKEND_PID, \"dashboard_pid\": $DASHBOARD_PID}" > "$ROOT_DIR/.glitchguard_pids.json"

echo "=== GLITCHGUARD is running! ==="
echo "  Backend API:   http://127.0.0.1:8000"
echo "  Documentation: http://127.0.0.1:8000/docs"
echo "  Dashboard:     http://127.0.0.1:5173"
echo "To terminate, execute: ./scripts/stop-glitchguard.sh"
