#!/usr/bin/env python3
"""Behavioral electrical simulation of the Jenga bench circuit.

Simulates the full power chain drawn in docs/architecture/schematic.png:

    Solar 6V/2W -> 1N5819 -> CN3791 MPPT -> 18650 (1S) -> 1A fuse
        -> MP1584 buck (3.3V) -> six I2C sensors + IRLZ44N payload switch

Each stage is a datasheet-parameterized behavioral model (no public
SPICE models exist for the CN3791/MP1584 modules, so component-level
SPICE is not possible; this is the honest system-level alternative).
The simulation is deterministic and time-stepped at 1 s across whole
orbits, using the same 57/38-minute sunlight/eclipse profile as the
flight reference model.

Outputs (regenerate with `python3 simulation/bench/circuit_model.py`):
    results/reports/bench_evidence_sheet.md
    results/csv/bench_power_budget.csv
    results/csv/bench_orbit_timeseries.csv

The iCEstick FPGA is USB-powered during development (see schematic
section 2) and is deliberately NOT a load on this battery rail; the
FPGA core's own mW-class power is characterized separately in
rtl/synthesis_reports/.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.constants import (
    ECLIPSE_MINUTES,
    ORBIT_MINUTES,
    SUNLIGHT_MINUTES,
    SYSTEM_VOLTAGE_V,
)
from simulation.utils.csv_export import write_dict_rows


# ---------------------------------------------------------------------------
# Stage models (schematic section numbers in comments)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SolarPanel:  # section 1
    rated_power_w: float = 2.0
    v_mp: float = 6.0
    v_oc: float = 7.2

    def power_w(self, illumination: float) -> float:
        return self.rated_power_w * max(0.0, min(1.0, illumination))


@dataclass(frozen=True)
class SchottkyDiode:  # section 1, D1 1N5819
    v_forward: float = 0.30

    @property
    def transfer_efficiency(self) -> float:
        return (SolarPanel().v_mp - self.v_forward) / SolarPanel().v_mp


@dataclass(frozen=True)
class Cn3791Mppt:  # section 1
    efficiency: float = 0.87          # PWM MPPT charger, typical
    v_charge_cv: float = 4.20         # single-cell CC/CV termination
    i_charge_max_a: float = 2.0       # module limit


@dataclass(frozen=True)
class Battery18650:  # section 1
    capacity_mah: float = 2600.0
    r_internal_ohm: float = 0.050
    # SOC% -> open-circuit voltage, generic Li-ion NMC curve
    ocv_points: tuple[tuple[float, float], ...] = (
        (0, 3.00), (5, 3.30), (10, 3.45), (20, 3.55), (30, 3.62),
        (40, 3.67), (50, 3.72), (60, 3.78), (70, 3.84), (80, 3.91),
        (90, 4.02), (100, 4.20),
    )

    def ocv(self, soc: float) -> float:
        soc = max(0.0, min(100.0, soc))
        pts = self.ocv_points
        for (s0, v0), (s1, v1) in zip(pts, pts[1:]):
            if soc <= s1:
                return v0 + (v1 - v0) * (soc - s0) / (s1 - s0)
        return pts[-1][1]

    def loaded_v(self, soc: float, discharge_a: float) -> float:
        return self.ocv(soc) - discharge_a * self.r_internal_ohm


@dataclass(frozen=True)
class Fuse:  # section 1, F1
    rating_a: float = 1.0


@dataclass(frozen=True)
class Mp1584Buck:  # section 1
    v_out: float = SYSTEM_VOLTAGE_V
    efficiency: float = 0.85          # light-load typical
    dropout_v: float = 0.30           # min input headroom above v_out

    @property
    def v_in_min(self) -> float:
        return self.v_out + self.dropout_v

    def input_power_w(self, output_power_w: float) -> float:
        return output_power_w / self.efficiency


@dataclass(frozen=True)
class PayloadSwitch:  # section 5, Q1 IRLZ44N
    r_ds_on_ohm: float = 0.050        # conservative at Vgs = 3.3 V
    payload_current_a: float = 0.050  # demo payload (LED board)
    sunlight_duty: float = 0.10       # bursty enable from power_controller


@dataclass(frozen=True)
class SensorLoad:  # section 3
    name: str
    i2c_addr: str
    active_ma: float      # sunlight sample rate
    low_rate_ma: float    # eclipse/safe 1 Hz duty-cycled


SENSORS = (
    SensorLoad("MPU6050 IMU (accel+gyro)", "0x69", 3.80, 0.05),
    SensorLoad("HMC5883L magnetometer", "0x1E", 0.10, 0.005),
    SensorLoad("BH1750 light sensor", "0x23", 0.12, 0.01),
    SensorLoad("INA226 power monitor", "0x40", 0.33, 0.33),
    SensorLoad("MCP9808 temp sensor", "0x18", 0.20, 0.10),
    SensorLoad("DS3231 RTC", "0x68", 0.20, 0.20),
    SensorLoad("I2C pull-ups (avg, 2x4.7k)", "-", 0.30, 0.05),
)

PANEL = SolarPanel()
DIODE = SchottkyDiode()
MPPT = Cn3791Mppt()
BATTERY = Battery18650()
FUSE = Fuse()
BUCK = Mp1584Buck()
PAYLOAD = PayloadSwitch()

SAFE_MODE_SOC_THRESHOLD = 35.0  # mirrors fpga_activation_policy


# ---------------------------------------------------------------------------
# Rail budget per operating mode
# ---------------------------------------------------------------------------


def sensors_ma(mode: str) -> float:
    if mode == "sunlight_active":
        return sum(s.active_ma for s in SENSORS)
    return sum(s.low_rate_ma for s in SENSORS)


def rail_ma(mode: str) -> float:
    """Average 3.3 V rail current for a mode, payload duty included."""
    ma = sensors_ma(mode)
    if mode == "sunlight_active":
        ma += PAYLOAD.payload_current_a * 1000.0 * PAYLOAD.sunlight_duty
    return ma


def rail_peak_ma() -> float:
    """Worst case: all sensors active and payload switched on."""
    return sensors_ma("sunlight_active") + PAYLOAD.payload_current_a * 1000.0


def fuse_peak_a(soc: float = 0.0) -> float:
    """Peak fuse current: buck input at worst-case (lowest) battery V."""
    rail_w = rail_peak_ma() / 1000.0 * BUCK.v_out
    v_bat = BATTERY.ocv(soc)
    return BUCK.input_power_w(rail_w) / v_bat


def dropout_soc_floor() -> float:
    """SOC below which the loaded battery voltage falls under buck V_in_min."""
    i_dis = BUCK.input_power_w(rail_peak_ma() / 1000.0 * BUCK.v_out) / BUCK.v_in_min
    soc = 100.0
    while soc > 0.0 and BATTERY.loaded_v(soc, i_dis) >= BUCK.v_in_min:
        soc -= 0.1
    return round(soc, 1)


def full_dark_autonomy_h(mode: str) -> float:
    """Hours from 100% SOC to the dropout floor with zero solar input."""
    usable_mah = BATTERY.capacity_mah * (100.0 - dropout_soc_floor()) / 100.0
    rail_w = rail_ma(mode) / 1000.0 * BUCK.v_out
    i_bat_ma = BUCK.input_power_w(rail_w) / BATTERY.ocv(50.0) * 1000.0
    return usable_mah / i_bat_ma


# ---------------------------------------------------------------------------
# Time-stepped orbit simulation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OrbitSummary:
    orbits: int
    harvested_mwh_per_orbit: float
    consumed_rail_mwh_per_orbit: float
    consumed_battery_mwh_per_orbit: float
    eclipse_soc_drop_pct: float
    soc_min_pct: float
    soc_max_pct: float
    energy_margin_percent: float
    dropout_events: int


def simulate(orbits: int = 10, start_soc: float = 60.0, dt_s: float = 1.0):
    """Run the electrical simulation; returns (per-minute samples, summary)."""
    orbit_s = ORBIT_MINUTES * 60.0
    sun_s = SUNLIGHT_MINUTES * 60.0

    soc = start_soc
    samples: list[dict[str, object]] = []
    harvested_wh = 0.0
    rail_wh = 0.0
    battery_out_wh = 0.0
    soc_min, soc_max = soc, soc
    eclipse_start_soc = None
    eclipse_drops: list[float] = []
    dropout_events = 0

    steps = int(orbits * orbit_s / dt_s)
    for step in range(steps):
        t = step * dt_s
        t_orbit = t % orbit_s
        in_sun = t_orbit < sun_s
        illumination = 1.0 if in_sun else 0.0
        mode = "sunlight_active" if in_sun else "eclipse_low"
        if soc < SAFE_MODE_SOC_THRESHOLD:
            mode = "eclipse_low"  # safe mode: shed to low-rate rail

        # Rail draw -> buck input from the battery node
        rail_w = rail_ma(mode) / 1000.0 * BUCK.v_out
        bat_out_w = BUCK.input_power_w(rail_w)

        # Harvest -> CC/CV charge into the battery node
        panel_w = PANEL.power_w(illumination) * DIODE.transfer_efficiency
        charge_w = panel_w * MPPT.efficiency
        if soc >= 100.0:
            charge_w = min(charge_w, bat_out_w)  # float: cover load only
        v_bat = BATTERY.ocv(soc)
        charge_w = min(charge_w, MPPT.i_charge_max_a * v_bat)

        net_w = charge_w - bat_out_w
        soc += (net_w / v_bat) * (dt_s / 3600.0) / BATTERY.capacity_mah * 1000.0 * 100.0
        soc = max(0.0, min(100.0, soc))

        i_dis_a = bat_out_w / v_bat
        v_loaded = BATTERY.loaded_v(soc, i_dis_a)
        if v_loaded < BUCK.v_in_min:
            dropout_events += 1

        harvested_wh += charge_w * dt_s / 3600.0
        rail_wh += rail_w * dt_s / 3600.0
        battery_out_wh += bat_out_w * dt_s / 3600.0
        soc_min, soc_max = min(soc_min, soc), max(soc_max, soc)

        if in_sun and eclipse_start_soc is not None:
            eclipse_start_soc = None
        if not in_sun and eclipse_start_soc is None:
            eclipse_start_soc = soc
        if not in_sun and (t_orbit + dt_s) >= orbit_s and eclipse_start_soc is not None:
            eclipse_drops.append(eclipse_start_soc - soc)

        if step % int(60.0 / dt_s) == 0:  # one sample per minute
            samples.append(
                {
                    "t_min": round(t / 60.0, 1),
                    "mode": mode,
                    "illumination": illumination,
                    "rail_mw": round(rail_w * 1000.0, 3),
                    "battery_v_loaded": round(v_loaded, 4),
                    "soc_percent": round(soc, 4),
                    "charge_mw": round(charge_w * 1000.0, 1),
                }
            )

    consumed = battery_out_wh
    margin = 100.0 * (harvested_wh - consumed) / harvested_wh if harvested_wh else 0.0
    summary = OrbitSummary(
        orbits=orbits,
        harvested_mwh_per_orbit=harvested_wh * 1000.0 / orbits,
        consumed_rail_mwh_per_orbit=rail_wh * 1000.0 / orbits,
        consumed_battery_mwh_per_orbit=battery_out_wh * 1000.0 / orbits,
        eclipse_soc_drop_pct=(sum(eclipse_drops) / len(eclipse_drops)) if eclipse_drops else 0.0,
        soc_min_pct=soc_min,
        soc_max_pct=soc_max,
        energy_margin_percent=margin,
        dropout_events=dropout_events,
    )
    return samples, summary


# ---------------------------------------------------------------------------
# Evidence sheet generation
# ---------------------------------------------------------------------------


def budget_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for s in SENSORS:
        rows.append(
            {
                "load": s.name,
                "i2c_addr": s.i2c_addr,
                "active_ma": s.active_ma,
                "low_rate_ma": s.low_rate_ma,
                "active_mw": round(s.active_ma * BUCK.v_out, 3),
                "low_rate_mw": round(s.low_rate_ma * BUCK.v_out, 3),
            }
        )
    rows.append(
        {
            "load": "Payload via IRLZ44N (avg, 10% sunlight duty)",
            "i2c_addr": "-",
            "active_ma": PAYLOAD.payload_current_a * 1000.0 * PAYLOAD.sunlight_duty,
            "low_rate_ma": 0.0,
            "active_mw": round(PAYLOAD.payload_current_a * 1000.0 * PAYLOAD.sunlight_duty * BUCK.v_out, 3),
            "low_rate_mw": 0.0,
        }
    )
    return rows


def write_evidence_sheet(path: Path, summary: OrbitSummary) -> None:
    floor = dropout_soc_floor()
    peak_ma = rail_peak_ma()
    fuse_a = fuse_peak_a()
    pay_v_drop = PAYLOAD.payload_current_a * PAYLOAD.r_ds_on_ohm
    pay_diss_mw = PAYLOAD.payload_current_a**2 * PAYLOAD.r_ds_on_ohm * 1000.0

    lines = [
        "# Jenga Bench Circuit — Simulated Electrical Evidence Sheet",
        "",
        "Generated by `python3 simulation/bench/circuit_model.py` —",
        "deterministic behavioral simulation of the full power chain in",
        "`docs/architecture/schematic.png` (solar -> 1N5819 -> CN3791 MPPT ->",
        "18650 -> 1A fuse -> MP1584 buck -> 3.3V rail -> sensors + payload",
        "switch). All stage parameters are datasheet typicals; see",
        "Assumptions.",
        "",
        "## 1. Stage models",
        "",
        "| Stage (schematic §) | Model | Key parameters |",
        "| --- | --- | --- |",
        f"| Solar panel (§1) | rated-power source | {PANEL.rated_power_w:.1f} W, Vmp {PANEL.v_mp:.1f} V, Voc {PANEL.v_oc:.1f} V |",
        f"| 1N5819 (§1) | series Vf drop | Vf {DIODE.v_forward:.2f} V -> {DIODE.transfer_efficiency*100:.0f}% transfer |",
        f"| CN3791 MPPT (§1) | CC/CV behavioral charger | eff {MPPT.efficiency*100:.0f}%, CV {MPPT.v_charge_cv:.2f} V, Imax {MPPT.i_charge_max_a:.1f} A |",
        f"| 18650 (§1) | OCV curve + IR | {BATTERY.capacity_mah:.0f} mAh, Rint {BATTERY.r_internal_ohm*1000:.0f} mΩ |",
        f"| 1 A fuse (§1) | current limit check | rating {FUSE.rating_a:.1f} A |",
        f"| MP1584 (§1) | efficiency + dropout | eff {BUCK.efficiency*100:.0f}%, Vout {BUCK.v_out:.1f} V, Vin(min) {BUCK.v_in_min:.1f} V |",
        f"| IRLZ44N (§5) | Rds(on) switch | {PAYLOAD.r_ds_on_ohm*1000:.0f} mΩ at Vgs 3.3 V |",
        "",
        "## 2. 3.3 V rail budget (per mode)",
        "",
        "| Load | I2C | Active (mA) | Low-rate (mA) |",
        "| --- | --- | ---: | ---: |",
    ]
    for s in SENSORS:
        lines.append(f"| {s.name} | `{s.i2c_addr}` | {s.active_ma:.2f} | {s.low_rate_ma:.3f} |")
    lines += [
        f"| Payload via IRLZ44N (avg 10% duty) | - | {PAYLOAD.payload_current_a*1000*PAYLOAD.sunlight_duty:.2f} | 0 |",
        f"| **Total (avg)** | | **{rail_ma('sunlight_active'):.2f}** | **{rail_ma('eclipse_low'):.3f}** |",
        "",
        f"Average rail power: sunlight-active **{rail_ma('sunlight_active')*BUCK.v_out:.1f} mW**, "
        f"eclipse/safe low-rate **{rail_ma('eclipse_low')*BUCK.v_out:.2f} mW**.",
        "",
        "## 3. Peak current and fuse margin",
        "",
        f"- Worst-case rail current (all sensors active + payload on): **{peak_ma:.1f} mA**",
        f"- Worst-case fuse (buck-input) current at 0% SOC battery: **{fuse_a*1000:.0f} mA**",
        f"- **Fuse margin: {FUSE.rating_a/fuse_a:.0f}× under the {FUSE.rating_a:.0f} A rating**",
        "",
        "## 4. MP1584 dropout floor vs safe-mode policy",
        "",
        f"- Buck regulation requires battery ≥ {BUCK.v_in_min:.1f} V under load",
        f"- Simulated electrical floor: **{floor:.1f}% SOC**",
        f"- Policy safe-mode threshold: **{SAFE_MODE_SOC_THRESHOLD:.0f}% SOC** "
        f"(FPGA activation policy) — **{SAFE_MODE_SOC_THRESHOLD-floor:.1f} points above** the",
        "  electrical floor, so the scheduler sheds load before the converter",
        "  ever reaches dropout (risk P1 mitigated by policy).",
        "",
        f"## 5. Orbit simulation ({summary.orbits} orbits, 1 s steps, "
        f"{SUNLIGHT_MINUTES:.0f}/{ECLIPSE_MINUTES:.0f} min sun/eclipse)",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Energy harvested per orbit | {summary.harvested_mwh_per_orbit:.1f} mWh |",
        f"| Rail energy consumed per orbit | {summary.consumed_rail_mwh_per_orbit:.2f} mWh |",
        f"| Battery-side consumption per orbit | {summary.consumed_battery_mwh_per_orbit:.2f} mWh |",
        f"| Energy margin | {summary.energy_margin_percent:.1f}% surplus |",
        f"| SOC drop per eclipse | {summary.eclipse_soc_drop_pct:.3f} % |",
        f"| SOC range across run | {summary.soc_min_pct:.1f}% – {summary.soc_max_pct:.1f}% |",
        f"| Buck dropout events | {summary.dropout_events} |",
        "",
        "The chain is massively energy-positive: the panel recharges an",
        "entire eclipse's discharge within minutes of re-entering sunlight,",
        "and the battery sits in CV/float for most of the sunlit phase.",
        "",
        "## 6. Battery autonomy (no solar input)",
        "",
        f"- Low-rate mode (eclipse/safe rail): **{full_dark_autonomy_h('eclipse_low'):.0f} h "
        f"(≈ {full_dark_autonomy_h('eclipse_low')/24:.0f} days)**",
        f"- Active mode (sensors + payload duty): **{full_dark_autonomy_h('sunlight_active'):.0f} h "
        f"(≈ {full_dark_autonomy_h('sunlight_active')/24:.1f} days)**",
        "",
        "## 7. Payload switch (IRLZ44N)",
        "",
        f"- Drop across switch at {PAYLOAD.payload_current_a*1000:.0f} mA: {pay_v_drop*1000:.1f} mV",
        f"- Dissipation: {pay_diss_mw:.3f} mW — no heatsinking required",
        "- Gate: 3.3 V logic-level drive (100 Ω series, 100 kΩ pulldown per schematic §5)",
        "",
        "## 8. Assumptions and limitations",
        "",
        "- Behavioral stage models with datasheet-typical parameters; no",
        "  public SPICE models exist for the CN3791/MP1584 modules, so",
        "  switching transients, inrush, and ripple are not modeled.",
        "- The iCEstick FPGA is USB-powered during development (schematic",
        "  §2) and is **not** a load on this battery rail; FPGA core power",
        "  is characterized separately in `rtl/synthesis_reports/`.",
        "- Solar input is modeled at full rating in sunlight; the indoor",
        "  desk-lamp demo delivers a small fraction of it (the energy",
        "  margin absorbs this).",
        "- Sensor currents are datasheet supply currents; bus transaction",
        "  overhead is folded into the pull-up average.",
        "- Roadmap item R5 replaces these simulated figures with live",
        "  INA226 measurements on the assembled bench.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python3 simulation/bench/circuit_model.py",
        "```",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    samples, summary = simulate()
    write_dict_rows(ROOT / "results" / "csv" / "bench_power_budget.csv", budget_rows())
    write_dict_rows(ROOT / "results" / "csv" / "bench_orbit_timeseries.csv", samples)
    write_evidence_sheet(ROOT / "results" / "reports" / "bench_evidence_sheet.md", summary)
    print("- wrote results/csv/bench_power_budget.csv")
    print("- wrote results/csv/bench_orbit_timeseries.csv")
    print("- wrote results/reports/bench_evidence_sheet.md")
    print(
        f"RESULT margin={summary.energy_margin_percent:.1f}% "
        f"eclipse_soc_drop={summary.eclipse_soc_drop_pct:.3f}% "
        f"dropout_floor={dropout_soc_floor():.1f}% fuse_peak={fuse_peak_a()*1000:.0f}mA"
    )


if __name__ == "__main__":
    main()
