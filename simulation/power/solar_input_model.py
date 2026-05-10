"""Solar input estimate for a body-mounted CubeSat panel."""


def sunlight_energy_mwh(peak_power_w: float, sunlight_minutes: float, efficiency_factor: float = 0.65) -> float:
    return peak_power_w * 1000.0 * efficiency_factor * sunlight_minutes / 60.0
