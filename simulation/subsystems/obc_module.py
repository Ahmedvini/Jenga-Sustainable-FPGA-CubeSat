"""OBC subsystem model."""

ACTIVE_CURRENT_MA = 12.0
LOW_POWER_CURRENT_MA = 2.1


def current_for_mode(mode: str) -> float:
    return ACTIVE_CURRENT_MA if mode == "active" else LOW_POWER_CURRENT_MA
