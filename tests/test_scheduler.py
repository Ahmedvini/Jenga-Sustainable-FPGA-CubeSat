from simulation.scheduler.mission_scheduler import power_mode_for


def test_comms_turns_off_in_eclipse():
    assert power_mode_for("comms", "eclipse") == "off"


def test_sensing_low_rate_in_eclipse():
    assert power_mode_for("sensing", "eclipse") == "low_rate"
