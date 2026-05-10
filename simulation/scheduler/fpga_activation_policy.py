"""Policy for activating the FPGA accelerator."""


def should_activate_fpga(workload: str, orbit_state: str, battery_soc: float) -> bool:
    high_value_workload = workload in {"compression", "sensor_fusion", "fault_detection", "can_filter"}
    return high_value_workload and orbit_state == "sunlight" and battery_soc >= 0.35
