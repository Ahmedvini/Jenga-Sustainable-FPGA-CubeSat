"""Telemetry sizing helpers."""


def packet_bits(payload_bytes: int, overhead_bytes: int = 12) -> int:
    return (payload_bytes + overhead_bytes) * 8
