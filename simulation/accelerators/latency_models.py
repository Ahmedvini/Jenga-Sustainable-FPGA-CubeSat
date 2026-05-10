"""Latency assumptions for MCU and FPGA execution."""


def speedup(workload: str) -> float:
    return {"compression": 6.0, "sensor_fusion": 4.0, "can_filter": 5.0, "fir": 8.0}.get(workload, 1.0)
