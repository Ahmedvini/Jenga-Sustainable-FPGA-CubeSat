"""Mission timeline utilities."""

from simulation.constants import ORBIT_MINUTES
from simulation.orbit.orbit_model import state_at_minute


def build_mission_timeline(orbits: int, step_min: float = 5.0) -> list[dict[str, float | str]]:
    timeline = []
    total_minutes = orbits * ORBIT_MINUTES
    minute = 0.0
    while minute < total_minutes:
        timeline.append({"minute": minute, "orbit": int(minute // ORBIT_MINUTES) + 1, "state": state_at_minute(minute)})
        minute += step_min
    return timeline
