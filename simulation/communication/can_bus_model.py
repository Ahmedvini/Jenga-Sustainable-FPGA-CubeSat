"""Simple CAN bus timing model."""


def transmit_time_ms(bits: int, bitrate_bps: int = 1_000_000) -> float:
    return bits / bitrate_bps * 1000.0
