#!/usr/bin/env python3
"""
GLITCHGUARD Serial Connection Manager
Manages real-time bidirectional communication with CrossBar Dabao / Baochip-1x.
Maintains connection lifecycle, background ingestion thread, heartbeat health,
handshake negotiation, and dispatch to backend/WebSocket listeners.
"""

import json
import logging
import queue
import re
import threading
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import serial

try:
    from .device_discovery import (
        DabaoDeviceDescriptor,
        DabaoInterfaceMode,
        DeviceDiscovery,
    )
except ImportError:
    from serial_comms.device_discovery import (
        DabaoDeviceDescriptor,
        DabaoInterfaceMode,
        DeviceDiscovery,
    )

logger = logging.getLogger("glitchguard.connection")


class ConnectionState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    DISCOVERING = "DISCOVERING"
    CONNECTING = "CONNECTING"
    HANDSHAKING = "HANDSHAKING"
    CONNECTED = "CONNECTED"
    DEGRADED = "DEGRADED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"


class DeviceHandshakeInfo:
    def __init__(self):
        self.device_type: str = "CrossBar Dabao"
        self.silicon_id: str = "Baochip-1x A0"
        self.bootloader_ver: Optional[str] = None
        self.firmware_ver: Optional[str] = None
        self.monitor_ver: str = "GLITCHGUARD v1.0.0"
        self.public_serial: Optional[str] = None
        self.mode: DabaoInterfaceMode = DabaoInterfaceMode.UNKNOWN
        self.clock_skipping_active: Optional[bool] = None
        self.attack_counter: int = 0
        self.handshake_time_utc: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_type": self.device_type,
            "silicon_id": self.silicon_id,
            "bootloader_ver": self.bootloader_ver,
            "firmware_ver": self.firmware_ver,
            "monitor_ver": self.monitor_ver,
            "public_serial": self.public_serial,
            "mode": self.mode.value,
            "clock_skipping_active": self.clock_skipping_active,
            "attack_counter": self.attack_counter,
            "handshake_time_utc": self.handshake_time_utc,
        }


class ConnectionDiagnostics:
    def __init__(self):
        self.selected_port: Optional[str] = None
        self.baudrate: int = 115200
        self.messages_received: int = 0
        self.invalid_messages: int = 0
        self.heartbeats_received: int = 0
        self.last_heartbeat_timestamp: Optional[float] = None
        self.heartbeat_intervals: List[float] = []
        self.reconnect_count: int = 0
        self.connection_errors: int = 0
        self.last_error_message: Optional[str] = None

    def record_heartbeat(self):
        now = time.time()
        if self.last_heartbeat_timestamp:
            delta = now - self.last_heartbeat_timestamp
            self.heartbeat_intervals.append(delta)
            if len(self.heartbeat_intervals) > 50:
                self.heartbeat_intervals.pop(0)
        self.last_heartbeat_timestamp = now
        self.heartbeats_received += 1

    @property
    def mean_heartbeat_interval(self) -> float:
        if not self.heartbeat_intervals:
            return 0.0
        return sum(self.heartbeat_intervals) / len(self.heartbeat_intervals)

    @property
    def heartbeat_jitter(self) -> float:
        if len(self.heartbeat_intervals) < 2:
            return 0.0
        mean = self.mean_heartbeat_interval
        variance = sum((x - mean) ** 2 for x in self.heartbeat_intervals) / len(self.heartbeat_intervals)
        return variance ** 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "selected_port": self.selected_port,
            "baudrate": self.baudrate,
            "messages_received": self.messages_received,
            "invalid_messages": self.invalid_messages,
            "heartbeats_received": self.heartbeats_received,
            "last_heartbeat_ago_sec": (
                round(time.time() - self.last_heartbeat_timestamp, 2)
                if self.last_heartbeat_timestamp
                else None
            ),
            "mean_heartbeat_interval_sec": round(self.mean_heartbeat_interval, 3),
            "heartbeat_jitter_sec": round(self.heartbeat_jitter, 4),
            "reconnect_count": self.reconnect_count,
            "connection_errors": self.connection_errors,
            "last_error": self.last_error_message,
        }


class ConnectionManager:
    """
    Authoritative physical serial connection manager for GLITCHGUARD.
    Coordinates device discovery, background ingestion, handshaking,
    and structured command execution.
    """

    def __init__(self, manual_port: Optional[str] = None, baudrate: int = 115200):
        self.manual_port = manual_port
        self.baudrate = baudrate
        self.state: ConnectionState = ConnectionState.DISCONNECTED
        self.device_info: DeviceHandshakeInfo = DeviceHandshakeInfo()
        self.diagnostics: ConnectionDiagnostics = ConnectionDiagnostics()
        self.diagnostics.baudrate = baudrate

        self._ser: Optional[serial.Serial] = None
        self._rx_thread: Optional[threading.Thread] = None
        self._watchdog_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # Listeners for received events / telemetry
        self._telemetry_listeners: List[Callable[[Dict[str, Any]], None]] = []

    def register_telemetry_listener(self, callback: Callable[[Dict[str, Any]], None]):
        """Registers a listener function to receive decoded telemetry objects."""
        if callback not in self._telemetry_listeners:
            self._telemetry_listeners.append(callback)

    def _notify_listeners(self, message: Dict[str, Any]):
        for listener in self._telemetry_listeners:
            try:
                listener(message)
            except Exception as e:
                logger.error(f"Error in telemetry listener callback: {e}")

    def start(self):
        """Starts the connection manager background loop and auto-discovery."""
        self._stop_event.clear()
        if not self._watchdog_thread or not self._watchdog_thread.is_alive():
            self._watchdog_thread = threading.Thread(
                target=self._connection_watchdog_loop,
                daemon=True,
                name="GlitchGuard-Watchdog",
            )
            self._watchdog_thread.start()
        logger.info("ConnectionManager background watchdog started.")

    def stop(self):
        """Stops all threads and disconnects serial port."""
        self._stop_event.set()
        self.disconnect()
        logger.info("ConnectionManager stopped.")

    def disconnect(self):
        """Safely closes serial port and updates connection state."""
        with self._lock:
            if self._ser and hasattr(self._ser, "is_open") and self._ser.is_open:
                try:
                    self._ser.close()
                except Exception as e:
                    logger.error(f"Error closing port: {e}")
            self._ser = None
            self.state = ConnectionState.DISCONNECTED
        logger.info("Serial connection closed.")

    def _connection_watchdog_loop(self):
        """Periodically checks connection health and attempts discovery/reconnection."""
        while not self._stop_event.is_set():
            try:
                if self.state in [ConnectionState.DISCONNECTED, ConnectionState.RECONNECTING, ConnectionState.ERROR]:
                    self._attempt_connection()
                elif self.state == ConnectionState.CONNECTED:
                    # Check for stale heartbeats (> 5.0 seconds since last activity)
                    if (
                        self.diagnostics.last_heartbeat_timestamp
                        and time.time() - self.diagnostics.last_heartbeat_timestamp > 5.0
                    ):
                        logger.warning("Heartbeat deadline exceeded. Transitioning to DEGRADED.")
                        self.state = ConnectionState.DEGRADED
            except Exception as e:
                logger.error(f"Exception in watchdog loop: {e}")
                self.diagnostics.connection_errors += 1
                self.diagnostics.last_error_message = str(e)
                self.state = ConnectionState.ERROR

            time.sleep(2.0)

    def _attempt_connection(self):
        """Discovers Dabao device and performs non-destructive handshake."""
        self.state = ConnectionState.DISCOVERING
        dev = DeviceDiscovery.get_preferred_device(self.manual_port)
        if not dev:
            self.state = ConnectionState.DISCONNECTED
            return

        self.state = ConnectionState.CONNECTING
        self.diagnostics.selected_port = dev.port
        try:
            logger.info(f"Opening physical Dabao port {dev.port} at {self.baudrate} baud...")
            ser = serial.Serial(dev.port, self.baudrate, timeout=1.0)
            self._ser = ser
        except Exception as e:
            logger.error(f"Failed to open port {dev.port}: {e}")
            self.diagnostics.connection_errors += 1
            self.diagnostics.last_error_message = str(e)
            self.diagnostics.reconnect_count += 1
            self.state = ConnectionState.RECONNECTING
            return

        # Perform Handshake
        self.state = ConnectionState.HANDSHAKING
        success = self._perform_handshake(dev)
        if success:
            self.state = ConnectionState.CONNECTED
            # Start background reader
            self._rx_thread = threading.Thread(
                target=self._reader_loop,
                daemon=True,
                name="GlitchGuard-SerialReader",
            )
            self._rx_thread.start()
            logger.info(f"Physical Dabao connected and verified on {dev.port}.")
        else:
            logger.warning(f"Handshake failed on {dev.port}. Retrying...")
            self.disconnect()
            self.state = ConnectionState.RECONNECTING

    def _perform_handshake(self, dev: DabaoDeviceDescriptor) -> bool:
        """Executes a non-destructive handshake query appropriate for the active mode."""
        if not self._ser:
            return False

        try:
            self.device_info.mode = dev.mode
            self.device_info.public_serial = dev.serial_number

            # Send probe newline to awaken prompt
            self._ser.write(b"\r\n")
            time.sleep(0.2)
            banner = self._ser.read(1024).decode("utf-8", errors="replace")

            if dev.mode == DabaoInterfaceMode.BOOTLOADER or "Command not recognized" in banner or "audit" in banner:
                self.device_info.mode = DabaoInterfaceMode.BOOTLOADER
                # Query audit
                self._ser.write(b"audit\r\n")
                time.sleep(0.3)
                audit_resp = self._ser.read(2048).decode("utf-8", errors="replace")

                # Parse Semver
                semver_m = re.search(r"Semver is:\s*([^\r\n]+)", audit_resp)
                if semver_m:
                    self.device_info.bootloader_ver = semver_m.group(1).strip()

                # Parse Attack Counter
                attack_m = re.search(r"Possible attack attempts:\s*(\d+)", audit_resp)
                if attack_m:
                    self.device_info.attack_counter = int(attack_m.group(1))

                # Query Clock Skipping
                self._ser.write(b"skipping check\r\n")
                time.sleep(0.2)
                skip_resp = self._ser.read(512).decode("utf-8", errors="replace")
                self.device_info.clock_skipping_active = "true" in skip_resp.lower()

            elif dev.mode == DabaoInterfaceMode.XOUS_RUNTIME or "[console]" in banner:
                self.device_info.mode = DabaoInterfaceMode.XOUS_RUNTIME
                # Query Xous version
                self._ser.write(b"ver xous\r\n")
                time.sleep(0.3)
                ver_resp = self._ser.read(1024).decode("utf-8", errors="replace")
                ver_m = re.search(r"Xous version:\s*([^\r\n]+)", ver_resp)
                if ver_m:
                    self.device_info.firmware_ver = ver_m.group(1).strip()

            self.device_info.handshake_time_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            self.diagnostics.record_heartbeat()
            return True

        except Exception as e:
            logger.error(f"Handshake exception: {e}")
            return False

    def _reader_loop(self):
        """Continuously reads incoming lines from physical Dabao serial port."""
        logger.info("Serial background reader thread running.")
        while not self._stop_event.is_set():
            line = None
            with self._lock:
                if not self._ser or not getattr(self._ser, "is_open", False):
                    break
                try:
                    if self._ser.in_waiting > 0:
                        line_bytes = self._ser.readline()
                        if line_bytes:
                            line = line_bytes.decode("utf-8", errors="replace").strip()
                except Exception as e:
                    logger.error(f"Serial reader exception on {self.diagnostics.selected_port}: {e}")
                    self.diagnostics.connection_errors += 1
                    self.diagnostics.last_error_message = str(e)
                    self.disconnect()
                    self.state = ConnectionState.RECONNECTING
                    break

            if not line:
                time.sleep(0.05)
                continue

            self.diagnostics.messages_received += 1

            # Check if framed JSON protocol message
            if line.startswith("{") and line.endswith("}"):
                try:
                    msg_obj = json.loads(line)
                    if msg_obj.get("message_type") == "HEARTBEAT" or msg_obj.get("event_type") == "NORMAL":
                        self.diagnostics.record_heartbeat()
                        if self.state == ConnectionState.DEGRADED:
                            self.state = ConnectionState.CONNECTED
                    self._notify_listeners(msg_obj)
                except Exception:
                    self.diagnostics.invalid_messages += 1
            else:
                # Raw console or debug message
                raw_event = {
                    "protocol_version": "1.0",
                    "message_type": "CONSOLE_OUTPUT",
                    "timestamp_ns": int(time.time() * 1e9),
                    "source": "hardware_sensor" if self.device_info.mode == DabaoInterfaceMode.BOOTLOADER else "runtime_monitor",
                    "raw_line": line,
                }
                self.diagnostics.record_heartbeat()
                self._notify_listeners(raw_event)

    def send_command(self, cmd_name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sends an allowlisted command to the physical Dabao board and awaits response.
        Strictly rejects dangerous or prohibited commands.
        """
        clean_cmd = cmd_name.strip().upper()

        # Prohibited security violation commands
        PROHIBITED = ["LOCKDOWN", "SELF_DESTRUCT", "PARANOID", "BLOW_FUSES", "ZEROIZE", "ERASE"]
        if clean_cmd in PROHIBITED:
            raise ValueError(f"Command '{cmd_name}' is prohibited by GLITCHGUARD hardware security policy.")

        if not self._ser or not self._ser.is_open:
            return {"status": "error", "message": "Device not connected"}

        with self._lock:
            try:
                if clean_cmd == "PING":
                    self._ser.write(b"echo PONG\r\n")
                    time.sleep(0.1)
                    resp = self._ser.read(256).decode("utf-8", errors="replace")
                    return {"status": "success", "command": "PING", "response": resp.strip()}

                elif clean_cmd == "GET_STATUS":
                    cmd_str = b"audit\r\n" if self.device_info.mode == DabaoInterfaceMode.BOOTLOADER else b"ver xous\r\n"
                    self._ser.write(cmd_str)
                    time.sleep(0.2)
                    resp = self._ser.read(1024).decode("utf-8", errors="replace")
                    return {"status": "success", "command": "GET_STATUS", "response": resp.strip()}

                elif clean_cmd == "GET_CAPABILITIES":
                    cmd_str = b"skipping check\r\n" if self.device_info.mode == DabaoInterfaceMode.BOOTLOADER else b"test proc\r\n"
                    self._ser.write(cmd_str)
                    time.sleep(0.2)
                    resp = self._ser.read(1024).decode("utf-8", errors="replace")
                    return {"status": "success", "command": "GET_CAPABILITIES", "response": resp.strip()}

                else:
                    return {"status": "error", "message": f"Unsupported command '{cmd_name}'"}

            except Exception as e:
                logger.error(f"Error sending command {cmd_name}: {e}")
                return {"status": "error", "message": str(e)}


# Global authoritative instance for the application
global_connection_manager = ConnectionManager()
