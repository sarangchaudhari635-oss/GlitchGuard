#!/usr/bin/env python3
"""
GLITCHGUARD Dynamic Hardware Device Discovery Service
Scans system serial interfaces to identify physical CrossBar Dabao / Baochip-1x hardware.
Distinguishes between Bootloader mode (PID 0x6196) and Xous Runtime mode (PID 0x6197).
"""

import logging
import os
import sys
from enum import Enum
from typing import Dict, List, Optional, Tuple

import serial.tools.list_ports

logger = logging.getLogger("glitchguard.discovery")

# Known USB Vendor & Product IDs for Baochip-1x / Dabao
DABAO_VID = 0x1D50
PID_BOOTLOADER = 0x6196
PID_XOUS_RUNTIME = 0x6197

class DabaoInterfaceMode(str, Enum):
    BOOTLOADER = "BOOTLOADER"
    XOUS_RUNTIME = "XOUS_RUNTIME"
    UNKNOWN = "UNKNOWN"

class DabaoDeviceDescriptor:
    def __init__(
        self,
        port: str,
        description: str,
        hwid: str,
        vid: Optional[int],
        pid: Optional[int],
        serial_number: Optional[str],
        mode: DabaoInterfaceMode,
    ):
        self.port = port
        self.description = description
        self.hwid = hwid
        self.vid = vid
        self.pid = pid
        self.serial_number = serial_number
        self.mode = mode

    def to_dict(self) -> Dict:
        return {
            "port": self.port,
            "description": self.description,
            "hwid": self.hwid,
            "vid": f"0x{self.vid:04X}" if self.vid else None,
            "pid": f"0x{self.pid:04X}" if self.pid else None,
            "serial_number": self.serial_number,
            "mode": self.mode.value,
        }

    def __repr__(self):
        return f"<DabaoDevice {self.port} [{self.mode.value}] VID:PID={self.vid:04X}:{self.pid:04X} SN={self.serial_number}>"


class DeviceDiscovery:
    """
    Scans host serial ports and identifies Dabao hardware dynamically.
    Works across Windows (COMx) and Linux (/dev/ttyUSBx or /dev/ttyACMx).
    """

    @staticmethod
    def scan_ports() -> List[DabaoDeviceDescriptor]:
        """Scans all available COM / tty ports and returns detected Dabao devices."""
        detected: List[DabaoDeviceDescriptor] = []
        try:
            available_ports = list(serial.tools.list_ports.comports())
        except Exception as e:
            logger.error(f"Error enumerating serial ports: {e}")
            return []

        for p in available_ports:
            vid = p.vid
            pid = p.pid
            hwid = p.hwid or ""
            sn = p.serial_number

            # Check for direct VID match or HWID substring
            is_dabao = False
            mode = DabaoInterfaceMode.UNKNOWN

            if vid == DABAO_VID:
                is_dabao = True
                if pid == PID_BOOTLOADER:
                    mode = DabaoInterfaceMode.BOOTLOADER
                elif pid == PID_XOUS_RUNTIME:
                    mode = DabaoInterfaceMode.XOUS_RUNTIME
            elif "1D50" in hwid.upper():
                is_dabao = True
                if "6196" in hwid.upper():
                    mode = DabaoInterfaceMode.BOOTLOADER
                    pid = PID_BOOTLOADER
                elif "6197" in hwid.upper():
                    mode = DabaoInterfaceMode.XOUS_RUNTIME
                    pid = PID_XOUS_RUNTIME
                vid = DABAO_VID

            if is_dabao:
                descriptor = DabaoDeviceDescriptor(
                    port=p.device,
                    description=p.description or "CrossBar Dabao",
                    hwid=hwid,
                    vid=vid,
                    pid=pid,
                    serial_number=sn,
                    mode=mode,
                )
                detected.append(descriptor)

        return detected

    @classmethod
    def get_preferred_device(cls, manual_port: Optional[str] = None) -> Optional[DabaoDeviceDescriptor]:
        """
        Returns the preferred Dabao device:
        1. If manual_port specified, attempts to find that port.
        2. Prefers XOUS_RUNTIME mode if active.
        3. Falls back to BOOTLOADER mode.
        """
        devices = cls.scan_ports()
        if not devices:
            return None

        if manual_port:
            for d in devices:
                if d.port.upper() == manual_port.upper():
                    return d
            logger.warning(f"Manual port {manual_port} not found among Dabao devices.")

        # Prefer runtime mode over bootloader if multiple are connected
        runtime_devices = [d for d in devices if d.mode == DabaoInterfaceMode.XOUS_RUNTIME]
        if runtime_devices:
            return runtime_devices[0]

        return devices[0]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Scanning for physical Dabao hardware...")
    devs = DeviceDiscovery.scan_ports()
    print(f"Found {len(devs)} Dabao device(s):")
    for dev in devs:
        print(f"  {dev}")
