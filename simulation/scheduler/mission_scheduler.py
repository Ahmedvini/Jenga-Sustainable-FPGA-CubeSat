"""Mission scheduler for orbit-aware power modes."""


def power_mode_for(module: str, orbit_state: str) -> str:
    if orbit_state == "sunlight":
        return "active"
    if module in {"comms", "fpga"}:
        return "off"
    if module == "sensing":
        return "low_rate"
    return "sleep"
