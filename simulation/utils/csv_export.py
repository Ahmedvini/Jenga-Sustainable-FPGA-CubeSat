"""CSV export helpers."""

import csv
from pathlib import Path


def write_dict_rows(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_phase_rows(path: Path, scenarios: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["scenario", "phase", "duration_min", "load", "current_ma", "voltage_v", "power_mw"])
        for scenario in scenarios:
            for phase in scenario.phases:
                for load in phase.loads:
                    writer.writerow(
                        [
                            scenario.name,
                            phase.name,
                            f"{phase.duration_min:.2f}",
                            load.name,
                            f"{load.current_ma:.2f}",
                            f"{load.voltage_v:.2f}",
                            f"{load.power_mw:.2f}",
                        ]
                    )
