# Jenga — Speaker Notes (current 15-slide deck)

Matches `Black_and_White_Modern_Aerospace_Presentation` as presented to
judging today. Supersedes the 7-slide script in `PRESENTATION_PLAN.md`
(kept for the Q&A bank and demo run sheet, which still apply unchanged).

Format: **5-min presentation** target below (≈4:45 to leave buffer,
per your own rehearsal checklist) **+ 5-min live demo + 4-min Q&A**.
Timing column is cumulative — rehearse against a stopwatch and adjust.

**⚠ Before you go on stage:** Slide 8 currently shows two numbers that
don't match the repo's own generated evidence — say the corrected
numbers out loud even if you don't have time to fix the slide art:
**Buck Dropout SOC Floor = 27.5%** (not 15%), **Peak Fuse Current =
71 mA** (not 0.38 A). Details in `docs/FINAL_EVIDENCE_SHEET.md` and
`results/reports/bench_evidence_sheet.md`.

---

## Slide 1 — Title (0:00–0:10)

**Say:** "Jenga — a sustainable FPGA CubeSat. One idea drives everything
you're about to see: a satellite should never spend power the mission
state doesn't need."

*(No numbers here — just set the hook and move fast.)*

## Slide 2 — QR code (0:10–0:15)

**Say:** "The full repo is open — scan this anytime, everything I show
you reproduces from a clean clone."

*(Don't linger — this is a placeholder slide, not content.)*

## Slide 3 — "Every 95 minutes..." (0:15–0:35)

**Say:** "Every 95-minute low-Earth orbit has 57 minutes of sunlight
and 38 minutes of eclipse. In eclipse, a CubeSat loses its only power
source — yet most CubeSat electronics keep consuming almost the same
energy as if the sun were still shining. Jenga asks a simple question:
what if the satellite only powered the hardware it actually needed?"

**Key numbers:** 95 min orbit = 57 sun / 38 eclipse.

## Slide 4 — Problem Statement (0:35–0:55)

**Say:** "Conventional CubeSat electronics stay powered through the
whole orbit regardless of mission state. In eclipse, that wasted
energy accelerates battery degradation, raises thermal load, and
shortens the satellite's operational life. Battery wear is the
single biggest mission-ending mechanism in small satellites."

## Slide 5 — Proposed Solution (0:55–1:15)

**Say:** "Our answer: FPGA-based, orbit-aware power management. The
FPGA *is* the on-board computer — hardware state machines replace
software scheduling, dynamically switching subsystem power rails based
on whether we're in sunlight, eclipse, or a low-battery safe mode. And
the whole platform is built as modular, plug-and-play electronics —
we call that PMEP."

## Slide 6 — Why FPGA? (1:15–1:45)

**Say:** "FPGAs give true hardware parallelism instead of sequential
CPU execution — dedicated logic for every task instead of a shared
bottleneck. FPGA-based OBCs aren't new — NASA and ESA already fly
them. What's novel here is the combination: orbit-aware power
management done entirely in hardware, a hardware-state-machine OBC
with no soft CPU at all, our plug-and-play module protocol, and — as
far as we've found — one of the few CubeSat OBC platforms with a
**fully open-source RTL-to-bitstream flow** for the deployed target,
plus complete documentation and reproducible workflows."

**If asked:** scope "fully open-source" to the deployed iCEstick
target specifically — the ZCU106/Zynq-7010 comparisons use Vivado
only as a cross-vendor benchmark, not the flight target.

## Slide 7 — Architecture (1:45–2:25)

**Say:** "Here's the full system. The FPGA runs the scheduler, the
power controller, orbit-state tracking, CAN packet filtering, RLE
telemetry compression, and FIR sensor filtering — all as Verilog
finite-state machines, no soft CPU, no OS. The real power chain: a
solar panel through an MPPT charger into an 18650 Li-ion cell, fused,
then bucked down to a 3.3-volt rail that feeds six I2C sensors. There
are two layers behind every number I'll show you: a Python reference
model for the numbers, and this physical bench prototype as proof."

**Optional insert here:** the new *FPGA Internal Architecture* slide —
if you add it, this is where it goes (right after this one), and you'd
split the "say" line: finish the physical-wiring story here, then use
the new slide to walk the internal FSM cascade (orbit_controller →
scheduler → power_controller) and the parallel data plane (CAN filter,
RLE, FIR) before moving to Slide 8.

## Slide 8 — Simulation of Circuit (2:25–2:50)

**Say:** "We modeled the full power chain behaviorally — no public
SPICE models exist for these charger/buck modules, so this is the
honest system-level alternative. Worst case, the fuse only ever sees
71 milliamps against its 1-amp rating — a 14× margin. The buck
converter's electrical dropout floor is 27.5% state of charge, and our
safe-mode policy cuts the load at 35% — a 7.5-point cushion before the
converter ever gets in trouble. Across a 10-orbit simulation, the
system runs with a 91% energy surplus and zero dropout events."

**Key numbers (say the corrected ones, regardless of slide art):**
71 mA peak fuse current, 14× margin, 27.5% dropout floor, 35% safe-mode
threshold, 91.3% energy surplus.

## Slide 9 — How It Saves Energy (2:50–3:15)

**Say:** "Orbit-aware duty cycling plus per-module switched rails is
the whole mechanism — and the control overhead itself is charged
inside these numbers, not hidden. Average power drops from 242.5
milliwatts always-on to 126.5 with duty cycling — that's our
conservative, headline claim. The FPGA-burst scenario goes further,
to 70.4 milliwatts, but that assumes compression shortens radio time,
so we present it as an extension, not the main result."

**Key numbers:** 242.5 → 126.5 mW (−47.8%); FPGA burst 70.4 mW
(−71.0%); safe mode 27.3 mW.

## Slide 10 — Implementation Evidence (3:15–3:45)

**Say:** "Same RTL, three independent toolchains, three device
classes. On our deployed target — the Lattice iCE40HX1K, synthesized
with a fully open-source Yosys-plus-nextpnr flow — we use 427 of 1280
logic cells, just 33.4%, with zero BRAM and zero DSP blocks, and
timing closes at 12 megahertz with 73.7 nanoseconds of slack. Cross-
validated on Xilinx Vivado for a ZCU106 and a Zynq-7010: same LUT-level
logic, same functional result. And read static power bottom-up — 592
milliwatts, then 90, then sub-10 — that's almost an order of magnitude
per step down in device class, which is the quantitative case for
flying the smallest chip that fits the job."

**Key numbers:** 427/1280 LC = 33.4%; 592 mW → 90 mW → sub-10 mW.

## Slide 11 — Sustainability Impact (3:45–4:10)

**Say:** "This is the 25% of scoring that matters as much as the
engineering. Halving average power roughly halves battery cycling —
143.6 down to 74.9 equivalent full cycles per year, a 91.7% cycle-life
extension. That's a satellite that lives twice as long before its
battery — the one truly consumable part — wears out. Thermal
dissipation falls about 48%, simplifying thermal design. And because
the deployed toolchain is entirely open-source with zero licensing
cost, any university team can reproduce, repair, or extend this
exact platform."

**Key numbers:** 143.6 → 74.9 cycles/yr (−47.8%, +91.7% life); −48%
thermal.

## Slide 12 — Results (4:10–4:25)

**Say:** "To summarize in one table: baseline 242.55 milliwatts,
384.04 milliwatt-hours per orbit. Duty-cycled: 126.54 milliwatts,
200.35 milliwatt-hours — 47.83% saved. That's the number to remember."

**Key number:** **47.83%** reduction in orbital energy consumption.

## Slide 13 — Future Work (4:25–4:35)

**Say:** "What's next: live power measurement with the INA226 to
replace simulated numbers with measured ones, full I2C sensor
integration, real UART telemetry, a path from FPGA to ASIC, PCB
design, and ultimately a flight-ready CubeSat implementation."

*(Say it fast — this is a list slide, don't dwell.)*

## Slide 14 — Q&A (4:35–4:40)

**Say:** "That's Jenga — sustainable, open-source, FPGA-based. Happy to
take questions, and then I'll show it running live."

*(Transition slide — hands off either to Q&A or straight into the
live demo, per the judging format. Confirm which order onsite.)*

## Slide 15 — Thank You / Team (4:40–4:45)

**Say:** "Thank you — and thanks to the team who made this possible."
*(Point to each photo by name as you say it — fill in your teammates'
names here before you go on stage.)*

---

## Q&A bank (unchanged from PRESENTATION_PLAN.md — still accurate)

1. **"Is 47.83% real or optimistic?"** — Datasheet supply currents,
   deterministic phase model, control/monitoring overhead charged
   inside the optimized numbers. Documented limits: instantaneous mode
   transitions, fixed 38-min eclipse.
2. **"Why FPGA instead of a low-power MCU?"** — The reference model
   *is* MCU-based; the FPGA OBC removes the always-on CPU entirely,
   making power policy hardware-native. Static-power ladder: 592 → 90
   → sub-10 mW. No proprietary runtime either.
3. **"What's measured vs. modeled?"** — Modeled: power scenarios
   (datasheet currents). Measured/tool-verified: all utilization and
   timing on three toolchains, working bitstream on real silicon.
   Roadmap item adds INA226 live measurement.
4. **"Radiation / space qualification?"** — This prototype demonstrates
   architecture, not flight qualification; the same RTL retargets
   rad-tolerant parts (portability already proven across 3 vendors'
   tools).
5. **"Why RLE, not a stronger codec?"** — Fits in 1280 LC with zero
   BRAM; telemetry is run-heavy; compression only needs to beat
   radio-on time, not win a benchmark.
6. **"Single point of failure — one FPGA?"** — Safe-mode policy +
   watchdog-style POR; modularity (PMEP) isolates subsystem faults; a
   flight version would add TMR on the ~160-LUT core (cheap at this
   size — this is aspirational, not implemented today, say so if
   pressed).
7. **"MP1584 from a 1S cell — dropout?"** — Known, documented risk:
   below ~3.6 V the buck hits dropout at 27.5% SOC; the 35% safe-mode
   threshold gives a 7.5-point cushion; buck-boost swap is a roadmap
   item.
8. **"Did you use AI?"** — Yes, disclosed in `docs/AI_DISCLOSURE.md`
   (Claude Code for engineering assistance; every number reproduces
   from committed code).
