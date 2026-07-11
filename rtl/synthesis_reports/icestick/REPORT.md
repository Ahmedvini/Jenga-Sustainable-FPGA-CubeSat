# Jenga OBC on the iCEstick (iCE40HX1K) — Consolidated Synthesis Report

Target: Lattice iCEstick evaluation board — iCE40HX1K, TQ144 package,
12 MHz on-board oscillator. This is the **OBC deployment target** of the
Jenga CubeSat prototype (see `docs/architecture/SYSTEM_ARCHITECTURE.md`).

Flow: **Yosys 0.33 → nextpnr-ice40 0.6 → icepack → icetime** — fully
open source, no vendor tools or licenses. The build runs entirely
without hardware; `make prog` (iceprog) flashes a connected board but
is deliberately not part of `make all`.

**Last re-verified: 2026-07-06, from a clean rebuild and on hardware**
(`make clean all` + `make prog`): this build adds the R1 UART telemetry
transmitter, and its live output was captured from the board —
`docs/bench_uart_capture.txt`. All numbers below are from that build.

Reproduce from the repo root:

```bash
make -C rtl/synthesis/icestick clean all stat-core schematic
make -C rtl/synthesis/icestick prog     # only with an iCEstick connected
```

## 1. Result summary

| Metric | Result |
| --- | --- |
| Place-and-route | **success** (nextpnr-ice40, deterministic) |
| Bitstream | **built** (`icepack`, `build/icestick_top.bin`) |
| Logic cells | **922 / 1280 = 72.0%** (core alone: 157 LUT4) |
| BRAM / DSP | **0 / 16 BRAM tiles; iCE40 has no DSP — none needed** |
| I/O pins | 7 / 112 (clk + 5 LEDs + UART TX) |
| Global buffers | 8 / 8 (clk + promoted resets/enables) |
| Timing at 12 MHz | **PASSED**, WNS **+74.18 ns** |
| Fmax (nextpnr) | 110.91 MHz |
| Fmax (icetime path analysis) | 9.15 ns critical path → **109.32 MHz** |
| UART telemetry | **verified live on hardware** (115200 8N1, on-board FTDI) |

## 2. Fit verdict

**The design fits: place-and-route and bitstream generation succeed,
using 72% of the HX1K's logic cells, zero BRAM, and timing passes at
12 MHz with 74.2 ns of slack.** It could run ~9× faster than the
iCEstick clock requires. This build includes the UART telemetry
transmitter and ASCII framing (roadmap R1, verified live on hardware);
the remaining ~28% plus all 16 unused BRAM tiles are the budget for the
I2C master and sensor sequencer (R2) — tight, with mitigations planned:
see the revised resource plan in
`docs/architecture/SYSTEM_ARCHITECTURE.md` §8.

## 3. RTL portability review (Xilinx → iCE40)

- **No Xilinx-specific constructs found.** The RTL is plain
  Verilog-2001: no primitives (BUFG/MMCM/DSP48), no IP cores, no vendor
  attributes. Nothing needed to be rewritten.
- **I/O count, not logic, was the only porting obstacle.**
  `fpga_accelerator_top` exposes 132 port bits; the HX1K-TQ144 has ~96
  user I/Os. The deployment wrapper `icestick_top.v` keeps the full
  core on-chip: a 32-bit LFSR drives all core inputs (packets arrive in
  visible bursts) and every output cone reaches the five on-board LEDs,
  so synthesis cannot trim any core logic.
- **Human-visible demo timing.** `orbit_controller` has a `PRESCALER`
  parameter (default 1 = original behavior everywhere else; testbenches
  and Vivado evidence unaffected). The iCEstick build sets 1,250,000,
  so one 95-tick orbit takes ≈9.9 s.
- **No DSP blocks on iCE40**: the FIR's constant coefficients
  (1, 2, 2, 1) map to shift/add logic (SB_CARRY chains). No multiplier
  hardware needed — confirmed by the zero-DSP result on the Vivado
  targets too.
- **Register init values** (wrapper POR counter and LFSR seed) use
  iCE40's supported FF initialization; the core itself uses only
  synchronous reset.

## 4. Utilization

From `yosys_stat_core.rpt` (core alone), `yosys_stat.rpt`
(core + wrapper), and `nextpnr_report.json` (placed and routed):

| Metric | Core only | Core + demo wrapper | Placed (nextpnr) | HX1K capacity | Used |
| --- | ---: | ---: | ---: | ---: | ---: |
| SB_LUT4 | 157 | 702 | — | — | — |
| Flip-flops (SB_DFF*) | 120 | 429 | — | — | — |
| SB_CARRY | 89 | 291 | — | — | — |
| Logic cells (LC) | — | — | **922** | 1280 | **72.0%** |
| BRAM (4 kbit) | 0 | 0 | 0 | 16 | 0% |
| I/O pins | — | 7 | 7 | 112 (die) | 6.3% |
| Global buffers | — | — | 8 | 8 | 100% |

The wrapper's growth over the core (LFSR, orbit prescaler, burst-window
counter, LED pulse-stretchers, and now the R1 UART transmitter with its
ASCII frame sequencer and telemetry counters) makes the demo observable
at human speed and streams live state to the laptop; the core itself is
the 157-LUT4 column. The frame character mux is the single largest
wrapper block — moving it into an SB_RAM4K message ROM is the first
planned optimization for R2 headroom. All 8 global
buffers are used because nextpnr promotes the clock plus high-fanout
reset/enable nets; staged modules on the same clock domain will not
need more.

## 5. Timing and clock

Clock: 12 MHz (83.33 ns period), constrained in nextpnr (`--freq 12`)
and independently checked by icetime (`-c 12`).

| Source | Result |
| --- | --- |
| nextpnr achieved Fmax | **110.91 MHz** |
| icetime critical path | **9.15 ns → 109.32 MHz** |
| icetime 12 MHz check | **PASSED** |
| **WNS at 12 MHz** | **+74.18 ns** (83.33 − 9.15) |

Raw data: `icetime_timing.rpt` (full critical-path breakdown),
`nextpnr_report.json`; the run logs (`nextpnr.log`, `yosys.log`)
regenerate locally and are excluded from git by the global `*.log`
rule.

## 6. Power

The open-source IceStorm flow has **no power estimator**, so unlike the
Vivado targets there is no tool-generated power report. From the iCE40
family datasheet, the HX1K is a sub-10 mW-class device (static core
current at 1.2 V in the sub-mA range, plus small dynamic power at
12 MHz for a ~33%-utilized design) — clearly below both Vivado targets'
static figures. Treat this as a datasheet-order estimate, not a
measured or tool-computed value. Roadmap item R5 replaces this estimate
with live INA226 measurements on the bench.

## 7. Visual artifacts

All three regenerate from the current netlist (2026-07-03 build):

| File | What it shows | How to read it |
| --- | --- | --- |
| `schematic.svg` (33 KB) | Top-level block view of the OBC core from `yosys show`: orbit controller, scheduler, power controller, CAN packet filter, RLE compressor, FIR filter and their interconnect | Confirms the module structure matches `docs/architecture/` §7 |
| `placed.svg` (330 KB) | nextpnr placement map of the HX1K die — every used logic cell, IO, and global buffer at its physical location | The occupied cells vs empty tiles visualize the ~66% headroom left for the staged OBC modules |
| `routed.svg` (~22 MB) | Full routing view — every wire segment of the routed design | Open in a browser, not an editor; shows congestion-free routing at 33% fill |

Regenerate the placement/routing views with:

```bash
cd rtl/synthesis/icestick
nextpnr-ice40 --hx1k --package tq144 --freq 12 \
    --json build/icestick_top.json --pcf icestick.pcf \
    --asc build/icestick_top.asc \
    --placed-svg ../../synthesis_reports/icestick/placed.svg \
    --routed-svg ../../synthesis_reports/icestick/routed.svg
```

## 8. Artifact index

| File | Producer | Tracked in git |
| --- | --- | --- |
| `REPORT.md` | this consolidated report | ✅ |
| `yosys_stat.rpt` | `yosys tee stat` — core + wrapper cell counts | ✅ |
| `yosys_stat_core.rpt` | `make stat-core` — core-only cell counts | ✅ |
| `nextpnr_report.json` | nextpnr `--report` — utilization + fmax, machine-readable | ✅ |
| `icetime_timing.rpt` | `make timing` — critical-path breakdown, 12 MHz check | ✅ |
| `schematic.svg` | `make schematic` (yosys show) | ✅ |
| `placed.svg` | nextpnr `--placed-svg` | ✅ |
| `routed.svg` | nextpnr `--routed-svg` | ✅ (large, ~22 MB) |
| `yosys.log`, `nextpnr.log` | full tool logs | ❌ (`*.log` gitignored; regenerate with `make`) |
| `build/icestick_top.{json,asc,bin}` | netlist, placement, bitstream | ❌ (`build/` gitignored; regenerate with `make`) |

## 9. Cross-vendor comparison

Same RTL, three targets, three independent toolchains. The Vivado
columns were re-verified 2026-07-03 against the current RTL (fresh
out-of-context run: identical 44 LUTs / 90 FFs, WNS +8.249 ns).

| | ZCU106 (XCZU7EV) | Zynq-7010 | iCEstick (iCE40HX1K) |
| --- | ---: | ---: | ---: |
| Toolchain | Vivado 2025.2 | Vivado 2025.2 | Yosys + nextpnr (open source) |
| Process | 16 nm FinFET | 28 nm | 40 nm |
| LUT type | LUT6 | LUT6 | LUT4 |
| LUTs | 44 | 43 | 157 (core) |
| Flip-flops | 90 | 90 | 120 (core) |
| BRAM / DSP | 0 / 0 | 0 / 0 | 0 / 0 |
| Timing @ 100 MHz | met, +8.25 ns | met, +4.57 ns | Fmax ≈ 109 MHz* |
| Timing @ 12 MHz (board clock) | — | — | met, +74.18 ns |
| Dynamic power | ~1 mW (tool) | ~2 mW (tool) | n/a (no tool) |
| Device static power | 592 mW (tool) | 90 mW (tool) | sub-10 mW class (datasheet) |

*The iCE40 board clock is 12 MHz; 109 MHz is the icetime path-based
Fmax estimate, marginally above the 100 MHz constraint used on the
Vivado runs.

The LUT-count difference is architectural, not a design change: iCE40
LUT4s implement less logic per cell than UltraScale+/7-series LUT6s,
and Yosys/Vivado make different carry/register-retiming choices. The
takeaway for Jenga: the OBC logic is tiny and vendor-portable, and
static leakage — which dominates every target's total power — falls by
roughly an order of magnitude with each step down in device class.
That is the quantitative argument for flying the smallest FPGA that
fits the workload, on a switched power rail.

## 10. On-hardware LED demo

The bitstream runs a human-speed demo (one orbit ≈ 9.9 s, prescaler
1,250,000):

| LED | Signal | Behavior |
| --- | --- | --- |
| D5 (green) | sunlight | on ~6 s (sunlight), off ~4 s (eclipse) |
| D1 | `fpga_power_en` | FPGA burst rail — only in sunlight with pending work |
| D2 | `comms_power_en` | comms rail — shuts off in eclipse |
| D3 | processing activity | filter/compression/FIR valids, pulse-stretched to visible flashes |
| D4 | datapath activity | XOR-fold of payload/sample outputs, edge-triggered |
| `uart_txd` (pin 8) | live telemetry | `JGA n=.. s=.. b=.. p=.. z=.. f=..` ASCII frames ~3×/s via the on-board FTDI; captured sample with the eclipse compression-gating visible: `docs/bench_uart_capture.txt` |

Flash with `make -C rtl/synthesis/icestick prog`; read telemetry at
115200 8N1 from the board's second FTDI serial port (no extra wiring —
the FTDI channel B is hard-wired to iCE40 pin 8).
