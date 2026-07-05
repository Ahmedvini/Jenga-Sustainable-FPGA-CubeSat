#!/usr/bin/env python3
"""Render the bench circuit simulation as an animated proof-of-concept clip.

Runs the deterministic behavioral simulation from circuit_model.py for
three orbits and renders a progressive time-series animation — battery
state of charge and 3.3 V rail power over sunlight/eclipse bands, with
a live readout — plus a static overview frame:

    video/bench_sim_poc.gif           (animation; convert to mp4 with
                                       `ffmpeg -i bench_sim_poc.gif ...`)
    results/graphs/bench_orbit_profile.png   (final frame, static)

Requires matplotlib + pillow; exits gracefully without them.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.constants import ORBIT_MINUTES, SUNLIGHT_MINUTES
from simulation.bench.circuit_model import simulate

# Colorblind-validated pair (dataviz six-checks, light surface)
COLOR_SOC = "#1d4ed8"
COLOR_RAIL = "#0d9488"
BAND_SUN = ("#fbbf24", 0.18)
BAND_ECLIPSE = ("#64748b", 0.15)
INK = "#111827"
INK_MUTED = "#6b7280"
GRID = "#e5e7eb"

ORBITS = 3
FPS = 14
HOLD_FRAMES = 28  # ~2 s freeze on the completed plot


def render() -> int:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.animation import FuncAnimation, PillowWriter
    except ImportError:
        print("matplotlib/pillow not installed - skipping video render")
        return 0

    samples, summary = simulate(orbits=ORBITS, start_soc=60.0)
    t = [s["t_min"] for s in samples]
    soc = [s["soc_percent"] for s in samples]
    rail = [s["rail_mw"] for s in samples]
    modes = [s["mode"] for s in samples]

    fig, (ax_soc, ax_rail) = plt.subplots(
        2, 1, figsize=(8.9, 5.0), dpi=100, sharex=True,
        gridspec_kw={"hspace": 0.18, "top": 0.80, "bottom": 0.11,
                     "left": 0.09, "right": 0.97},
    )
    fig.patch.set_facecolor("white")
    fig.text(0.09, 0.955, "Jenga bench circuit — simulated orbit profile",
             fontsize=13, fontweight="bold", color=INK)
    fig.text(0.09, 0.905,
             "solar 6V/2W → CN3791 MPPT → 18650 → 1A fuse → MP1584 → 3.3V"
             " sensor rail  ·  57/38 min sun/eclipse",
             fontsize=8.5, color=INK_MUTED)
    readout = fig.text(0.09, 0.845, "", fontsize=10, color=INK,
                       family="monospace")

    total_min = ORBITS * ORBIT_MINUTES
    for ax in (ax_soc, ax_rail):
        for k in range(ORBITS):
            start = k * ORBIT_MINUTES
            ax.axvspan(start, start + SUNLIGHT_MINUTES,
                       color=BAND_SUN[0], alpha=BAND_SUN[1], lw=0)
            ax.axvspan(start + SUNLIGHT_MINUTES, start + ORBIT_MINUTES,
                       color=BAND_ECLIPSE[0], alpha=BAND_ECLIPSE[1], lw=0)
        ax.set_xlim(0, total_min)
        ax.grid(axis="y", color=GRID, lw=0.8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(colors=INK_MUTED, labelsize=8.5)

    ax_soc.set_ylim(55, 103)
    ax_soc.set_title("Battery state of charge (%)", loc="left",
                     fontsize=9.5, color=INK)
    ax_soc.text(SUNLIGHT_MINUTES / 2, 58, "sunlight", ha="center",
                fontsize=8, color=INK_MUTED)
    ax_soc.text(SUNLIGHT_MINUTES + (ORBIT_MINUTES - SUNLIGHT_MINUTES) / 2,
                58, "eclipse", ha="center", fontsize=8, color=INK_MUTED)

    ax_rail.set_ylim(0, max(rail) * 1.18)
    ax_rail.set_title("3.3 V rail power (mW)", loc="left",
                      fontsize=9.5, color=INK)
    ax_rail.set_xlabel("mission time (min)", fontsize=9, color=INK_MUTED)

    (line_soc,) = ax_soc.plot([], [], color=COLOR_SOC, lw=2)
    (line_rail,) = ax_rail.plot([], [], color=COLOR_RAIL, lw=2)
    (dot_soc,) = ax_soc.plot([], [], "o", color=COLOR_SOC, ms=5)
    (dot_rail,) = ax_rail.plot([], [], "o", color=COLOR_RAIL, ms=5)

    def update(frame: int):
        i = min(frame, len(t) - 1)
        line_soc.set_data(t[: i + 1], soc[: i + 1])
        line_rail.set_data(t[: i + 1], rail[: i + 1])
        dot_soc.set_data([t[i]], [soc[i]])
        dot_rail.set_data([t[i]], [rail[i]])
        orbit_no = int(t[i] // ORBIT_MINUTES) + 1
        mode = "SUNLIGHT ACTIVE" if modes[i] == "sunlight_active" else "ECLIPSE LOW-RATE"
        readout.set_text(
            f"t={t[i]:6.0f} min  orbit {orbit_no}/{ORBITS}  "
            f"mode {mode:<16s}  SOC {soc[i]:6.2f}%  rail {rail[i]:5.2f} mW"
        )
        return line_soc, line_rail, dot_soc, dot_rail, readout

    frames = len(t) + HOLD_FRAMES
    anim = FuncAnimation(fig, update, frames=frames, blit=False)

    out_gif = ROOT / "video" / "bench_sim_poc.gif"
    out_gif.parent.mkdir(parents=True, exist_ok=True)
    anim.save(out_gif, writer=PillowWriter(fps=FPS))
    print(f"- wrote {out_gif.relative_to(ROOT)} "
          f"({len(t)} data frames at {FPS} fps)")

    update(len(t) - 1)
    out_png = ROOT / "results" / "graphs" / "bench_orbit_profile.png"
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    print(f"- wrote {out_png.relative_to(ROOT)}")
    plt.close(fig)

    print(f"RESULT margin={summary.energy_margin_percent:.1f}% "
          f"soc_range={summary.soc_min_pct:.1f}-{summary.soc_max_pct:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(render())
