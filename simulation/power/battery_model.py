"""Simple battery lifetime model for comparing design cases."""


def watt_hours(voltage_v: float, capacity_mah: float) -> float:
    return voltage_v * capacity_mah / 1000.0


def equivalent_full_cycles_per_year(daily_energy_mwh: float, battery_wh: float) -> float:
    daily_energy_wh = daily_energy_mwh / 1000.0
    return daily_energy_wh * 365.0 / battery_wh


def lifetime_extension_percent(baseline_cycles: float, optimized_cycles: float) -> float:
    return (baseline_cycles / optimized_cycles - 1.0) * 100.0
