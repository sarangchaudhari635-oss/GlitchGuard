# GLITCHGUARD Unified Start Script (Windows PowerShell)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "       GLITCHGUARD: Open-Silicon Security Framework       " -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $RootDir "host-tools"
$DashboardDir = Join-Path $RootDir "dashboard"

# 1. Hardware Discovery Check
Write-Host "[1/3] Interrogating physical serial interfaces..." -ForegroundColor Yellow
$DiscoveryOutput = python "$BackendDir\serial_comms\device_discovery.py"
Write-Host $DiscoveryOutput -ForegroundColor Gray

# 2. Start FastAPI Telemetry Backend
Write-Host "[2/3] Starting FastAPI Telemetry Backend (Port 8000)..." -ForegroundColor Yellow
$BackendJob = Start-Process -FilePath "python" -ArgumentList "-m uvicorn backend.main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $BackendDir -PassThru -WindowStyle Hidden
Write-Host "FastAPI Backend started with PID: $($BackendJob.Id)" -ForegroundColor Green

# 3. Production dashboard served from backend — no separate Vite dev server needed
#    Optionally start Vite dev server for active frontend development:
#    npm run dev -- --host 127.0.0.1 (from dashboard/ directory)
Write-Host "[3/3] Production dashboard served by FastAPI backend at port 8000." -ForegroundColor Green
Write-Host "      (Run 'npm run dev' in dashboard/ for hot-reload dev mode on :5173)" -ForegroundColor Gray

# Save PIDs for stop script
$PidFile = Join-Path $RootDir ".glitchguard_pids.json"
@{
    backend_pid = $BackendJob.Id
    dashboard_pid = $null
    started_at = (Get-Date).ToString("o")
} | ConvertTo-Json | Set-Content -Path $PidFile

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "GLITCHGUARD is running!" -ForegroundColor Green
Write-Host "  API Backend:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Live Dashboard: http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  Swagger Docs:   http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "  API Events:     http://127.0.0.1:8000/api/events" -ForegroundColor White
Write-Host "To terminate, execute: .\scripts\stop-glitchguard.ps1" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
