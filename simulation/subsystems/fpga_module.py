"""FPGA accelerator subsystem model."""

ACTIVE_CURRENT_MA = 28.0
OFF_CURRENT_MA = 0.01


def current_for_active(active: bool) -> float:
    return ACTIVE_CURRENT_MA if active else OFF_CURRENT_MA
