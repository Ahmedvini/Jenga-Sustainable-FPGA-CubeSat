#!/usr/bin/env python3
"""Minimal test runner for environments without pytest."""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


TEST_MODULES = [
    "tests.test_power_model",
    "tests.test_orbit_model",
    "tests.test_scheduler",
    "tests.test_fpga_models",
    "tests.test_energy_analysis",
]


def main() -> int:
    failures = 0
    total = 0
    for module_name in TEST_MODULES:
        module = importlib.import_module(module_name)
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("test_"):
                continue
            total += 1
            try:
                func()
                print(f"PASS {module_name}.{name}")
            except Exception as exc:
                failures += 1
                print(f"FAIL {module_name}.{name}: {exc}")
    print(f"{total - failures}/{total} tests passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
