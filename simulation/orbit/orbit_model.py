"""Orbit phase model."""

from dataclasses import dataclass

from simulation.constants import ECLIPSE_MINUTES, ORBIT_MINUTES, SUNLIGHT_MINUTES


@dataclass(frozen=True)
class OrbitState:
    minute: float
    state: str


def state_at_minute(minute: float) -> str:
    orbit_minute = minute % ORBIT_MINUTES
    if orbit_minute < SUNLIGHT_MINUTES:
        return "sunlight"
    return "eclipse"


def timeline(step_min: float = 1.0) -> list[OrbitState]:
    points = []
    minute = 0.0
    while minute < ORBIT_MINUTES:
        points.append(OrbitState(minute, state_at_minute(minute)))
        minute += step_min
    return points


def phase_durations() -> dict[str, float]:
    return {"sunlight": SUNLIGHT_MINUTES, "eclipse": ECLIPSE_MINUTES}
