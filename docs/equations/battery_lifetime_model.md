# Battery Lifetime Model

Battery capacity:

```text
battery_Wh = voltage_V * capacity_mAh / 1000
```

Equivalent full cycles per year:

```text
cycles_year = daily_energy_Wh * 365 / battery_Wh
```

Lifetime extension estimate:

```text
extension_percent = (baseline_cycles / optimized_cycles - 1) * 100
```
