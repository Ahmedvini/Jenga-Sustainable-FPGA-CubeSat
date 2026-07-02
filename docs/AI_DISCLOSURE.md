# EcoSat — AI and External Resource Disclosure

**AESS Sustainability Hackathon 2026 — Challenge 1**
Author: Ahmed Elsheikh (ahmed.elsheikh@ejust.edu.eg) · Date: 2026-07-03

## AI tools used

**Claude Code (Anthropic)** was used as a development assistant throughout the
project for:

- Drafting and refactoring the Python power/energy simulation
  (`simulation/`), its tests (`tests/`), and the plotting code.
- Drafting Verilog modules and self-checking testbenches (`rtl/`) and the
  PMEP protocol demo (`src/pmep_module_manager.c`).
- Writing and editing project documentation (README, evidence sheet,
  presentation outline, this disclosure).
- Reviewing the repository for inconsistencies between documented and
  computed results, and planning the final-phase work.

All AI-assisted code was executed, tested, and reviewed by the author. The
system architecture, component selection, power-mode strategy, scenario
definitions, and all datasheet-derived current values are the author's design
decisions; the author can explain and defend every part of the submission.

## External software

| Resource | Use |
| --- | --- |
| Python 3 (standard library) | Core simulation — no third-party runtime dependency |
| matplotlib | Generating result plots in `results/graphs/` |
| pytest | Optional test runner (tests also run dependency-free via `tests/run_tests.py`) |
| Icarus Verilog (iverilog/vvp) | RTL simulation of the FPGA accelerator modules |
| AMD Vivado 2025.2 | Out-of-context synthesis/implementation reports (ZCU106 and Zynq-7010 targets) |
| GCC | Compiling the PMEP protocol demonstration |

## External references

- Component datasheets used for load currents and design justification
  (stored in `docs/references/`): TI CC1120, ST STM32L496, AMD/Xilinx Spartan
  FPGA family, TI TMP117, ADI ADXL345, TI INA3221, TI TPS63020, ADI LTC4412.
- Published papers on hardware-accelerated telemetry compression and
  small-satellite power management (stored in `docs/references/papers/`),
  used as background for the FPGA burst-processing concept.

No proprietary, licensed, or third-party project code was copied into this
repository. All Verilog, C, and Python source in the repository was written
for this project.
