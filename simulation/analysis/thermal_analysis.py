"""Thermal comparison helpers."""

from simulation.power.thermal_model import relative_thermal_load


def thermal_reduction_percent(power_mw: float, baseline_power_mw: float) -> float:
    return (1.0 - relative_thermal_load(power_mw, baseline_power_mw)) * 100.0
