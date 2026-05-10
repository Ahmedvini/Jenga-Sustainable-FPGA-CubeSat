"""Energy and savings calculations."""

from simulation.constants import HOURS_PER_DAY, ORBIT_MINUTES
from simulation.power.power_model import Scenario


def energy_per_orbit_mwh(average_power_mw: float) -> float:
    return average_power_mw * ORBIT_MINUTES / 60.0


def daily_energy_mwh(average_power_mw: float) -> float:
    return average_power_mw * HOURS_PER_DAY


def savings_percent(baseline_value: float, optimized_value: float) -> float:
    return (baseline_value - optimized_value) / baseline_value * 100.0


def summarize_scenario(scenario: Scenario, baseline_power_mw: float) -> dict[str, float | str]:
    baseline_orbit_mwh = energy_per_orbit_mwh(baseline_power_mw)
    return {
        "scenario": scenario.name,
        "average_power_mw": scenario.average_power_mw,
        "energy_per_orbit_mwh": scenario.energy_per_orbit_mwh,
        "power_savings_percent": savings_percent(baseline_power_mw, scenario.average_power_mw),
        "energy_savings_percent": savings_percent(baseline_orbit_mwh, scenario.energy_per_orbit_mwh),
    }
