# GLITCHGUARD Serial Communications Package
from .device_discovery import DeviceDiscovery, DabaoDeviceDescriptor, DabaoInterfaceMode
from .connection_manager import (
    ConnectionManager,
    ConnectionState,
    DeviceHandshakeInfo,
    ConnectionDiagnostics,
    global_connection_manager,
)
from .connector import SerialConnector

__all__ = [
    "DeviceDiscovery",
    "DabaoDeviceDescriptor",
    "DabaoInterfaceMode",
    "ConnectionManager",
    "ConnectionState",
    "DeviceHandshakeInfo",
    "ConnectionDiagnostics",
    "global_connection_manager",
    "SerialConnector",
]
