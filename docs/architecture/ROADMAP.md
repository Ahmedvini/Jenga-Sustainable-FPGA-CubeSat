# Roadmap

Post-submission engineering plan. R-numbers are referenced from the
README and architecture doc. Constraint for all items: fit iCE40HX1K
(see resource budget, SYSTEM_ARCHITECTURE.md §8); FSM-only, no soft CPU.

| # | Item | Outcome |
|---|---|---|
| R1 | Real UART TX (115200 8N1) replacing the `uart_debug` stub, + self-checking TB | live telemetry to the laptop |
| R2 | I2C master FSM + round-robin sensor sequencer (6 devices, BRAM result store), + TB with I2C slave model | real sensor data into the datapath |
| R3 | Telemetry FSM: integrate `packet_encoder` + `telemetry_buffer` (move FIFO to SB_RAM4K), drain gated by `comms_power_en` | end-to-end sensors→UART chain |
| R4 | Close the loop on policy: BH1750 → measured sunlight into `orbit_controller`; INA226 SOC proxy → safe-mode threshold in RTL (mirrors `fpga_activation_policy`) | measured, not scheduled, orbit state |
| R5 | Measured-vs-simulated power report: log INA226 over one demo orbit, compare with `results/csv/scenario_phase_power.csv` | strongest possible evidence artifact |
| R6 | Rename `fpga_accelerator_top` → `obc_top` and regenerate all synthesis reports (Vivado ×2 + iCEstick) in one commit | naming matches architecture |
| R7 | Rename reference-model load labels to class-generic names and regenerate `results/` + evidence sheet | decouple docs from legacy part names |
| R8 | MP1584 dropout decision: characterize 3.3 V rail vs battery voltage; keep, swap to buck-boost, or lower rail to 3.0 V | closes risk P1 |
| R9 | If R1–R4 exceed ~85% LC: drop CAN path from board build or migrate to iCE40UP5K (same flow) | guaranteed fit |
| R10 | Fold `simulation/subsystems/` + `power_model.py` duplicate current tables into one time-stepped engine (long-standing planned refactor) | single source of truth |
