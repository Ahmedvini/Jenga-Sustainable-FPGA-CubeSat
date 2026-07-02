"""Matplotlib plot generation for simulation results.

The core simulation is stdlib-only; matplotlib is an optional dependency.
If it is missing, plot generation is skipped with a console note and the
rest of the pipeline still runs.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Sequence

from simulation.constants import ORBIT_MINUTES, SUNLIGHT_MINUTES


BASELINE_COLOR = "tab:red"
SCENARIO_COLORS = ("tab:blue", "tab:green", "tab:purple", "tab:orange")


def _pretty(name: str) -> str:
    return name.replace("_", " ")


def _phase_steps(scenario) -> tuple[list[float], list[float]]:
    xs: list[float] = []
    ys: list[float] = []
    elapsed = 0.0
    for phase in scenario.phases:
        xs.extend([elapsed, elapsed + phase.duration_min])
        ys.extend([phase.total_power_mw, phase.total_power_mw])
        elapsed += phase.duration_min
    return xs, ys


def generate_all_plots(
    baseline_power_mw: float,
    baseline_cycles_per_year: float,
    scenarios: Sequence,
    scenario_rows: Sequence[dict],
    out_dir: Path,
) -> list[Path]:
    """Render every result plot into out_dir and return the written paths."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print(
            "matplotlib not installed; skipping plots "
            "(python3 -m pip install -r requirements.txt)"
        )
        return []

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    names = ["baseline\nalways on"] + [
        "\n".join(textwrap.wrap(_pretty(scenario.name), 12)) for scenario in scenarios
    ]
    colors = [BASELINE_COLOR] + list(SCENARIO_COLORS[: len(scenarios)])
    baseline_energy_mwh = baseline_power_mw * ORBIT_MINUTES / 60.0

    # Power vs orbit time
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axvspan(SUNLIGHT_MINUTES, ORBIT_MINUTES, color="0.88", zorder=0, label="Eclipse (38 min)")
    ax.plot(
        [0.0, ORBIT_MINUTES],
        [baseline_power_mw, baseline_power_mw],
        color=BASELINE_COLOR,
        linewidth=2.0,
        linestyle="--",
        label=f"baseline always on ({baseline_power_mw:.1f} mW avg)",
    )
    peak = baseline_power_mw
    for scenario, color in zip(scenarios, SCENARIO_COLORS):
        xs, ys = _phase_steps(scenario)
        peak = max(peak, max(ys))
        ax.plot(
            xs,
            ys,
            color=color,
            linewidth=2.0,
            label=f"{_pretty(scenario.name)} ({scenario.average_power_mw:.1f} mW avg)",
        )
    ax.set_xlim(0.0, ORBIT_MINUTES)
    ax.set_ylim(0.0, peak * 1.2)
    ax.set_xlabel("Time into orbit (minutes)")
    ax.set_ylabel("Electrical power (mW)")
    ax.set_title("Power draw across one 95-minute LEO orbit (550 km SSO)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    path = out_dir / "power_vs_time.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    written.append(path)

    # Average power and energy per orbit, per scenario
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    powers = [baseline_power_mw] + [scenario.average_power_mw for scenario in scenarios]
    energies = [baseline_energy_mwh] + [scenario.energy_per_orbit_mwh for scenario in scenarios]

    bars1 = ax1.bar(names, powers, color=colors)
    power_labels = [f"{value:.1f}" for value in powers]
    for i, row in enumerate(scenario_rows):
        power_labels[i + 1] += f"\n-{row['power_savings_percent']:.1f}%"
    ax1.bar_label(bars1, labels=power_labels, fontsize=9)
    ax1.set_ylabel("Average power (mW)")
    ax1.set_title("Average power per scenario")
    ax1.set_ylim(0.0, max(powers) * 1.3)

    bars2 = ax2.bar(names, energies, color=colors)
    energy_labels = [f"{value:.1f}" for value in energies]
    for i, row in enumerate(scenario_rows):
        energy_labels[i + 1] += f"\n-{row['energy_savings_percent']:.1f}%"
    ax2.bar_label(bars2, labels=energy_labels, fontsize=9)
    ax2.set_ylabel("Energy per orbit (mWh)")
    ax2.set_title("Energy per 95-minute orbit")
    ax2.set_ylim(0.0, max(energies) * 1.3)

    fig.suptitle("Baseline vs optimized scenarios (savings vs always-on baseline)")
    path = out_dir / "scenario_comparison.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    written.append(path)

    # Battery cycling
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    cycles = [baseline_cycles_per_year] + [
        row["battery_cycles_per_year"] for row in scenario_rows
    ]
    bars = ax.bar(names, cycles, color=colors)
    cycle_labels = [f"{baseline_cycles_per_year:.1f}"]
    for row in scenario_rows:
        cycle_labels.append(
            f"{row['battery_cycles_per_year']:.1f}\n"
            f"(+{row['battery_lifetime_extension_percent']:.0f}% life)"
        )
    ax.bar_label(bars, labels=cycle_labels, fontsize=9)
    ax.set_ylabel("Equivalent full battery cycles per year")
    ax.set_title("Battery cycling per year (fewer cycles = longer battery life)")
    ax.set_ylim(0.0, max(cycles) * 1.35)
    path = out_dir / "battery_cycles.png"
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    written.append(path)

    return written
