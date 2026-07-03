# Jenga (EcoSat) — Equipment and Safety Declaration

**AESS Sustainability Hackathon 2026 — Challenge 1**
Author: Ahmed Elsheikh (ahmed.elsheikh@ejust.edu.eg) · Date: 2026-07-03

## Equipment brought onsite

| Item | Purpose | Power source |
| --- | --- | --- |
| 1 × laptop | Live demo (Python simulation, RTL simulation, PMEP C demo, UART ground station) | Internal battery / standard mains adapter |
| 1 × Lattice iCEstick FPGA board (iCE40HX1K) | CubeSat OBC prototype — runs the scheduler/power/telemetry RTL | USB from the laptop (5 V, < 2.5 W) |
| 1 × 18650 Li-ion cell (single cell, in a protected holder) | Prototype energy storage | Charged only via the CN3791 board below |
| 1 × CN3791 MPPT solar charge controller module | CC/CV Li-ion charging with over-charge termination | Solar panel input only |
| 1 × 6 V / 2 W monocrystalline solar panel | Energy harvesting demo (desk-lamp illuminated indoors) | Passive source, ≤ 2 W |
| 1 × MP1584 buck converter module | Regulated 3.3 V sensor rail | Battery via fuse |
| Protection parts: 1 A fuse, 1N5819 Schottky diode | Over-current and reverse-current protection | — |
| I2C sensor breakouts: MPU6050, HMC5883L, BH1750, INA226, MCP9808, DS3231 | Attitude, magnetic, light, power, temperature, and time sensing | 3.3 V rail (< 1 W total) |
| 1 × IRLZ44N MOSFET + small resistive payload (LED board) | Payload power-switch demo | 3.3 V rail |
| Breadboard, jumper wires, USB cables | Interconnect | — |

## Battery safety statement (18650 Li-ion)

- **One** single cell, no series/parallel packs; total stored energy ≈ 9–12 Wh.
- Charged **only** through the CN3791 CC/CV charger (4.2 V termination);
  never charged unattended and never charged from mains directly.
- Discharge path is protected by a **1 A fuse**; worst-case system load
  is < 0.5 A at 3.3 V.
- Cell is carried and stored in an insulated holder; terminals are
  never exposed; no soldering directly to the cell.
- If the venue restricts loose lithium cells, the demo falls back to
  USB-only power (see contingency below) with zero functional loss to
  the FPGA demo.

## General safety statement

- **No RF transmission.** The UHF radio exists only as a modeled
  electrical load in simulation. Prototype telemetry uses wired UART.
- **No lasers, chemicals, pressurized systems, high voltage, or moving
  mechanical parts.** Highest voltage present is the ~7 V open-circuit
  solar panel.
- **No mains-connected custom hardware.** Only the laptop uses mains.
- **No network dependency.** All demo software runs locally.

## Contingency addendum

If any hardware element is unavailable or restricted onsite, the demo
degrades gracefully: (1) solar/battery chain replaced by USB 5 V into
the MP1584; (2) sensors reduced to any available subset (single shared
I2C bus, hot-pluggable); (3) full laptop-only fallback (simulation +
RTL testbenches + PMEP demo), which is self-sufficient. Any change to
this equipment list before the repository freeze will be reflected in
an updated declaration.
