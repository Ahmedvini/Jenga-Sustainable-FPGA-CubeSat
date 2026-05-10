from simulation.orbit.orbit_model import state_at_minute


def test_orbit_state_changes_after_sunlight_period():
    assert state_at_minute(0) == "sunlight"
    assert state_at_minute(56.9) == "sunlight"
    assert state_at_minute(57.0) == "eclipse"
