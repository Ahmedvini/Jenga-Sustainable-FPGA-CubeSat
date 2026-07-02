# Jenga CubeSat Prototype — Bill of Materials

Bench prototype BOM (2026-07-03). Reference simulation components
(STM32L496, CC1120, …) are a modeled dataset, not procured hardware —
see `docs/architecture/SYSTEM_ARCHITECTURE.md`.

| # | Item | Qty | Function | Key spec / note |
|--:|---|--:|---|---|
| 1 | Lattice iCEstick (iCE40HX1K-TQ144) | 1 | FPGA OBC | 12 MHz osc, USB-powered, open-source flow |
| 2 | Solar panel, 6 V 2 W monocrystalline | 1 | energy harvest | Voc ≈ 7.2 V, Vmp ≈ 6 V |
| 3 | CN3791 MPPT charger module | 1 | 1S Li-ion charge | CC/CV 4.20 V; MPPT set for 6 V panel |
| 4 | 18650 Li-ion cell | 1 | storage | single cell, protected holder |
| 5 | 18650 holder (insulated) | 1 | mounting | no direct soldering to cell |
| 6 | 1N5819 Schottky diode | 1 | reverse block | panel → charger |
| 7 | Fuse, 1 A + holder | 1 | over-current | battery discharge path |
| 8 | MP1584 buck module | 1 | 3.3 V rail | see dropout risk P1 in architecture doc |
| 9 | MPU6050 breakout (GY-521) | 1 | IMU | I2C `0x69` — **AD0 strapped high** |
| 10 | HMC5883L breakout (GY-273) | 1 | magnetometer | I2C `0x1E` |
| 11 | BH1750 breakout | 1 | light / eclipse detect | I2C `0x23` (ADDR low) |
| 12 | INA226 breakout + shunt | 1 | V/I power monitor | I2C `0x40`; high-side on battery output |
| 13 | MCP9808 breakout | 1 | temperature | I2C `0x18` |
| 14 | DS3231 breakout | 1 | RTC | I2C `0x68` (fixed) |
| 15 | IRLZ44N MOSFET (TO-220) | 1 | payload switch | logic-level; 100 kΩ pulldown + 220 Ω gate R |
| 16 | Resistors: 2× 4.7 kΩ (I2C), 100 kΩ, 220 Ω | — | pull-ups / gate | I2C pull-ups to 3.3 V |
| 17 | Breadboard + jumpers + USB cables | — | interconnect | common ground everywhere |

Explicitly **not** in the BOM: RF radio (modeled only), soft-CPU or SoC
of any kind, mains-connected custom hardware, additional lithium cells.
