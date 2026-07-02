# EcoSat — Equipment and Safety Declaration

**AESS Sustainability Hackathon 2026 — Challenge 1**
Author: Ahmed Elsheikh (ahmed.elsheikh@ejust.edu.eg) · Date: 2026-07-03

## Equipment brought onsite

| Item | Purpose | Power source |
| --- | --- | --- |
| 1 × laptop | Runs the entire live demo (Python simulation, Icarus Verilog RTL simulation, compiled PMEP C demo) | Internal battery / standard mains adapter |

No other equipment is required for the demonstration.

## Safety statement

- **No RF transmission.** The CC1120 UHF radio exists in this project only as
  a modeled electrical load in simulation. No radio hardware is present and
  nothing transmits at any time.
- **No hazardous batteries.** No lithium cells or battery packs beyond the
  laptop's own internal battery. The 7.4 V / 2000 mAh battery in the project
  is a simulation parameter only.
- **No lasers, chemicals, pressurized systems, high voltage, or moving
  mechanical parts.**
- **No network dependency.** All demo software runs locally from the
  repository; no external services are contacted during the demo.

## Contingency addendum

If an FPGA development board is added to the demo before judging (declared
stretch goal), it would be a USB-powered evaluation board (5 V, < 2.5 W, no
external power supply, no RF). This declaration will be updated and
resubmitted before the repository freeze if that happens; otherwise the
laptop-only declaration above is complete and final.
