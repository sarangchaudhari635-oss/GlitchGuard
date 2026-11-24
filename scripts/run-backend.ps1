Write-Host "=== Launching GLITCHGUARD FastAPI Telemetry Backend ===" -ForegroundColor Cyan
Write-Host "Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
cd host-tools
python backend/main.py
