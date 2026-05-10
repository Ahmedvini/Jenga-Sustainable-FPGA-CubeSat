"""Battery-life comparison helpers."""

from simulation.power.battery_model import equivalent_full_cycles_per_year, watt_hours


def annual_cycles(daily_energy_mwh: float, voltage_v: float = 7.4, capacity_mah: float = 2000.0) -> float:
    return equivalent_full_cycles_per_year(daily_energy_mwh, watt_hours(voltage_v, capacity_mah))
