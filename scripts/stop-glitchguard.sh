#!/usr/bin/env bash
# GLITCHGUARD Unified Stop Script (Linux/WSL2)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$ROOT_DIR/.glitchguard_pids.json"

echo "Shutting down GLITCHGUARD services..."

if [ -f "$PID_FILE" ]; then
    BACKEND_PID=$(grep -o '"backend_pid": [0-9]*' "$PID_FILE" | awk '{print $2}')
    DASHBOARD_PID=$(grep -o '"dashboard_pid": [0-9]*' "$PID_FILE" | awk '{print $2}')

    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
    fi
    if [ -n "$DASHBOARD_PID" ]; then
        kill "$DASHBOARD_PID" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
fi

# Fallback kill on ports 8000 and 5173
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 5173/tcp 2>/dev/null || true

echo "GLITCHGUARD services stopped successfully."
