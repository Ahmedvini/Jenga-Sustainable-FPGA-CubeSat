# EcoSat / SMIS — Final Phase Win Plan

Working plan for AESH Sustainability Hackathon 2026, Challenge 1, Final Phase.
Owner: solo (code). Written 2026-07-02.

## Hard constraints

- **Today is 2026-07-02.** Final digital package (repo, evidence sheet,
  presentation, backup demo, disclosures) is due **2026-07-03, 23:59 EEST —
  tomorrow night.** That is the real deadline; everything below is sequenced
  around it.
- Onsite: 6 July (workshops, no judging) → 7 July 12:00 EEST repo freeze →
  13:30 EEST judging (15 min/team: 5-min presentation, 5-min live demo,
  4-min Q&A).
- Scoring is **75% technical, 25% sustainability**. Technical rigor and
  internal consistency is the dominant lever.
- Rules: "Continue the same challenge and core project qualified in Phase 1.
  Scope may be refined, but the project may not be replaced." → we keep the
  modular CubeSat electronics platform + PMEP + duty-cycled power concept.
  We are *rebuilding how it's proven*, not changing what it is.

## Decisions locked in this session

1. **Demo for judging = software simulation + RTL simulation, run live from
   the repo.** No physical hardware bring-up assumed. If time remains after
   4 July, stretch goal is running the RTL on a real FPGA dev board (see
   Phase 2). This matches the guide's explicit allowance for "executable
   simulation or validated analytical model."
2. **Solo developer, code only.** Plan is sequenced so that if time runs out,
   we lose the least valuable items last, not the required ones.
3. **The Python simulation is the canonical numbers going forward.** The old
   TDD docx (361.4→213.0 mW, 41.1%) is out of sync with `results/` and is
   *not* being reconciled line-by-line right now — the whole technical
   writeup is being rebuilt from the (improved) simulation instead. The TDD
   docx gets replaced/rewritten near the end of Phase 1, once the numbers it
   needs to describe are final.
4. Plan is saved here; execution happens in a following session/turn, driven
   from this checklist.

## Why this plan, not a smaller one

The guide's "What Is Not Sufficient" list is effectively the judging rubric's
failure modes. Mapping our current known gaps against it:

| Pitfall the guide warns about | Where we're currently exposed |
| --- | --- |
| "An unexplained percentage improvement or a baseline that performs a different task" | TDD docx numbers (361.4 mW) vs `results/` numbers (242.55 mW) actively disagree today |
| "Screenshots without runnable files, parameter values, units, or interpretation" | `results/graphs/` is empty — `simulation/utils/plotting.py` is a stub that writes a text placeholder, not a real plot, even though `matplotlib` is already a listed dependency |
| "A complex project that cannot demonstrate one stable core function" | `simulation/subsystems/`, `scheduler/`, `communication/`, most of `orbit/` and `accelerators/` are never imported by `simulation/main.py` — they're unused scaffolding that only unit tests touch in isolation. A judge reading the repo sees a 5-module architecture claim that the code doesn't actually run. |
| "Testing across multiple operating cases" | RTL testbenches drive stimulus and dump a `.vcd` but assert nothing — `iverilog` **is** installed here (README's claim otherwise is stale) and all three run clean, but "runs" ≠ "verified correct" |
| Missing required deliverables | `presentation/`, `video/` are empty; no evidence sheet, safety declaration, or AI disclosure exist anywhere in the repo |

Fixing these is higher-leverage than adding new features, because they're the
exact things the rubric is designed to catch.

---

## Phase 1 — MUST ship before 2026-07-03 23:59 EEST

Ordered by priority tier. If time runs out, stop at the end of a tier, not
mid-tier.

### Tier P0 — required deliverables that don't yet exist at all

These are graded checkboxes in the guide's Section 2 table. Missing any one
is a guaranteed point loss independent of code quality.

- [x] **Final Evidence Sheet** (`docs/FINAL_EVIDENCE_SHEET.md`, one page):
      problem, core function, baseline, improved case, test conditions,
      primary technical KPI, primary sustainability KPI, one limitation,
      repo link.
- [x] **Equipment and Safety Declaration** (`docs/EQUIPMENT_SAFETY_DECLARATION.md`):
      state plainly — no RF transmission, no hazardous batteries/lasers/
      chemicals/pressure/mechanical motion; demo is a laptop running Python
      + Icarus Verilog simulation only (update if a real board gets added
      in Phase 2).
- [x] **AI / External Resource Disclosure** (`docs/AI_DISCLOSURE.md`): Claude
      Code usage and what it was used for, `matplotlib`/`pytest` deps,
      datasheets already in `docs/references/` (CC1120, STM32L496, Spartan),
      any other external source.
- [x] **Backup Demo Video — script** (`video/backup_demo.md`): 60–90s screen
      capture of `python3 simulation/main.py` running + one generated plot +
      RTL testbench pass output. Script and shot list are done; the
      **recording itself is still pending** — record from a fresh clone now
      that the Phase 1 code changes have landed.
- [x] **Final Presentation** (`presentation/slide_outline.md` now, built into
      slides after): slide-by-slide talking points sized to 5 minutes.
      Outline done; building the actual slides is still pending.

### Tier P1 — fixes that directly answer the guide's stated pitfalls

- [x] **Real plots.** Replace `simulation/utils/plotting.py`'s placeholder
      with actual `matplotlib` output into `results/graphs/`: power-vs-time
      across one orbit (sunlight/eclipse annotated), baseline-vs-optimized
      bar chart, battery-cycle comparison. Call it from `simulation/main.py`
      so `python3 simulation/main.py` regenerates everything in one command
      (keeps the "reproducibility" story clean).
- [x] **Self-checking RTL testbenches.** Add expected-vs-actual comparisons
      and `PASS`/`FAIL` `$display` output (with nonzero exit on failure) to
      `tb_fir_filter.v`, `tb_rle_compressor.v`, `tb_can_filter.v`. Update
      `rtl/simulations/iverilog/run_iverilog.sh` to fail loudly if any
      testbench reports `FAIL`.
- [x] **README correction.** Remove the stale "iverilog wasn't available"
      claim (it *is* installed and all three testbenches run clean here).
      Regenerate the Key Results table from the rebuilt simulation output.
      Fix the "five cooperative modules" section so it accurately reflects
      what code is actually wired up (see P2) rather than implying all of
      `simulation/` participates in producing the numbers.
- [x] **Include the PMEP C demo as a third runnable artifact.** It already
      compiles and runs cleanly (`gcc -DPMEP_DEMO_MAIN src/pmep_module_manager.c
      -o pmep_demo && ./pmep_demo`) and produces a genuinely good console
      trace of hot-swap enumeration + orbit-based power-mode switching.
      Currently the README never tells anyone this exists or how to run it —
      add a build/run line and fold it into the live-demo run sheet (Phase 5).
- [x] **Explicit control/decision-logic overhead statement.** The guide
      requires "net savings calculation including controller, sensor,
      communication, and decision-logic overhead." Confirm in the Evidence
      Sheet that OBC active/low-power current figures already include
      scheduler and PMEP decision-logic execution (not a separately
      hidden cost) — state this explicitly so it can't be challenged in Q&A.
- [x] **One documented limitation/trade-off** (guide requires exactly this):
      e.g. mode transitions are modeled as instantaneous (no inrush/settling
      current spike), and eclipse duration is fixed rather than
      season/beta-angle dependent. State it in the Evidence Sheet and be
      ready to defend it in Q&A.
- [x] **Multiple operating cases.** (Done as `safe_mode_low_battery` in
      `power_model.py` + tests.) Add at least one alternate scenario run
      beyond the two already in `SCENARIOS` — e.g. degraded battery SOC
      (FPGA burst policy correctly refuses to activate below 35% SOC per
      `fpga_activation_policy.py`, if that logic gets wired in per P2), or a
      module-fault/hot-swap-removal case exercised through
      `pmep_module_manager.c`.

### Tier P2 — the highest-leverage technical rebuild (do only after P0+P1 are committed)

This is the single biggest "win" lever but also the biggest regression risk
right before a deadline — **do this on a branch, keep the current passing
`main` as a fallback you can submit if it runs out of time.**

- [ ] Turn the simulation into a genuine discrete time-stepped engine: drive
      it minute-by-minute using `orbit_model.state_at_minute()`,
      `mission_scheduler.power_mode_for()`, `sleep_controller`'s mode
      multipliers, and the `subsystems/*.current_for_*()` lookups — instead
      of the current hand-typed static `Load`/`Phase`/`Scenario` tables in
      `power_model.py`. This makes the "modular architecture" claim in the
      README literally true (the modules the docs describe are what
      computes the numbers), and it naturally produces genuine per-minute
      time-series data for the P1 plots instead of two flat phase averages.
      Keep the existing scenario-level API (`SCENARIOS`, `average_power_mw`,
      etc.) so `main.py`, the CSV writers, and existing tests keep working —
      or update tests deliberately, not incidentally.
  - [ ] Wire `fpga_activation_policy.should_activate_fpga()` in so the FPGA
        burst scenario is a real policy decision (workload + orbit state +
        battery SOC), not a fixed 6-minute phase.
  - [ ] Either delete `simulation/communication/*` (currently imported by
        nothing, tested by nothing) or wire it into the comms-module current
        draw. An unused, untested module sitting in the repo is a liability
        under "complex project that cannot demonstrate one stable core
        function" — don't leave orphaned code either way.
  - [ ] Reconcile the duplicate constants in `simulation/config.py` vs
        `simulation/constants.py` (same orbit/eclipse minutes defined twice)
        into one source.
- [ ] Once the engine is real, regenerate every number in README, the new
      Evidence Sheet, and a rewritten TDD to match — write these last, after
      the numbers are final, so nothing gets written twice.

---

## Phase 2 — 2026-07-04 to 2026-07-05 (buffer days before onsite)

Only start here once Phase 1 is fully committed and pushed.

- [ ] Rehearse the 5-minute live demo end-to-end against a stopwatch.
- [x] ~~If a Spartan-7/compatible FPGA dev board is actually available: load
      the RTL, show it running physically instead of only in `iverilog`.~~
      **Decided 2026-07-02: no physical board available.** Instead, the RTL
      is implemented (out-of-context) in Vivado 2025.2 for two targets:
      ZCU106 / Zynq UltraScale+ XCZU7EV (development target) and Spartan-7
      (flight-class low-power reference). Real utilization/timing/power
      reports live in `rtl/synthesis_reports/`, regenerated by
      `./rtl/synthesis/vivado/run_vivado.sh`. The flight power model keeps
      the Spartan-class FPGA; the Equipment and Safety Declaration stays
      laptop-only.
- [ ] Polish plots (labels, units, consistent color scheme across all
      generated charts).
- [ ] Deepen `docs/sustainability/lifecycle_analysis.md` — it currently
      admits "a full lifecycle assessment would add manufacturing energy,
      launch mass impact, replacement frequency, and end-of-life disposal
      assumptions" as future work. Adding even a rough quantified estimate
      for one of these strengthens the 25%-weighted sustainability score.
- [ ] Dry-run the Q&A: be ready to defend the one documented limitation, the
      "why these components" datasheet justifications, and why the FPGA
      burst scenario is presented as an extension rather than the headline
      claim.

## Phase 3 — 2026-07-06 (onsite Day 1)

- [ ] Test the live demo on whatever machine will actually be used at
      judging (not just your own laptop) — dependency drift is the #1 live
      demo failure mode.
- [ ] Confirm the backup demo video plays correctly on that machine too.

## Phase 4 — 2026-07-07, before 12:00 EEST freeze

- [ ] Final review pass: `python3 tests/run_tests.py`,
      `./rtl/simulations/iverilog/run_iverilog.sh`, and
      `python3 simulation/main.py` all run clean from a fresh clone.
- [ ] Tag the frozen commit. Confirm the Evidence Sheet's repo link points
      at the right tag/branch.

## Phase 5 — Live demo run sheet (13:30 EEST judging, 5-minute cap)

Exact sequence to rehearse and execute:

1. State the core function in one sentence (orbit-aware duty-cycled power
   switching across 4 hot-swap modules, managed by PMEP, optional FPGA
   burst mode).
2. `python3 simulation/main.py` — show it regenerate all CSVs, the report,
   and the plots in one command (reproducibility).
3. Show the power-vs-time plot — baseline flat line vs. optimized
   sunlight/eclipse step profile.
4. `./rtl/simulations/iverilog/run_iverilog.sh` — show `PASS` on all three
   testbenches (real verification, not just "it didn't crash").
5. `./pmep_demo` — show live hot-swap enumeration + orbit-based power-mode
   switching console trace.
6. State the headline number, the one documented limitation, and the
   primary sustainability KPI (battery cycle reduction / thermal drop).
7. Stop with time to spare — judges value hitting the 5-minute cap over
   cramming in more.

---

## If time runs out

Cut from the bottom up: Phase 2 stretch items first, then Tier P2 (the
engine rebuild — `main` stays on the current static-table simulation, which
already runs and passes tests, so it's a safe fallback), never Tier P0
(required deliverables) or the P1 plots/RTL-assertions fix, since those are
what directly answer the guide's stated failure modes.
