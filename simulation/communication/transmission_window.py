"""Transmission-window estimates."""


def packets_per_window(window_seconds: float, packet_time_ms: float) -> int:
    return int(window_seconds * 1000.0 / packet_time_ms)
