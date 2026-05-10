from simulation.accelerators.compression_accelerator_model import rle_compress
from simulation.scheduler.fpga_activation_policy import should_activate_fpga


def test_rle_compression():
    assert rle_compress([1, 1, 1, 2, 2, 3]) == [(1, 3), (2, 2), (3, 1)]


def test_fpga_activation_requires_sunlight_and_soc():
    assert should_activate_fpga("compression", "sunlight", 0.8)
    assert not should_activate_fpga("compression", "eclipse", 0.8)
    assert not should_activate_fpga("compression", "sunlight", 0.2)
