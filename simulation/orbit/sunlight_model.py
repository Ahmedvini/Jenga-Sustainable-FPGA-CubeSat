"""Sunlight helper functions."""

from simulation.constants import ORBIT_MINUTES, SUNLIGHT_MINUTES


def is_sunlight(minute: float) -> bool:
    return (minute % ORBIT_MINUTES) < SUNLIGHT_MINUTES


def sunlight_fraction() -> float:
    return SUNLIGHT_MINUTES / ORBIT_MINUTES
