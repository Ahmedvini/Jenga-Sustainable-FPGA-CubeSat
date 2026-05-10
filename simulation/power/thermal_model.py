"""First-order thermal-load estimates based on dissipated electrical power."""


def relative_thermal_load(power_mw: float, baseline_power_mw: float) -> float:
    return power_mw / baseline_power_mw


def estimated_temperature_drop_c(power_savings_percent: float, max_drop_c: float = 12.0) -> float:
    return max_drop_c * min(max(power_savings_percent, 0.0), 50.0) / 50.0
