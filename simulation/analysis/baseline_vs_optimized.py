"""Baseline vs optimized comparison helpers."""

from simulation.power.energy_estimator import summarize_scenario
from simulation.power.power_model import SCENARIOS, baseline_average_power_mw


def comparison_rows() -> list[dict[str, float | str]]:
    baseline = baseline_average_power_mw()
    return [summarize_scenario(scenario, baseline) for scenario in SCENARIOS]
