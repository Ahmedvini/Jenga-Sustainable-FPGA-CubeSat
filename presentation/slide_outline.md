# Final Presentation — Slide Outline (5-minute cap)

> **Superseded (2026-07-03):** `PRESENTATION_PLAN.md` is the current
> plan (Jenga branding, per-slide script, Q&A prep). Kept for history.
> Status change since this was written: the bench **power chain is now
> assembled and working** (solar → CN3791 MPPT → 18650 → fuse →
> MP1584 → 3.3 V), and the slide 3 note about missing architecture
> images is stale — `docs/architecture/schematic.png` exists.

Seven slides, ~40 s each. The live demo is separate (see
`presentation/demo_run_sheet.md`) — this deck must NOT eat demo time.

## Slide 1 — Title (0:00–0:20)

- EcoSat: Sustainable Modular Electronics for CubeSats.
- One sentence: "Satellite electronics should not draw full power when the
  mission state doesn't require it."
- Name, challenge, repo URL.

## Slide 2 — Problem & baseline (0:20–1:00)

- Conventional CubeSat stacks are monolithic and always-on: MCU, sensors,
  radio, bus logic powered for all 95 minutes of the orbit.
- Baseline (same mission, datasheet currents at 3.3 V): **242.55 mW average,
  384.04 mWh per orbit**.
- Why it matters: every wasted mWh deepens battery discharge each orbit —
  battery wear is what typically ends a CubeSat mission.

## Slide 3 — The EcoSat design (1:00–1:50)

- Modular hot-swap electronics: OBC, power, sensing, comms + optional FPGA
  accelerator. (Needs a system block diagram — the old `docs/architecture/`
  images were removed; redraw one for this slide. RTL-level fallback:
  `rtl/synthesis_reports/zcu106/schematic.pdf`.)
- PMEP: USB-style plug-and-play enumeration over CAN/I2C with a DETECT line —
  modules are discovered, configured, and power-managed at runtime.
- Orbit-aware duty cycling: active / low-rate / sleep / off per module, driven
  by sunlight vs. eclipse state.

## Slide 4 — Results (1:50–2:40)

- Table: baseline 242.55 mW → duty-cycled **126.54 mW (47.83% saved)** →
  FPGA-burst extension 70.41 mW (70.97%).
- Show `results/graphs/power_vs_time.png`: flat baseline vs. stepped profile.
- Honesty framing (judges reward it): duty-cycled is the conservative main
  claim; FPGA burst additionally assumes compression shortens radio time
  57 → 6 min, so it is presented as an extension scenario.
- Net accounting: OBC currents include scheduler + PMEP decision logic —
  control overhead is inside these numbers.

## Slide 5 — Verification (2:40–3:30)

- Python simulation: deterministic, stdlib-only core, 8-test suite, one
  command regenerates every CSV, plot, and report.
- RTL: FIR filter, RLE compressor, CAN filter pass **self-checking** Icarus
  Verilog testbenches (expected-vs-actual, PASS/FAIL exit codes).
- PMEP protocol logic runs as a compiled C demo: live hot-swap enumeration
  and orbit-based power-mode switching.

## Slide 6 — Sustainability impact (3:30–4:15)

- Battery: equivalent full cycles ≈143.6 → ≈74.9 per year (−47.8%) → ≈92%
  cycle-life extension → longer missions, fewer replacement satellites.
- Thermal: ~48% lower average dissipation → simpler thermal design.
- Modularity: hot-swap modules enable reuse, repair, and incremental upgrade
  instead of whole-stack redesign (SDG 9 / 12 alignment).

## Slide 7 — Limitation & close (4:15–5:00)

- Documented limitation (stated before judges ask): mode transitions modeled
  as instantaneous — no inrush/settling energy; eclipse fixed at 38 min, not
  season-dependent. Bounds precision, doesn't change the conclusion.
- Close: "Everything you just saw regenerates from one command in a public
  repo — that's the standard sustainable space electronics should be held to."
- Hand off to live demo.

## Delivery notes

- Rehearse to ≤ 4:45 against a stopwatch; judges value ending under the cap.
- Every number spoken must match `results/reports/simulation_summary.md` and
  the Final Evidence Sheet exactly.
- Keep slide text sparse; the tables above are talking points, not slide copy.
