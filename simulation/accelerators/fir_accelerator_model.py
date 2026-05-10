"""FIR accelerator estimate."""

from simulation.accelerators.latency_models import speedup


def estimated_fir_runtime_ms(mcu_runtime_ms: float) -> float:
    return mcu_runtime_ms / speedup("fir")
