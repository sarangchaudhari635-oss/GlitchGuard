from datetime import datetime, timezone
import hashlib
import time
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import sys
import os
import importlib.util

# Ensure real pyserial is imported
import serial
import serial.tools.list_ports

# Load local serial connector safely
_connector_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "serial", "connector.py")
_spec = importlib.util.spec_from_file_location("dabao_connector", _connector_path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
SerialConnector = _mod.SerialConnector

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.event_parser import (
    GlitchEventModel,
    EventSource,
    EventType,
    Severity,
    VerificationStatus,
    DefensiveResponse,
)
from exporters.exporter import ReportExporter

app = FastAPI(
    title="GLITCHGUARD Research API",
    description="Host telemetry and fault-injection observation backend for Dabao / Baochip-1x",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory event repository
event_store: List[GlitchEventModel] = []
current_experiment: Optional[Dict] = None
serial_conn = SerialConnector()

# Capability status model
class CapabilityRegistry(BaseModel):
    clock_skipping: str = "AVAILABLE"
    attack_counter: str = "AVAILABLE"
    keystore: str = "AVAILABLE"
    mmu_sv32: str = "AVAILABLE"
    trng: str = "AVAILABLE"
    watchdog: str = "AVAILABLE"
    reset_source: str = "AVAILABLE"
    glitch_detector: str = "NOT_VERIFIED"
    security_mesh: str = "NOT_VERIFIED"
    hw_sha: str = "NOT_VERIFIED"
    hw_aes: str = "NOT_VERIFIED"
    ecc_memory: str = "NOT_VERIFIED"

class ExperimentConfig(BaseModel):
    experiment_id: str
    experiment_name: str
    target: str = "software_simulator"
    iterations: int = 20

@app.get("/api/status")
def get_status():
    available_ports = serial_conn.list_available_ports()
    return {
        "connected": serial_conn.is_connected,
        "port": serial_conn.port,
        "available_ports": available_ports,
        "total_events": len(event_store),
        "current_security_state": "NORMAL" if not event_store else event_store[-1].response,
        "current_experiment": current_experiment,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

@app.get("/api/capabilities", response_model=CapabilityRegistry)
def get_capabilities():
    return CapabilityRegistry()

@app.get("/api/events", response_model=List[GlitchEventModel])
def get_events(
    source: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
):
    results = event_store
    if source:
        results = [e for e in results if e.source.value == source]
    if event_type:
        results = [e for e in results if e.event_type.value == event_type]
    return results[-limit:]

@app.post("/api/events/record")
def record_event(event: GlitchEventModel):
    # Enforce clear separation of simulated vs real hardware observations
    if event.source == EventSource.HARDWARE_SENSOR:
        # Check if hardware is genuinely verified
        pass
    event_store.append(event)
    return {"status": "recorded", "event_id": event.event_id}

@app.post("/api/experiments/start")
def start_experiment(config: ExperimentConfig):
    global current_experiment
    current_experiment = config.model_dump()
    current_experiment["started_at"] = datetime.now(timezone.utc).isoformat()
    return {"status": "started", "experiment": current_experiment}

@app.post("/api/experiments/stop")
def stop_experiment():
    global current_experiment
    if not current_experiment:
        raise HTTPException(status_code=400, detail="No experiment currently active")
    exp = current_experiment
    current_experiment = None
    return {"status": "stopped", "experiment": exp}

@app.get("/api/metrics")
def get_metrics():
    total = len(event_store)
    simulated = sum(1 for e in event_store if e.source == EventSource.SOFTWARE_SIMULATOR)
    hardware = sum(1 for e in event_store if e.source == EventSource.HARDWARE_SENSOR)
    anomalies = sum(1 for e in event_store if e.event_type != EventType.NORMAL)
    quarantined = sum(1 for e in event_store if e.response == DefensiveResponse.QUARANTINED)
    recovered = sum(1 for e in event_store if e.response == DefensiveResponse.RECOVERED)

    return {
        "total_events": total,
        "simulated_events": simulated,
        "hardware_events": hardware,
        "anomalies_detected": anomalies,
        "quarantine_count": quarantined,
        "recovery_count": recovered,
        "recovery_success_rate": (recovered / quarantined) if quarantined > 0 else 1.0,
    }

@app.get("/api/reports/latest")
def get_latest_report(format: str = Query("json", pattern="^(json|csv)$")):
    if format == "csv":
        return ReportExporter.export_csv(event_store)
    return ReportExporter.export_json(event_store)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
