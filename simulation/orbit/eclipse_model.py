"""Eclipse helper functions."""

from simulation.constants import ECLIPSE_MINUTES, ORBIT_MINUTES, SUNLIGHT_MINUTES


def is_eclipse(minute: float) -> bool:
    return (minute % ORBIT_MINUTES) >= SUNLIGHT_MINUTES


def eclipse_fraction() -> float:
    return ECLIPSE_MINUTES / ORBIT_MINUTES
