from simulation.power.power_model import MODULAR_DUTY_CYCLED, baseline_average_power_mw


def test_baseline_power_matches_budget():
    assert round(baseline_average_power_mw(), 2) == 242.55


def test_modular_design_reduces_power():
    assert MODULAR_DUTY_CYCLED.average_power_mw < baseline_average_power_mw()
    assert round(MODULAR_DUTY_CYCLED.average_power_mw, 2) == 126.54
