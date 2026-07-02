from simulation.constants import ORBIT_MINUTES
from simulation.power.power_model import (
    MODULAR_DUTY_CYCLED,
    SAFE_MODE_LOW_BATTERY,
    SCENARIOS,
    baseline_average_power_mw,
)


def test_baseline_power_matches_budget():
    assert round(baseline_average_power_mw(), 2) == 242.55


def test_modular_design_reduces_power():
    assert MODULAR_DUTY_CYCLED.average_power_mw < baseline_average_power_mw()
    assert round(MODULAR_DUTY_CYCLED.average_power_mw, 2) == 126.54


def test_scenario_phases_cover_full_orbit():
    for scenario in SCENARIOS:
        total = sum(phase.duration_min for phase in scenario.phases)
        assert total == ORBIT_MINUTES, scenario.name


def test_safe_mode_sheds_load_below_duty_cycled():
    assert SAFE_MODE_LOW_BATTERY.average_power_mw < MODULAR_DUTY_CYCLED.average_power_mw
    beacon = next(p for p in SAFE_MODE_LOW_BATTERY.phases if p.name == "Beacon downlink")
    assert beacon.duration_min <= 5.0
    fpga_loads = [
        load
        for phase in SAFE_MODE_LOW_BATTERY.phases
        for load in phase.loads
        if "FPGA" in load.name
    ]
    assert fpga_loads == []
