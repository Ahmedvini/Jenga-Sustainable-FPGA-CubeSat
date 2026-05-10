# Power Model

For each load:

```text
P_mW = I_mA * V
```

For each orbit phase:

```text
E_phase_mWh = P_phase_mW * duration_minutes / 60
```

For a full orbit:

```text
P_average_mW = sum(E_phase_mWh) / (orbit_minutes / 60)
```

The simulation uses a 95-minute orbit with 57 minutes sunlight and 38 minutes
eclipse.
