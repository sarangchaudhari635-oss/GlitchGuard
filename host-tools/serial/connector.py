import logging
from typing import Callable, Optional, List, Dict, Any
import serial
import serial.tools.list_ports

logger = logging.getLogger("glitchguard.serial")

class SerialConnector:
    """
    Handles serial communication with the Dabao / Baochip-1x development board.
    Supports connection-loss handling, frame parsing, and reconnection.
    """

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self._on_message_callback: Optional[Callable[[str], None]] = None

    @staticmethod
    def list_available_ports() -> List[Dict[str, Any]]:
        try:
            ports = list(serial.tools.list_ports.comports())
            return [{"device": p.device, "description": p.description, "hwid": p.hwid} for p in ports]
        except Exception as e:
            logger.error(f"Error enumerating COM ports: {e}")
            return []

    def connect(self) -> bool:
        if not self.port:
            logger.warning("No COM port configured for Dabao board.")
            self.is_connected = False
            return False

        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.is_connected = True
            logger.info(f"Connected to Dabao on {self.port} at {self.baudrate} baud.")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Dabao on {self.port}: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        if self.serial_conn and hasattr(self.serial_conn, "is_open") and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except Exception as e:
                logger.error(f"Error closing serial port: {e}")
        self.is_connected = False

    def read_line(self) -> Optional[str]:
        if not self.is_connected or not self.serial_conn:
            return None
        try:
            line = self.serial_conn.readline()
            if line:
                return line.decode("utf-8", errors="replace").strip()
        except Exception as e:
            logger.error(f"Serial read error on {self.port}: {e}")
            self.disconnect()
        return None

    def write_line(self, data: str) -> bool:
        if not self.is_connected or not self.serial_conn:
            return False
        try:
            payload = (data + "\n").encode("utf-8")
            self.serial_conn.write(payload)
            self.serial_conn.flush()
            return True
        except Exception as e:
            logger.error(f"Serial write error on {self.port}: {e}")
            self.disconnect()
            return False
