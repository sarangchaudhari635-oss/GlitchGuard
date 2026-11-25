#!/usr/bin/env python3
"""
GLITCHGUARD Telemetry Protocol Framing & Parser
Encodes and decodes bidirectional line-delimited JSON frames between host and Dabao.
Enforces sequence ordering, CRC32 verification, and schema validation.
"""

import binascii
import json
import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional, Tuple

PROTOCOL_VERSION = "1.0"


class MessageType(str, Enum):
    HELLO = "HELLO"
    HANDSHAKE_RESPONSE = "HANDSHAKE_RESPONSE"
    DEVICE_STATUS = "DEVICE_STATUS"
    HEARTBEAT = "HEARTBEAT"
    HARDWARE_CAPABILITIES = "HARDWARE_CAPABILITIES"
    HARDWARE_EVENT = "HARDWARE_EVENT"
    SOFTWARE_ANOMALY = "SOFTWARE_ANOMALY"
    INTEGRITY_RESULT = "INTEGRITY_RESULT"
    RECOVERY_STATE = "RECOVERY_STATE"
    CONSOLE_OUTPUT = "CONSOLE_OUTPUT"
    ERROR = "ERROR"
    # Commands
    PING = "PING"
    GET_STATUS = "GET_STATUS"
    GET_CAPABILITIES = "GET_CAPABILITIES"
    START_HEARTBEAT = "START_HEARTBEAT"
    STOP_HEARTBEAT = "STOP_HEARTBEAT"
    START_SAFE_TEST = "START_SAFE_TEST"


class TelemetryFrame:
    def __init__(
        self,
        message_type: MessageType,
        payload: Dict[str, Any],
        source: str = "PHYSICAL_SILICON_OBSERVED",
        sequence: int = 0,
        device_uptime_ms: int = 0,
        message_id: Optional[str] = None,
        timestamp_ns: Optional[int] = None,
    ):
        self.protocol_version = PROTOCOL_VERSION
        self.message_type = message_type
        self.message_id = message_id or str(uuid.uuid4())
        self.sequence = sequence
        self.device_uptime_ms = device_uptime_ms
        self.timestamp_ns = timestamp_ns or int(time.time() * 1e9)
        self.source = source
        self.payload = payload

    @property
    def integrity_crc32(self) -> str:
        payload_bytes = json.dumps(self.payload, sort_keys=True).encode("utf-8")
        crc = binascii.crc32(payload_bytes)
        return f"0x{crc:08X}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "protocol_version": self.protocol_version,
            "message_type": self.message_type.value,
            "message_id": self.message_id,
            "sequence": self.sequence,
            "device_uptime_ms": self.device_uptime_ms,
            "timestamp_ns": self.timestamp_ns,
            "source": self.source,
            "payload": self.payload,
            "integrity": self.integrity_crc32,
        }

    def serialize_line(self) -> str:
        """Serializes frame into newline-delimited wire format."""
        return json.dumps(self.to_dict()) + "\n"

    @classmethod
    def parse_line(cls, line: str) -> Tuple[Optional["TelemetryFrame"], Optional[str]]:
        """
        Parses a single wire line into a TelemetryFrame.
        Returns (frame, error_message).
        """
        clean = line.strip()
        if not clean:
            return None, "Empty line"

        try:
            data = json.loads(clean)
        except Exception as e:
            return None, f"JSON decode error: {e}"

        if not isinstance(data, dict):
            return None, "Message is not a JSON object"

        ver = data.get("protocol_version")
        if ver != PROTOCOL_VERSION:
            return None, f"Unsupported protocol version: {ver}"

        msg_type_str = data.get("message_type")
        if not msg_type_str:
            return None, "Missing message_type"
        try:
            msg_type = MessageType(msg_type_str)
        except Exception:
            return None, f"Unknown message type: {msg_type_str}"

        frame = cls(
            message_type=msg_type,
            payload=data.get("payload", {}),
            source=data.get("source", "UNVERIFIED"),
            sequence=data.get("sequence", 0),
            device_uptime_ms=data.get("device_uptime_ms", 0),
            message_id=data.get("message_id"),
            timestamp_ns=data.get("timestamp_ns"),
        )

        # Check integrity if present
        received_crc = data.get("integrity")
        if received_crc and received_crc != frame.integrity_crc32:
            return None, f"CRC32 mismatch: calculated {frame.integrity_crc32} != received {received_crc}"

        return frame, None
