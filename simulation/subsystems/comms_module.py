"""Communications subsystem model."""


def current_for_state(state: str) -> float:
    return {"tx_rx": 35.0, "idle": 0.01, "off": 0.01}.get(state, 0.01)
