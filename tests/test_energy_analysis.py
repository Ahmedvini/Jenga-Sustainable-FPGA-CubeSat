from simulation.power.energy_estimator import savings_percent


def test_savings_percent():
    assert savings_percent(100.0, 75.0) == 25.0
