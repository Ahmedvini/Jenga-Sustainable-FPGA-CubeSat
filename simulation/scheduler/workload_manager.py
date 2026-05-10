"""Workload classification for MCU vs FPGA execution."""


def assign_processor(workload: str) -> str:
    if workload in {"compression", "sensor_fusion", "can_filter"}:
        return "fpga"
    return "mcu"
