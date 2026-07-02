# EcoSat — Equipment and Safety Declaration

**AESS Sustainability Hackathon 2026 — Challenge 1**
Author: Ahmed Elsheikh (ahmed.elsheikh@ejust.edu.eg) · Date: 2026-07-03

## Equipment brought onsite

| Item | Purpose | Power source |
| --- | --- | --- |
| 1 × laptop | Runs the live demo (Python simulation, Icarus Verilog RTL simulation, compiled PMEP C demo) | Internal battery / standard mains adapter |
| 1 × Lattice iCEstick FPGA evaluation board | Runs the accelerator RTL on real silicon (LED orbit/power-mode demo) | USB from the laptop (5 V, < 2.5 W) |
| Small sensor breakout modules (candidates: TMP117 temperature, ADXL345 accelerometer, INA3221/INA219 current monitor — final selection in progress) + breadboard and jumper wires | CubeSat prototype sensing demo | 3.3 V from USB-powered board rails (< 1 W total) |

All hardware is USB-powered from the laptop; no external power supplies,
no mains-connected custom hardware.

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

The sensor selection for the CubeSat prototype is still being finalized;
any sensor used will be a low-voltage (≤ 5 V) I2C/SPI breakout module of
the classes listed above — no RF transmitters, no lithium cells, no
actuators. If the final selection differs from the candidates listed, this
declaration will be updated before the repository freeze. If the hardware
prototype is not ready in time, the demo falls back to the laptop-only
setup, which is fully self-sufficient.
