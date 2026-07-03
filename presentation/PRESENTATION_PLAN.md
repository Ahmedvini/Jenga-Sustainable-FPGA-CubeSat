# Jenga — Presentation Plan (PRIVATE, gitignored)

Judging format: **5-min presentation + 5-min live demo + 4-min Q&A**.
Scoring: **75% technical / 25% sustainability**. Onsite 6 July,
judging 13:30. This file is prep material — not part of the package.

Deck: 7 slides, 16:9. Build in PowerPoint / Google Slides / Canva.
Export **PDF** for the submission package (name it
`Jenga_Presentation.pdf`), keep the editable file + a USB copy.

---

## Slide 1 — Title (0:00–0:15)

**On slide**
- Jenga — Sustainable FPGA CubeSat
- FPGA-based CubeSat On-Board Computer prototype
- Ahmed Elsheikh · E-JUST · AESS Sustainability Hackathon 2026, Challenge 1
- Repo: github.com/Ahmedvini/Jenga-Sustainable-FPGA-CubeSat (small QR optional)

**Visual**: cropped hero from `docs/architecture/schematic.png` (title
banner + iCEstick section), or a photo of the iCEstick.

**Say**: "Jenga is a CubeSat electronics platform built on one idea:
a satellite should never spend power the mission state doesn't need.
I'll show you the architecture, the measured evidence, and why it
matters for sustainability."

## Slide 2 — Problem (0:15–0:45)

**On slide**
- Conventional CubeSat stack: MCU + sensors + radio always on, all orbit
- 95-min LEO orbit = 57 min sunlight + 38 min eclipse
- Baseline: **242.55 mW average, 384.04 mWh per orbit**
- Consequence: deep battery discharge every orbit → battery wear is the
  #1 mission-ending mechanism

**Visual**: `results/graphs/power_vs_time.png` (baseline dashed red
line dominates; eclipse band shaded).

**Say**: "In eclipse there is nothing to downlink and little to sense —
yet a monolithic board burns full power through it, every orbit,
~15 times a day."

## Slide 3 — Architecture (0:45–1:45)  ← longest slide

**On slide**
- **The FPGA *is* the OBC**: scheduler, power controller, orbit state,
  CAN filter, RLE compression, FIR filter — all HDL finite-state
  machines. No soft CPU, no OS.
- Power chain: Solar 6V/2W → CN3791 MPPT → 18650 → fuse → MP1584 → 3.3 V
- Six-sensor shared I2C bus (IMU, mag, lux, power, temp, RTC), single
  FPGA master
- Two layers: reference power model (numbers) + bench prototype (proof)

**Visual**: `docs/architecture/schematic.png` (full) — walk it left to
right. Backup: Mermaid system diagram from
`docs/architecture/SYSTEM_ARCHITECTURE.md` §1 rendered at mermaid.live.

**Say**: "Power management isn't firmware asking politely — it's
hardware state machines driving switched rails. The whole OBC fits in
a third of the smallest FPGA Lattice makes, which is exactly the
sustainability point: fly the smallest silicon that does the job."

## Slide 4 — How it saves energy + results (1:45–2:45)

**On slide** (the results table, verbatim from README)

| Scenario | Avg power | Energy/orbit | Saved |
|---|---|---|---|
| Baseline always-on | 242.55 mW | 384.04 mWh | — |
| **Duty-cycled (main claim)** | **126.54 mW** | **200.35 mWh** | **47.83%** |
| + FPGA burst (extension) | 70.41 mW | 111.49 mWh | 70.97% |
| Safe mode, low battery | 27.28 mW | 43.20 mWh | operating case |

- Orbit-aware duty cycling + per-module switched rails
- Control overhead is **inside** the numbers (scheduler current charged)
- Deterministic model, datasheet currents — regenerates with one command

**Visual**: `results/graphs/scenario_comparison.png`.

**Say**: "47.83% is the conservative claim. The burst mode assumes
compression shortens radio time — I present it as an extension, not
the headline. And safe mode shows the policy sheds load below 35%
battery instead of falling over."

## Slide 5 — Implementation evidence (2:45–3:45)

**On slide** (cross-vendor table, from icestick REPORT.md §9)

| | ZCU106 (16nm) | Zynq-7010 (28nm) | iCE40HX1K (40nm) |
|---|---|---|---|
| Toolchain | Vivado | Vivado | **Yosys+nextpnr (open source)** |
| LUTs / FFs | 44 / 90 | 43 / 90 | 157 / 120 (core) |
| Timing | +8.25 ns @100MHz | +4.57 ns @100MHz | +73.7 ns @12MHz |
| Device static | 592 mW | 90 mW | sub-10 mW class |

- Same RTL, three vendors, three independent toolchains — all pass
- 427/1280 LC (33.4%) on the deployed board; bitstream is deterministic
- Self-checking testbenches (golden models), 10/10 unit tests

**Visual**: `rtl/synthesis_reports/icestick/placed.svg` (die view
showing 2/3 empty) or `rtl/synthesis_reports/zcu106/gui_utilization_percent.png`.

**Say**: "Every number regenerates from four commands in the repo.
And read the static power row bottom-up: each step down in device
class cuts leakage by roughly 10× — that's the quantitative case for
the smallest FPGA on a switched rail."

## Slide 6 — Sustainability impact (3:45–4:30)  ← the 25%

**On slide**
- **Battery wear**: 143.6 → 74.9 equivalent full cycles/year (−47.8%)
  ≈ **91.7% cycle-life extension** → longer missions, less orbital junk
- Thermal dissipation −48% → simpler thermal design, less material
- **Open-source toolchain**: no licenses → reproducible, repairable,
  reusable by any university team
- Modular hot-swap (PMEP) → subsystem reuse across missions

**Visual**: `results/graphs/battery_cycles.png`.

**Say**: "The battery is the consumable. Halving its cycling means the
same satellite lives roughly twice as long before its storage wears
out — that's fewer replacement launches for the same mission-years."

## Slide 7 — Status + roadmap + close (4:30–5:00)

**On slide**
- Working today: full sim + tests, 3-toolchain synthesis, LED orbit
  demo on real silicon, drawn hardware design + BOM
- Next: I2C sensor front-end, UART telemetry, **INA226 live measured
  power vs the model** (the killer follow-up)
- One sentence: **"Fly the smallest FPGA that fits the workload, on a
  switched rail."**

**Say**: "Everything you saw is in the public repo and reproduces from
a fresh clone. Now let me show it running." → hand off to demo.

---

## Demo (5 min) — use `presentation/demo_run_sheet.md` (tracked, already written)

Order: sim run → graphs → tests → RTL testbenches → PMEP demo →
synthesis reports → (if iCEstick present: LED orbit demo, else backup
video). Rehearse the handoff sentence from slide 7.

## Q&A prep (4 min) — anticipated questions

1. **"Is 47.83% real or optimistic?"** — Datasheet supply currents,
   deterministic phase model, control/monitoring overhead charged
   inside the optimized numbers (evidence sheet, net-savings section).
   Known limits documented: instantaneous transitions, fixed 38-min
   eclipse.
2. **"Why an FPGA instead of a low-power MCU?"** — The reference model
   *is* MCU-based; the FPGA OBC removes the always-on CPU entirely and
   makes power policy hardware-native. Static-power ladder: 592 → 90 →
   sub-10 mW. Also: no proprietary runtime, fully open toolchain.
3. **"What's measured vs modeled?"** — Modeled: power scenarios
   (datasheet currents). Measured/tool-verified: all utilization &
   timing on three toolchains, working bitstream on real silicon.
   Roadmap R5 adds INA226 live measurement.
4. **"Radiation / space qualification?"** — Prototype demonstrates
   architecture, not flight qualification; the same RTL retargets
   rad-tolerant parts (portability proven across 3 vendors' tools).
5. **"Why RLE, not a stronger codec?"** — Fits in 1280 LC with zero
   BRAM; telemetry is run-heavy; compression ratio only needs to beat
   radio-on time, not win benchmarks.
6. **"Single point of failure — one FPGA?"** — Safe-mode policy +
   watchdog-style POR; modularity (PMEP) isolates subsystem faults;
   flight version would add TMR on the ~160-LUT core (cheap at this
   size).
7. **"MP1584 from a 1S cell — dropout?"** — Known risk P1, documented:
   below ~3.6 V the buck hits dropout; the 35% SOC safe-mode threshold
   doubles as the electrical floor; buck-boost swap is roadmap R8.
8. **"Did you use AI?"** — Yes, disclosed in `docs/AI_DISCLOSURE.md`
   (Claude Code for engineering assistance; all numbers reproduce from
   committed code).

## Asset checklist (copy into the deck)

- [ ] `docs/architecture/schematic.png` (slides 1, 3)
- [ ] `results/graphs/power_vs_time.png` (slide 2)
- [ ] `results/graphs/scenario_comparison.png` (slide 4)
- [ ] `results/graphs/battery_cycles.png` (slide 6)
- [ ] `rtl/synthesis_reports/icestick/placed.svg` → export PNG (slide 5)
- [ ] `rtl/synthesis_reports/zcu106/gui_utilization_percent.png` (slide 5 alt)
- [ ] Mermaid §1 diagram rendered at mermaid.live (slide 3 backup)

## Build & rehearsal checklist

- [ ] Build deck (16:9), max ~40 words per slide, numbers in tables
- [ ] Export `Jenga_Presentation.pdf` into the submission package
- [ ] Copy deck + PDF + backup video to USB stick
- [ ] Timed rehearsal ×2 (target 4:45, leave 15 s buffer)
- [ ] Rehearse demo from a fresh clone once
- [ ] Charge laptop; disable notifications; offline-capable everything
