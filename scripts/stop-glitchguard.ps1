# GLITCHGUARD Unified Stop Script (Windows PowerShell)
Write-Host "Shutting down GLITCHGUARD services..." -ForegroundColor Yellow

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir
$PidFile = Join-Path $RootDir ".glitchguard_pids.json"

if (Test-Path $PidFile) {
    try {
        $Pids = Get-Content $PidFile | ConvertFrom-Json
        if ($Pids.backend_pid) {
            Write-Host "Stopping Backend (PID: $($Pids.backend_pid))..." -ForegroundColor Gray
            Stop-Process -Id $Pids.backend_pid -Force -ErrorAction SilentlyContinue
        }
        if ($Pids.dashboard_pid) {
            Write-Host "Stopping Dashboard (PID: $($Pids.dashboard_pid))..." -ForegroundColor Gray
            Stop-Process -Id $Pids.dashboard_pid -Force -ErrorAction SilentlyContinue
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    } catch {
        Write-Host "Error parsing PID file. Falling back to port-based cleanup..." -ForegroundColor Red
    }
}

# Fallback: Kill processes on port 8000 and 5173
Get-NetTCPConnection -LocalPort 8000, 5173 -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.OwningProcess -gt 0) {
        Write-Host "Killing process on port $($_.LocalPort) (PID: $($_.OwningProcess))..." -ForegroundColor Gray
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "GLITCHGUARD services stopped successfully." -ForegroundColor Green
