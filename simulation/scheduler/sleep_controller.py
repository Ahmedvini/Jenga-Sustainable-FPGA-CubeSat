"""Sleep-mode selection helpers."""


def sleep_current_multiplier(mode: str) -> float:
    return {"active": 1.0, "low_rate": 0.15, "sleep": 0.05, "off": 0.001}.get(mode, 1.0)
