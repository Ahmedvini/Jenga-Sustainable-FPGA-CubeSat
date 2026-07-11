"""Tests for the bench circuit behavioral simulation."""

from simulation.bench.circuit_model import (
    BATTERY,
    BUCK,
    FUSE,
    SAFE_MODE_SOC_THRESHOLD,
    dropout_soc_floor,
    full_dark_autonomy_h,
    fuse_peak_a,
    rail_ma,
    rail_peak_ma,
    simulate,
)


def test_rail_budget_mode_ordering():
    assert rail_ma("sunlight_active") > rail_ma("eclipse_low") > 0.0
    assert rail_peak_ma() > rail_ma("sunlight_active")


def test_fuse_margin_at_least_5x():
    assert fuse_peak_a() * 5.0 < FUSE.rating_a


def test_dropout_floor_below_policy_threshold():
    floor = dropout_soc_floor()
    assert 0.0 < floor < SAFE_MODE_SOC_THRESHOLD


def test_battery_ocv_monotonic():
    vs = [BATTERY.ocv(s) for s in range(0, 101, 5)]
    assert all(a <= b for a, b in zip(vs, vs[1:]))
    assert vs[0] == 3.0 and vs[-1] == 4.2


def test_orbit_energy_positive_and_no_dropout():
    _, summary = simulate(orbits=3, start_soc=60.0)
    assert summary.harvested_mwh_per_orbit > summary.consumed_battery_mwh_per_orbit
    assert summary.energy_margin_percent > 50.0
    assert summary.dropout_events == 0
    assert 0.0 <= summary.soc_min_pct <= summary.soc_max_pct <= 100.0


def test_eclipse_discharges_battery_slightly():
    _, summary = simulate(orbits=3, start_soc=60.0)
    assert 0.0 < summary.eclipse_soc_drop_pct < 1.0


def test_buck_conservation():
    assert BUCK.input_power_w(1.0) > 1.0  # efficiency < 100%


def test_full_dark_autonomy_exceeds_one_orbit():
    assert full_dark_autonomy_h("sunlight_active") > 2.0
    assert full_dark_autonomy_h("eclipse_low") > full_dark_autonomy_h("sunlight_active")


def test_simulation_deterministic():
    s1, sum1 = simulate(orbits=2)
    s2, sum2 = simulate(orbits=2)
    assert sum1 == sum2
    assert s1 == s2
