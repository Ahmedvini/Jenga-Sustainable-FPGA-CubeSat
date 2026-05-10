# Thermal Reduction

Electrical power that is not converted to useful work becomes heat. Lower average
power therefore reduces thermal load inside the CubeSat.

The simulation reports relative thermal load as:

```text
relative_thermal_load = optimized_average_power / baseline_average_power
```

This is a first-order estimate. A final thermal model should include orbital
environment, conduction paths, radiation surfaces, and component placement.
