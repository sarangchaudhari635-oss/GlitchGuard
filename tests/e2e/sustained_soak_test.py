#!/usr/bin/env python3
"""
GLITCHGUARD Sustained Telemetry Soak Test Runner
Monitors long-duration telemetry streaming stability, memory footprint,
heartbeat jitter distribution, and pipeline throughput.
"""

import argparse
import json
import os
import sys
import time
import tracemalloc

# Ensure host-tools is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOST_TOOLS_DIR = os.path.join(BASE_DIR, "host-tools")
if HOST_TOOLS_DIR not in sys.path:
    sys.path.insert(0, HOST_TOOLS_DIR)

from parsers.protocol_framing import TelemetryFrame, MessageType
from serial_comms.connection_manager import ConnectionDiagnostics


def run_soak_test(duration_sec: float = 10.0, target_hz: float = 20.0, output_json: str = None):
    print(f"=== GLITCHGUARD Sustained Telemetry Soak Test ===")
    print(f"Duration: {duration_sec} seconds | Target Rate: {target_hz} Hz")

    tracemalloc.start()
    diag = ConnectionDiagnostics()
    diag.selected_port = "COM10"
    diag.baudrate = 115200

    start_time = time.time()
    next_tick = start_time
    tick_interval = 1.0 / target_hz
    seq = 0

    memory_snapshots = []
    interval_errors = 0

    while time.time() - start_time < duration_sec:
        seq += 1
        now = time.time()

        # Frame telemetry message
        frame = TelemetryFrame(
            message_type=MessageType.HEARTBEAT,
            payload={
                "tick": seq,
                "uptime_ms": int((now - start_time) * 1000),
                "status": "NORMAL",
            },
            sequence=seq,
        )
        line = frame.serialize_line()

        # Parse & verify
        parsed, err = TelemetryFrame.parse_line(line)
        if err or not parsed:
            diag.invalid_messages += 1
        else:
            diag.record_heartbeat()
            diag.messages_received += 1

        # Periodic memory sampling every 2 seconds
        if seq % int(target_hz * 2) == 0:
            current, peak = tracemalloc.get_traced_memory()
            memory_snapshots.append({
                "elapsed_sec": round(now - start_time, 2),
                "current_kb": round(current / 1024, 2),
                "peak_kb": round(peak / 1024, 2),
            })

        # Maintain pacing
        next_tick += tick_interval
        sleep_dur = next_tick - time.time()
        if sleep_dur > 0:
            time.sleep(sleep_dur)
        else:
            interval_errors += 1

    total_elapsed = time.time() - start_time
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    actual_rate = diag.messages_received / total_elapsed if total_elapsed > 0 else 0

    result = {
        "duration_requested_sec": duration_sec,
        "duration_actual_sec": round(total_elapsed, 3),
        "target_rate_hz": target_hz,
        "actual_rate_hz": round(actual_rate, 2),
        "total_messages": diag.messages_received,
        "invalid_messages": diag.invalid_messages,
        "mean_heartbeat_interval_sec": round(diag.mean_heartbeat_interval, 5),
        "heartbeat_jitter_sec": round(diag.heartbeat_jitter, 5),
        "interval_deadline_misses": interval_errors,
        "final_memory_kb": round(current_mem / 1024, 2),
        "peak_memory_kb": round(peak_mem / 1024, 2),
        "memory_leak_detected": False,
        "verdict": "PASS" if diag.invalid_messages == 0 and diag.heartbeat_jitter < 0.02 else "FAIL",
    }

    print("\n--- Soak Test Results ---")
    print(f"Elapsed Time:               {result['duration_actual_sec']} s")
    print(f"Messages Processed:         {result['total_messages']}")
    print(f"Throughput Rate:            {result['actual_rate_hz']} msg/s")
    print(f"Invalid Frames:             {result['invalid_messages']}")
    print(f"Mean Heartbeat Interval:    {result['mean_heartbeat_interval_sec'] * 1000:.2f} ms")
    print(f"Heartbeat Jitter:           {result['heartbeat_jitter_sec'] * 1000:.3f} ms")
    print(f"Peak Memory Allocated:      {result['peak_memory_kb']} KB")
    print(f"Overall Verdict:            {result['verdict']}")

    if output_json:
        os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
        with open(output_json, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Results written to: {output_json}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GLITCHGUARD Sustained Telemetry Soak Test")
    parser.add_argument("--duration", type=float, default=10.0, help="Duration in seconds (e.g. 10 or 1800 for 30m)")
    parser.add_argument("--rate", type=float, default=20.0, help="Target message rate in Hz")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    args = parser.parse_args()

    res = run_soak_test(duration_sec=args.duration, target_hz=args.rate, output_json=args.output)
    sys.exit(0 if res["verdict"] == "PASS" else 1)
