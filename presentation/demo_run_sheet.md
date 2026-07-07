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
3. **Show `results/graphs/power_vs_time.png`** (~40 s): flat baseline vs.
   stepped sunlight/eclipse profile; point at the 6-minute FPGA burst spike.
4. **THE HARDWARE MOMENT** (~60 s): iCEstick already running (boots from
   flash — just plug it in). Point at the LEDs: green = sunlight/eclipse
   (~10 s orbit), D2 comms rail and D1 burst rail shutting down in
   eclipse. Then run
   **`python3 tools/telemetry_monitor.py`** — live decoded telemetry
   from the FPGA over the same USB cable. Point at one line: in ECLIPSE
   the RLE counter freezes ("compression gated off") while CAN filtering
   continues — "that is the scheduler policy, running in silicon, in the
   data." (If asked: stimulus is an on-chip LFSR; the I2C sensor
   front-end is the next integration step and the sensors are on the
   bench.)
5. **`./rtl/simulations/iverilog/run_iverilog.sh`** (~35 s): four
   self-checking testbenches print PASS against golden models —
   verification, not just "it didn't crash".
6. **`./pmep_demo` + implementation evidence** (~45 s): hot-swap
   enumeration trace; then one breath on the three-target story — same
   RTL on ZCU106 (Vivado), Zynq-7010, and iCE40HX1K (open-source flow);
   timing met everywhere; static power falls an order of magnitude per
   device-class step — fly the smallest FPGA that fits.
7. **Close** (~25 s): headline number (47.83% energy per orbit), the one
   documented limitation (instantaneous mode transitions, fixed eclipse),
   and the sustainability KPI (≈92% battery cycle-life extension). Stop
   with time to spare.

Fallback: if anything fails live, switch to the backup video
(`video/`, 75 s) and narrate over it.
