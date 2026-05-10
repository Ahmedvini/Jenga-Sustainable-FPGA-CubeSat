"""Scenario configuration values."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MissionConfig:
    orbit_minutes: float = 95.0
    sunlight_minutes: float = 57.0
    eclipse_minutes: float = 38.0
    battery_capacity_mah: float = 2000.0
    battery_voltage_v: float = 7.4
    solar_peak_power_w: float = 2.4


DEFAULT_CONFIG = MissionConfig()
