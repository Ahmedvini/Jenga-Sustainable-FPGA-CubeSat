# Live Demo Run Sheet (5-minute cap)

Exact sequence, rehearsed against a stopwatch. Every number spoken must
match `results/reports/simulation_summary.md` and the Final Evidence Sheet.

1. **One-sentence core function** (~15 s): orbit-aware duty-cycled power
   switching across hot-swap modules, managed by the PMEP plug-and-play
   protocol, with optional FPGA burst acceleration.
2. **`python3 simulation/main.py`** (~60 s): one command regenerates every
   CSV, the report, and all plots. Read the printed lines: baseline
   242.55 mW → duty-cycled 126.54 mW (47.83% saved) → FPGA burst 70.41 mW
   (70.97%) → safe mode 27.28 mW (policy check, not a savings claim).
3. **Show `results/graphs/power_vs_time.png`** (~35 s): flat baseline vs.
   stepped sunlight/eclipse profile; point at the 6-minute FPGA burst spike.
4. **`./rtl/simulations/iverilog/run_iverilog.sh`** (~45 s): three
   self-checking testbenches print PASS against golden models — verification,
   not just "it didn't crash".
5. **`./pmep_demo`** (~45 s): live hot-swap enumeration and orbit-driven
   power-mode switching trace.
6. **Power-chain hardware** (~35 s): desk lamp on the solar panel →
   CN3791 MPPT charging the 18650 → fused output → MP1584 delivering a
   regulated 3.3 V rail (show the multimeter / indicator LED). One
   line: "the switched rails in the model exist in copper on this
   bench, not just in the spreadsheet."
7. **Implementation evidence** (~25 s): same RTL implemented on three
   targets — ZCU106 (Vivado), Zynq-7010, and iCE40HX1K via a fully
   open-source flow; timing met everywhere; static power falls an order of
   magnitude per device-class step, which is why the flight part is the
   smallest FPGA that fits.
8. **Close** (~25 s): headline number (47.83% energy per orbit), the one
   documented limitation (instantaneous mode transitions, fixed eclipse),
   and the sustainability KPI (≈92% battery cycle-life extension). Stop
   with time to spare. (Running total ≈ 4:45 — keeps the 15 s buffer.)

Fallback: if anything fails live, switch to the backup video
(`video/`, 75 s) and narrate over it. If the battery/solar chain is
restricted onsite, run the rail from USB 5 V into the MP1584 (per the
safety declaration contingency) and say so plainly.
