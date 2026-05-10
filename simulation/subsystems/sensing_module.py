"""Sensing subsystem model."""


def current_for_rate(sample_rate_hz: float) -> float:
    if sample_rate_hz >= 10.0:
        return 8.5
    return 0.9
