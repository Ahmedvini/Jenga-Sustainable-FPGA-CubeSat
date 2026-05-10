"""Power module model."""


def current_for_state(state: str) -> float:
    return 5.2 if state == "charging" else 1.8
