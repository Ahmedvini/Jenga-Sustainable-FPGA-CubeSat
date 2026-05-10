"""Energy-analysis helpers."""


def orbit_savings_mwh(baseline_mwh: float, optimized_mwh: float) -> float:
    return baseline_mwh - optimized_mwh
