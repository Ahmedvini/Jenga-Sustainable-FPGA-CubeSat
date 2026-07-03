"""Power-budget primitives and scenario calculations.

Flight REFERENCE model: load names/currents (STM32L496-class OBC,
CC1120-class radio, ...) are the documented datasheet basis of the
baseline-vs-optimized comparison. The bench prototype implements the
same policy on an FPGA-based OBC (iCE40HX1K); see docs/architecture/.
Do not rename loads without regenerating results/ and the evidence
sheet.
"""

from dataclasses import dataclass

from simulation.constants import ORBIT_MINUTES, SYSTEM_VOLTAGE_V


@dataclass(frozen=True)
class Load:
    name: str
    current_ma: float
    voltage_v: float = SYSTEM_VOLTAGE_V

    @property
    def power_mw(self) -> float:
        return self.current_ma * self.voltage_v


@dataclass(frozen=True)
class Phase:
    name: str
    duration_min: float
    loads: tuple[Load, ...]

    @property
    def total_power_mw(self) -> float:
        return sum(load.power_mw for load in self.loads)

    @property
    def energy_mwh(self) -> float:
        return self.total_power_mw * self.duration_min / 60.0


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    phases: tuple[Phase, ...]

    @property
    def energy_per_orbit_mwh(self) -> float:
        return sum(phase.energy_mwh for phase in self.phases)

    @property
    def average_power_mw(self) -> float:
        return self.energy_per_orbit_mwh / (ORBIT_MINUTES / 60.0)


BASELINE_LOADS = (
    Load("Microcontroller, always active 80 MHz", 22.0),
    Load("Environmental sensors, continuous sampling", 18.0),
    Load("UHF transceiver, RX idle", 14.0),
    Load("Power management IC", 8.5),
    Load("Bus interface and logic", 5.0),
    Load("Memory, Flash and SRAM active", 6.0),
)


def baseline_average_power_mw() -> float:
    return sum(load.power_mw for load in BASELINE_LOADS)


MODULAR_DUTY_CYCLED = Scenario(
    "modular_duty_cycled",
    "Four-module MCU design with sunlight/eclipse duty cycling.",
    (
        Phase(
            "Sunlight",
            57.0,
            (
                Load("OBC STM32L496, active 80 MHz", 12.0),
                Load("Power module, charging and tracking", 5.2),
                Load("Sensing module, 10 Hz sample", 8.5),
                Load("Comms module, TX/RX active", 35.0),
            ),
        ),
        Phase(
            "Eclipse",
            38.0,
            (
                Load("OBC STM32L496, low-power 4 MHz", 2.1),
                Load("Power module, battery monitor only", 1.8),
                Load("Sensing module, 1 Hz low-rate sample", 0.9),
                Load("Comms module, rail switched off", 0.01),
            ),
        ),
    ),
)

HYBRID_FPGA_BURST = Scenario(
    "hybrid_fpga_burst",
    "Optional MCU + FPGA design: burst acceleration reduces radio active time.",
    (
        Phase(
            "Sunlight acquisition",
            51.0,
            (
                Load("OBC STM32L496, active 80 MHz", 12.0),
                Load("Power module, charging and tracking", 5.2),
                Load("Sensing module, 10 Hz sample", 8.5),
                Load("Comms module, idle rail enabled", 0.01),
                Load("Spartan FPGA accelerator, rail off", 0.01),
            ),
        ),
        Phase(
            "FPGA processing and compressed downlink",
            6.0,
            (
                Load("OBC STM32L496, active 80 MHz", 12.0),
                Load("Power module, charging and tracking", 5.2),
                Load("Sensing module, 10 Hz sample", 8.5),
                Load("Comms module, TX/RX active", 35.0),
                Load("Spartan FPGA accelerator, burst active", 28.0),
            ),
        ),
        Phase(
            "Eclipse",
            38.0,
            (
                Load("OBC STM32L496, low-power 4 MHz", 2.1),
                Load("Power module, battery monitor only", 1.8),
                Load("Sensing module, 1 Hz low-rate sample", 0.9),
                Load("Comms module, rail switched off", 0.01),
                Load("Spartan FPGA accelerator, rail off", 0.01),
            ),
        ),
    ),
)

SAFE_MODE_LOW_BATTERY = Scenario(
    "safe_mode_low_battery",
    "Operating-case check, not a savings claim: battery SOC is below the 35% "
    "FPGA-activation threshold, so the scheduler sheds load to prioritize "
    "recharge. FPGA burst is refused (fpga_activation_policy), comms is "
    "limited to a 3-minute beacon, and sensing stays at low rate in sunlight.",
    (
        Phase(
            "Sunlight recovery",
            54.0,
            (
                Load("OBC STM32L496, low-power 4 MHz", 2.1),
                Load("Power module, charging and tracking", 5.2),
                Load("Sensing module, 1 Hz low-rate sample", 0.9),
                Load("Comms module, rail switched off", 0.01),
            ),
        ),
        Phase(
            "Beacon downlink",
            3.0,
            (
                Load("OBC STM32L496, active 80 MHz", 12.0),
                Load("Power module, charging and tracking", 5.2),
                Load("Sensing module, 1 Hz low-rate sample", 0.9),
                Load("Comms module, TX/RX active", 35.0),
            ),
        ),
        Phase(
            "Eclipse",
            38.0,
            (
                Load("OBC STM32L496, low-power 4 MHz", 2.1),
                Load("Power module, battery monitor only", 1.8),
                Load("Sensing module, 1 Hz low-rate sample", 0.9),
                Load("Comms module, rail switched off", 0.01),
            ),
        ),
    ),
)

SCENARIOS = (MODULAR_DUTY_CYCLED, HYBRID_FPGA_BURST, SAFE_MODE_LOW_BATTERY)
